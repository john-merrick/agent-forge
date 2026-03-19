import subprocess

from backend.tools.registry import ToolDef, register_tool


def execute(command: str) -> str:
    """Run a shell command with a 30-second timeout. Use with caution."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated)"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30s"
    except Exception as e:
        return f"Error: {e}"


register_tool(
    ToolDef(
        name="shell_command",
        description="Run a shell command (30s timeout). WARNING: use with caution",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
            },
            "required": ["command"],
        },
        function=execute,
    )
)
