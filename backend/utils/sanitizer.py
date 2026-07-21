from utils.guardrails import validate_startup_idea

def sanitize_input(text: str) -> str:
    return validate_startup_idea(text)
