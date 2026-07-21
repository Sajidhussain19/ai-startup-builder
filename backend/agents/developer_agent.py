from dotenv import load_dotenv
from llm.gateway import chat_completion
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages

load_dotenv()

def run_developer_agent(startup_idea: str) -> dict:
    """
    Developer Agent - Generates system architecture and tech stack
    """
    print(f"👨‍💻 Developer Agent working on: {startup_idea}")

    prompt = f"""
    You are an expert software architect and CTO.
    
    Design the complete technical architecture for: "{startup_idea}"
    
    Provide:
    
    1. TECH STACK - Frontend, Backend, Database, AI/ML, DevOps
    2. SYSTEM ARCHITECTURE - How all components connect
    3. DATABASE SCHEMA - Key tables/collections needed
    4. API ENDPOINTS - List of core API endpoints
    5. AI/ML COMPONENTS - What models and algorithms to use
    6. SECURITY MEASURES - How to secure the system
    7. SCALABILITY PLAN - How to scale from 100 to 1 million users
    
    Be specific with technology choices and explain why.
    """

    llm_result = chat_completion(
        agent_name="Developer Agent",
        messages=build_guardrailed_messages(
            "You are an expert CTO and software architect specializing in AI-powered SaaS applications.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = llm_result["content"]
    guarded = apply_output_guardrails("Developer Agent", result)

    return {
        "agent": "Developer Agent",
        "status": guarded["status"],
        "output": guarded["output"],
        "model": llm_result["model"],
        "fallback_used": llm_result["fallback_used"],
        "usage": llm_result["usage"],
        "cost": llm_result["cost"],
        "latency_ms": llm_result["latency_ms"]
    }
