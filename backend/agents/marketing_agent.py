from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_marketing_agent(startup_idea: str) -> dict:
    """
    Marketing Agent - Creates growth and marketing strategies
    """
    print(f"📣 Marketing Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert startup marketing strategist.
    
    Create a complete marketing strategy for this startup: "{startup_idea}"
    
    Provide:
    
    1. BRAND IDENTITY - Brand voice, colors, and personality
    2. MARKETING CHANNELS - Top 5 channels to use and why
    3. CONTENT STRATEGY - What content to create and where
    4. SOCIAL MEDIA PLAN - Platform-specific strategies
    5. GROWTH HACKS - 5 creative low-cost growth strategies
    6. LAUNCH CAMPAIGN - Step by step launch plan
    7. KPIs TO TRACK - Key metrics to measure success
    
    Be creative, specific, and actionable.
    """

    llm_result = chat_completion(
        agent_name="Marketing Agent",
        messages=build_guardrailed_messages(
            "You are an expert startup marketing strategist who specializes in growth hacking and digital marketing.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("Marketing Agent", result)

    return {
        "agent": "Marketing Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
