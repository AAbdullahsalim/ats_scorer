import os
import streamlit as st
from pathlib import Path
import pandas as pd
from src.parser import ResumeParser
from src.scorer import HybridScorer

st.set_page_config(page_title="AI ATS Resume Matcher", page_icon="🤖", layout="wide")

@st.cache_resource
def load_scorer():
    return HybridScorer()

def main():
    st.title("🤖 AI-Powered ATS Resume Matcher & Scorer")
    st.markdown("Upload a Job Description and candidate resumes to rank them using Hybrid Dense/Sparse AI matching.")

    scorer = load_scorer()
    parser = ResumeParser()

    st.sidebar.header("⚙️ Configuration & Uploads")
    uploaded_jd = st.sidebar.file_uploader("Upload Job Description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
    uploaded_cvs = st.sidebar.file_uploader("Upload Candidate CVs (.pdf, .docx)", type=["pdf", "docx"], accept_multiple_files=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚖️ Scoring Weights")
    vector_weight = st.sidebar.slider("Semantic Vector Weight", 0.0, 1.0, 0.6)
    bm25_weight = st.sidebar.slider("Keyword BM25 Weight", 0.0, 1.0, 0.4)

    if st.sidebar.button("🚀 Run ATS Analysis", type="primary"):
        if not uploaded_jd or not uploaded_cvs:
            st.error("Please upload both a Job Description and at least one Candidate CV!")
            return

        with st.spinner("Processing documents and calculating hybrid scores..."):
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
                st.error("Could not extract text from the uploaded CVs.")
                return

            results = scorer.score_candidates(
                jd_text=jd_text,
                candidates=candidates,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight
            )

        st.success(f"Successfully analyzed {len(results)} candidate(s)!")
        st.markdown("### 🏆 Candidate Ranking Results")

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
        
        # Display as interactive table
        st.dataframe(df_results, use_container_width=True)

        # Phase 5 Feature: Export CSV Report Download Button
        csv_data = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Ranking Report as CSV",
            data=csv_data,
            file_name="ats_candidate_rankings.csv",
            mime="text/csv",
            type="secondary"
        )

        # Expandable candidate details view
        st.markdown("---")
        st.markdown("### 🔍 Candidate Section Breakdown")
        for res in results:
            with st.expander(f"Rank - {res['file_name']} (Final Score: {res['final_score_pct']}%)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Extracted Skills:**")
                    st.write(res["sections"].get("skills", "No specific skills section isolated."))
                with col2:
                    st.markdown("**Extracted Experience:**")
                    st.write(res["sections"].get("experience", "No specific experience section isolated."))

if __name__ == "__main__":
    main()