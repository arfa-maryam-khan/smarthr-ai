"""
SmartHR AI - Main Application Interface

This is the UI of the Streamlit app. It handles:
- Navigation between pages (Home, Policy Assistant, Recruitment Hub)
- UI rendering for all three pages
- Session state management (keeps data between reruns)
- File uploads and processing

This is the UI that users interact with. All the heavy lifting
(AI models, parsing, screening) happens in the modules/ folder.
"""

import streamlit as st
import os
from modules.policy_chatbot import PolicyChatbot
from modules.recruitment import RecruitmentEngine
import pandas as pd
import plotly.graph_objects as go


# PAGE CONFIGURATION
# sets up the page layout and browser tab
st.set_page_config(
    page_title="SmartHR AI",
    page_icon="🤖",
    layout="wide"
)


# SESSION STATE INITIALIZATION
# Streamlit reruns the entire script on every interaction. Session state lets us
# persist data between reruns.

# Policy chatbot state
if 'policy_chatbot' not in st.session_state:
    st.session_state.policy_chatbot = None  # The loaded chatbot instance
    st.session_state.policies_loaded = False  # Whether policies are indexed

# Recruitment engine state
if 'recruitment_engine' not in st.session_state:
    st.session_state.recruitment_engine = None  # The loaded engine instance
    st.session_state.screening_results = None  # Most recent screening results

# Chat history for policy assistant
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # List of Q&A pairs

# Current page tracking
if 'page' not in st.session_state:
    st.session_state.page = 'home'  # Start on home page


# NAVIGATION FUNCTIONS
# These callback(on_click) functions change which page is displayed.

def nav_home():
    """Navigate to the home page"""
    st.session_state.page = 'home'

def nav_policy():
    """Navigate to the policy assistant page"""
    st.session_state.page = 'policy'

def nav_recruitment():
    """Navigate to the recruitment hub page"""
    st.session_state.page = 'recruitment'


# SIDEBAR NAVIGATION
# The sidebar is visible on all pages and provides navigation
with st.sidebar:
    st.title("🤖 SmartHR AI")
    st.markdown("---")
    
    # Navigation buttons - on_click triggers the callback before rerun
    st.button("🏠 Home", on_click=nav_home, use_container_width=True)
    st.button("💬 Policy Assistant", on_click=nav_policy, use_container_width=True)
    st.button("📄 Recruitment Hub", on_click=nav_recruitment, use_container_width=True)
    
    st.markdown("---")
    st.caption("Powered by Groq • Sentence-BERT • FAISS")


# HOME PAGE
if st.session_state.page == 'home':
    # Main header
    st.title("🤖 SmartHR AI")
    st.markdown("### Intelligent HR Assistant for Policy Management & Recruitment")
    
    st.markdown("---")
    
    # Two-column layout for the two main features
    col1, col2 = st.columns(2)
    
    # Policy Assistant card
    with col1:
        st.markdown("### 💬 Policy Assistant")
        st.info(
            "Upload HR policy PDFs and ask questions in natural language. "
            "AI answers with source citations using RAG (Retrieval-Augmented Generation)."
        )
        
        # Launch button navigates to policy page
        st.button(
            "🚀 Launch Policy Assistant",
            key="launch_policy",
            on_click=nav_policy,
            use_container_width=True,
            type="primary"
        )
    
    # Recruitment Hub card
    with col2:
        st.markdown("### 📄 Recruitment Hub")
        st.info(
            "Upload resumes + job description to get intelligent candidate rankings "
            "and auto-generated interview questions."
        )
        
        # Launch button navigates to recruitment page
        st.button(
            "🚀 Launch Recruitment Hub",
            key="launch_recruit",
            on_click=nav_recruitment,
            use_container_width=True,
            type="primary"
        )
    
    # Tech stack footer
    st.markdown("---")
    st.markdown("### 🔧 Tech Stack")
    st.markdown("**Sentence-BERT** • **FAISS** • **Groq Llama 3.3** • **PyPDF2**")


# POLICY ASSISTANT PAGE
elif st.session_state.page == 'policy':
    # Back button at the top
    st.button("← Back to Home", key="back_policy", on_click=nav_home)
    
    st.title("💬 HR Policy Assistant")
    
    # Document upload section (collapsed if policies already loaded)
    with st.expander("📤 Upload Policy Documents", expanded=not st.session_state.policies_loaded):
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key="policy_uploader"
        )
        
        # Process button
        if st.button("🚀 Process Documents", type="primary", key="process_docs"):
            if uploaded_files:
                with st.spinner("Processing documents... This may take a minute."):
                    # Save uploaded files to disk
                    os.makedirs('data/policies', exist_ok=True)
                    
                    # Clear old policy files first
                    for f in os.listdir('data/policies'):
                        if f.endswith('.pdf'):
                            os.remove(os.path.join('data/policies', f))
                    
                    # Save new files
                    for file in uploaded_files:
                        with open(f"data/policies/{file.name}", "wb") as f:
                            f.write(file.getbuffer())
                    
                    try:
                        # Initialize chatbot and process the PDFs
                        chatbot = PolicyChatbot()
                        
                        # Load policies and build the searchable vector store
                        if chatbot.load_policies() and chatbot.build_vector_store():
                            st.session_state.policy_chatbot = chatbot
                            st.session_state.policies_loaded = True
                            st.success("✅ Documents processed successfully!")
                            st.rerun()  # Refresh to show the chat interface
                        else:
                            st.error("Failed to process documents")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please upload PDF files first")
    
    # Chat interface (only show if policies are loaded)
    if st.session_state.policies_loaded:
        st.markdown("---")
        st.markdown("### 💭 Ask Questions")
        
        # Question input
        query = st.text_input(
            "Your question:",
            placeholder="e.g., How many vacation days do I get?",
            key="policy_query"
        )
        
        # Ask button - triggers the RAG pipeline
        if st.button("Ask", type="primary", key="ask_button") and query:
            with st.spinner("Searching policy documents..."):
                try:
                    # Call the chatbot to generate an answer
                    response = st.session_state.policy_chatbot.generate_response(query)
                    
                    # Add to chat history (newest first)
                    st.session_state.chat_history.insert(0, {
                        'q': query,
                        'a': response['answer'],
                        's': response['sources']
                    })
                    
                    st.rerun()  # Refresh to show the new Q&A
                    
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
        
        # Display chat history (all previous Q&As)
        for chat in st.session_state.chat_history:
            st.markdown(f"**Q:** {chat['q']}")
            st.markdown(f"**A:** {chat['a']}")
            
            # Show which policy documents were used
            if chat['s']:
                st.caption(f"📚 Sources: {', '.join(chat['s'])}")
            
            st.markdown("---")
    else:
        st.info("👆 Upload and process policy documents to start asking questions")


# RECRUITMENT HUB PAGE
elif st.session_state.page == 'recruitment':
    # Back button at the top
    st.button("← Back to Home", key="back_recruit", on_click=nav_home)
    
    st.title("📄 Recruitment Hub")
    
    # Initialize the recruitment engine (only once per session)
    # This loads all the AI models, so we do it lazily
    if st.session_state.recruitment_engine is None:
        with st.spinner("Loading AI models... (first time takes ~1 minute)"):
            try:
                st.session_state.recruitment_engine = RecruitmentEngine()
            except Exception as e:
                st.error(f"Failed to load recruitment engine: {str(e)}")
                st.stop()  # Can't continue without the engine
    
    # Two tabs: screening and interview questions
    tab1, tab2 = st.tabs(["🎯 Screen Candidates", "❓ Interview Questions"])
    
    # TAB 1: CANDIDATE SCREENING
    with tab1:
        # Two-column layout for inputs
        col1, col2 = st.columns(2)
        
        # Left column: Resume upload
        with col1:
            st.markdown("**Upload Resumes**")
            resumes = st.file_uploader(
                "PDF files",
                type=['pdf'],
                accept_multiple_files=True,
                key="resume_uploader"
            )
        
        # Right column: Job description
        with col2:
            st.markdown("**Job Description**")
            jd = st.text_area(
                "Paste job description here",
                height=200,
                key="jd_input"
            )
        
        # Threshold slider - candidates above this score get shortlisted
        threshold = st.slider(
            "Shortlist threshold (%)",
            min_value=0,
            max_value=100,
            value=50,
            key="threshold_slider",
            help="Candidates with scores above this will be shortlisted"
        )
        
        # Screen button - does the heavy lifting
        if st.button("🚀 Screen Candidates", type="primary", key="screen_button"):
            if resumes and jd:
                with st.spinner("Screening candidates... This may take a minute."):
                    # Save uploaded resumes to disk
                    os.makedirs('temp/resumes', exist_ok=True)
                    
                    # Clear old resume files
                    for f in os.listdir('temp/resumes'):
                        os.remove(os.path.join('temp/resumes', f))
                    
                    # Save new resumes and collect paths
                    paths = []
                    for resume_file in resumes:
                        path = f"temp/resumes/{resume_file.name}"
                        with open(path, "wb") as f:
                            f.write(resume_file.getbuffer())
                        paths.append(path)
                    
                    try:
                        # Run the screening engine
                        # This: extracts skills, compares to JD, calculates scores
                        results = st.session_state.recruitment_engine.screen_candidates(
                            paths,
                            jd,
                            threshold
                        )
                        
                        # Store results in session state
                        st.session_state.screening_results = results
                        st.session_state.current_jd = jd  # Save JD for question generation
                        
                        st.rerun()  # Refresh to show results
                        
                    except Exception as e:
                        st.error(f"Error during screening: {str(e)}")
                        st.rerun()
            else:
                st.warning("Please upload resumes and provide a job description")
        
        # Display screening results (if we have any)
        if st.session_state.screening_results:
            st.markdown("---")
            st.markdown("### 📊 Screening Results")
            
            # Convert results to DataFrame for easy display
            df = pd.DataFrame(st.session_state.screening_results)
            
            # Summary metrics at the top
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Candidates", len(df))
            with col2:
                st.metric("Shortlisted", len(df[df['shortlisted']]))
            with col3:
                st.metric("Average Score", f"{df['final_score'].mean():.1f}")
            
            # Bar chart showing scores (green = shortlisted, red = not shortlisted)
            fig = go.Figure(data=[go.Bar(
                x=df['name'],
                y=df['final_score'],
                marker_color=['green' if shortlisted else 'red' for shortlisted in df['shortlisted']]
            )])
            fig.update_layout(
                title="Candidate Scores",
                xaxis_title="Candidate Name",
                yaxis_title="Final Score"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed results table
            st.dataframe(
                df[[
                    'name',
                    'email',
                    'final_score',
                    'similarity_score',
                    'skill_match_rate',
                    'matched_skills_count'
                ]],
                use_container_width=True
            )
    
    # TAB 2: INTERVIEW QUESTIONS
    with tab2:
        # Only show this tab if we have screening results
        if st.session_state.screening_results:
            # Filter to only shortlisted candidates
            shortlisted = [r for r in st.session_state.screening_results if r['shortlisted']]
            
            if shortlisted:
                # Dropdown to select which candidate
                candidate = st.selectbox(
                    "Select candidate",
                    [c['name'] for c in shortlisted],
                    key="candidate_select"
                )
                
                # Get the full info for this candidate
                info = next(c for c in shortlisted if c['name'] == candidate)
                
                # Show candidate summary
                st.write(f"**Final Score:** {info['final_score']}")
                st.write(f"**Matched Skills:** {', '.join(info['matched_skills'][:5])}")
                
                # Slider for number of questions
                num_q = st.slider(
                    "Number of questions",
                    min_value=3,
                    max_value=10,
                    value=5,
                    key="num_questions"
                )
                
                # Generate questions button
                if st.button("🤖 Generate Interview Questions", type="primary", key="generate_q"):
                    with st.spinner("Generating personalized questions..."):
                        try:
                            # Call the AI to generate questions
                            questions_data = st.session_state.recruitment_engine.generate_interview_questions(
                                st.session_state.current_jd,
                                info,
                                num_q
                            )
                            
                            # Store in session state
                            st.session_state.generated_questions = questions_data
                            st.rerun()  # Refresh to display questions
                            
                        except Exception as e:
                            st.error(f"Error generating questions: {str(e)}")
                            st.rerun()
                
                # Display generated questions
                if 'generated_questions' in st.session_state and st.session_state.generated_questions:
                    st.markdown("### ❓ Interview Questions")
                    st.info("💡 Keywords below each question help you evaluate the candidate's answer")
                    
                    # Show each question with its evaluation keywords
                    for i, q_data in enumerate(st.session_state.generated_questions, 1):
                        if isinstance(q_data, dict):
                            # Show the question
                            st.markdown(f"**{i}. {q_data.get('question', 'Question unavailable')}**")
                            
                            # Show evaluation keywords as colored badges
                            if 'keywords' in q_data and q_data['keywords']:
                                keywords_html = " ".join([
                                    f'<span style="background-color: #e1f5ff; padding: 4px 8px; '
                                    f'border-radius: 4px; margin: 2px; display: inline-block; '
                                    f'font-size: 0.85em;">{keyword}</span>'
                                    for keyword in q_data['keywords']
                                ])
                                st.markdown(
                                    f'<div style="margin-top: 8px; margin-bottom: 20px;">'
                                    f'🔑 <b>Look for:</b> {keywords_html}</div>',
                                    unsafe_allow_html=True
                                )
                        else:
                            # Fallback if format is different
                            st.markdown(f"**{i}. {q_data}**")
            else:
                st.info("No candidates were shortlisted. Try lowering the threshold or uploading more resumes.")
        else:
            st.info("Screen candidates first in the 'Screen Candidates' tab")