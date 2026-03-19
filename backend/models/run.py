from pydantic import BaseModel


class RunRecord(BaseModel):
    id: str
    agent_id: str
    status: str
    started_at: str | None
    completed_at: str | None
    input_data: str | None
    output_data: str | None
    tokens_in: int
    tokens_out: int
    cost_estimate: float
    latency_ms: int
    error: str | None


class RunTrigger(BaseModel):
    input_data: dict | None = None
