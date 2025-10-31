"""
Streamlit Application for AI Cover Letter Generator
Multi-Agent System with Producer and Critic Agents
"""

import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime
import os

# Import agents
from agents.producer_agent import generate_cover_letter, refine_cover_letter
from agents.critic_agent import critique_cover_letter
from agents.workflow import run_single_iteration_workflow, get_final_cover_letter, get_workflow_summary

# Import utilities
from utils.pdf_parser import extract_text_from_pdf
from utils.contact_extractor import extract_contact_info
from utils.export_utils import create_docx, create_pdf

# Page configuration
st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for API key
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY environment variable not set!")
    st.stop()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .stProgress > div > div > div > div {
        background-color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'final_letter' not in st.session_state:
    st.session_state.final_letter = None

# Header
st.markdown('<p class="main-header">📝 AI Cover Letter Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate tailored cover letters using multi-agent AI with iterative refinement</p>', unsafe_allow_html=True)

# Sidebar - Input Section
st.sidebar.header("📋 Input Your Information")

# Job Description Input
st.sidebar.subheader("1️⃣ Job Description")
job_description = st.sidebar.text_area(
    "Paste the job description here",
    placeholder="Copy and paste the full job description...",
    height=200,
    help="Include all requirements, qualifications, and company information"
)

# User Draft Input
st.sidebar.subheader("2️⃣ Your Current Cover Letter")
user_draft = st.sidebar.text_area(
    "Paste your current cover letter draft",
    placeholder="Your existing cover letter or key points...\n\nInclude:\n- Your name\n- Contact information\n- Relevant experience\n- Skills and achievements",
    height=300,
    help="This will be used as the base for improvement. Include your contact info at the end."
)

st.sidebar.markdown("---")

# Advanced Settings
st.sidebar.subheader("⚙️ Advanced Settings")

with st.sidebar.expander("🎯 Generation Settings", expanded=False):
    quality_threshold = st.slider(
        "Quality Threshold",
        min_value=7.0,
        max_value=9.5,
        value=9.0,
        step=0.5,
        help="Stop early if initial score exceeds this threshold (saves 6-10 seconds!)"
    )
    
    st.info(f"""
    **How it works:**
    - Score ≥ {quality_threshold}: Uses initial draft (fast!)
    - Score < {quality_threshold}: Refines once more
    """)

st.sidebar.markdown("---")

# Generate Button
generate_button = st.sidebar.button(
    "🚀 Generate Cover Letter",
    type="primary",
    use_container_width=True
)

# Clear button
if st.sidebar.button("🔄 Clear & Start Over", use_container_width=True):
    st.session_state.generated = False
    st.session_state.workflow_results = None
    st.session_state.final_letter = None
    st.rerun()

# Main Generation Logic
if generate_button:
    # Validation
    if not job_description or len(job_description.strip()) < 50:
        st.error("⚠️ Please provide a job description (at least 50 characters)")
        st.stop()
    
    if not user_draft or len(user_draft.strip()) < 100:
        st.error("⚠️ Please provide your cover letter draft (at least 100 characters)")
        st.stop()
    
    # Create progress containers
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    # Start timer
    start_time = time.time()
    
    try:
        # Phase 1: Contact Extraction
        with status_container.container():
            st.info("👤 Extracting contact information...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        # Phase 2: Generation
        with status_container.container():
            st.info("✍️ Generating cover letter with AI agents...")
        progress_bar.progress(20)
        
        # Run the multi-agent workflow
        workflow_results = run_single_iteration_workflow(
            job_description=job_description,
            user_draft=user_draft,
            quality_threshold=quality_threshold
        )
        
        progress_bar.progress(80)
        
        # Get final cover letter
        final_letter = get_final_cover_letter(workflow_results)
        summary = get_workflow_summary(workflow_results)
        
        progress_bar.progress(100)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Success message
        with status_container.container():
            st.success(f"✅ Cover letter generated successfully in {elapsed_time:.1f} seconds!")
        
        time.sleep(0.5)
        status_container.empty()
        progress_bar.empty()
        
        # Store in session state
        st.session_state.generated = True
        st.session_state.workflow_results = workflow_results
        st.session_state.final_letter = final_letter
        st.session_state.summary = summary
        st.session_state.elapsed_time = elapsed_time
        
    except Exception as e:
        progress_bar.empty()
        status_container.error(f"❌ Error: {str(e)}")
        st.exception(e)
        st.stop()

# Display Results (if generated)
if st.session_state.generated and st.session_state.workflow_results:
    
    workflow_results = st.session_state.workflow_results
    final_letter = st.session_state.final_letter
    summary = st.session_state.summary
    elapsed_time = st.session_state.elapsed_time
    
    st.markdown("---")
    
    # Summary Metrics
    st.subheader("📊 Generation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        iterations = len(workflow_results['drafts'])
        st.metric(
            "Iterations",
            iterations,
            help="Number of drafts created"
        )
    
    with col2:
        improvement = summary['improvement']
        st.metric(
            "Final Quality Score",
            f"{summary['final_score']}/10",
            f"+{improvement:.1f}" if improvement > 0 else f"{improvement:.1f}",
            delta_color="normal",
            help="Overall quality assessment"
        )
    
    with col3:
        st.metric(
            "Processing Time",
            f"{elapsed_time:.1f}s",
            help="Total generation time"
        )
    
    with col4:
        stop_reason = summary['stop_reason']
        if 'early' in stop_reason:
            display_reason = "✅ Quality Met"
            reason_help = "Initial draft met quality threshold"
        else:
            display_reason = "🔄 Refined"
            reason_help = "Draft was refined once"
        
        st.metric(
            "Result",
            display_reason,
            help=reason_help
        )
    
    st.markdown("---")
    
    # Contact Information
    st.subheader("👤 Extracted Contact Information")
    
    contact_info = workflow_results.get('contact_info', {})
    
    if contact_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Name**")
            st.write(contact_info.get('name', 'Not Found'))
        
        with col2:
            st.markdown("**Email**")
            st.write(contact_info.get('email', 'Not Found'))
        
        with col3:
            st.markdown("**Phone**")
            st.write(contact_info.get('phone', 'Not Found'))
    
    st.markdown("---")
    
    # Final Cover Letter Display
    st.subheader("📄 Your Generated Cover Letter")
    
    # Download Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📄 Download TXT",
            final_letter,
            file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        try:
            docx_buffer = create_docx(final_letter, contact_info)
            st.download_button(
                "📘 Download DOCX",
                docx_buffer.getvalue(),
                file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"DOCX export failed: {e}")
    
    with col3:
        try:
            pdf_output = create_pdf(final_letter, contact_info)
            # Handle both bytes and bytearray from fpdf2
            if isinstance(pdf_output, bytearray):
                pdf_bytes = bytes(pdf_output)
            else:
                pdf_bytes = pdf_output
            
            st.download_button(
                "📕 Download PDF",
                pdf_bytes,
                file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error(f"PDF export failed: {e}")
    
    st.markdown("")
    
    # Display the letter
    st.text_area(
        "Final Cover Letter",
        final_letter,
        height=400,
        key="final_display",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quality Score Progression
    st.subheader("📈 Quality Score Progression")
    
    scores = [c['overall_score'] for c in workflow_results['critiques']]
    iterations_list = list(range(1, len(scores) + 1))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=iterations_list,
        y=scores,
        mode='lines+markers',
        name='Quality Score',
        line=dict(color='#10b981', width=3),
        marker=dict(size=12, symbol='circle'),
        hovertemplate='Iteration %{x}<br>Score: %{y}/10<extra></extra>'
    ))
    
    fig.add_hline(
        y=quality_threshold,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"Target: {quality_threshold}",
        annotation_position="right"
    )
    
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Quality Score (out of 10)",
        yaxis_range=[0, 10],
        height=400,
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed Critique Breakdown
    st.subheader("📝 Detailed Quality Breakdown")
    
    final_critique = summary['final_critique']
    
    # Score breakdown
    st.markdown("**Quality Scores:**")
    
    score_cols = st.columns(5)
    score_labels = [
        "Job Alignment",
        "Skill Highlighting",
        "Professional Tone",
        "Examples",
        "Length & Structure"
    ]
    
    for col, label, key in zip(score_cols, score_labels, final_critique['scores'].keys()):
        with col:
            st.metric(label, f"{final_critique['scores'][key]}/10")
    
    st.markdown("")
    
    # Issues and Suggestions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔴 Issues Addressed:**")
        if final_critique.get('issues'):
            for issue in final_critique['issues']:
                st.markdown(f"- {issue}")
        else:
            st.markdown("_No major issues found!_")
    
    with col2:
        st.markdown("**💡 Final Suggestions:**")
        if final_critique.get('suggestions'):
            for suggestion in final_critique['suggestions']:
                st.markdown(f"- {suggestion}")
        else:
            st.markdown("_Looks great!_")
    
    st.markdown("---")
    
    # All Versions History
    st.subheader("📚 All Versions & Critiques")
    
    tabs = st.tabs([f"📄 Version {i+1}" for i in range(len(workflow_results['drafts']))])
    
    for i, tab in enumerate(tabs):
        with tab:
            draft = workflow_results['drafts'][i]
            critique = workflow_results['critiques'][i]
            
            # Version info
            if i == 0:
                st.info("🎯 **Initial Draft** - Generated from your input")
            else:
                st.info(f"🔄 **Refined Version {i}** - Improved based on critique")
            
            st.markdown("")
            
            # Scores
            st.markdown("**Quality Scores:**")
            score_cols_tab = st.columns(6)
            
            score_labels_tab = [
                "Job Align",
                "Skills",
                "Tone",
                "Examples",
                "Length",
                "Overall"
            ]
            
            score_keys = list(critique['scores'].keys())
            
            for j, (col, label) in enumerate(zip(score_cols_tab[:5], score_labels_tab[:5])):
                col.metric(label, f"{critique['scores'][score_keys[j]]}/10")
            
            score_cols_tab[5].metric(score_labels_tab[5], f"{critique['overall_score']}/10")
            
            st.markdown("")
            
            # Issues and suggestions for this version
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 Issues:**")
                if critique.get('issues'):
                    for issue in critique['issues']:
                        st.markdown(f"- {issue}")
                else:
                    st.markdown("_None_")
            
            with col2:
                st.markdown("**💡 Suggestions:**")
                if critique.get('suggestions'):
                    for suggestion in critique['suggestions']:
                        st.markdown(f"- {suggestion}")
                else:
                    st.markdown("_None_")
            
            st.markdown("---")
            
            # Draft content
            st.markdown(f"**Cover Letter ({len(draft.split())} words):**")
            st.text_area(
                f"Version {i+1}",
                draft,
                height=300,
                key=f"draft_{i}",
                label_visibility="collapsed"
            )

else:
    # Landing page when no letter is generated
    st.markdown("""
    <div style="background-color: #dbeafe; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6; margin: 1rem 0;">
    
    ### 🚀 How to Get Started:
    
    1. **Paste the job description** in the sidebar (at least 50 characters)
    2. **Paste your current cover letter** or key points (at least 100 characters)
       - Include your name and contact information
       - Mention your relevant skills and experience
    3. **Adjust quality threshold** if desired (default: 9.0)
    4. **Click "Generate Cover Letter"** and wait 6-16 seconds
    5. **Download** your cover letter in TXT, DOCX, or PDF format
    
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("✨ What Makes This Special?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 Multi-Agent AI**
        
        Two specialized agents work together:
        - **Producer Agent**: Writes & refines
        - **Critic Agent**: Evaluates quality
        
        Iterative refinement until quality threshold is met.
        """)
    
    with col2:
        st.markdown("""
        **⚡ Smart & Fast**
        
        Intelligent workflow:
        - **6-8 seconds**: High-quality initial draft
        - **12-16 seconds**: Full refinement cycle
        - Early exit when threshold met
        """)
    
    with col3:
        st.markdown("""
        **🎯 Professional Quality**
        
        Every letter includes:
        - Tailored to job description
        - Professional formatting
        - No placeholders or brackets
        - Proper contact information
        """)
    
    st.markdown("---")
    
    st.subheader("📊 How It Works")
    
    st.markdown("""
    ```
    1. 👤 Extract Contact Information
    2. ✍️  Generate Initial Draft (Producer Agent)
    3. 🔍 Evaluate Quality (Critic Agent)
       ├─ Score ≥ Threshold → ✅ Done! (Fast Path)
       └─ Score < Threshold → Continue to step 4
    4. ♻️  Refine Based on Feedback (Producer Agent)
    5. 🔍 Final Evaluation (Critic Agent)
    6. 💾 Download in 3 formats (TXT, DOCX, PDF)
    ```
    """)
    
    st.markdown("---")
    
    st.subheader("💡 Tips for Best Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **For Your Draft:**
        - Include your full name
        - Add email and phone number
        - Mention specific skills and achievements
        - Reference relevant experience
        - Use concrete examples
        """)
    
    with col2:
        st.markdown("""
        **For Job Description:**
        - Copy the entire posting
        - Include company information
        - Keep all requirements listed
        - Include role responsibilities
        - Preserve formatting
        """)
    
    st.markdown("---")
    
    st.info("""
    **📌 Note:** This application uses Google's Gemini API for AI generation. 
    Make sure `GEMINI_API_KEY` is set in your environment variables.
    """)
    
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <strong>Built with:</strong> Multi-Agent AI • Streamlit • Python • Gemini API
    </div>
    """, unsafe_allow_html=True)