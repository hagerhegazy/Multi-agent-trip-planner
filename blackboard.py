"""The blackboard: shared state every agent reads from and writes to.

Each agent writes ONE key, so parallel agents never overwrite each other.
"""
from typing import TypedDict


class Blackboard(TypedDict, total=False):
    user_text: str      # raw request from the user
    request: dict       # parsed by the planner: destination, time, duration...
    flights: dict       # written by the flight agent
    hotels: dict        # written by the hotels agent
    activities: dict    # written by the activity agent
    budget: dict        # written by the budget agent
    final_plan: str     # written by the out agent
    weather: dict       # written by the weather agent