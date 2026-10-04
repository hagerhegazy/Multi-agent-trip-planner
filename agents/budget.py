"""Budget agent.

Computes the trip cost from what the other agents wrote on the blackboard.
If Excel MCP tools are passed in, it also saves the budget to an Excel file.
This is the ONLY place the planner touches the MCP.
"""
import json
import math
from pathlib import Path

from llm import ask_json, get_llm, num

OUT_XLSX = (Path(__file__).resolve().parent.parent / "trip_budget.xlsx").as_posix()
CHART_PNG = (Path(__file__).resolve().parent.parent / "charts" / "budget.png").as_posix()
EXCEL_PROMPT = """You create Excel files and charts using ONLY the run_excel_code tool.
Never call a tool named "python" or "browser"; they do not exist.
Use pandas/openpyxl for Excel and matplotlib for charts (never plt.show(); use plt.tight_layout(), plt.savefig(path), plt.close()).
Write exactly the numbers you are given; do not recalculate or invent any.
After saving, print the saved paths to confirm.
If the tool returns an error, fix the code and retry."""


def _pick(block: dict) -> dict:
    options = block.get("options") or []
    i = int(num(block.get("pick_index"), 0))
    return options[i] if 0 <= i < len(options) else (options[0] if options else {})


async def run(state, excel_tools=None):
    r = state["request"]
    people = r["travelers"]
    days = r["duration_days"]
    nights = max(days - 1, 1)
    rooms = math.ceil(people / 2)

    flight = _pick(state.get("flights", {}))
    hotel = _pick(state.get("hotels", {}))
    activities = state.get("activities", {}).get("activities", [])

    daily = ask_json(
        f"Estimate typical daily costs in USD PER PERSON in {r['destination']} for a {r['style']} traveler. "
        'Return JSON: {"food_per_day": number, "local_transport_per_day": number}'
    )

    lines = [
        {"item": "Flights", "detail": flight.get("airline", "n/a"),
         "cost": num(flight.get("price_usd")) * people},
        {"item": "Hotel", "detail": f"{hotel.get('name', 'n/a')} x {nights} nights x {rooms} room(s)",
         "cost": num(hotel.get("price_per_night_usd")) * nights * rooms},
        {"item": "Activities", "detail": f"{len(activities)} activities",
         "cost": sum(num(a.get("price_usd")) for a in activities) * people},
        {"item": "Food", "detail": f"{days} days", "cost": num(daily.get("food_per_day")) * days * people},
        {"item": "Local transport", "detail": f"{days} days",
         "cost": num(daily.get("local_transport_per_day")) * days * people},
    ]
    subtotal = sum(l["cost"] for l in lines)
    lines.append({"item": "Buffer (10%)", "detail": "unexpected costs", "cost": round(subtotal * 0.1, 2)})

    budget = {
        "currency": "USD",
        "lines": [{**l, "cost": round(l["cost"], 2)} for l in lines],
        "total": round(subtotal * 1.1, 2),
    }

    if excel_tools:
        try:
            budget["excel_result"] = await _save_to_excel(budget, excel_tools)
            budget["excel_file"] = OUT_XLSX
        except Exception as e:  # a failed Excel save must not kill the whole plan
            budget["excel_error"] = f"{type(e).__name__}: {e}"

    return {"budget": budget}   # <- this line was missing


async def _save_to_excel(budget: dict, excel_tools) -> str:
    from langgraph.prebuilt import create_react_agent

    agent = create_react_agent(get_llm(0), excel_tools, prompt=EXCEL_PROMPT)
    Path(CHART_PNG).parent.mkdir(exist_ok=True)
    task = (
        f"1) Create the Excel file at this exact path: {OUT_XLSX}\n"
            "Sheet 'Budget' with columns Item, Detail, Cost (USD): one row per line below, "
            "then a final 'Total' row using the given total.\n"
        f"2) Draw a horizontal bar chart of Cost by Item (exclude the Total row, add value labels, save it to this exact path: {CHART_PNG}. "
            "Set the x-axis upper limit to 1.2 × the largest value so value labels are not clipped.\n"
        f"title 'Trip budget (USD)') and save it to this exact path: {CHART_PNG}\n"
        f"Data (JSON): {json.dumps(budget)}"
    )
    messages = [("user", task)]
    for attempt in range(3):
        try:
            result = await agent.ainvoke({"messages": messages}, {"recursion_limit": 15})
            return result["messages"][-1].content
        except Exception as e:
            if "tool_use_failed" in str(e) and attempt < 2:
                messages = messages + [("user", "Use only the run_excel_code tool.")]
                continue
            raise