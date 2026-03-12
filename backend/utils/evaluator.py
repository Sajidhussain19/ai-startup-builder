from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_agent_output(agent_name: str, input_idea: str, actual_output: str) -> dict:
    """
    Custom eval pipeline using GPT as judge
    """
    print(f"📊 Evaluating {agent_name}...")

    prompt = f"""
    You are an expert AI output evaluator.
    
    Evaluate this AI agent output on a scale of 0.0 to 1.0 for each metric.
    
    AGENT: {agent_name}
    USER INPUT: {input_idea}
    AGENT OUTPUT: {actual_output[:1000]}
    
    Score these metrics:
    1. relevancy - Is the output relevant to the input idea?
    2. completeness - Does it cover all expected sections?
    3. accuracy - Does it seem factually reasonable?
    4. clarity - Is it well structured and clear?
    5. actionability - Can someone act on this output?
    
    Respond ONLY with valid JSON like this:
    {{
        "relevancy": 0.9,
        "completeness": 0.8,
        "accuracy": 0.85,
        "clarity": 0.9,
        "actionability": 0.75,
        "reason": "Brief explanation of scores"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0
        )

        raw = response.choices[0].message.content.strip()
        # Clean JSON if wrapped in backticks
        raw = raw.replace("```json", "").replace("```", "").strip()
        scores = json.loads(raw)

        # Calculate overall score out of 10
        metrics = ["relevancy", "completeness", "accuracy", "clarity", "actionability"]
        avg = sum(scores.get(m, 0) for m in metrics) / len(metrics)
        overall_score = round(avg * 10, 2)

        return {
            "agent": agent_name,
            "overall_score": overall_score,
            "metrics": {m: scores.get(m, 0) for m in metrics},
            "reason": scores.get("reason", ""),
            "passed": overall_score >= 7.0,
            "evaluated_at": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "agent": agent_name,
            "overall_score": 0,
            "error": str(e),
            "evaluated_at": datetime.now().isoformat()
        }


def evaluate_all_agents(idea: str, results: dict) -> dict:
    """
    Evaluates all agent outputs and returns scores
    """
    print("\n📊 Starting custom eval pipeline...")
    print("=" * 50)

    eval_results = {}

    for agent_name, agent_data in results.items():
        if isinstance(agent_data, dict) and "output" in agent_data:
            eval_result = evaluate_agent_output(
                agent_name=agent_name,
                input_idea=idea,
                actual_output=agent_data["output"]
            )
            eval_results[agent_name] = eval_result
            status = "✅" if eval_result.get("passed") else "⚠️"
            print(f"{status} {agent_name}: {eval_result['overall_score']}/10")

    # System wide score
    all_scores = [r["overall_score"] for r in eval_results.values() if "overall_score" in r]
    system_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0

    print("=" * 50)
    print(f"🏆 System Score: {system_score}/10")

    return {
        "system_score": system_score,
        "total_evaluated": len(eval_results),
        "passed": sum(1 for r in eval_results.values() if r.get("passed")),
        "agent_evals": eval_results
    }