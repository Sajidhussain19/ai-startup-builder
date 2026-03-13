from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run_marketing_agent(startup_idea: str) -> dict:
    """
    Marketing Agent - Creates growth and marketing strategies
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert startup marketing strategist who specializes in growth hacking and digital marketing."
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
        "agent": "Marketing Agent",
        "status": "completed",
        "output": result
    }