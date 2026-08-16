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
        if not node:
            return "Error: Function with this offset could not be found"
        self.__current_node = node
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
        for mode, payload in self._invoke(
            "Crack this given crackme by patching some bytes in the code. (Call get_current_function_code() to get the entrypoint assembly code)"
            "Tell me what bytes need to change before patching."
            "Navigate with your navigation tools. And when you complete tell me what things you wish me cleared at first"
        ):
            if mode == "messages":
                chunk, metadata = payload

                if chunk.content:
                    print(chunk.content, flush=True, end="")

            elif mode == "updates":
                for node_name, values in payload.items():
                    if not isinstance(values, dict):
                        continue

                    messages = values.get("messages", [])

                    if not messages:
                        continue

                    last_msg = messages[-1]

                    for tool in getattr(last_msg, "tool_calls", []):
                        print(f"\n⚡ ACTION: {tool.get('name', 'unknown')}")
                        print(f"   ARGS: {tool.get('args', {})}")

    def _invoke(self, message: str):
        self.state["messages"].append(HumanMessage(message))
        return self._agent.stream(self.state, stream_mode=["messages", "updates"])

    @tool(
        description="List all the functions thats are inside the given target function"
    )
    def list_funcmaps(self, target_function: str): ...
