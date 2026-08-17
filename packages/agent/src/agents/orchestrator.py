from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from ._base import AgentBase
from core.llms import build_orchestrator_agent
from core.states import OrchestratorState
from tools.builtin import get_default_tools
from memoryhelper.funcmap import FunctionMap, FunctionNode
from memoryhelper.memoryhelper import MemoryHelper
from .subagent import SubAgent


class OrchestratorAgent(AgentBase):
    def __init__(self):
        self._agent = build_orchestrator_agent(
            "main-orchestrator",
            tools=get_default_tools()
            + [
                tool(
                    self.get_current_function_code, description="Returns the current function code"
                ),
                tool(
                    self.get_current_function_offset,
                    description="Returns current function offset (0 = entrypoint)",
                ),
                tool(
                    self.list_functions_offsets,
                    description="List the functions offsets that can be called by the current function ",
                ),
                tool(
                    self.set_current_offset_and_get_func_code,
                    description="Move the current offset to a target function offset. Returns the target offset function code",
                ),
            ],
        )
        self.__mem_helper = MemoryHelper()
        self.__funcmap: FunctionMap | None = None
        self.__current_node: FunctionNode | None = None
        self.state: OrchestratorState = {
            "messages": [],
            "strings": {},
            "current_offset": "",
            "memory": [],
        }
        self.subagents: list[SubAgent] = []

    def bind(self, process_name: str) -> bool:
        return self.__mem_helper.attach(process_name)

    def map_functions(self):
        self.__funcmap = self.__mem_helper.build_funcmap()
        self.__current_node = self.__funcmap

    def get_current_function_code(self) -> str:
        return self.__current_node.asm_code

    def get_current_function_offset(self) -> str:
        return self.__current_node.asm_code

    def list_functions_offsets(self) -> list[str]:
        if not self.__current_node:
            return []
        return [node.offset for node in self.__current_node.inner_nodes]

    def set_current_offset_and_get_func_code(self, offset: str) -> str:
        node = self.__funcmap.find_node(offset)
        if not node or not node.asm_code:
            return f"Error: Function with this offset {offset} could not be found"
        self.__current_node = node
        if not len(self.__current_node.asm_code):
            print("#"*50)
            print("RET IS NULL")
            print("#"*50)
        return self.__current_node.asm_code

    # @tool(
    #     description="Patch a target memory offset by a given string bytes sequence (hexadecimal representation)"
    # )
    def patch_bytes(self, memory_offset: str, bytes_sequence: str):
        print(f"patching {memory_offset} with {bytes_sequence}")
        bytes_ = [int(byte, base=16) for byte in bytes_sequence.split(" ")]
        self.__mem_helper.patch_bytes_from_addr(
            int(memory_offset, base=16), bytes_, len(bytes_)
        )

    def spawn_subagent(self, start_offset: str): ...

    def debug_assembly(self):
        message = (
            "Crack this given crackme by patching some bytes in the code. "
            "(Call get_current_function_code() to get the entrypoint assembly code.)\n"
            "Tell me what bytes need to change before patching.\n"
            "Navigate with your navigation tools.\n"
            "When you complete, tell me what things you wish me cleared at first."
        )

        for mode, payload in self._invoke(message):

            # ============================================================
            # LLM TOKEN STREAM
            # ============================================================
            if mode == "messages":
                chunk, metadata = payload

                # Ignore empty chunks
                if not chunk.content:
                    continue

                # content can sometimes be a list depending on the model
                if isinstance(chunk.content, list):
                    text = ""

                    for item in chunk.content:
                        if isinstance(item, dict):
                            text += item.get("text", "")
                        elif isinstance(item, str):
                            text += item

                else:
                    text = str(chunk.content)

                if text:
                    print(text, end="", flush=True)

            # ============================================================
            # GRAPH NODE UPDATES
            # ============================================================
            elif mode == "updates":

                for node_name, values in payload.items():

                    if not isinstance(values, dict):
                        continue

                    print(
                        f"\n\n{'─' * 60}\n"
                        f"🔄 NODE: {node_name}\n"
                        f"{'─' * 60}",
                        flush=True
                    )

                    messages = values.get("messages", [])

                    if not messages:
                        continue

                    for msg in messages:

                        # ------------------------------------------------
                        # Assistant message
                        # ------------------------------------------------
                        content = getattr(msg, "content", None)

                        if content:
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict):
                                        text = item.get("text", "")
                                        if text:
                                            print(
                                                f"🤖 {text}",
                                                flush=True
                                            )
                            else:
                                print(
                                    f"🤖 {content}",
                                    flush=True
                                )

                        # ------------------------------------------------
                        # Tool calls
                        # ------------------------------------------------
                        tool_calls = getattr(msg, "tool_calls", [])

                        for tool in tool_calls:

                            name = tool.get("name", "unknown")
                            args = tool.get("args", {})

                            print(
                                f"\n⚡ TOOL CALL\n"
                                f"   ├─ {name}\n"
                                f"   └─ args: {args}",
                                flush=True
                            )

                        # ------------------------------------------------
                        # Tool result 
                        # ------------------------------------------------
                        if getattr(msg, "type", None) == "tool":

                            print(
                                f"\n🔧 TOOL RESULT\n"
                                f"{content}\n",
                                flush=True
                            )


    def _invoke(self, message: str):
        self.state["messages"].append(
            HumanMessage(content=message)
        )

        return self._agent.stream(
            self.state,
            stream_mode=["messages", "updates"],
        )
    @tool(
        description="List all the functions thats are inside the given target function"
    )
    def list_funcmaps(self, target_function: str): ...

    @property
    def function_map(self):
        return self.__funcmap
