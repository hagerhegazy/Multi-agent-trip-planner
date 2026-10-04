from agents.base import run_specialist

SCHEMA = """{
  "options": [{"airline": str, "route": str, "price_usd": number (round trip, PER PERSON), "notes": str}],
  "pick_index": int,
  "estimated": bool
}"""


def run(state):
    r = state["request"]
    origin = r.get("origin") or "a major nearby hub"
    queries = [
        f"flights from {origin} to {r['destination']} {r['time']} round trip price",
        f"cheapest airlines {origin} to {r['destination']}",
    ]
    result = run_specialist(
        "flight",
        "Suggest 3 realistic round-trip flight options, prefer direct flights when they exist, and pick the best value.",
        SCHEMA, queries, r,
    )
    return {"flights": result}
