# AI Startup Builder

AI Startup Builder is a FastAPI + Streamlit application that turns a startup idea into a complete startup plan using specialized AI agents.

## What It Generates

- CEO strategy and business model
- Market research and competitor analysis
- Marketing and launch plan
- Financial plan and pricing strategy
- Technical architecture
- Investor pitch deck content
- Optional startup logo generation

## Project Structure

```text
backend/
  agents/                 AI agents for strategy, research, marketing, finance, tech, pitch, and logo generation
  orchestrator/           Sequential and LangGraph orchestration flows
  utils/                  Guardrails, evaluation, sanitization, and report writing
  main.py                 FastAPI app and API routes
frontend/
  streamlit_app.py        Streamlit UI
Dockerfile                Backend container for Render
render.yaml               Render Blueprint for backend and frontend services
requirements.txt          Backend dependencies
frontend/requirements.txt Frontend dependencies
```

## Guardrails

The backend includes centralized guardrails in `backend/utils/guardrails.py`.

They help with:

- Blocking prompt-injection attempts
- Blocking clearly unsafe startup ideas, such as malware, phishing, credential theft, fraud, spam, weapons, or illegal harm
- Rejecting sensitive data such as emails, phone numbers, and API-key-like strings in startup ideas
- Adding consistent model instructions to all text-generation agents
- Screening generated output for unsafe operational content
- Returning blocked requests as HTTP `400` errors

## Environment Variables

Backend:

```text
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=ai-startup-builder
LANGCHAIN_API_KEY=optional_langsmith_key
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
ENABLE_DEBUG_ENV=false
```

Frontend:

```text
BACKEND_URL=https://your-backend-service.onrender.com
```

When deployed through `render.yaml`, `BACKEND_URL` is wired automatically from the backend service.

## Run Locally

Backend:

```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
pip install -r frontend/requirements.txt
set BACKEND_URL=http://127.0.0.1:8000
streamlit run frontend/streamlit_app.py
```

PowerShell users can set the frontend URL like this:

```powershell
$env:BACKEND_URL="http://127.0.0.1:8000"
streamlit run frontend\streamlit_app.py
```

## Run With Docker

```bash
docker build -t ai-startup-builder-backend .
docker run --rm -e PORT=8000 -e OPENAI_API_KEY=your_openai_api_key -p 8000:8000 ai-startup-builder-backend
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Deploy To Render

This repo includes `render.yaml`, so the easiest deploy path is Render Blueprint.

1. Push the repo to GitHub.
2. In Render, choose **New +** then **Blueprint**.
3. Select the `Sajidhussain19/ai-startup-builder` repository.
4. Render will detect `render.yaml`.
5. Add `OPENAI_API_KEY` when Render prompts for it.
6. Deploy both services.

The Blueprint creates:

- `ai-startup-builder-backend`: FastAPI Docker service
- `ai-startup-builder-frontend`: Streamlit web service

The backend uses Render's dynamic `$PORT`, and the frontend receives the backend URL from the backend service reference.

## API Endpoints

```text
GET  /api/v1/health
POST /api/v1/generate/ceo
POST /api/v1/generate/research
POST /api/v1/generate/marketing
POST /api/v1/generate/finance
POST /api/v1/generate/developer
POST /api/v1/generate/pitch
POST /api/v1/generate/logo
POST /api/v1/generate/all
POST /api/v1/generate/full
POST /api/v1/generate/langgraph
POST /api/v1/eval/agent
```

Request body:

```json
{
  "idea": "AI scheduling app for small clinics"
}
```

## Verification

Useful pre-deploy checks:

```bash
python -m compileall backend frontend
python -c "import yaml; yaml.safe_load(open('render.yaml', encoding='utf-8')); print('render yaml parses')"
docker build -t ai-startup-builder-backend-check .
```

Then run the Docker image and confirm `/api/v1/health` returns `200`.
