from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run_pitch_agent(startup_idea: str) -> dict:
    """
    Pitch Agent - Generates investor pitch deck content
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert pitch consultant who creates compelling investor presentations for startups."
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
        "agent": "Pitch Agent",
        "status": "completed",
        "output": result
    }