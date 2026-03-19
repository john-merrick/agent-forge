from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    model: str
    provider: str = "ollama"
    system_prompt: str = ""
    user_prompt_template: str = ""
    tools: list[str] = Field(default_factory=list)
    schedule: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = None
    model: str | None = None
    provider: str | None = None
    system_prompt: str | None = None
    user_prompt_template: str | None = None
    tools: list[str] | None = None
    schedule: str | None = Field(default=None)
    is_active: bool | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    model: str
    provider: str
    system_prompt: str
    user_prompt_template: str
    tools: list[str]
    schedule: str | None
    is_active: bool
    created_at: str
    updated_at: str
    file_path: str | None = None
