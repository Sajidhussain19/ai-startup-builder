from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from agents.ceo_agent import run_ceo_agent
from agents.research_agent import run_research_agent
from agents.marketing_agent import run_marketing_agent
from agents.finance_agent import run_finance_agent
from agents.developer_agent import run_developer_agent
from agents.pitch_agent import run_pitch_agent
from utils.evaluator import evaluate_all_agents
from utils.file_writer import save_startup_report
import operator

# ============================================
# STEP 1 — DEFINE THE STATE
# ============================================

class StartupState(TypedDict):
    # Input
    idea: str

    # Agent outputs
    ceo_output: str
    research_output: str
    marketing_output: str
    finance_output: str
    developer_output: str
    pitch_output: str

    # Tracking
    errors: Annotated[list, operator.add]
    completed_agents: Annotated[list, operator.add]
    current_steps: Annotated[list, operator.add]

    # Final outputs
    evaluations: dict
    saved_to: str


# ============================================
# STEP 2 — NODES
# ============================================

def ceo_node(state: StartupState) -> dict:
    print("🏢 CEO Agent running...")
    try:
        result = run_ceo_agent(state["idea"])
        return {
            "ceo_output": result["output"],
            "completed_agents": ["ceo"],
            "current_steps": ["ceo_done"]
        }
    except Exception as e:
        print(f"❌ CEO Agent failed: {e}")
        return {
            "ceo_output": "",
            "errors": [f"CEO Agent failed: {str(e)}"],
            "current_steps": ["ceo_failed"]
        }


def research_node(state: StartupState) -> dict:
    print("🔬 Research Agent running...")
    try:
        result = run_research_agent(state["idea"])
        return {
            "research_output": result["output"],
            "completed_agents": ["research"],
            "current_steps": ["research_done"]
        }
    except Exception as e:
        print(f"❌ Research Agent failed: {e}")
        return {
            "research_output": "",
            "errors": [f"Research Agent failed: {str(e)}"],
            "current_steps": ["research_failed"]
        }


def finance_node(state: StartupState) -> dict:
    print("💰 Finance Agent running...")
    try:
        result = run_finance_agent(state["idea"])
        return {
            "finance_output": result["output"],
            "completed_agents": ["finance"],
            "current_steps": ["finance_done"]
        }
    except Exception as e:
        print(f"❌ Finance Agent failed: {e}")
        return {
            "finance_output": "",
            "errors": [f"Finance Agent failed: {str(e)}"],
            "current_steps": ["finance_failed"]
        }


def marketing_node(state: StartupState) -> dict:
    print("📣 Marketing Agent running...")
    try:
        result = run_marketing_agent(state["idea"])
        return {
            "marketing_output": result["output"],
            "completed_agents": ["marketing"],
            "current_steps": ["marketing_done"]
        }
    except Exception as e:
        print(f"❌ Marketing Agent failed: {e}")
        return {
            "marketing_output": "",
            "errors": [f"Marketing Agent failed: {str(e)}"],
            "current_steps": ["marketing_failed"]
        }


def developer_node(state: StartupState) -> dict:
    print("👨‍💻 Developer Agent running...")
    try:
        result = run_developer_agent(state["idea"])
        return {
            "developer_output": result["output"],
            "completed_agents": ["developer"],
            "current_steps": ["developer_done"]
        }
    except Exception as e:
        print(f"❌ Developer Agent failed: {e}")
        return {
            "developer_output": "",
            "errors": [f"Developer Agent failed: {str(e)}"],
            "current_steps": ["developer_failed"]
        }


def pitch_node(state: StartupState) -> dict:
    print("🎤 Pitch Agent running...")
    try:
        result = run_pitch_agent(state["idea"])
        return {
            "pitch_output": result["output"],
            "completed_agents": ["pitch"],
            "current_steps": ["pitch_done"]
        }
    except Exception as e:
        print(f"❌ Pitch Agent failed: {e}")
        return {
            "pitch_output": "",
            "errors": [f"Pitch Agent failed: {str(e)}"],
            "current_steps": ["pitch_failed"]
        }


def evaluator_node(state: StartupState) -> dict:
    print("📊 Evaluator running...")
    try:
        results = {
            "ceo":       {"output": state.get("ceo_output", "")},
            "research":  {"output": state.get("research_output", "")},
            "marketing": {"output": state.get("marketing_output", "")},
            "finance":   {"output": state.get("finance_output", "")},
            "developer": {"output": state.get("developer_output", "")},
            "pitch":     {"output": state.get("pitch_output", "")},
        }
        eval_scores = evaluate_all_agents(state["idea"], results)
        return {
            "evaluations": eval_scores,
            "current_steps": ["evaluation_done"]
        }
    except Exception as e:
        return {
            "evaluations": {"error": str(e)},
            "current_steps": ["evaluation_failed"]
        }


def save_node(state: StartupState) -> dict:
    print("💾 Saving report...")
    try:
        results = {
            "ceo":       {"output": state.get("ceo_output", "")},
            "research":  {"output": state.get("research_output", "")},
            "marketing": {"output": state.get("marketing_output", "")},
            "finance":   {"output": state.get("finance_output", "")},
            "developer": {"output": state.get("developer_output", "")},
            "pitch":     {"output": state.get("pitch_output", "")},
        }
        saved_path = save_startup_report(state["idea"], results)
        return {
            "saved_to": saved_path,
            "current_steps": ["completed"]
        }
    except Exception as e:
        return {
            "saved_to": None,
            "current_steps": ["save_failed"]
        }


# ============================================
# STEP 3 — CONDITIONAL ROUTING
# ============================================

def should_continue_after_ceo(state: StartupState) -> str:
    steps = state.get("current_steps", [])
    if "ceo_failed" in steps:
        print("⚠️ CEO failed — routing to pitch directly")
        return "pitch"
    return "research"


# ============================================
# STEP 4 — BUILD CLEAN SEQUENTIAL GRAPH
# ✅ No fan-in issues
# ✅ Still uses LangGraph state + conditional routing
# ✅ Clean single execution path
# ============================================

def build_startup_graph():
    workflow = StateGraph(StartupState)

    # Add all nodes
    workflow.add_node("ceo", ceo_node)
    workflow.add_node("research", research_node)
    workflow.add_node("finance", finance_node)
    workflow.add_node("marketing", marketing_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("pitch", pitch_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("save", save_node)

    # Entry point
    workflow.set_entry_point("ceo")

    # ✅ CEO → Research (or pitch if failed)
    workflow.add_conditional_edges(
        "ceo",
        should_continue_after_ceo,
        {
            "research": "research",
            "pitch": "pitch"
        }
    )

    # ✅ Clean sequential path — zero duplicates
    # CEO → Research → Finance → Marketing → Developer → Pitch
    workflow.add_edge("research", "finance")
    workflow.add_edge("finance", "marketing")
    workflow.add_edge("marketing", "developer")
    workflow.add_edge("developer", "pitch")
    workflow.add_edge("pitch", "evaluator")
    workflow.add_edge("evaluator", "save")
    workflow.add_edge("save", END)

    app = workflow.compile()
    print("✅ LangGraph workflow compiled — clean sequential flow!")
    return app


# ============================================
# STEP 5 — RUN THE GRAPH
# ============================================

startup_graph = build_startup_graph()


def run_langgraph_agents(startup_idea: str) -> dict:
    print(f"\n🚀 LangGraph Orchestrator starting: {startup_idea}")
    print("=" * 50)

    initial_state = {
        "idea": startup_idea,
        "ceo_output": "",
        "research_output": "",
        "marketing_output": "",
        "finance_output": "",
        "developer_output": "",
        "pitch_output": "",
        "errors": [],
        "completed_agents": [],
        "current_steps": [],
        "evaluations": {},
        "saved_to": ""
    }

    final_state = startup_graph.invoke(initial_state)

    print("=" * 50)
    print("🎉 LangGraph workflow complete!")
    print(f"📋 Steps completed: {final_state.get('current_steps', [])}")

    return {
        "status": "completed",
        "idea": startup_idea,
        "total_agents": 6,
        "successful": len(final_state.get("completed_agents", [])),
        "failed": len(final_state.get("errors", [])),
        "results": {
            "ceo":       {"output": final_state.get("ceo_output", "")},
            "research":  {"output": final_state.get("research_output", "")},
            "marketing": {"output": final_state.get("marketing_output", "")},
            "finance":   {"output": final_state.get("finance_output", "")},
            "developer": {"output": final_state.get("developer_output", "")},
            "pitch":     {"output": final_state.get("pitch_output", "")},
        },
        "errors": final_state.get("errors", []),
        "evaluations": final_state.get("evaluations", {}),
        "saved_to": final_state.get("saved_to", ""),
        "completed_agents": final_state.get("completed_agents", []),
        "steps_completed": final_state.get("current_steps", [])
    }