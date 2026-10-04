from agents.base import run_specialist

SCHEMA = """{
  "activities": [{"name": str, "description": str, "price_usd": number (PER PERSON, 0 if free), "best_time": str}],
  "estimated": bool
}"""


def run(state):
    r = state["request"]
    interests = ", ".join(r.get("interests") or []) or "general sightseeing"
    queries = [
        f"top things to do in {r['destination']}",
        f"{r['destination']} {interests} attractions ticket price",
    ]
    result = run_specialist(
        "activity",
        f"Suggest about {max(3, r['duration_days'] * 2)} activities for a {r['duration_days']}-day trip "
        f"(interests: {interests}). Mix paid and free ones.",
        SCHEMA, queries, r,
    )
    return {"activities": result}
