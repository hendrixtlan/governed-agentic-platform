from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph

from agentic_platform.auth.context import ExecutionContext
from agentic_platform.config import get_settings
from agentic_platform.graph.nodes import create_nodes
from agentic_platform.graph.state import WorkflowState
from agentic_platform.llm.provider import create_agent_model


def build_graph():
    settings = get_settings()
    model = create_agent_model(settings)
    nodes = create_nodes(model)

    builder = StateGraph(WorkflowState, context_schema=ExecutionContext)
    for name, node in nodes.items():
        builder.add_node(name, node)
    builder.add_edge(START, "plan")

    # Production: replace with a durable PostgreSQL checkpointer.
    return builder.compile(checkpointer=InMemorySaver())


graph = build_graph()
