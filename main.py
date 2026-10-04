"""Command-line runner:  python main.py "5 days in Rome in November, 2 people, love food" """
import asyncio
import sys

from planner import run_trip

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "5 days in Rome in November for 2 people, love food and history"
    board = asyncio.run(run_trip(text, on_update=lambda n: print(f"[done] {n}")))
    print("\n" + board["final_plan"])
