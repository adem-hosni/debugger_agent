from abc import ABC

from memoryhelper.funcmap import FunctionMap, FunctionNode
from memoryhelper.memoryhelper import MemoryHelper
from langchain.agents.middleware.types import AgentState


class AgentBase(ABC):
    def __init__(self):
        self._agent = None
        self.__mem_helper: MemoryHelper | None = None
        self.__funcmap: FunctionMap | None = None
        self.__current_node: FunctionNode | None = None
        self.state: AgentState = {}
