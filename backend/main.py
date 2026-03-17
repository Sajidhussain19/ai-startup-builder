from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from utils.sanitizer import sanitize_input
from agents.ceo_agent import run_ceo_agent
from agents.research_agent import run_research_agent
from agents.marketing_agent import run_marketing_agent
from agents.finance_agent import run_finance_agent
from agents.developer_agent import run_developer_agent
from agents.pitch_agent import run_pitch_agent
from agents.logo_agent import run_logo_agent
from orchestrator.orchestrator import run_all_agents
from utils.evaluator import evaluate_agent_output
from orchestrator.langgraph_orchestrator import run_langgraph_agents
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load secrets from .env FIRST
load_dotenv()

# LangSmith monitoring - reads from environment
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "ai-startup-builder")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="AI Startup Builder",
    version="1.0.0"
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class StartupRequest(BaseModel):
    idea: str

# Health check route
@app.get("/api/v1/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {
        "status": "running",
        "version": "1.0.0",
        "message": "AI Startup Builder is alive!"
    }

# Debug env vars
@app.get("/api/v1/debug/env")
async def debug_env(request: Request):
    return {
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2"),
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT"),
        "LANGCHAIN_API_KEY_SET": bool(os.getenv("LANGCHAIN_API_KEY")),
        "OPENAI_KEY_SET": bool(os.getenv("OPENAI_API_KEY"))
    }

# Logo Agent route - DALL-E 3
@app.post("/api/v1/generate/logo")
@limiter.limit("3/minute")
async def generate_logo(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    # Run CEO agent first to extract startup name
    ceo_result = run_ceo_agent(clean_idea)
    ceo_output = ceo_result.get("output", "")

    # Extract startup name from CEO output
    startup_name = "AI Startup"
    for line in ceo_output.split("\n"):
        if "STARTUP NAME" in line.upper() or "**" in line:
            name = line.replace("**", "").replace("#", "").strip()
            if name and len(name) < 50 and len(name) > 2:
                startup_name = name
                break

    result = run_logo_agent(startup_name, clean_idea)
    result["startup_name"] = startup_name
    return result

# CEO Agent route
@app.post("/api/v1/generate/ceo")
@limiter.limit("5/minute")
async def generate_ceo_strategy(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_ceo_agent(clean_idea)
    return result

# Research Agent route
@app.post("/api/v1/generate/research")
@limiter.limit("5/minute")
async def generate_research(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_research_agent(clean_idea)
    return result

# Marketing Agent route
@app.post("/api/v1/generate/marketing")
@limiter.limit("5/minute")
async def generate_marketing(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_marketing_agent(clean_idea)
    return result

# Finance Agent route
@app.post("/api/v1/generate/finance")
@limiter.limit("5/minute")
async def generate_finance(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_finance_agent(clean_idea)
    return result

# Developer Agent route
@app.post("/api/v1/generate/developer")
@limiter.limit("5/minute")
async def generate_developer(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_developer_agent(clean_idea)
    return result

# Pitch Agent route
@app.post("/api/v1/generate/pitch")
@limiter.limit("5/minute")
async def generate_pitch(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_pitch_agent(clean_idea)
    return result

# Orchestrator route - runs ALL agents
@app.post("/api/v1/generate/full")
@limiter.limit("2/minute")
async def generate_full_startup(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_all_agents(clean_idea)
    return result

# Orchestrator - runs ALL agents at once
@app.post("/api/v1/generate/all")
@limiter.limit("2/minute")
async def generate_all_startup(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_all_agents(clean_idea)
    return result

# Eval a single agent output
@app.post("/api/v1/eval/agent")
@limiter.limit("10/minute")
async def eval_agent(request: Request, body: dict):
    idea = body.get("idea", "")
    agent_name = body.get("agent_name", "")
    output = body.get("output", "")

    result = evaluate_agent_output(agent_name, idea, output)
    return result

# LangGraph Orchestrator route
@app.post("/api/v1/generate/langgraph")
@limiter.limit("2/minute")
async def generate_langgraph(request: Request, body: StartupRequest):
    try:
        clean_idea = sanitize_input(body.idea)
    except ValueError as e:
        return {"error": str(e)}

    result = run_langgraph_agents(clean_idea)
    return result