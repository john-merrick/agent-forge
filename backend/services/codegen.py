import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from backend.config import settings
from backend.models.agent import AgentResponse

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
    keep_trailing_newline=True,
)


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "agent"


def get_agent_file_path(agent: AgentResponse) -> Path:
    return settings.agents_path / f"{_slugify(agent.name)}.py"


def generate_agent_file(agent: AgentResponse) -> str:
    settings.agents_path.mkdir(parents=True, exist_ok=True)

    template = _env.get_template("agent_template.py.j2")
    code = template.render(
        agent_name=agent.name,
        agent_id=agent.id,
        model=agent.model,
        provider=agent.provider,
        system_prompt=agent.system_prompt,
        user_prompt_template=agent.user_prompt_template,
        tools=agent.tools,
    )

    file_path = get_agent_file_path(agent)
    file_path.write_text(code)
    return str(file_path)


def remove_agent_file(agent: AgentResponse) -> None:
    path = get_agent_file_path(agent)
    if path.exists():
        path.unlink()
