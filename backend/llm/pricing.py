import os
from typing import Dict


# Prices are USD per 1M tokens. Defaults verified against official OpenAI model
# pricing pages on 2026-07-21; env vars can override without a code deploy.
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {
        "input": float(os.getenv("GPT_4O_MINI_INPUT_PER_1M", "0.15")),
        "output": float(os.getenv("GPT_4O_MINI_OUTPUT_PER_1M", "0.60")),
    },
    "gpt-4.1-mini": {
        "input": float(os.getenv("GPT_41_MINI_INPUT_PER_1M", "0.40")),
        "output": float(os.getenv("GPT_41_MINI_OUTPUT_PER_1M", "1.60")),
    },
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> dict:
    pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]

    return {
        "input_cost_usd": round(input_cost, 8),
        "output_cost_usd": round(output_cost, 8),
        "total_cost_usd": round(input_cost + output_cost, 8),
    }
