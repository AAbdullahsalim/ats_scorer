import os
import streamlit as st
from pathlib import Path
import pandas as pd

# Core Engine Imports
from src.parser import ResumeParser, extract_must_haves_with_keybert, extract_required_yoe
from src.scorer import HybridScorer, evaluate_must_haves, apply_must_have_penalty, estimate_candidate_yoe, apply_yoe_modifier

st.set_page_config(page_title="AI ATS Resume Matcher", page_icon="🤖", layout="wide")

@st.cache_resource
def load_scorer():
    return HybridScorer()

@st.cache_resource
def load_parser():
    return ResumeParser()

def main():
    st.title("🤖 AI-Powered ATS Resume Matcher & Scorer")
    st.markdown("Upload a Job Description to auto-extract requirements, then score candidate resumes using Hybrid Dense/Sparse AI matching.")

    scorer = load_scorer()
    parser = load_parser()

    # ==========================================
    # SIDEBAR: UPLOADS & WEIGHTS
    # ==========================================
    st.sidebar.header("⚙️ Configuration & Uploads")
    uploaded_jd = st.sidebar.file_uploader("Upload Job Description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
    uploaded_cvs = st.sidebar.file_uploader("Upload Candidate CVs (.pdf, .docx)", type=["pdf", "docx"], accept_multiple_files=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Base Scoring Weights")
    vector_weight = st.sidebar.slider("Semantic Vector Weight", 0.0, 1.0, 0.6)
    bm25_weight = st.sidebar.slider("Keyword BM25 Weight", 0.0, 1.0, 0.4)

    # ==========================================
    # MAIN AREA: DYNAMIC REQUIREMENT EXTRACTION
    # ==========================================
    jd_text = ""
    must_have_skills = []
    target_yoe = 0.0
    strict_mode = False

    # Initialize robust session states
    if "custom_skills" not in st.session_state:
        st.session_state.custom_skills = []
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []
    if "current_jd_name" not in st.session_state:
        st.session_state.current_jd_name = None

    if uploaded_jd:
        st.markdown("---")
        st.subheader("🎯 Auto-Extracted Job Requirements")
        st.caption("Review and adjust the extracted requirements before analyzing candidates.")
        
        # Pre-process JD 
        jd_path = os.path.join("jds", uploaded_jd.name)
        os.makedirs("jds", exist_ok=True)
        with open(jd_path, "wb") as f:
            f.write(uploaded_jd.getbuffer())
        
        jd_text = parser.parse_jd(jd_path)
        auto_skills = extract_must_haves_with_keybert(jd_text)
        auto_yoe = extract_required_yoe(jd_text)

        # 1. Reset state ONLY if a new JD is uploaded
        if st.session_state.current_jd_name != uploaded_jd.name:
            st.session_state.current_jd_name = uploaded_jd.name
            st.session_state.custom_skills = [] 
            st.session_state.selected_skills = auto_skills.copy() 

        col1, col2 = st.columns([3, 1])
        with col1:
            # 2. Callback 1: Safely add new skills to our background state
            def add_custom_skill():
                new_s = st.session_state.new_skill_input.strip()
                if new_s:
                    if new_s not in st.session_state.custom_skills:
                        st.session_state.custom_skills.append(new_s)
                    if new_s not in st.session_state.selected_skills:
                        st.session_state.selected_skills.append(new_s)
                # Clear the text box seamlessly
                st.session_state.new_skill_input = ""

            # 3. Callback 2: Safely track when a user clicks 'X' to remove a skill
            def sync_skills():
                st.session_state.selected_skills = st.session_state.skills_widget

            # Text input mapping to Callback 1
            st.text_input(
                "➕ Type a missing skill (e.g., 'Next.js') and press Enter:", 
                key="new_skill_input", 
                on_change=add_custom_skill
            )
            
            # Combine options 
            all_options = list(set(auto_skills + st.session_state.custom_skills + ["Python", "AWS", "SQL", "Docker", "Kubernetes", "React", "Java", "Next.js"]))
            
            # Ensure selected skills are actually valid options to prevent Streamlit crashes
            safe_defaults = [s for s in st.session_state.selected_skills if s in all_options]

            # 4. Render multiselect with our synced state and Callback 2
            must_have_skills = st.multiselect(
                "Must-Have Skills (Click 'X' to remove):",
                options=all_options,
                default=safe_defaults,
                key="skills_widget",
                on_change=sync_skills
            )
            
            strict_mode = st.checkbox("Strict Mode: Completely hide candidates missing ANY of these skills.")
            
        with col2:
            target_yoe = st.number_input("Required Years of Experience:", min_value=0.0, value=auto_yoe, step=0.5)
    # SCORING EXECUTION
    # ==========================================
    if uploaded_jd and uploaded_cvs:
        st.markdown("---")
        if st.button("🚀 Run ATS Analysis", type="primary", use_container_width=True):
            
            with st.spinner("Processing documents, extracting keywords, and calculating hybrid scores..."):
                os.makedirs("sample_cvs", exist_ok=True)
                candidates = []
                
                # Parse all CVs
                for cv_file in uploaded_cvs:
                    cv_path = os.path.join("sample_cvs", cv_file.name)
                    with open(cv_path, "wb") as f:
                        f.write(cv_file.getbuffer())
                    
                    parsed_data = parser.parse_cv(cv_path)
                    if parsed_data:
                        candidates.append(parsed_data)

                if not candidates:
                    st.error("Could not extract text from the uploaded CVs.")
                    return

                # Get base hybrid scores (MiniLM + BM25)
                base_results = scorer.score_candidates(
                    jd_text=jd_text,
                    candidates=candidates,
                    vector_weight=vector_weight,
                    bm25_weight=bm25_weight
                )

                # Apply KeyBERT penalties and YOE modifiers
                final_results = []
                for res in base_results:
                    # Combine sections into a single string if full_text isn't explicitly saved
                    cv_full_text = " ".join(res.get("sections", {}).values())
                    base_score = res['final_score_pct']
                    
                    # 1. Must-Have Penalty Module
                    must_have_eval = evaluate_must_haves(cv_full_text, must_have_skills)
                    if strict_mode and must_have_eval["ratio"] < 1.0:
                        continue  # Skip candidate entirely if strict mode is on
                        
                    score_after_skills = apply_must_have_penalty(base_score, must_have_eval["ratio"])
                    
                    # 2. Years of Experience (YOE) Module
                    candidate_yoe = estimate_candidate_yoe(cv_full_text)
                    final_score = apply_yoe_modifier(score_after_skills, candidate_yoe, target_yoe)
                    
                    # Update dictionary for rendering
                    res["base_score"] = base_score
                    res["final_score_pct"] = final_score
                    res["matched_skills"] = must_have_eval["matched"]
                    res["missing_skills"] = must_have_eval["missing"]
                    res["candidate_yoe"] = candidate_yoe
                    final_results.append(res)

                # Sort by new final penalized score
                final_results = sorted(final_results, key=lambda x: x["final_score_pct"], reverse=True)

            # ==========================================
            # RESULTS DISPLAY
            # ==========================================
            st.success(f"Successfully analyzed {len(final_results)} candidate(s)!")
            st.markdown("### 🏆 Candidate Ranking Results")

            display_data = []
            for idx, res in enumerate(final_results, start=1):
                display_data.append({
                    "Rank": idx,
                    "Candidate File": res["file_name"],
                    "Final Match %": res['final_score_pct'],
                    "Base Score %": res['base_score'],
                    "Est. YOE": f"{res['candidate_yoe']} yrs",
                    "Skills Hit Rate": f"{len(res['matched_skills'])}/{len(must_have_skills)}"
                })

            df_results = pd.DataFrame(display_data)
            st.dataframe(df_results, use_container_width=True)

            # CSV Export
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Ranking Report as CSV",
                data=csv_data,
                file_name="ats_candidate_rankings.csv",
                mime="text/csv",
                type="secondary"
            )

            # Expandable Breakdown View
            st.markdown("---")
            st.markdown("### 🔍 Candidate Deep Dive")
            for res in final_results:
                # Add indicator if they were boosted or penalized
                score_delta = res['final_score_pct'] - res['base_score']
                indicator = "📈 Boosted" if score_delta > 0 else ("📉 Penalized" if score_delta < 0 else "➖ Neutral")
                
                with st.expander(f"#{res.get('Rank', '?')} - {res['file_name']} (Final Score: {res['final_score_pct']}% | {indicator})"):
                    
                    st.markdown(f"**Experience:** Estimated **{res['candidate_yoe']} years** (Target: {target_yoe} years)")
                    
                    if res['matched_skills']:
                        st.success(f"✅ **Matched Skills:** {', '.join(res['matched_skills'])}")
                    if res['missing_skills']:
                        st.error(f"❌ **Missing Skills:** {', '.join(res['missing_skills'])}")
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Extracted Skills Section:**")
                        st.write(res["sections"].get("skills", "No specific skills section isolated."))
                    with col2:
                        st.markdown("**Extracted Experience Section:**")
                        st.write(res["sections"].get("experience", "No specific experience section isolated."))

if __name__ == "__main__":
    main()