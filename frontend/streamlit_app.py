import streamlit as st
import requests
import json

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
BACKEND_URL = "http://127.0.0.1:8000"

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
        status_text.text("🔄 Running all agents + evaluation pipeline... this may take 2-3 minutes. Please wait ⏳")
        progress_bar.progress(20)

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/generate/all",
                json={"idea": idea},
                timeout=300  # 5 minutes
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

                # ✅ Eval scores section
                evals = data.get("evaluations", {})
                if evals and "agent_evals" in evals:
                    st.markdown("---")
                    st.markdown("### 📊 Agent Quality Scores")

                    system_score = evals.get("system_score", 0)
                    passed = evals.get("passed", 0)
                    total_evaluated = evals.get("total_evaluated", 0)

                    score_color = "green" if system_score >= 7 else "orange" if system_score >= 5 else "red"

                    scol1, scol2, scol3 = st.columns(3)
                    with scol1:
                        st.metric("🏆 System Score", f"{system_score}/10")
                    with scol2:
                        st.metric("✅ Agents Passed", f"{passed}/{total_evaluated}")
                    with scol3:
                        quality = "Excellent" if system_score >= 8 else "Good" if system_score >= 6 else "Needs Work"
                        st.metric("📈 Quality", quality)

                    # Per agent scores
                    st.markdown("#### Per Agent Scores")
                    agent_evals = evals.get("agent_evals", {})
                    score_cols = st.columns(len(agent_evals))

                    for i, (agent, eval_data) in enumerate(agent_evals.items()):
                        with score_cols[i]:
                            score = eval_data.get("overall_score", 0)
                            emoji = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
                            st.metric(
                                label=agent.upper(),
                                value=f"{score}/10",
                                delta=f"{emoji} {'Pass' if eval_data.get('passed') else 'Fail'}"
                            )

                    # Show detailed metrics in expander
                    with st.expander("🔍 View Detailed Metrics"):
                        for agent, eval_data in agent_evals.items():
                            st.markdown(f"**{agent.upper()} Agent**")
                            metrics = eval_data.get("metrics", {})
                            if metrics:
                                mcols = st.columns(5)
                                for j, (metric, score) in enumerate(metrics.items()):
                                    with mcols[j % 5]:
                                        st.metric(metric.capitalize(), f"{round(score * 10, 1)}/10")
                            if eval_data.get("reason"):
                                st.caption(f"💬 {eval_data['reason']}")
                            st.markdown("---")

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
                st.error(f"❌ Backend error: {response.status_code}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again — evaluation pipeline can take up to 3 minutes.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Make sure FastAPI server is running on port 8000.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888'>Built with FastAPI + OpenAI + Streamlit 🚀</p>",
    unsafe_allow_html=True
)