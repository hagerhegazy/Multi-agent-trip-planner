"""Planner: parses the request, fans out to the agents, joins at the budget agent."""
from langgraph.graph import END, START, StateGraph
from agents import activity, budget, flight, hotels, out_agent, weather
from blackboard import Blackboard
from llm import ask_json, num

PARSE_PROMPT = """Extract trip details from the user's text. Return JSON:
{{"origin": string or null, "destination": string,
  "time": string (month, dates or season; "flexible" if unknown),
  "duration_days": integer, "travelers": integer,
  "style": "budget" | "mid-range" | "luxury", "interests": [strings]}}

User text: {text}"""


def planner_node(state: Blackboard):
    data = ask_json(PARSE_PROMPT.format(text=state["user_text"]))
    request = {
        "origin": data.get("origin"),
        "destination": data.get("destination") or state["user_text"],
        "time": data.get("time") or "flexible",
        "duration_days": max(int(num(data.get("duration_days"), 5)), 1),
        "travelers": max(int(num(data.get("travelers"), 1)), 1),
        "style": data.get("style") or "mid-range",
        "interests": data.get("interests") or [],
    }
    return {"request": request}


def build_graph(excel_tools=None):
    async def budget_node(state: Blackboard):
        return await budget.run(state, excel_tools)

    g = StateGraph(Blackboard)
    g.add_node("planner", planner_node)
    g.add_node("flight", flight.run)
    g.add_node("hotels", hotels.run)
    g.add_node("activity", activity.run)
    g.add_node("weather", weather.run)
    g.add_node("budget", budget_node)
    g.add_node("out_agent", out_agent.run)

    g.add_edge(START, "planner")
    for name in ("flight", "hotels", "activity", "weather"):   # run in parallel
        g.add_edge("planner", name)
    g.add_edge(["flight", "hotels", "activity", "weather"], "budget")  # wait for all four
    g.add_edge("budget", "out_agent")
    g.add_edge("out_agent", END)
    return g.compile()


async def run_trip(user_text: str, use_excel: bool = False, on_update=None) -> Blackboard:
    excel_tools = None
    if use_excel:
        from mcp_client import load_excel_tools
        excel_tools = await load_excel_tools()

    graph = build_graph(excel_tools)
    board: Blackboard = {"user_text": user_text}
    async for chunk in graph.astream({"user_text": user_text}, stream_mode="updates"):
        for node, update in chunk.items():
            board.update(update)
            if on_update:
                on_update(node)
    return board
