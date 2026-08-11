import re
from pathlib import Path
import pdfplumber
from docx import Document
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
        extracted_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    extracted_text.append(text)
        return "\n".join(extracted_text)

    def extract_text_from_docx(self, docx_path: str) -> str:
        doc = Document(docx_path)
        extracted_text = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(extracted_text)

    def clean_text(self, text: str) -> str:
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', ' ', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def split_into_sections(self, text: str) -> dict:
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
        return self.parse(file_path)

    def parse_jd(self, file_path: str) -> str:
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


# Master Technical Vocabulary Whitelist to strictly filter out garbage phrases
TECH_WHITELIST = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust", "ruby", "php",
    "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "angular", "node.js", "nodejs", "express", "fastapi", "flask", "django", "nestjs",
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "dynamodb", "elasticsearch", "kafka", "rabbitmq",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv", "hugging face", "langchain", "llm", "transformers",
    "git", "github", "gitlab", "linux", "graphql", "rest apis", "websockets", "microservices", "agile", "scrum", "jira"
}

kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def extract_must_haves_with_keybert(jd_text: str, top_n: int = 15) -> list:
    """
    Strict Hybrid Extraction: Scans the JD text against a rigorous technical whitelist 
    and filters out all non-tech action words or messy multi-word phrases.
    """
    if not jd_text or not jd_text.strip():
        return ["Python", "AWS", "Docker", "NestJS", "Next.js"]

    text_lower = jd_text.lower()
    found_skills = set()

    # Step 1: Scan text for exact technical entities using word boundaries
    for tech in TECH_WHITELIST:
        pattern = r'(?<!\w)' + re.escape(tech) + r'(?!\w)'
        if re.search(pattern, text_lower):
            # Normalize display formatting
            if tech in ["aws", "gcp", "ci/cd"]:
                display = tech.upper()
            elif tech == "c++":
                display = "C++"
            elif tech == "c#":
                display = "C#"
            elif tech == "nestjs":
                display = "NestJS"
            elif tech in ["next.js", "nextjs"]:
                display = "Next.js"
            elif tech in ["node.js", "nodejs"]:
                display = "Node.js"
            elif tech in ["postgresql", "postgres"]:
                display = "PostgreSQL"
            else:
                display = tech.title()
            found_skills.add(display)

    # Step 2: Use KeyBERT as a supplementary scanner, but strictly filter out noise words
    noise_words = {
        "engineer", "developer", "developing", "develop", "cloud", "apis", "api", "backend", 
        "frontend", "system", "systems", "team", "candidate", "experience", "work", "working", 
        "using", "role", "position", "company", "skills", "knowledge", "ability", "strong", "ai", "ml"
    }

    keywords = kw_model.extract_keywords(jd_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=20)
    for kw, score in keywords:
        phrase_lower = kw.lower().strip()
        tokens = set(phrase_lower.split())
        
        # Reject phrases containing noise words
        if tokens.intersection(noise_words):
            continue
            
        for tech in TECH_WHITELIST:
            if tech in phrase_lower:
                found_skills.add(tech.title() if tech not in ["c++", "c#"] else tech.upper())

    final_list = sorted(list(found_skills))
    return final_list if final_list else ["Python", "NestJS", "Next.js", "AWS", "Docker"]

def extract_required_yoe(jd_text: str) -> float:
    text_lower = jd_text.lower()
    pattern = r'(\d+)\+?\s*(?:to|-)?\s*(?:\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience'
    match = re.search(pattern, text_lower)
    
    if match:
        return float(match.group(1))
    return 1.0