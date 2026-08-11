from typing import TypedDict

class OrchestratorState(TypedDict):
    strings: dict[str, str]
    current_offset: str
    memory: list[str]


class SubAgentState(TypedDict):
    ...
