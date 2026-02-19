"""
Resume Screening AI - Main Streamlit Application
BERT-powered NLP system for intelligent resume screening
"""

import utils.session
import streamlit as st
import pandas as pd
from datetime import datetime

# Core imports
from core.bert_matcher import load_bert_model, extract_keywords_from_jd
from core.scorer import process_all_resumes

# UI imports
from ui.styles import get_custom_css, create_grade_badge_html, create_skill_pill_html, create_recommendation_box_html
from ui.charts import (
    plot_candidate_ranking_bar,
    plot_score_breakdown_radar,
    plot_skills_heatmap,
    plot_score_distribution,
    plot_experience_vs_score,
    plot_skills_overlap_donut
)
from utils.report_generator import generate_pdf_report


# Page configuration
st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'jd_analysis' not in st.session_state:
    st.session_state.jd_analysis = None
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'model' not in st.session_state:
    st.session_state.model = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""


# === SIDEBAR ===
with st.sidebar:
    st.markdown("## 🤖 Resume Screening AI")
    st.markdown("*Powered by BERT Transformers*")
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    
    model_choice = st.radio(
        "BERT Model:",
        ["Fast (MiniLM-L6)", "Accurate (MPNet-base)"],
        index=0,
        help="Fast model is recommended for quick screening"
    )
    
    min_score_threshold = st.slider(
        "Minimum Score Threshold:",
        min_value=0,
        max_value=100,
        value=40,
        step=5,
        help="Filter candidates below this score"
    )
    
    show_top_n = st.number_input(
        "Show Top N Candidates:",
        min_value=5,
        max_value=50,
        value=50,
        step=5,
        help="Limit results display"
    )
    
    st.markdown("---")
    
    # About section
    st.markdown("### 📖 About")
    st.markdown("""
    This AI system uses **BERT transformers** for semantic understanding to match resumes with job descriptions.
    
    **Features:**
    - 🧠 Semantic similarity matching
    - 🔍 Skills extraction & analysis
    - 📊 Detailed scoring breakdown
    - 📈 Interactive visualizations
    - 📄 PDF report generation
    """)
    
    # How it works
    with st.expander("🔬 How It Works"):
        st.markdown("""
        1. **Extract**: Parse PDF/DOCX resumes
        2. **Analyze**: Extract skills, experience, education
        3. **Match**: BERT semantic similarity with JD
        4. **Score**: Weighted scoring algorithm
        5. **Rank**: Sort candidates by match score
        """)


# === MAIN HEADER ===
st.markdown('<h1 class="app-header">🤖 Resume Screening AI</h1>', unsafe_allow_html=True)
st.markdown("### Intelligent Resume Screening with BERT Transformers")
st.markdown("---")


# === TABS ===
tab1, tab2, tab3 = st.tabs(["📋 Screen Resumes", "📊 Results Dashboard", "👤 Candidate Detail"])


# === TAB 1: SCREEN RESUMES ===
with tab1:
    st.markdown("## 📝 Job Description")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        job_description = st.text_area(
            "Paste the job description here:",
            height=250,
            placeholder="Enter the complete job description including required skills, experience, and qualifications...",
            value=st.session_state.job_description
        )
        st.session_state.job_description = job_description
    
    with col2:
        st.markdown("**Or upload JD file:**")
        jd_file = st.file_uploader("Upload JD (.txt)", type=['txt'], key='jd_upload')
        
        if jd_file:
            jd_text = jd_file.read().decode('utf-8')
            st.session_state.job_description = jd_text
            job_description = jd_text
            st.success("✅ JD file loaded!")
        
        if job_description:
            word_count = len(job_description.split())
            st.metric("Word Count", word_count)
    
    st.markdown("---")
    st.markdown("## 📂 Upload Resumes")
    
    uploaded_files = st.file_uploader(
        "Upload resume files (PDF or DOCX):",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="You can upload multiple resumes at once"
    )
    
    if uploaded_files:
        st.success(f"✅ **{len(uploaded_files)} resumes uploaded**")
        
        # Show uploaded files in a nice grid
        cols = st.columns(3)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                file_size_kb = len(file.getvalue()) / 1024
                st.markdown(f"""
                <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <b>📄 {file.name}</b><br/>
                    <small>{file_size_kb:.1f} KB</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        can_process = job_description and len(job_description.strip()) > 50 and uploaded_files and len(uploaded_files) > 0
        
        if not can_process:
            if not job_description or len(job_description.strip()) < 50:
                st.warning("⚠️ Please enter a job description (at least 50 characters)")
            if not uploaded_files:
                st.warning("⚠️ Please upload at least one resume")
        
        process_button = st.button(
            "🚀 Screen All Resumes",
            disabled=not can_process,
            use_container_width=True,
            type="primary"
        )
    
    # Processing logic
    if process_button:
        with st.spinner("🔄 Processing resumes... This may take a moment..."):
            try:
                # Step 1: Load BERT model
                st.info("📥 Loading BERT model...")
                model_name = 'all-MiniLM-L6-v2' if model_choice == "Fast (MiniLM-L6)" else 'all-mpnet-base-v2'
                
                if st.session_state.model is None:
                    st.session_state.model = load_bert_model(model_name)
                
                model = st.session_state.model
                
                # Step 2: Process all resumes
                st.info(f"🔍 Screening {len(uploaded_files)} resumes...")
                
                results_df = process_all_resumes(uploaded_files, job_description, model)
                
                # Step 3: Extract JD analysis
                jd_analysis = extract_keywords_from_jd(job_description)
                
                # Save to session state
                st.session_state.results_df = results_df
                st.session_state.jd_analysis = jd_analysis
                st.session_state.processing_done = True
                
                # Success message
                top_candidate = results_df.iloc[0]
                st.success(f"""
                ✅ **Successfully screened {len(results_df)} resumes!**
                
                🏆 Top Match: **{top_candidate['name']}** with **{top_candidate['final_score']:.1f}%** score
                """)
                
                # Show quick stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Screened", len(results_df))
                
                with col2:
                    st.metric("Top Score", f"{results_df['final_score'].max():.1f}%")
                
                with col3:
                    st.metric("Average Score", f"{results_df['final_score'].mean():.1f}%")
                
                with col4:
                    shortlisted = len(results_df[results_df['grade'].isin(['A', 'B'])])
                    st.metric("Shortlisted (A+B)", shortlisted)
                
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
                st.exception(e)


# === TAB 2: RESULTS DASHBOARD ===
with tab2:
    if st.session_state.processing_done and st.session_state.results_df is not None:
        df = st.session_state.results_df
        jd_analysis = st.session_state.jd_analysis
        
        # Filter by threshold
        df_filtered = df[df['final_score'] >= min_score_threshold].head(show_top_n)
        
        st.markdown("## 📊 Screening Results")
        st.markdown(f"*Showing {len(df_filtered)} candidates (filtered by score ≥ {min_score_threshold}%)*")
        st.markdown("---")
        
        # Results table
        st.markdown("### 📋 All Candidates")
        
        # Prepare display dataframe
        display_df = df_filtered[[
            'rank', 'name', 'grade', 'final_score', 'skills_score', 
            'experience_years', 'matched_skills_count', 'missing_skills_count'
        ]].copy()
        
        display_df.columns = [
            'Rank', 'Name', 'Grade', 'Final Score (%)', 'Skills Match (%)',
            'Experience (yrs)', 'Matched Skills', 'Missing Skills'
        ]
        
        # Display with styling
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Visualizations
        st.markdown("### 📈 Visualizations")
        
        # Row 1: Rankings and Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ranking = plot_candidate_ranking_bar(df_filtered)
            st.plotly_chart(fig_ranking, use_container_width=True)
        
        with col2:
            fig_distribution = plot_score_distribution(df)
            st.plotly_chart(fig_distribution, use_container_width=True)
        
        # Row 2: Skills Heatmap
        st.markdown("### 🔥 Skills Analysis")
        
        required_skills = jd_analysis.get('required_skills', [])
        candidates_list = df_filtered.to_dict('records')
        
        fig_heatmap = plot_skills_heatmap(candidates_list, required_skills)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Row 3: Experience vs Score
        fig_exp_score = plot_experience_vs_score(df_filtered)
        st.plotly_chart(fig_exp_score, use_container_width=True)
        
    else:
        st.info("👈 Please screen resumes first using the 'Screen Resumes' tab")


# === TAB 3: CANDIDATE DETAIL ===
with tab3:
    if st.session_state.processing_done and st.session_state.results_df is not None:
        df = st.session_state.results_df
        jd_analysis = st.session_state.jd_analysis
        
        st.markdown("## 👤 Candidate Profile")
        
        # Candidate selector
        candidate_names = [f"{row['name']} (Score: {row['final_score']:.1f}%)" for _, row in df.iterrows()]
        selected_idx = st.selectbox(
            "Select a candidate:",
            range(len(candidate_names)),
            format_func=lambda x: candidate_names[x]
        )
        
        candidate = df.iloc[selected_idx]
        
        st.markdown("---")
        
        # Profile card
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### {candidate['name']}")
            if candidate['email']:
                st.markdown(f"📧 {candidate['email']}")
            if candidate['phone']:
                st.markdown(f"📱 {candidate['phone']}")
            if candidate['linkedin']:
                st.markdown(f"🔗 [LinkedIn]({candidate['linkedin']})")
            if candidate['github']:
                st.markdown(f"💻 [GitHub]({candidate['github']})")
        
        with col2:
            grade_html = create_grade_badge_html(candidate['grade'])
            st.markdown(grade_html, unsafe_allow_html=True)
        
        with col3:
            st.metric("Final Score", f"{candidate['final_score']:.1f}%")
        
        st.markdown("---")
        
        # Score metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🧠 Semantic", f"{candidate['semantic_score']:.0f}%")
        with col2:
            st.metric("🔧 Skills", f"{candidate['skills_score']:.0f}%")
        with col3:
            st.metric("💼 Experience", f"{candidate['experience_score']:.0f}%")
        with col4:
            st.metric("🎓 Education", f"{candidate['education_score']:.0f}%")
        
        st.markdown("---")
        
        # Two columns for details
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Radar chart
            fig_radar = plot_score_breakdown_radar(candidate.to_dict())
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Education
            st.markdown("### 🎓 Education")
            education_list = candidate.get('education', [])
            if education_list:
                for edu in education_list:
                    st.markdown(f"**{edu.get('degree', 'N/A')}**")
                    if edu.get('institution'):
                        st.markdown(f"*{edu['institution']}*")
                    if edu.get('year'):
                        st.markdown(f"Year: {edu['year']}")
                    st.markdown("---")
            else:
                st.info("No education information extracted")
            
            # Experience
            st.markdown(f"### 💼 Experience: {candidate['experience_years']:.1f} years")
        
        with col_right:
            # Matched Skills
            st.markdown("### ✅ Matched Skills")
            matched_skills = candidate.get('matched_skills', [])
            
            if matched_skills:
                # Group by category if possible
                skills_html = ""
                for skill in matched_skills[:20]:  # Limit to 20
                    skills_html += create_skill_pill_html(skill, matched=True)
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.info("No matched skills")
            
            st.markdown("---")
            
            # Missing Skills
            st.markdown("### ❌ Missing Skills")
            missing_skills = candidate.get('missing_skills', [])
            
            if missing_skills:
                skills_html = ""
                for skill in missing_skills[:20]:  # Limit to 20
                    skills_html += create_skill_pill_html(skill, matched=False)
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.success("No missing skills!")
            
            st.markdown("---")
            
            # Donut chart
            fig_donut = plot_skills_overlap_donut(matched_skills, jd_analysis.get('required_skills', []))
            st.plotly_chart(fig_donut, use_container_width=True)
        
        # Recommendation box
        st.markdown("---")
        st.markdown("### 💡 Recommendation")
        
        rec_html = create_recommendation_box_html(candidate['grade'], candidate['recommendation'])
        st.markdown(rec_html, unsafe_allow_html=True)
        
        # Auto-generated detailed recommendation
        if candidate['grade'] in ['A', 'B']:
            st.success(f"""
            **{candidate['name']}** is a strong candidate with {candidate['final_score']:.1f}% match score. 
            They have {candidate['matched_skills_count']} of the required skills and {candidate['experience_years']:.1f} years of experience.
            **Recommendation: Schedule interview immediately.**
            """)
        elif candidate['grade'] == 'C':
            st.warning(f"""
            **{candidate['name']}** shows moderate fit with {candidate['final_score']:.1f}% match score.
            They are missing {candidate['missing_skills_count']} key skills.
            **Recommendation: Review manually and consider for interview if other factors align.**
            """)
        else:
            st.error(f"""
            **{candidate['name']}** has limited alignment with {candidate['final_score']:.1f}% match score.
            Significant gaps in required skills and experience.
            **Recommendation: Not recommended for this position.**
            """)
    
    else:
        st.info("👈 Please screen resumes first using the 'Screen Resumes' tab")


# === DOWNLOAD SECTION ===
if st.session_state.processing_done and st.session_state.results_df is not None:
    st.markdown("---")
    st.markdown("## 📥 Export Results")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # CSV download
        csv_data = st.session_state.results_df.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # PDF download
        try:
            pdf_bytes = generate_pdf_report(
                st.session_state.results_df,
                st.session_state.jd_analysis,
                st.session_state.job_description
            )
            
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"screening_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.6); padding: 2rem;">
    <p>🤖 Resume Screening AI | Powered by BERT Transformers & Streamlit</p>
    <p><small>Built with ❤️ using Python, spaCy, sentence-transformers, and Plotly</small></p>
</div>
""", unsafe_allow_html=True)
