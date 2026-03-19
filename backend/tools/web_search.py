from backend.tools.registry import ToolDef, register_tool


def execute(query: str) -> str:
    """Search the web using DuckDuckGo HTML."""
    import httpx

    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "AgentForge/1.0"},
            )
            # Return raw text (agent will parse)
            return r.text[:3000]
    except Exception as e:
        return f"Search failed: {e}"


register_tool(
    ToolDef(
        name="web_search",
        description="Search the web for information using DuckDuckGo",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
        function=execute,
    )
)
