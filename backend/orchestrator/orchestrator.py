from agents.ceo_agent import run_ceo_agent
from agents.research_agent import run_research_agent
from agents.marketing_agent import run_marketing_agent
from agents.finance_agent import run_finance_agent
from agents.developer_agent import run_developer_agent
from agents.pitch_agent import run_pitch_agent
from utils.file_writer import save_startup_report
from utils.evaluator import evaluate_all_agents

def run_all_agents(startup_idea: str) -> dict:
    """
    Orchestrator - Runs all agents in sequence, evaluates outputs, saves report
    """
    print(f"\n🚀 Orchestrator starting for: {startup_idea}")
    print("=" * 50)

    results = {}
    errors = {}

    # Define agent pipeline
    agents = [
        ("ceo", run_ceo_agent),
        ("research", run_research_agent),
        ("marketing", run_marketing_agent),
        ("finance", run_finance_agent),
        ("developer", run_developer_agent),
        ("pitch", run_pitch_agent),
    ]

    # Run each agent
    for agent_name, agent_func in agents:
        try:
            print(f"▶ Running {agent_name} agent...")
            result = agent_func(startup_idea)
            results[agent_name] = result
            print(f"✅ {agent_name} agent completed")
        except Exception as e:
            print(f"❌ {agent_name} agent failed: {str(e)}")
            errors[agent_name] = str(e)

    # Run eval pipeline on all outputs
    print("\n📊 Running evaluation pipeline...")
    try:
        eval_scores = evaluate_all_agents(startup_idea, results)
    except Exception as e:
        eval_scores = {"error": str(e)}
        print(f"⚠️ Evaluation failed: {str(e)}")

    # Save report to file
    try:
        saved_path = save_startup_report(startup_idea, results)
    except Exception as e:
        saved_path = None
        print(f"⚠️ Could not save report: {str(e)}")

    print("=" * 50)
    print("🎉 All agents completed!")

    return {
        "status": "completed",
        "idea": startup_idea,
        "total_agents": len(agents),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
        "evaluations": eval_scores,
        "saved_to": saved_path
    }