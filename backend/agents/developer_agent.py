from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run_developer_agent(startup_idea: str) -> dict:
    """
    Developer Agent - Generates system architecture and tech stack
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert CTO and software architect specializing in AI-powered SaaS applications."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1000,
        temperature=0.7
    )

    result = response.choices[0].message.content

    return {
        "agent": "Developer Agent",
        "status": "completed",
        "output": result
    }