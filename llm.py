"""LLM helpers shared by every agent."""
import json
import os
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0.2) -> ChatGroq:
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=temperature,
    )


def ask_text(prompt: str, temperature: float = 0.4) -> str:
    return get_llm(temperature).invoke(prompt).content


def ask_json(prompt: str) -> dict:
    """Ask for JSON and parse it defensively (models sometimes add fences/text)."""
    raw = get_llm(0).invoke(prompt + "\n\nReturn ONLY valid JSON. No markdown, no commentary.").content
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return {"error": "no JSON returned", "raw": raw}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"error": "invalid JSON", "raw": raw}


def num(value, default: float = 0.0) -> float:
    """LLMs sometimes return '$120' or '120 USD' instead of 120."""
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value or ""))
    return float(match.group(0).replace(",", "")) if match else default
