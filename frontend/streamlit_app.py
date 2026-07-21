import streamlit as st
import requests
import json
import os

# Page config
st.set_page_config(
    page_title="AI Startup Builder",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-badge {
        color: #4CAF50;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🚀 AI Startup Builder</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Enter your idea. Our AI agents will build your complete startup plan.</p>', unsafe_allow_html=True)

# Backend URL
backend_raw_url = os.getenv("BACKEND_URL", "https://ai-startup-builder-backend.onrender.com").rstrip("/")
BACKEND_URL = backend_raw_url if backend_raw_url.startswith(("http://", "https://")) else f"http://{backend_raw_url}"
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN", "")
OBSERVABILITY_ADMIN_TOKEN = os.getenv("OBSERVABILITY_ADMIN_TOKEN", os.getenv("BACKEND_API_TOKEN", ""))
FRONTEND_PASSWORD = os.getenv("FRONTEND_PASSWORD", "")


if FRONTEND_PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("### AI Startup Builder")
        password = st.text_input("Access password", type="password")
        if st.button("Unlock", type="primary"):
            if password == FRONTEND_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password.")
        st.stop()


def app_headers() -> dict:
    return {"X-App-Token": BACKEND_API_TOKEN} if BACKEND_API_TOKEN else {}


def admin_headers() -> dict:
    return {"X-Admin-Token": OBSERVABILITY_ADMIN_TOKEN} if OBSERVABILITY_ADMIN_TOKEN else app_headers()


def get_json(path: str, timeout: int = 20):
    response = requests.get(f"{BACKEND_URL}{path}", headers=admin_headers(), timeout=timeout)
    response.raise_for_status()
    return response.json()

# Input section
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    idea = st.text_input(
        "💡 Your Startup Idea",
        placeholder="e.g. Build a startup for AI diet planning",
        help="Describe your startup idea in one sentence"
    )

    generate_btn = st.button(
        "🚀 Generate Full Startup Plan",
        use_container_width=True,
        type="primary"
    )

st.markdown("---")

# Generate on button click
if generate_btn:
    if not idea or len(idea.strip()) < 5:
        st.error("⚠️ Please enter a valid startup idea (at least 5 characters)")
    else:
        # Progress tracking
        st.markdown("### 🤖 Agents Working...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        agents_status = {
            "CEO Agent": "⏳",
            "Research Agent": "⏳",
            "Marketing Agent": "⏳",
            "Finance Agent": "⏳",
            "Developer Agent": "⏳",
            "Pitch Agent": "⏳"
        }

        # Show initial status
        status_cols = st.columns(6)
        for i, (agent, status) in enumerate(agents_status.items()):
            with status_cols[i]:
                st.markdown(f"**{agent}**\n\n{status}")

        # Call orchestrator
        status_text.text("🔄 Running all agents... this may take 30-60 seconds")
        progress_bar.progress(20)

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/generate/all",
                json={"idea": idea},
                headers=app_headers(),
                timeout=120
            )

            progress_bar.progress(100)

            if response.status_code == 200:
                data = response.json()
                status_text.text("✅ All agents completed!")

                # Success message
                st.success(f"✅ Successfully generated startup plan for: **{idea}**")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Agents", data.get("total_agents", 0))
                with col2:
                    st.metric("Successful", data.get("successful", 0))
                with col3:
                    st.metric("Failed", data.get("failed", 0))

                st.markdown("---")

                # Display each agent result in tabs
                results = data.get("results", {})

                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "🏢 CEO Strategy",
                    "🔬 Research",
                    "📣 Marketing",
                    "💰 Finance",
                    "👨‍💻 Developer",
                    "🎤 Pitch Deck"
                ])

                with tab1:
                    st.markdown("## 🏢 CEO Agent — Startup Strategy")
                    if "ceo" in results:
                        st.markdown(results["ceo"]["output"])

                with tab2:
                    st.markdown("## 🔬 Research Agent — Market Analysis")
                    if "research" in results:
                        st.markdown(results["research"]["output"])

                with tab3:
                    st.markdown("## 📣 Marketing Agent — Marketing Strategy")
                    if "marketing" in results:
                        st.markdown(results["marketing"]["output"])

                with tab4:
                    st.markdown("## 💰 Finance Agent — Financial Plan")
                    if "finance" in results:
                        st.markdown(results["finance"]["output"])

                with tab5:
                    st.markdown("## 👨‍💻 Developer Agent — Tech Architecture")
                    if "developer" in results:
                        st.markdown(results["developer"]["output"])

                with tab6:
                    st.markdown("## 🎤 Pitch Agent — Investor Pitch Deck")
                    if "pitch" in results:
                        st.markdown(results["pitch"]["output"])

                # Download full report
                st.markdown("---")
                st.markdown("### 📥 Download Full Report")
                full_report = json.dumps(data, indent=2)
                st.download_button(
                    label="⬇️ Download JSON Report",
                    data=full_report,
                    file_name=f"startup_plan_{idea[:20].replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            else:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                st.error(f"❌ Backend error: {response.status_code} - {error_detail}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The agents are taking too long. Try again.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Make sure FastAPI server is running on port 8000.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

st.markdown("---")
st.markdown("### Observability Dashboard")

obs_col1, obs_col2 = st.columns([1, 4])
with obs_col1:
    refresh_obs = st.button("Refresh", use_container_width=True)

if refresh_obs:
    try:
        summary = get_json("/api/v1/observability/summary")
        recent = get_json("/api/v1/observability/recent?limit=25")
        totals = summary.get("totals", {})

        metric_cols = st.columns(6)
        metric_cols[0].metric("LLM Calls", int(totals.get("total_calls", 0)))
        metric_cols[1].metric("Spend", f"${float(totals.get('total_cost_usd', 0)):.6f}")
        metric_cols[2].metric("Tokens", int(totals.get("total_tokens", 0)))
        metric_cols[3].metric("Avg Latency", f"{float(totals.get('avg_latency_ms', 0)):.0f} ms")
        metric_cols[4].metric("Failures", int(totals.get("failed_calls", 0)))
        metric_cols[5].metric("Fallbacks", int(totals.get("fallback_calls", 0)))

        st.markdown("#### Spend By Agent")
        st.dataframe(summary.get("by_agent", []), use_container_width=True, hide_index=True)

        st.markdown("#### Spend By Model")
        st.dataframe(summary.get("by_model", []), use_container_width=True, hide_index=True)

        st.markdown("#### Recent LLM Calls")
        st.dataframe(recent.get("items", []), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Could not load observability data: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888'>Built with FastAPI + OpenAI + Streamlit 🚀</p>",
    unsafe_allow_html=True
)
