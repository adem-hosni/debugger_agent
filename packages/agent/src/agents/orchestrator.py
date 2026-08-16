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
                self.current_code,
                self.current_offset,
                self.list_functions_offsets,
                self.set_current_offset,
            ],
        )
        self.__mem_helper = MemoryHelper()
        self.__funcmap: FunctionMap | None = None
        self.__current_node: FunctionNode | None = None
        self.state: OrchestratorState = {}
        self.subagents: list[SubAgent] = []

    def bind(self, process_name: str) -> bool:
        return self.__mem_helper.attach(process_name)

    def map_functions(self):
        self.__funcmap = self.__mem_helper.build_funcmap()
        self.__current_node = self.__funcmap

    @tool(description="Returns the current function code")
    def current_code(self) -> str:
        return self.__current_node.asm_code

    @tool(description="Returns current function offset (0 = entrypoint)")
    def current_offset(self) -> str:
        return self.__current_node.asm_code

    @tool(
        description="List the functions offsets that can be called by the current function "
    )
    def list_functions_offsets(self) -> list[str]:
        return [node.offset for node in self.__current_node.inner_nodes]

    @tool(
        description="Move the current offset to a target function offset. Returns the target offset function code"
    )
    def set_current_offset(self, offset: str) -> str:
        self.__current_node = self.__funcmap.find_node(offset)
        if not self.__current_node:
            return "Error: Function with this offset could not be found"
        return self.__current_node.asm_code

    @tool(description="Patch a target memory offset by a given string bytes sequence (hexadecimal representation)")
    def patch_bytes(self, memory_offset: str, bytes_sequence: str):
        print(f"patching {memory_offset} with {bytes_sequence}")
        bytes_ = [int(byte, base=16) for byte in bytes_sequence.split(" ")]
        self.__mem_helper.patch_bytes_from_addr(int(memory_offset, base=16))

    def spawn_subagent(self, start_offset: str): ...

    def debug_assembly(self):
        for mode, payload in self._invoke("Crack this given crackme by patching some bytes in the code. Tell me what bytes need to change before patching"):
            print(f"{mode}: {payload}")

    def _invoke(self, message: str):
        self.state["messages"].append(HumanMessage(message))
        return self._agent.stream(self.state, stream_mode=["messages", "updates"])

    @tool(
        description="List all the functions thats are inside the given target function"
    )
    def list_funcmaps(self, target_function: str): ...
