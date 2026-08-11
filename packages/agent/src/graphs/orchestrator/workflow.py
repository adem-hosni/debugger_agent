from langgraph.graph import StateGraph, END

from core.llms import orchestrator_llm
from core.states import OrchestratorState
from .nodes import *
from tools.orchestrator import get_orchestrator_tools


def build_graph():
    tools = get_orchestrator_tools()
    orchestrator_llm.bind_tools(tools)

    workflow = StateGraph(OrchestratorState)

    workflow.add_node("reverse_funcnode", reverse_funcnode)
    workflow.add_node("subagent_spawn", subagent_spawn)
    workflow.add_node("jump_funcnode", jump_funcnode)

    workflow.set_entry_point("reverse_funcnode")
    
    workflow.add_edge("reverse_funcnode", "subagent_spawn")
    workflow.add_edge("subagent_spawn", "jump_funcnode")
    
