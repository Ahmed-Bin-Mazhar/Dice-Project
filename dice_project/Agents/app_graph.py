from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

from .router_agent import route_question
from .db_agent import run_db_agent
from .KB_agent import run_kb_agent


class AppState(TypedDict, total=False):
    question: str
    route: str             # "db" or "kb"
    sql_query: str         # SQL string if applicable
    query_result: str      # Formatted results or human-readable answer
    query_rows: list       # Raw rows from DB
    answer: str            # KB answer or DB human-readable summary
    attempts: int
    relevance: str
    sql_error: bool


# -----------------------------
# Node functions
# -----------------------------
def router_node(state: AppState) -> AppState:
    """Classify the question and decide which agent to route to."""
    try:
        decision = route_question(state["question"])
        state["route"] = decision.route
        state["relevance"] = decision.route
    except Exception as e:
        # Fallback to KB route if routing fails
        state["route"] = "kb"
        state["relevance"] = f"Routing error: {e}"
    return state


def db_node(state: AppState) -> AppState:
    """Execute database queries and store results."""
    res = run_db_agent(state["question"])
    
    # Consistently map DB agent fields to AppState
    state["answer"] = res.get("answer", "")
    state["sql_query"] = res.get("sql_query", "")
    state["query_result"] = res.get("query_result", "")
    state["query_rows"] = res.get("query_rows", [])
    state["sql_error"] = not res.get("ok", False)
    
    return state


def kb_node(state: AppState) -> AppState:
    """Call the KB API and store full JSON response."""
    res = run_kb_agent(state["question"])
    state["answer"] = res            # store full API JSON
    state["sql_query"] = ""
    state["query_result"] = ""
    state["query_rows"] = []
    state["sql_error"] = False
    return state


# -----------------------------
# Routing logic
# -----------------------------
def route_router(state: AppState) -> str:
    """Decide the next node based on route decision."""
    return "db" if state.get("route") == "db" else "kb"


# -----------------------------
# Build and compile app graph
# -----------------------------
def build_app():
    g = StateGraph(AppState)

    # Add nodes
    g.add_node("route", router_node)
    g.add_node("db", db_node)
    g.add_node("kb", kb_node)

    # Conditional routing from route node
    g.add_conditional_edges("route", route_router, {"db": "db", "kb": "kb"})
    
    # End nodes
    g.add_edge("db", END)
    g.add_edge("kb", END)

    # Entry point
    g.set_entry_point("route")

    return g.compile()
