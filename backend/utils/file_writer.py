import os
import uuid
from datetime import datetime

# Allowed output types
ALLOWED_EXTENSIONS = {".md", ".txt", ".json"}

def save_startup_report(idea: str, results: dict) -> str:
    """
    Saves the full startup report as a markdown file
    """
    # Create safe unique filename
    safe_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"startup_report_{safe_id}_{timestamp}.md"

    # Validate extension (security measure #6)
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    # Build output path
    output_dir = os.path.join(os.path.dirname(__file__), "../../generated_startups")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Build markdown report
    report = f"""# 🚀 AI Startup Report
**Idea:** {idea}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 🧑‍💼 CEO Strategy
{results.get('ceo', {}).get('output', 'N/A')}

---

## 🔬 Market Research
{results.get('research', {}).get('output', 'N/A')}

---

## 📣 Marketing Strategy
{results.get('marketing', {}).get('output', 'N/A')}

---

## 💰 Financial Plan
{results.get('finance', {}).get('output', 'N/A')}

---

## 👨‍💻 Technical Architecture
{results.get('developer', {}).get('output', 'N/A')}

---

## 🎤 Investor Pitch Deck
{results.get('pitch', {}).get('output', 'N/A')}
"""

    # Write file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Report saved: {filename}")
    return filename