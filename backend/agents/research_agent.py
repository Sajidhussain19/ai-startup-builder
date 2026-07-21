from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_research_agent(startup_idea: str) -> dict:
    """
    Research Agent - Performs market analysis and competitor research
    """
    print(f"🔬 Research Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert market research analyst.
    
    Analyze this startup idea: "{startup_idea}"
    
    Provide detailed research on:
    
    1. MARKET SIZE - Total addressable market (TAM) with numbers
    2. MARKET TRENDS - Current trends supporting this idea
    3. TOP COMPETITORS - List 5 competitors with their strengths/weaknesses
    4. GAPS IN MARKET - What are competitors missing?
    5. TARGET CUSTOMER PROFILE - Detailed persona of ideal customer
    6. MARKET ENTRY STRATEGY - Best way to enter this market
    7. RISKS - Top 3 market risks to watch out for
    
    Use real market data and statistics where possible.
    Be specific and analytical.
    """

    llm_result = chat_completion(
        agent_name="Research Agent",
        messages=build_guardrailed_messages(
            "You are an expert market research analyst with deep knowledge of startup ecosystems and market dynamics.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("Research Agent", result)

    return {
        "agent": "Research Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
