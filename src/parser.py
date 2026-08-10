import re
from pathlib import Path
import pdfplumber
from docx import Document
from datetime import datetime
from keybert import KeyBERT
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

class ResumeParser:
    def __init__(self):
        self.section_keywords = {
            "experience": ["experience", "work history", "employment history", "professional experience"],
            "skills": ["skills", "technical skills", "competencies", "core qualifications"],
            "education": ["education", "academic background", "degrees", "qualifications"]
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text from PDF using pdfplumber with layout preservation."""
        extracted_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    extracted_text.append(text)
        return "\n".join(extracted_text)

    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extracts text from Word documents paragraph by paragraph."""
        doc = Document(docx_path)
        extracted_text = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(extracted_text)

    def clean_text(self, text: str) -> str:
        """Cleans extracted text by normalizing spaces, tabs, and bullets."""
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', ' ', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def split_into_sections(self, text: str) -> dict:
        """Heuristic section splitter for Skills, Experience, Education, and Other."""
        lines = text.split('\n')
        sections = {"experience": [], "skills": [], "education": [], "other": []}
        current_section = "other"

        for line in lines:
            line_clean = line.strip().lower()
            if len(line_clean) < 35:
                matched = False
                for section_name, keywords in self.section_keywords.items():
                    if any(kw == line_clean or line_clean.startswith(kw) for kw in keywords):
                        current_section = section_name
                        matched = True
                        break
                if matched:
                    continue

            sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    def parse(self, file_path: str) -> dict:
        """Core parsing method for candidate resumes."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        cleaned_text = self.clean_text(raw_text)
        sections = self.split_into_sections(cleaned_text)

        return {
            "file_name": path.name,
            "full_text": cleaned_text,
            "sections": sections
        }

    def parse_cv(self, file_path: str) -> dict:
        """Alias for parse to match Streamlit app requirements."""
        return self.parse(file_path)

    def parse_jd(self, file_path: str) -> str:
        """Parses job description files (.pdf, .docx, .txt)."""
        path = Path(file_path)
        if not path.exists():
            return ""

        ext = path.suffix.lower()
        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_path)
        elif ext == ".txt":
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
        else:
            raw_text = ""

        return self.clean_text(raw_text)



kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def extract_must_haves_with_keybert(jd_text: str, top_n: int = 15) -> list:
    """
    Dynamically extracts technical keywords using local semantic embeddings.
    Filters out common JD corporate jargon to reduce noise.
    """
    if not jd_text or not jd_text.strip():
        return []
        
    # 1. Custom JD Jargon Stop Words to kill the "blabber"
    ats_stop_words = [
        'experience', 'years', 'team', 'work', 'skills', 'knowledge', 
        'required', 'preferred', 'ability', 'strong', 'understanding', 
        'using', 'development', 'software', 'working', 'company', 'role', 
        'business', 'environment', 'design', 'support', 'management',
        'good', 'excellent', 'fast', 'paced', 'including', 'related',
        'communication', 'candidate', 'opportunity', 'requirements'
    ]
    
    # Combine standard English stop words (and/the/it) with our JD stop words
    combined_stop_words = list(ENGLISH_STOP_WORDS) + ats_stop_words

    # Extract slightly more keywords initially, so we have room to filter
    keywords = kw_model.extract_keywords(
        jd_text, 
        keyphrase_ngram_range=(1, 2), 
        stop_words=combined_stop_words, 
        top_n=top_n * 2 
    )
    
    clean_skills = []
    for kw in keywords:
        word = kw[0].title()
        score = kw[1]
        
        # 2. Raised Threshold: Only keep terms with a score > 0.40 (was 0.3)
        # 3. Length Filter: Ignore single-letter glitches or massive phrases
        if score > 0.40 and 2 <= len(word) <= 30:
            clean_skills.append(word)
            
    # Return unique items, capped at the original top_n requested
    return list(set(clean_skills))[:top_n]

def extract_required_yoe(jd_text: str) -> float:
    """
    Looks for patterns like '3+ years of experience', '2-4 years', 'minimum 1 year'
    Returns the minimum required years as a float. Defaults to 0.0 if not found.
    """
    text_lower = jd_text.lower()
    
    # Matches: "3+ years", "2 to 4 years", "1 year"
    pattern = r'(\d+)\+?\s*(?:to|-)?\s*(?:\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience'
    match = re.search(pattern, text_lower)
    
    if match:
        return float(match.group(1))
    return 0.0