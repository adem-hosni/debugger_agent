from typing import TypedDict
from deepagents.graph import DeepAgentState

class OrchestratorState(DeepAgentState):
    strings: dict[str, str]
    current_offset: str
    memory: list[str]


class SubAgentState(TypedDict):
    ...
