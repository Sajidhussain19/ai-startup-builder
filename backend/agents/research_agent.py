from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert market research analyst with deep knowledge of startup ecosystems and market dynamics."
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
        "agent": "Research Agent",
        "status": "completed",
        "output": result
    }