from agents.base import run_specialist

SCHEMA = """{
  "options": [{"name": str, "area": str, "price_per_night_usd": number (per room), "why": str}],
  "pick_index": int,
  "estimated": bool
}"""


def run(state):
    r = state["request"]
    queries = [
        f"best {r['style']} hotels in {r['destination']} price per night",
        f"where to stay in {r['destination']} {r['time']}",
    ]
    result = run_specialist(
        "hotels",
        f"Suggest 3 hotels matching a {r['style']} style and pick the best value.",
        SCHEMA, queries, r,
    )
    return {"hotels": result}
