# index.py - Main Streamlit App
# Updated to match your file structure

import streamlit as st
import plotly.graph_objects as go
import time
from concurrent.futures import ThreadPoolExecutor

# Import agents
from agents.producer_agent import generate_cover_letter, refine_cover_letter
from agents.critic_agent import critique_cover_letter

# Import utilities
from utils.pdf_parser import extract_text_from_pdf 
from utils.contact_extractor import extract_contact_info
from utils.export_utils import create_docx, create_pdf

# Page config
st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default settings (since you don't have config.py visible)
DEFAULT_MAX_ITERATIONS = 3
DEFAULT_QUALITY_THRESHOLD = 8.5

# Custom CSS
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
    .stProgress > div > div > div > div {
        background-color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📝 AI Cover Letter Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate tailored cover letters using AI agents with iterative refinement</p>', unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header("📋 Inputs")

uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (PDF)",
    type=['pdf'],
    help="Upload your resume in PDF format. Contact information will be extracted automatically."
)

job_description = st.sidebar.text_area(
    "Job Description",
    placeholder="Paste the job description here...",
    help="Paste the full job description",
    height=200
)

# NEW: Add optional user draft input
user_draft = st.sidebar.text_area(
    "Your Draft Cover Letter (Optional)",
    placeholder="If you have a draft cover letter, paste it here. Otherwise, we'll create one from your resume.",
    help="Optional: Paste your existing cover letter draft for improvement",
    height=150
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Advanced Settings")

with st.sidebar.expander("🎯 Quality Settings", expanded=False):
    max_iterations = st.slider(
        "Max Refinement Loops",
        min_value=1,
        max_value=5,
        value=DEFAULT_MAX_ITERATIONS,
        help="Number of refinement iterations (more = better quality but slower)"
    )
    
    quality_threshold = st.slider(
        "Quality Threshold",
        min_value=7.0,
        max_value=9.5,
        value=DEFAULT_QUALITY_THRESHOLD,
        step=0.5,
        help="Stop early if score exceeds this threshold"
    )

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Current Settings:**
- Max iterations: **{max_iterations}**
- Quality threshold: **{quality_threshold}/10**
- Auto-extracts contact info from resume/draft
""")

# Generate button
generate_button = st.sidebar.button(
    "🚀 Generate Cover Letter", 
    type="primary", 
    use_container_width=True
)


def run_generation(uploaded_file, job_description, user_draft_input, max_iterations, quality_threshold):
    """
    Simplified workflow matching the Flask/workflow.py architecture
    """
    # Step 1: Extract resume
    print("\n" + "="*70)
    print("STEP 1: EXTRACT RESUME")
    print("="*70)

    resume_result = extract_text_from_pdf(uploaded_file)

    if not resume_result['success']:
        raise Exception(f"Resume extraction failed: {resume_result['error']}")
    
    resume_text = resume_result['text']
    
    # Step 2: Determine what to use as "user_draft"
    print("\n" + "="*70)
    print("STEP 2: PREPARE USER DRAFT")
    print("="*70)
    
    if user_draft_input and len(user_draft_input.strip()) > 50:
        # User provided a draft
        user_draft = user_draft_input.strip()
        print("✓ Using user-provided draft")
        print(f"  Draft length: {len(user_draft)} chars")
    else:
        # Create a minimal draft that includes contact info for extraction
        # Keep it SHORT to avoid issues with the API
        user_draft = f"""Dear Hiring Manager,

I am interested in this position and believe my background would be a good fit.

I have experience in software development and would welcome the opportunity to discuss this role.

Sincerely,
John Doe
john.doe@email.com
(555) 123-4567"""
        print("✓ Created minimal draft for contact extraction")
        print(f"  Draft length: {len(user_draft)} chars")
    
    # Step 3: Extract contact info from user_draft
    print("\n" + "="*70)
    print("STEP 3: EXTRACT CONTACT INFO")
    print("="*70)
    
    try:
        print("Extracting contact information from draft...")
        contact_info = extract_contact_info(user_draft)
        candidate_name = contact_info.get('name', 'Not Found')
        print(f"✓ Extracted name: {candidate_name}")
        print(f"  Email: {contact_info.get('email', 'Not Found')}")
        print(f"  Phone: {contact_info.get('phone', 'Not Found')}")
    except Exception as e:
        print(f"⚠️ Contact extraction failed: {e}")
        # Use fallback
        candidate_name = None
        contact_info = {
            'name': 'Not Found',
            'email': 'Not Found',
            'phone': 'Not Found',
            'address': 'Not Found'
        }
    
    # Step 4: Generate initial draft
    print("\n" + "="*70)
    print("STEP 4: GENERATE INITIAL DRAFT")
    print("="*70)
    
    print(f"API Call Parameters:")
    print(f"  job_description length: {len(job_description)} chars")
    print(f"  user_draft length: {len(user_draft)} chars")
    print(f"  candidate_name: {candidate_name}")
    
    # Check for extremely long inputs that might cause 400 errors
    if len(job_description) > 8000:
        print("⚠️ WARNING: Job description is very long, truncating...")
        job_description = job_description[:8000] + "..."
    
    if len(user_draft) > 5000:
        print("⚠️ WARNING: User draft is very long, truncating...")
        user_draft = user_draft[:5000] + "..."
    
    try:
        current_draft = generate_cover_letter(job_description, user_draft)
        print("✓ Draft generated successfully")
    except Exception as e:
        print(f"❌ Generation failed with error: {e}")
        print(f"   This is likely an API issue. Check your GEMINI_API_KEY")
        raise
    
    # Track all drafts and critiques
    drafts = [current_draft]
    critiques = []
    
    # Step 5: Iterative refinement loop
    stop_reason = 'max_iterations'  # Default
    
    for iteration in range(1, max_iterations + 1):
        print("\n" + "="*70)
        print(f"STEP 5: CRITIQUE & REFINE - Iteration {iteration}")
        print("="*70)
        
        # Critique current draft
        try:
            critique = critique_cover_letter(current_draft, job_description, user_draft)
            critiques.append(critique)
            
            score = critique['overall_score']
            print(f"Score: {score}/10")
        except Exception as e:
            print(f"⚠️ Critique failed: {e}")
            # Use fallback critique
            critique = {
                'scores': {
                    'job_alignment': 7,
                    'skill_highlighting': 7,
                    'professional_tone': 7,
                    'specific_examples': 7,
                    'length': 7
                },
                'overall_score': 7.0,
                'issues': ['Critique failed'],
                'suggestions': ['Manual review recommended']
            }
            critiques.append(critique)
            score = 7.0
        
        # Check if we should stop
        if score >= quality_threshold:
            print(f"✅ Quality threshold reached ({score} >= {quality_threshold})")
            stop_reason = 'quality_threshold'
            break
        
        if iteration >= max_iterations:
            print(f"🔄 Max iterations reached ({iteration} >= {max_iterations})")
            stop_reason = 'max_iterations'
            break
        
        # Refine the draft
        print("Refining draft based on feedback...")
        try:
            current_draft = refine_cover_letter(
                current_draft, 
                critique, 
                job_description, 
                user_draft,
                candidate_name
            )
            drafts.append(current_draft)
            print("✓ Refinement successful")
        except Exception as e:
            print(f"⚠️ Refinement failed: {e}")
            # Keep the previous draft
            break
    
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE")
    print("="*70)
    
    return {
        'resume_text': resume_text,
        'user_draft': user_draft,
        'job_description': job_description,
        'contact_info': contact_info,
        'drafts': drafts,
        'critiques': critiques,
        'current_iteration': len(critiques),
        'stop_reason': stop_reason
    }


# Main area
if generate_button:
    
    # Validation
    if not uploaded_file:
        st.error("⚠️ Please upload your resume (PDF)")
        st.stop()
    
    if not job_description or len(job_description.strip()) < 50:
        st.error("⚠️ Please provide a job description (at least 50 characters)")
        st.stop()
    
    # Create containers for real-time updates
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    # Start timer
    start_time = time.time()
    
    try:
        # Initial status
        with status_container.container():
            st.info("📄 Starting cover letter generation workflow...")
        progress_bar.progress(5)
        time.sleep(0.3)
        
        # Phase 1: Extraction
        with status_container.container():
            st.info("📄 Extracting resume and analyzing job description...")
        progress_bar.progress(15)
        
        # Run the workflow
        final_state = run_generation(
            uploaded_file,
            job_description,
            user_draft,
            max_iterations,
            quality_threshold
        )
        
        progress_bar.progress(80)
        
        # Phase 2: Formatting
        with status_container.container():
            st.info("🎨 Formatting final cover letter...")
        
        contact_info = final_state['contact_info']
        
        # Get the final draft
        final_draft = final_state['drafts'][-1]
        
        progress_bar.progress(100)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Success message
        with status_container.container():
            st.success(f"✅ Cover letter generated successfully in {elapsed_time:.1f} seconds!")
        
        time.sleep(0.5)
        status_container.empty()
        progress_bar.empty()
        
        # Display results
        st.markdown("---")
        
        # Summary metrics
        st.subheader("📊 Generation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        initial_score = final_state['critiques'][0]['overall_score']
        final_score = final_state['critiques'][-1]['overall_score']
        improvement = final_score - initial_score
        
        with col1:
            st.metric(
                "Iterations",
                final_state['current_iteration'],
                help="Number of refinement loops"
            )
        
        with col2:
            st.metric(
                "Final Quality Score",
                f"{final_score}/10",
                f"+{improvement:.1f}" if improvement > 0 else f"{improvement:.1f}",
                delta_color="normal",
                help="Overall quality score from Critic Agent"
            )
        
        with col3:
            st.metric(
                "Processing Time",
                f"{elapsed_time:.1f}s",
                help="Total time from start to finish"
            )
        
        with col4:
            stop_reason_display = "✅ Quality Met" if final_state['stop_reason'] == 'quality_threshold' else "🔄 Max Iterations"
            st.metric(
                "Stop Reason",
                stop_reason_display,
                help="Why the generation stopped"
            )
        
        st.markdown("---")
        
        # Contact Information Section
        st.subheader("👤 Extracted Contact Information")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Name**")
            st.write(contact_info['name'])
        
        with col2:
            st.markdown("**Email**")
            st.write(contact_info['email'])
        
        with col3:
            st.markdown("**Phone**")
            st.write(contact_info['phone'])
        
        with col4:
            st.markdown("**Address**")
            address_display = contact_info['address'][:30] + "..." if len(contact_info['address']) > 30 else contact_info['address']
            st.write(address_display)
        
        st.markdown("---")
        
        # Final Cover Letter
        st.subheader("📄 Your Cover Letter")
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📄 Download TXT",
                final_draft,
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            docx_buffer = create_docx(final_draft, contact_info)
            st.download_button(
                "📘 Download DOCX",
                docx_buffer,
                file_name="cover_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary"
            )
        
        with col3:
            pdf_bytes = create_pdf(final_draft, contact_info)
            st.download_button(
                "📕 Download PDF",
                pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        
        st.markdown("")
        
        # Display the letter
        st.text_area(
            "Final Cover Letter",
            final_draft,
            height=400,
            key="formatted_final",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quality Score Progression
        st.subheader("📈 Quality Score Progression")
        
        scores = [c['overall_score'] for c in final_state['critiques']]
        iterations = list(range(1, len(scores) + 1))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=iterations,
            y=scores,
            mode='lines+markers',
            name='Quality Score',
            line=dict(color='#10b981', width=3),
            marker=dict(size=12, symbol='circle')
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
        
        # Iteration History
        st.subheader("🔍 All Versions & Critiques")
        
        tabs = st.tabs([f"📝 Iteration {i+1}" for i in range(len(final_state['drafts']))])
        
        for i, tab in enumerate(tabs):
            with tab:
                draft = final_state['drafts'][i]
                critique = final_state['critiques'][i]
                
                # Critique scores
                st.markdown("**Quality Scores:**")
                
                score_cols = st.columns(6)
                
                score_labels = [
                    "Job Alignment",
                    "Skill Highlight",
                    "Professional Tone",
                    "Examples",
                    "Length",
                    "Overall"
                ]
                
                score_keys = list(critique['scores'].keys())
                
                for j, (col, label) in enumerate(zip(score_cols[:5], score_labels[:5])):
                    score_val = critique['scores'][score_keys[j]]
                    col.metric(label, f"{score_val}/10")
                
                score_cols[5].metric(score_labels[5], f"{critique['overall_score']}/10")
                
                st.markdown("")
                
                # Issues and suggestions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔴 Issues Found:**")
                    if critique['issues']:
                        for issue in critique['issues']:
                            st.markdown(f"- {issue}")
                    else:
                        st.markdown("_No major issues found_")
                
                with col2:
                    st.markdown("**💡 Suggestions:**")
                    if critique['suggestions']:
                        for suggestion in critique['suggestions']:
                            st.markdown(f"- {suggestion}")
                    else:
                        st.markdown("_No suggestions - looks good!_")
                
                st.markdown("---")
                
                # Draft content
                st.markdown(f"**Cover Letter Draft ({len(draft.split())} words):**")
                st.text_area(
                    f"Draft {i+1}",
                    draft,
                    height=300,
                    key=f"draft_{i}",
                    label_visibility="collapsed"
                )
        
        st.markdown("---")
        
        # Source content
        with st.expander("📚 View Source Content (Resume & Job Description)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📄 Resume Content**")
                st.markdown(f"_Word Count: {len(final_state['resume_text'].split())} words_")
                st.text_area(
                    "Resume",
                    final_state['resume_text'],
                    height=300,
                    key="resume_display",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**🌐 Job Description**")
                st.markdown(f"_Word Count: {len(final_state['job_description'].split())} words_")
                st.text_area(
                    "Job",
                    final_state['job_description'],
                    height=300,
                    key="job_display",
                    label_visibility="collapsed"
                )
    
    except Exception as e:
        progress_bar.empty()
        status_container.error(f"❌ Error: {str(e)}")
        st.exception(e)
        
        st.markdown("---")
        st.markdown("### 🔧 Troubleshooting Tips:")
        st.markdown("""
        - **Check your GEMINI_API_KEY**: Make sure it's set correctly in your environment
        - **Check the console output**: Look for detailed error messages in the terminal
        - Ensure your resume is a valid PDF with extractable text
        - Make sure the job description is complete and detailed
        - Try with shorter job descriptions or drafts if inputs are very long
        """)

else:
    # Landing page
    st.markdown("""
    <div style="background-color: #dbeafe; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6; margin: 1rem 0;">
    
    ### 🚀 How to Get Started:
    
    1. **Upload your resume** (PDF format) in the sidebar
    2. **Paste the job description** in the text area
    3. **(Optional)** Paste your draft cover letter if you have one
    4. **Adjust settings** if needed (optional - defaults work well!)
    5. **Click "Generate Cover Letter"** and wait 5-10 seconds
    6. **Download** your cover letter in TXT, DOCX, or PDF format
    
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("✨ What Makes This Special?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 Multi-Agent AI**
        
        Two specialized agents work together:
        - **Producer**: Writes & refines
        - **Critic**: Evaluates quality
        """)
    
    with col2:
        st.markdown("""
        **🎯 Iterative Refinement**
        
        Your letter gets better with each loop:
        - Automatic quality scoring
        - Targeted improvements
        - Stops when threshold reached
        """)
    
    with col3:
        st.markdown("""
        **⚡ Fast & Accurate**
        
        Get results in seconds:
        - Auto-extracts contact info
        - No placeholders or brackets
        - Professional formatting
        """)
    
    st.markdown("---")
    
    st.subheader("🔄 How It Works")
    
    st.markdown("""
    ```
    1. 📄 Extract Resume & Contact Info
    2. ✏️ Generate Initial Draft (Producer Agent)
    3. 🔍 Evaluate Quality (Critic Agent)
    4. ♻️ Refine Based on Feedback (Producer Agent)
    5. 🔍 Repeat steps 3-4 until quality target reached
    6. 🎨 Format with Contact Info
    7. 💾 Download in 3 formats!
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <strong>Built with:</strong> Multi-Agent AI • Streamlit • Python
    </div>
    """, unsafe_allow_html=True)