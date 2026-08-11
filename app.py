import os
import streamlit as st
from pathlib import Path
import pandas as pd
from src.parser import ResumeParser
from src.scorer import HybridScorer

# Page Configuration
st.set_page_config(
    page_title="TalentLens | Enterprise ATS Intelligence", 
    page_icon="", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- WEBFLOW-INSPIRED DESIGN SYSTEM & CSS ---
st.markdown("""
    <style>
    /* Global Reset & Modern SaaS Dark Theme */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .stApp {
        background-color: #090a0f;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.04) 0%, transparent 50%),
            linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 32px 32px, 32px 32px;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Hero Branding */
    .hero-container {
        padding: 40px 0px 24px 0px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 32px;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 9999px;
        background-color: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    /* Webflow-style Cards */
    .wf-card {
        background: #111318;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: border-color 0.2s ease;
    }
    .wf-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4);
    }

    /* Dataframe & Table Aesthetics */
    dataframe, table {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_scorer():
    return HybridScorer()

def main():
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = True

    # --- HERO SECTION ---
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">Enterprise Engine v2.4</div>
            <h1 style="font-size: 2.75rem; font-weight: 800; color: #ffffff; letter-spacing: -0.03em; margin: 0 0 8px 0;">
              TalentLens <span style="font-weight: 300; color: #64748b;">Applicant Matrix</span>
            </h1>
            <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0;">
              High-precision hybrid dense vector and sparse lexical ranking interface for talent acquisition workflows.
            </p>
        </div>
    """, unsafe_allow_html=True)

    scorer = load_scorer()
    parser = ResumeParser()

    # --- ACTION BAR & PANEL TOGGLE ---
    col_toggle, col_empty = st.columns([1, 5])
    with col_toggle:
        toggle_text = "Hide Upload Hub" if st.session_state.show_uploader else "Expand Upload Hub"
        if st.button(toggle_text, use_container_width=True):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()

    uploaded_jd = None
    uploaded_cvs = []

    if st.session_state.show_uploader:
        st.markdown('<div class="wf-card">', unsafe_allow_html=True)
        uc1, uc2 = st.columns(2, gap="large")
        
        with uc1:
            st.markdown("### Target Job Profile")
            st.markdown("<p style='color:#64748b; font-size:0.85rem; margin-bottom:12px;'>Upload baseline position requirements (.pdf, .docx, .txt)</p>", unsafe_allow_html=True)
            uploaded_jd = st.file_uploader("Upload JD", type=["pdf", "docx", "txt"], label_visibility="collapsed", key="jd_upload")

        with uc2:
            st.markdown("### Candidate Batch Pool")
            st.markdown("<p style='color:#64748b; font-size:0.85rem; margin-bottom:12px;'>Select multi-file folder bundle for deep analysis</p>", unsafe_allow_html=True)
            uploaded_cvs = st.file_uploader("Upload CVs", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed", key="cv_upload")
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Execution Button
    col_run, _ = st.columns([2, 4])
    with col_run:
        run_analysis = st.button("Run Evaluation Pipeline", type="primary", use_container_width=True)

    if run_analysis:
        if not uploaded_jd or not uploaded_cvs:
            st.error("Please supply both a Target Job Profile and a Candidate Batch before running execution.")
            return

        with st.status("Executing hybrid vector-lexical pipeline...", expanded=True) as status:
            st.write("Parsing document hierarchy and layout boundaries...")
            
            jd_path = os.path.join("jds", uploaded_jd.name)
            os.makedirs("jds", exist_ok=True)
            with open(jd_path, "wb") as f:
                f.write(uploaded_jd.getbuffer())
            
            jd_text = parser.parse_jd(jd_path)

            os.makedirs("sample_cvs", exist_ok=True)
            candidates = []
            
            for cv_file in uploaded_cvs:
                cv_path = os.path.join("sample_cvs", cv_file.name)
                with open(cv_path, "wb") as f:
                    f.write(cv_file.getbuffer())
                
                parsed_data = parser.parse_cv(cv_path)
                if parsed_data:
                    candidates.append(parsed_data)

            if not candidates:
                status.update(label="Extraction Failed", state="error")
                st.error("No valid text nodes extracted from the candidate batch.")
                return

            st.write("Evaluating dense semantic representations and token frequency models...")
            results = scorer.score_candidates(
                jd_text=jd_text,
                candidates=candidates,
                vector_weight=0.6,
                bm25_weight=0.4
            )
            status.update(label=f"Successfully processed {len(results)} candidate profiles.", state="complete", expanded=False)

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("### Candidate Leaderboard & Metrics")

        display_data = []
        for idx, res in enumerate(results, start=1):
            display_data.append({
                "Rank": idx,
                "Candidate File": res["file_name"],
                "Final Match %": res['final_score_pct'],
                "Vector %": res['vector_score_pct'],
                "BM25 %": res['bm25_score_pct']
            })

        df_results = pd.DataFrame(display_data)
        
        st.dataframe(df_results, use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Complete CSV Matrix",
            data=csv_data,
            file_name="ats_candidate_rankings.csv",
            mime="text/csv",
            type="secondary"
        )

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("### Granular Profile Section Breakdown")
        for res in results:
            with st.expander(f"Rank {res['file_name']} — Final Match Score: {res['final_score_pct']}%"):
                col_s, col_e = st.columns(2, gap="medium")
                with col_s:
                    st.markdown("**Core Skills Profile:**")
                    st.info(res["sections"].get("skills", "No dedicated skill block isolated."))
                with col_e:
                    st.markdown("**Professional Experience Node:**")
                    st.info(res["sections"].get("experience", "No dedicated experience block isolated."))

if __name__ == "__main__":
    main()