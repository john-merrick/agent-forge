# Pricing per 1M tokens (input, output) in USD
# Updated as of early 2025 — users can override via settings
PRICING = {
    "openai/gpt-4o": (2.50, 10.00),
    "openai/gpt-4o-mini": (0.15, 0.60),
    "anthropic/claude-3.5-sonnet": (3.00, 15.00),
    "anthropic/claude-3-haiku": (0.25, 1.25),
    "google/gemini-pro-1.5": (1.25, 5.00),
    "google/gemini-flash-1.5": (0.075, 0.30),
    "meta-llama/llama-3.1-70b-instruct": (0.52, 0.75),
    "meta-llama/llama-3.1-8b-instruct": (0.055, 0.055),
}


def estimate_cost(model: str, provider: str, tokens_in: int, tokens_out: int) -> float:
    if provider == "ollama":
        return 0.0

    if model in PRICING:
        input_price, output_price = PRICING[model]
        return (tokens_in * input_price + tokens_out * output_price) / 1_000_000

    return -1.0  # Unknown model
