import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document

class ResumeParser:
    def __init__(self):
        self.section_keywords = {
            "experience": ["experience", "work history", "employment history", "professional experience"],
            "skills": ["skills", "technical skills", "competencies", "core qualifications"],
            "education": ["education", "academic background", "degrees", "qualifications"]
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        extracted_text = []
        for page in reader.pages:
            text = page.extract_text()
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