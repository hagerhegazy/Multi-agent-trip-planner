"""Shared logic for the search-based specialists (flight, hotels, activity).

Search the web -> give the results to the LLM -> get structured JSON back.
"""
import json
from llm import ask_json
from tools.web_search import format_results, web_search


def run_specialist(role: str, task: str, schema: str, queries: list[str], request: dict) -> dict:
    results = []
    for q in queries:
        results += web_search(q)

    prompt = f"""You are the {role} agent in a trip-planning system.

Trip request:
{json.dumps(request, indent=2)}

Your task: {task}

Web search results (noisy, prices are approximate):
{format_results(results)}

Return JSON with exactly this shape:
{schema}

Rules: all prices in USD. If the search results have no exact price, give a realistic
estimate and set "estimated": true. Never invent booking links."""
    return ask_json(prompt)
