"""Web search tool (DuckDuckGo, no API key needed)."""


def web_search(query: str, n: int = 4) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:  # older package name
        from duckduckgo_search import DDGS
    try:
        hits = DDGS().text(query, max_results=n)
    except Exception:
        return []
    return [
        {"title": h.get("title", ""), "url": h.get("href", ""), "snippet": h.get("body", "")[:300]}
        for h in hits
    ]


def format_results(results: list[dict]) -> str:
    if not results:
        return "(no search results)"
    return "\n".join(f"- {r['title']} | {r['snippet']} ({r['url']})" for r in results)
