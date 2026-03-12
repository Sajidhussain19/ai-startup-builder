import bleach

def sanitize_input(text: str) -> str:
    # Remove any HTML or malicious content
    text = bleach.clean(text)
    # Strip extra whitespace
    text = text.strip()
    # Limit length
    if len(text) > 500:
        raise ValueError("Input too long. Maximum 500 characters allowed.")
    if len(text) < 5:
        raise ValueError("Input too short. Please describe your idea better.")
    return text