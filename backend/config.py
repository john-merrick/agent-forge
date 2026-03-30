from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_path: str = "data/agent_forge.db"
    agents_dir: str = "agents"
    ollama_base_url: str = "http://localhost:11434"
    openrouter_api_key: str = ""
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_prefix": "AGENT_FORGE_", "env_file": ".env"}

    @property
    def db_path(self) -> Path:
        return Path(self.database_path)

    @property
    def agents_path(self) -> Path:
        return Path(self.agents_dir)


settings = Settings()
