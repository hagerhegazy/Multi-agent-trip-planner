from agents.base import run_specialist

SCHEMA = """{
  "summary": str (one sentence),
  "avg_high_c": number,
  "avg_low_c": number,
  "rainy_days_estimate": number (out of the trip length),
  "conditions": str,
  "pack": [str],
  "best_for": str (which kinds of activities suit this weather),
  "estimated": bool
}"""


def run(state):
    r = state["request"]
    queries = [
        f"{r['destination']} weather in {r['time']} average temperature rainfall",
        f"what to pack for {r['destination']} in {r['time']}",
    ]
    result = run_specialist(
        "weather",
        f"Describe the typical weather for a {r['duration_days']}-day trip. "
        "Use climate averages for that time of year, not a forecast. Temperatures in Celsius.",
        SCHEMA, queries, r,
    )
    return {"weather": result}