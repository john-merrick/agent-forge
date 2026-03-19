from dataclasses import dataclass, field
from typing import Any, Callable

_tools: dict[str, "ToolDef"] = {}


@dataclass
class ToolDef:
    name: str
    description: str
    parameters: dict = field(default_factory=lambda: {"type": "object", "properties": {}})
    function: Callable[..., Any] | None = None


def register_tool(tool: ToolDef) -> None:
    _tools[tool.name] = tool


def get_tool(name: str) -> ToolDef | None:
    return _tools.get(name)


def list_tools() -> list[dict]:
    return [
        {"name": t.name, "description": t.description, "parameters": t.parameters}
        for t in _tools.values()
    ]


def _load_builtins() -> None:
    from backend.tools import web_search, file_reader, shell_command  # noqa: F401


_load_builtins()
