from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_pitch_agent(startup_idea: str) -> dict:
    """
    Pitch Agent - Generates investor pitch deck content
    """
    print(f"🎤 Pitch Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert startup pitch consultant who has helped raise millions in funding.
    
    Create a complete investor pitch deck for: "{startup_idea}"
    
    Structure it as 10 slides:
    
    SLIDE 1 - TITLE: Company name, tagline, founder info
    SLIDE 2 - PROBLEM: The pain point you're solving
    SLIDE 3 - SOLUTION: Your product and how it works
    SLIDE 4 - MARKET SIZE: TAM, SAM, SOM with numbers
    SLIDE 5 - PRODUCT: Key features and demo description
    SLIDE 6 - BUSINESS MODEL: How you make money
    SLIDE 7 - TRACTION: Early metrics or milestones
    SLIDE 8 - COMPETITION: Competitive landscape
    SLIDE 9 - TEAM: Key team members and expertise needed
    SLIDE 10 - ASK: How much funding and how you'll use it
    
    Make it compelling, concise, and investor-ready.
    """

    llm_result = chat_completion(
        agent_name="Pitch Agent",
        messages=build_guardrailed_messages(
            "You are an expert pitch consultant who creates compelling investor presentations for startups.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("Pitch Agent", result)

    return {
        "agent": "Pitch Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
