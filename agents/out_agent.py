"""Out agent: reads the whole blackboard and writes the final plan."""
import json

from llm import ask_text


def run(state):
    board = {k: v for k, v in state.items() if k not in ("user_text", "final_plan")}
    prompt = f"""You are the final-answer agent of a trip planner. Using the blackboard below,
write a clear trip plan in Markdown:

1. Trip summary (destination, dates/time, duration, travelers)
2. Weather overview (temperatures in °C, rain, what to pack)
3. Flight recommendation
4. Hotel recommendation
5. Day-by-day itinerary using the suggested activities (group nearby ones, mix paid and free;
   put outdoor activities at the times that suit the weather and indoor ones when rain is likely;
   do not repeat the same activity on different days)
6. Budget table with the total
7. A short note that prices and weather are estimates and should be verified before booking

Use only the data on the blackboard. Do not invent extra prices.

Blackboard:
{json.dumps(board, indent=2)}"""
    return {"final_plan": ask_text(prompt)}
