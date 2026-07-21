import os
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

from llm.pricing import estimate_cost_usd
from llm.usage_store import record_usage


load_dotenv()

PRIMARY_MODEL = os.getenv("PRIMARY_LLM_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = os.getenv("FALLBACK_LLM_MODEL", "gpt-4.1-mini")
ENABLE_FALLBACK = os.getenv("ENABLE_LLM_FALLBACK", "true").lower() == "true"
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))


def _client() -> OpenAI:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=LLM_TIMEOUT_SECONDS)
    return wrap_openai(client)


@traceable(name="LLM Gateway", run_type="llm")
def chat_completion(
    *,
    agent_name: str,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
    model: Optional[str] = None,
) -> Dict[str, object]:
    primary_model = model or PRIMARY_MODEL
    models = [primary_model]
    if ENABLE_FALLBACK and FALLBACK_MODEL and FALLBACK_MODEL != primary_model:
        models.append(FALLBACK_MODEL)

    last_error = None
    started_at = time.perf_counter()

    for index, selected_model in enumerate(models):
        fallback_used = index > 0
        try:
            response = _client().chat.completions.create(
                model=selected_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            usage = _extract_usage(response)
            costs = estimate_cost_usd(
                selected_model,
                usage["prompt_tokens"],
                usage["completion_tokens"],
            )
            content = response.choices[0].message.content or ""

            record_usage(
                agent_name=agent_name,
                model=selected_model,
                fallback_used=fallback_used,
                status="success",
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
                input_cost_usd=costs["input_cost_usd"],
                output_cost_usd=costs["output_cost_usd"],
                total_cost_usd=costs["total_cost_usd"],
                latency_ms=latency_ms,
            )

            return {
                "content": content,
                "model": selected_model,
                "fallback_used": fallback_used,
                "usage": usage,
                "cost": costs,
                "latency_ms": latency_ms,
            }
        except Exception as e:
            last_error = e
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            record_usage(
                agent_name=agent_name,
                model=selected_model,
                fallback_used=fallback_used,
                status="failed",
                error=str(e),
                latency_ms=latency_ms,
            )

    raise last_error


def _extract_usage(response) -> Dict[str, int]:
    usage = getattr(response, "usage", None)
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }
