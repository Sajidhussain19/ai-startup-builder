from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run_logo_agent(startup_name: str, startup_idea: str) -> dict:
    """
    Logo Agent - Generates a startup logo using DALL-E 3
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"🎨 Logo Agent generating logo for: {startup_name}")

    prompt = f"""
    Create a professional, modern startup logo icon for a company called "{startup_name}".
    The company is about: {startup_idea}
    
    Style requirements:
    - Minimalist and modern
    - Suitable for a tech startup
    - Clean white background
    - No text or letters in the image
    - Just a simple icon/symbol
    - Professional and memorable
    """

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = response.data[0].url

        return {
            "agent": "Logo Agent",
            "status": "completed",
            "startup_name": startup_name,
            "logo_url": image_url
        }

    except Exception as e:
        return {
            "agent": "Logo Agent",
            "status": "failed",
            "error": str(e)
        }