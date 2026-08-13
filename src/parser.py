import re
import io
from pathlib import Path
from typing import Union, Dict, List
import pdfplumber
from docx import Document
from keybert import KeyBERT

class ResumeParser:
    def __init__(self):
        self.section_keywords = {
            "experience": ["experience", "work history", "employment history", "professional experience"],
            "skills": ["skills", "technical skills", "competencies", "core qualifications"],
            "education": ["education", "academic background", "degrees", "qualifications"],
            "projects": ["projects", "project experience", "key projects", "selected projects"]
        }

    def _get_stream(self, file_source: Union[str, Path, io.BytesIO, bytes]) -> io.BytesIO:
        if isinstance(file_source, bytes):
            return io.BytesIO(file_source)
        elif isinstance(file_source, (str, Path)):
            path = Path(file_source)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_source}")
            with open(path, "rb") as f:
                return io.BytesIO(f.read())
        elif isinstance(file_source, io.BytesIO):
            file_source.seek(0)
            return file_source
        else:
            raise ValueError(f"Unsupported file source type: {type(file_source)}")

    def extract_text_from_pdf(self, file_source: Union[str, Path, io.BytesIO, bytes]) -> str:
        stream = self._get_stream(file_source)
        extracted_text = []
        with pdfplumber.open(stream) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    extracted_text.append(text)
        return "\n".join(extracted_text)

    def extract_text_from_docx(self, file_source: Union[str, Path, io.BytesIO, bytes]) -> str:
        stream = self._get_stream(file_source)
        doc = Document(stream)
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
        sections = {"experience": [], "skills": [], "education": [], "projects": [], "other": []}
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

            if current_section in sections:
                sections[current_section].append(line)
            else:
                sections["other"].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items()}

    def parse(self, file_source: Union[str, Path, io.BytesIO, bytes], file_name: str = "") -> dict:
        if not file_name and isinstance(file_source, (str, Path)):
            file_name = Path(file_source).name
        elif not file_name:
            file_name = "uploaded_document"

        ext = Path(file_name).suffix.lower() if file_name else ""
        if not ext and isinstance(file_source, (str, Path)):
            ext = Path(file_source).suffix.lower()

        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_source)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_source)
        else:
            try:
                raw_text = self.extract_text_from_pdf(file_source)
            except Exception:
                try:
                    raw_text = self.extract_text_from_docx(file_source)
                except Exception:
                    raise ValueError(f"Unsupported file format for: {file_name}")

        cleaned_text = self.clean_text(raw_text)
        sections = self.split_into_sections(cleaned_text)

        return {
            "file_name": file_name,
            "full_text": cleaned_text,
            "sections": sections
        }

    def parse_cv(self, file_source: Union[str, Path, io.BytesIO, bytes], file_name: str = "") -> dict:
        return self.parse(file_source, file_name=file_name)

    def parse_jd(self, file_source: Union[str, Path, io.BytesIO, bytes], file_name: str = "") -> str:
        if not file_name and isinstance(file_source, (str, Path)):
            file_name = Path(file_source).name
        elif not file_name:
            file_name = "jd_document"

        ext = Path(file_name).suffix.lower()

        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_source)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_source)
        elif ext == ".txt":
            if isinstance(file_source, (str, Path)):
                with open(file_source, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()
            elif isinstance(file_source, bytes):
                raw_text = file_source.decode('utf-8', errors='ignore')
            elif isinstance(file_source, io.BytesIO):
                file_source.seek(0)
                raw_text = file_source.read().decode('utf-8', errors='ignore')
            else:
                raw_text = ""
        else:
            stream = self._get_stream(file_source)
            raw_text = stream.read().decode('utf-8', errors='ignore')

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

def extract_must_haves_with_keybert(jd_text: str, keybert_model: KeyBERT = None, top_n: int = 15) -> list:
    """
    Strict Hybrid Extraction: Scans the JD text against a rigorous technical whitelist 
    and filters out all non-tech action words or messy multi-word phrases.
    Uses an injected KeyBERT model if provided, or lazily instantiates one.
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

    if keybert_model is None:
        keybert_model = KeyBERT(model='all-MiniLM-L6-v2')

    keywords = keybert_model.extract_keywords(jd_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=20)
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