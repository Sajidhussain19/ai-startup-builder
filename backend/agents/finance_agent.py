from openai import OpenAI
from dotenv import load_dotenv
from utils.guardrails import apply_output_guardrails, build_guardrailed_messages
import os

load_dotenv()

def run_finance_agent(startup_idea: str) -> dict:
    """
    Finance Agent - Estimates startup cost and revenue model
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=build_guardrailed_messages(
            "You are an expert startup CFO and financial analyst with experience in early-stage startups.",
            prompt
        ),
        max_tokens=1000,
        temperature=0.7
    )

    result = response.choices[0].message.content
    guarded = apply_output_guardrails("Finance Agent", result)

    return {
        "agent": "Finance Agent",
        "status": guarded["status"],
        "output": guarded["output"]
    }
