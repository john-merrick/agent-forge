from pathlib import Path

from backend.tools.registry import ToolDef, register_tool


def execute(path: str) -> str:
    """Read a local file. Path must be under the current working directory."""
    target = Path(path).resolve()
    cwd = Path.cwd().resolve()

    if not str(target).startswith(str(cwd)):
        return f"Error: path must be under {cwd}"

    if not target.exists():
        return f"Error: file not found: {path}"

    if not target.is_file():
        return f"Error: not a file: {path}"

    try:
        content = target.read_text()
        if len(content) > 10000:
            return content[:10000] + "\n... (truncated)"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


register_tool(
    ToolDef(
        name="file_reader",
        description="Read contents of a local file (must be under working directory)",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"},
            },
            "required": ["path"],
        },
        function=execute,
    )
)
