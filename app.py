"""
SmartHR AI - Intelligent HR Assistant
"""
import streamlit as st
import os
from modules.policy_chatbot import PolicyChatbot
from modules.recruitment import RecruitmentEngine
import pandas as pd
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="SmartHR AI",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'policy_chatbot' not in st.session_state:
    st.session_state.policy_chatbot = None
    st.session_state.policies_loaded = False

if 'recruitment_engine' not in st.session_state:
    st.session_state.recruitment_engine = None

if 'screening_results' not in st.session_state:
    st.session_state.screening_results = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.title("🤖 SmartHR AI")
    st.markdown("---")
    
    # Initialize page in session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Check if navigation was triggered from a button
    if 'nav_target' in st.session_state and st.session_state.nav_target:
        st.session_state.current_page = st.session_state.nav_target
        st.session_state.nav_target = None
    
    # Get the index of the current page
    pages = ["🏠 Home", "💬 Policy Assistant", "📄 Recruitment Hub"]
    current_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
    
    # Radio button for navigation
    page = st.radio(
        "Navigate",
        pages,
        index=current_index,
        key="page_radio"
    )
    
    # Update session state when radio changes
    if page != st.session_state.current_page:
        st.session_state.current_page = page
    
    st.markdown("---")
    
    # Quick home button (only show if not on home page)
    if st.session_state.current_page != "🏠 Home":
        if st.button("🏠 Quick Home", use_container_width=True, key="sidebar_home"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
        st.markdown("---")
    
    st.caption("Powered by Groq + Sentence-BERT + FAISS")
# ============================================================
# HOME PAGE
# ============================================================
if st.session_state.current_page == "🏠 Home":
    st.markdown('<p class="main-header">🤖 SmartHR AI</p>', unsafe_allow_html=True)
    st.markdown("### Intelligent HR Assistant for Policy Management & Recruitment")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Policy Assistant")
        st.info("""
        **Upload policy PDFs** and ask questions in natural language.
        
        AI answers with source citations using RAG (Retrieval-Augmented Generation).
        """)
        
        # Navigation button
        if st.button("🚀 Launch Policy Assistant", key="btn_policy", use_container_width=True, type="primary"):
            st.session_state.current_page = "💬 Policy Assistant"
            st.rerun()
    
    with col2:
        st.markdown("### 📄 Recruitment Hub")
        st.info("""
        **Upload resumes + JD** to get intelligent candidate rankings.
        
        Auto-generate personalized interview questions for shortlisted candidates.
        """)
        
        # Navigation button
        if st.button("🚀 Launch Recruitment Hub", key="btn_recruit", use_container_width=True, type="primary"):
            st.session_state.current_page = "📄 Recruitment Hub"
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔧 Tech Stack")
    st.markdown("**Sentence-BERT** • **FAISS** • **Groq Llama 3.3** • **PyPDF2**")
# ============================================================
# POLICY ASSISTANT
# ============================================================
elif st.session_state.current_page == "💬 Policy Assistant":
    # Back to Home button
    if st.button("← Back to Home", key="home_from_policy", type="secondary"):
        st.session_state.current_page = "🏠 Home"
        st.rerun()

    st.title("💬 HR Policy Assistant")
    
    # Upload section
    with st.expander("📤 Upload Policy Documents", expanded=not st.session_state.policies_loaded):
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if st.button("🚀 Process Documents", type="primary"):
            if uploaded_files:
                with st.spinner("Processing..."):
                    # Save files
                    os.makedirs('data/policies', exist_ok=True)
                    for f in os.listdir('data/policies'):
                        if f.endswith('.pdf'):
                            os.remove(os.path.join('data/policies', f))
                    
                    for file in uploaded_files:
                        with open(f"data/policies/{file.name}", "wb") as f:
                            f.write(file.getbuffer())
                    
                    try:
                        # Initialize chatbot
                        chatbot = PolicyChatbot()
                        if chatbot.load_policies() and chatbot.build_vector_store():
                            st.session_state.policy_chatbot = chatbot
                            st.session_state.policies_loaded = True
                            st.success("✅ Documents processed!")
                            st.rerun()
                        else:
                            st.error("Failed to process documents")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please upload files first")
    
    # Chat interface
    if st.session_state.policies_loaded:
        st.markdown("---")
        st.markdown("### 💭 Ask Questions")
        
        query = st.text_input("Your question:", placeholder="e.g., How many vacation days?")
        
        if st.button("Ask", type="primary") and query:
            with st.spinner("Searching..."):
                try:
                    response = st.session_state.policy_chatbot.generate_response(query)
                    st.session_state.chat_history.insert(0, {
                        'q': query,
                        'a': response['answer'],
                        's': response['sources']
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Show history
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"**Q:** {chat['q']}")
            st.markdown(f"**A:** {chat['a']}")
            if chat['s']:
                st.caption(f"Sources: {', '.join(chat['s'])}")
            st.markdown("---")
    else:
        st.info("👆 Upload and process documents to start")

# ============================================================
# RECRUITMENT HUB
# ============================================================
elif st.session_state.current_page == "📄 Recruitment Hub":
    # Back to Home button
    if st.button("← Back to Home", key="home_from_policy", type="secondary"):
        st.session_state.current_page = "🏠 Home"
        st.rerun()

    st.title("📄 Recruitment Hub")
    
    # Initialize engine (with better error handling)
    if st.session_state.recruitment_engine is None:
        with st.spinner("Loading AI models... (first time takes ~1 min)"):
            try:
                st.session_state.recruitment_engine = RecruitmentEngine()
                st.success("Ready!", icon="✅")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("💡 Check your GROQ_API_KEY in .env file")
                st.stop()
    
    tab1, tab2 = st.tabs(["🎯 Screen Candidates", "❓ Interview Questions"])
    
    # TAB 1: Screen
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Upload Resumes**")
            resumes = st.file_uploader("PDF files", type=['pdf'], accept_multiple_files=True, key="res")
        
        with col2:
            st.markdown("**Job Description**")
            jd = st.text_area("Paste JD here", height=200, key="jd")
        
        threshold = st.slider("Shortlist threshold (%)", 0, 100, 50)
        
        if st.button("🚀 Screen Candidates", type="primary"):
            if resumes and jd:
                with st.spinner("Screening..."):
                    # Save resumes
                    os.makedirs('temp/resumes', exist_ok=True)
                    for f in os.listdir('temp/resumes'):
                        os.remove(os.path.join('temp/resumes', f))
                    
                    paths = []
                    for r in resumes:
                        path = f"temp/resumes/{r.name}"
                        with open(path, "wb") as f:
                            f.write(r.getbuffer())
                        paths.append(path)
                    
                    try:
                        results = st.session_state.recruitment_engine.screen_candidates(paths, jd, threshold)
                        st.session_state.screening_results = results
                        st.session_state.current_jd = jd
                        st.success(f"✅ Screened {len(results)} candidates!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Upload resumes and JD first")
        
        # Show results
        if st.session_state.screening_results:
            st.markdown("---")
            st.markdown("### 📊 Results")
            
            df = pd.DataFrame(st.session_state.screening_results)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Shortlisted", len(df[df['shortlisted']]))
            with col3:
                st.metric("Avg Score", f"{df['final_score'].mean():.1f}")
            
            # Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=df['name'],
                    y=df['final_score'],
                    marker_color=['green' if s else 'red' for s in df['shortlisted']]
                )
            ])
            fig.update_layout(title="Candidate Scores", xaxis_title="Name", yaxis_title="Score")
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(
                df[['name', 'email', 'final_score', 'similarity_score', 'skill_match_rate', 'matched_skills_count']],
                use_container_width=True
            )
    
    # TAB 2: Questions
    with tab2:
        if st.session_state.screening_results:
            shortlisted = [r for r in st.session_state.screening_results if r['shortlisted']]
            
            if shortlisted:
                candidate = st.selectbox("Select candidate", [c['name'] for c in shortlisted])
                info = next(c for c in shortlisted if c['name'] == candidate)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Score:** {info['final_score']}")
                    st.write(f"**Experience:** {info['experience_years']} years")
                with col2:
                    st.write(f"**Matched Skills:** {', '.join(info['matched_skills'][:5])}")
                
                st.markdown("---")
                
                num_q = st.slider("Number of questions", 3, 10, 5)
                
                if st.button("🤖 Generate Questions", type="primary"):
                    with st.spinner("Generating personalized questions with evaluation criteria..."):
                        try:
                            questions_data = st.session_state.recruitment_engine.generate_interview_questions(
                                st.session_state.current_jd,
                                info,
                                num_q
                            )
                            
                            st.markdown("### ❓ Interview Questions")
                            st.info("💡 Keywords below each question help evaluate if the candidate's answer covers key concepts")
                            
                            for i, q_data in enumerate(questions_data, 1):
                                # Question
                                st.markdown(f"**{i}. {q_data['question']}**")
                                
                                # Keywords in colored badges
                                keywords_html = " ".join([
                                    f'<span style="background-color: #e1f5ff; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 0.85em;">{kw}</span>'
                                    for kw in q_data['keywords']
                                ])
                                
                                st.markdown(
                                    f'<div style="margin-top: 8px; margin-bottom: 20px;">🔑 <b>Look for:</b> {keywords_html}</div>',
                                    unsafe_allow_html=True
                                )
                            
                            # Download questions with keywords
                            download_text = ""
                            for i, q_data in enumerate(questions_data, 1):
                                download_text += f"{i}. {q_data['question']}\n"
                                download_text += f"   Key Concepts: {', '.join(q_data['keywords'])}\n\n"
                            
                            st.download_button(
                                "📥 Download Questions & Keywords",
                                download_text,
                                f"interview_questions_{info['name'].replace(' ', '_')}.txt",
                                "text/plain"
                            )
                        
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
            else:
                st.info("No shortlisted candidates")
        else:
            st.info("Screen candidates first in the 'Screen Candidates' tab")