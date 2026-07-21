from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_finance_agent(startup_idea: str) -> dict:
    """
    Finance Agent - Estimates startup cost and revenue model
    """
    print(f"💰 Finance Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert startup financial analyst and CFO.
    
    Create a financial plan for this startup: "{startup_idea}"
    
    Provide:
    
    1. STARTUP COSTS - Initial investment breakdown with numbers
    2. MONTHLY EXPENSES - Ongoing costs breakdown
    3. REVENUE PROJECTIONS - Month 1 to Month 12 estimates
    4. BREAK EVEN POINT - When will the startup break even?
    5. FUNDING STRATEGY - Bootstrap vs VC vs Angel investors
    6. PRICING STRATEGY - How to price the product
    7. FINANCIAL RISKS - Top 3 financial risks and mitigation
    
    Use realistic numbers. Be specific with dollar amounts.
    """

    llm_result = chat_completion(
        agent_name="Finance Agent",
        messages=build_guardrailed_messages(
            "You are an expert startup CFO and financial analyst with experience in early-stage startups.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("Finance Agent", result)

    return {
        "agent": "Finance Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
