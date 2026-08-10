# Local ATS Scorer & Resume Matcher Engine

An automated Applicant Tracking System (ATS) resume ranking engine built in Python.

---

## 📁 Project Structure

    ats_scorer/
    ├── jds/                      # Job Description files (.pdf, .docx, .txt)
    │   └── .gitkeep
    ├── sample_cvs/               # Candidate Resume files (.pdf, .docx)
    │   └── .gitkeep
    ├── src/                      # Core Engine Package
    │   ├── __init__.py           # Package initializer
    │   ├── parser.py             # Layout-aware PDF/DOCX extraction & text cleaner
    │   └── scorer.py             # Sentence-BERT + BM25 Hybrid Scorer (with section weighting)
    ├── .gitignore                # Environment, cache, and document exclusion
    ├── app.py                    # Interactive Streamlit Web Dashboard
    ├── main.py                   # Pipeline execution script
    ├── README.md                 # Project documentation
    └── requirements.txt          # Locked dependency manifest

---

## 🏗️ Architecture Pipeline

The system processes documents through a multi-stage pipeline combining local NLP embedding models with deterministic term-frequency algorithms.

      ┌───────────────────────┐             ┌─────────────────────────┐
      │ Candidate Resumes     │             │ Job Description         │
      │ (.pdf / .docx)        │             │ (.pdf / .docx / .txt)   │
      └──────────┬────────────┘             └────────────┬────────────┘
                 │                                       │
                 ▼                                       ▼
      ┌──────────────────────────────────────────────────────────────┐
      │ Document Parser Engine (src/parser.py)                      │
      │ - Extractor: pdfplumber (Layout-Aware) / python-docx         │
      │ - Cleaner: Regex symbol normalization & whitespace cleanup   │
      │ - Section Splitter: Skills, Experience, Education Buckets     │
      └──────────┬───────────────────────────────────────────────────┘
                 │
                 ▼
      ┌──────────────────────────────────────────────────────────────┐
      │ Hybrid Scoring Engine (src/scorer.py)                        │
      │                                                              │
      │  ┌──────────────────────────────┐ ┌────────────────────────┐ │
      │  │ Dense Semantic Search        │ │ Sparse Keyword Search   │ │
      │  │ - Model: MiniLM-L6-v2        │ │ - Engine: BM25Okapi    │ │
      │  │ - Metric: Cosine Similarity  │ │ - Term Frequency Match │ │
      │  └──────────────┬───────────────┘ └──────────┬─────────────┘ │
      │                 │                            │               │
      │                 └─────────────┬──────────────┘               │
      │                               ▼                              │
      │   Granular Section-Weighted Fusion (Skills 40%, Exp 40%, Full 20%)│
      └──────────┬───────────────────────────────────────────────────┘
                 │
                 ▼
      ┌──────────────────────────────────────────────────────────────┐
      │ Output Interfaces                                            │
      │ - Terminal CLI ASCII Table (main.py)                         │
      │ - Interactive Streamlit Web Dashboard & CSV Export (app.py)  │
      └──────────────────────────────────────────────────────────────┘

---

## 🚀 Phase Development Plan

### 🟩 Phase 1: Environment Setup & Document Parsing Engine (Completed)
* [x] Set up local Python virtual environment with VS Code.
* [x] Build document ingestion engine (src/parser.py) for PDF and DOCX formats using layout-aware pdfplumber.
* [x] Implement regex text-cleaning algorithms to normalize bullets, symbols, and line breaks.
* [x] Construct heuristic section splitter for Skills, Experience, and Education blocks.

### 🟩 Phase 2: Hybrid Search & Scoring Engine (Completed)
* [x] Integrate sentence-transformers with local all-MiniLM-L6-v2 embedding model.
* [x] Implement BM25 sparse keyword indexer using rank_bm25.
* [x] Create weighted score fusion module blending Vector Similarity and BM25 Term Weight.
* [x] Build terminal CLI runner (main.py) displaying formatted ASCII candidate rankings.

### 🟩 Phase 3: Score Fine-Tuning & Section Weighting (Completed)
* [x] Implement granular section-based weighting multipliers (40% Skills, 40% Experience, 20% Full Text) to eliminate short CV bias.
* [x] Add absolute score normalization using synthetic anchor "Perfect CVs" and dummy corpora to stabilize BM25 score ranges.
* [x] Build robust fallback handling for unstructured or noisy documents.

### 🟩 Phase 4: Interactive Web Interface (Completed)
* [x] Build interactive web dashboard using Streamlit (app.py).
* [x] Add dynamic drag-and-drop file uploaders for Job Descriptions and multiple candidate batches.
* [x] Implement real-time interactive weight tuning sliders and expandable section breakdown views.

### 🟩 Phase 5: Production Refinement & Exporting (Completed)
* [x] Add candidate report export functionality with a single-click CSV download button.
* [x] Optimize model overhead via Streamlit resource caching (@st.cache_resource).
* [x] Finalize dependency lock manifest (requirements.txt).

---

## ⚡ Quick Start Guide

### 1. Setup Virtual Environment
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate

    pip install -r requirements.txt

### 2. Add Documents
* Drop Job Description into the jds/ folder.
* Drop Candidate Resumes into the sample_cvs/ folder.

### 3. Run Terminal Pipeline (CLI)
    python main.py

### 4. Launch Web Dashboard (Streamlit UI)
    streamlit run app.py