from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run_ceo_agent(startup_idea: str) -> dict:
    """
    CEO Agent - Creates startup strategy and business model
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert startup CEO. Give clear, structured, actionable startup strategies."
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
        "agent": "CEO Agent",
        "status": "completed",
        "output": result
    }