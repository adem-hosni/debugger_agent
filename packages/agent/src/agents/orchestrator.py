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
            "main-orchestrator", tools=get_default_tools() + []
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

    def current_function(self) -> str:
        return self.__current_node.asm_code

    def list_functions_offsets(self) -> list[str]:
        return [node.offset for node in self.__current_node.inner_nodes]

    def set_current_offset(self, offset: str) -> str:
        self.__current_node = self.__funcmap.find_node(offset)
        if not self.__current_node:
            return "Error: Function with this offset could not be found"
        return self.__current_node.asm_code

    def spawn_subagent(self, start_offset: str):
        ...

    def debug_assembly(self): ...

    def _invoke(self, message: str):
        self.state["messages"].append(HumanMessage(message))
        self._agent.invoke(self.state)

    @tool(
        description="List all the functions thats are inside the given target function"
    )
    def list_funcmaps(self, target_function: str): ...
