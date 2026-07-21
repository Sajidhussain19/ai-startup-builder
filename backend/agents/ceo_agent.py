
from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_ceo_agent(startup_idea: str) -> dict:
    """
    CEO Agent - Creates startup strategy and business model
    """
    print(f"🤖 CEO Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert startup CEO and business strategist.
    
    A founder came to you with this idea: "{startup_idea}"
    
    Your job is to create a comprehensive startup strategy. Provide:
    
    1. STARTUP NAME - Creative and memorable name
    2. PROBLEM - What problem does this solve?
    3. SOLUTION - How does it solve it?
    4. TARGET MARKET - Who are the customers?
    5. BUSINESS MODEL - How does it make money?
    6. UNIQUE VALUE PROPOSITION - Why is this better than competitors?
    7. SHORT TERM GOALS - First 6 months plan
    
    Be specific, practical and concise.
    """

    llm_result = chat_completion(
        agent_name="CEO Agent",
        messages=build_guardrailed_messages(
            "You are an expert startup CEO. Give clear, structured, actionable startup strategies.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("CEO Agent", result)

    return {
        "agent": "CEO Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
