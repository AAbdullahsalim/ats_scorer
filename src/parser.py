import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import re
import io
from pathlib import Path
from typing import Union, Dict, List, Any, Tuple
import pymupdf as fitz  # PyMuPDF
from docx import Document

class ResumeParser:
    def __init__(self):
        self.section_keywords = {
            "experience": [
                "experience", "work history", "employment history", "professional experience",
                "career history", "work experience", "employment", "work background"
            ],
            "skills": [
                "skills", "technical skills", "competencies", "core qualifications",
                "technologies", "tech stack", "tools & technologies", "expertise",
                "areas of expertise", "key skills", "proficiencies"
            ],
            "education": [
                "education", "academic background", "degrees", "qualifications",
                "educational background", "academic qualifications", "academics"
            ],
            "projects": [
                "projects", "project experience", "key projects", "selected projects",
                "personal projects", "academic projects", "relevant projects"
            ],
            "summary": [
                "summary", "professional summary", "about me", "profile", "executive summary",
                "career objective", "objective", "overview"
            ]
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

    def extract_text_and_blocks_from_pdf(self, file_source: Union[str, Path, io.BytesIO, bytes]) -> List[Dict[str, Any]]:
        stream = self._get_stream(file_source)
        doc = fitz.open(stream=stream.read(), filetype="pdf")
        all_blocks = []

        for page_idx, page in enumerate(doc):
            page_rect = page.rect
            page_width = page_rect.width if page_rect else 600.0
            
            text_page = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            raw_blocks = text_page.get("blocks", [])
            
            page_blocks = []
            for b in raw_blocks:
                if b.get("type") != 0:
                    continue
                
                bbox = b.get("bbox", (0, 0, 0, 0))
                x0, y0, x1, y1 = bbox
                
                block_lines = []
                is_bold_block = False
                max_font_size = 0.0

                for line in b.get("lines", []):
                    line_spans = []
                    for span in line.get("spans", []):
                        span_text = span.get("text", "")
                        if not span_text.strip():
                            continue
                        
                        flags = span.get("flags", 0)
                        font_name = str(span.get("font", "")).lower()
                        font_size = float(span.get("size", 0.0))
                        
                        is_bold_span = bool(flags & 2) or ("bold" in font_name) or ("black" in font_name)
                        if is_bold_span:
                            is_bold_block = True
                        if font_size > max_font_size:
                            max_font_size = font_size
                            
                        line_spans.append(span_text)
                    
                    if line_spans:
                        block_lines.append(" ".join(line_spans))

                block_text = "\n".join(block_lines).strip()
                if block_text:
                    page_blocks.append({
                        "text": block_text,
                        "is_bold": is_bold_block,
                        "font_size": max_font_size,
                        "bbox": bbox,
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                        "page_num": page_idx + 1
                    })

            sorted_page_blocks = self._sort_blocks_by_layout(page_blocks, page_width)
            all_blocks.extend(sorted_page_blocks)

        doc.close()
        return all_blocks

    def _sort_blocks_by_layout(self, blocks: List[Dict[str, Any]], page_width: float) -> List[Dict[str, Any]]:
        if not blocks:
            return []

        midpoint = page_width / 2.0
        full_width_blocks = []
        column_blocks = []

        for b in blocks:
            width = b["x1"] - b["x0"]
            if width > 0.60 * page_width:
                full_width_blocks.append(b)
            else:
                column_blocks.append(b)

        left_col = []
        right_col = []

        for b in column_blocks:
            block_center = (b["x0"] + b["x1"]) / 2.0
            if block_center < midpoint:
                left_col.append(b)
            else:
                right_col.append(b)

        full_width_blocks.sort(key=lambda b: b["y0"])
        left_col.sort(key=lambda b: b["y0"])
        right_col.sort(key=lambda b: b["y0"])

        top_banners = [b for b in full_width_blocks if b["y0"] < page_width * 0.35]
        bottom_banners = [b for b in full_width_blocks if b["y0"] >= page_width * 0.35]

        return top_banners + left_col + right_col + bottom_banners

    def extract_text_and_blocks_from_docx(self, file_source: Union[str, Path, io.BytesIO, bytes]) -> List[Dict[str, Any]]:
        stream = self._get_stream(file_source)
        doc = Document(stream)
        blocks = []

        for idx, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue

            style_name = str(p.style.name).lower() if p.style else ""
            is_heading_style = "heading" in style_name
            
            is_bold = any(run.bold for run in p.runs if run.bold is not None) or is_heading_style
            
            font_size = 12.0
            for run in p.runs:
                if run.font and run.font.size:
                    font_size = max(font_size, float(run.font.size.pt))

            blocks.append({
                "text": text,
                "is_bold": is_bold,
                "font_size": font_size,
                "is_heading_style": is_heading_style,
                "bbox": (0, idx * 20, 500, (idx + 1) * 20),
                "y0": idx * 20
            })

        return blocks

    def clean_text(self, text: str) -> str:
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', ' ', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def _classify_heading(self, line: str, is_bold: bool = False, is_heading_style: bool = False) -> Tuple[bool, str]:
        """
        Multi-signal heading classifier:
        Combines keyword taxonomy matching, length constraints, bold weight, and case pattern.
        Returns (is_header, canonical_section_name)
        """
        clean_line = line.strip().lower()
        if not clean_line or len(clean_line) > 60:
            return False, ""

        normalized_line = re.sub(r'[:\-\_]+$', '', clean_line).strip()

        matched_section = None
        for sec_name, keywords in self.section_keywords.items():
            for kw in keywords:
                if normalized_line == kw or normalized_line.startswith(kw + " ") or normalized_line.startswith(kw + ":"):
                    matched_section = sec_name
                    break
            if matched_section:
                break

        if not matched_section:
            return False, ""

        score = 0
        if is_bold or is_heading_style:
            score += 2
        if line.isupper() or line.istitle():
            score += 2
        if len(clean_line) < 35:
            score += 1
        if normalized_line in [kw for kws in self.section_keywords.values() for kw in kws]:
            score += 3

        if score >= 3:
            return True, matched_section

        return False, ""

    def split_into_sections_from_blocks(self, blocks: List[Dict[str, Any]]) -> Dict[str, str]:
        sections = {
            "summary": [],
            "experience": [],
            "skills": [],
            "education": [],
            "projects": [],
            "other": []
        }
        current_section = "other"

        for b in blocks:
            text = b["text"]
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            for line in lines:
                is_header, sec_name = self._classify_heading(
                    line=line,
                    is_bold=b.get("is_bold", False),
                    is_heading_style=b.get("is_heading_style", False)
                )

                if is_header:
                    current_section = sec_name
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
            blocks = self.extract_text_and_blocks_from_pdf(file_source)
        elif ext == ".docx":
            blocks = self.extract_text_and_blocks_from_docx(file_source)
        else:
            try:
                blocks = self.extract_text_and_blocks_from_pdf(file_source)
            except Exception:
                try:
                    blocks = self.extract_text_and_blocks_from_docx(file_source)
                except Exception:
                    raise ValueError(f"Unsupported file format for: {file_name}")

        full_text = "\n".join([b["text"] for b in blocks])
        cleaned_text = self.clean_text(full_text)
        sections = self.split_into_sections_from_blocks(blocks)

        return {
            "file_name": file_name,
            "full_text": cleaned_text,
            "sections": sections
        }

    def parse_cv(self, file_source: Union[str, Path, io.BytesIO, bytes], file_name: str = "") -> dict:
        return self.parse(file_source, file_name=file_name)

    def parse_jd(self, file_source: Union[str, Path, io.BytesIO, bytes], file_name: str = "") -> str:
        parsed = self.parse(file_source, file_name=file_name)
        return parsed["full_text"]


# Master Technical Vocabulary Whitelist to strictly filter out garbage phrases
TECH_WHITELIST = {
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust", "ruby", "php",
    "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "angular", "node.js", "nodejs", "express", "fastapi", "flask", "django", "nestjs",
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd",
    "postgresql", "postgres", "mysql", "mongodb", "redis", "dynamodb", "elasticsearch", "kafka", "rabbitmq",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv", "hugging face", "langchain", "llm", "transformers",
    "git", "github", "gitlab", "linux", "graphql", "rest apis", "websockets", "microservices", "agile", "scrum", "jira"
}

def extract_must_haves_with_keybert(jd_text: str, keybert_model: Any = None, top_n: int = 15) -> list:
    """
    Strict Hybrid Extraction: Scans the JD text against a rigorous technical whitelist 
    and filters out all non-tech action words or messy multi-word phrases.
    Uses an injected KeyBERT model if provided, or lazily instantiates one.
    """
    if not jd_text or not jd_text.strip():
        return ["Python", "AWS", "Docker", "NestJS", "Next.js"]

    text_lower = jd_text.lower()
    found_skills = set()

    for tech in TECH_WHITELIST:
        pattern = r'(?<!\w)' + re.escape(tech) + r'(?!\w)'
        if re.search(pattern, text_lower):
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

    noise_words = {
        "engineer", "developer", "developing", "develop", "cloud", "apis", "api", "backend", 
        "frontend", "system", "systems", "team", "candidate", "experience", "work", "working", 
        "using", "role", "position", "company", "skills", "knowledge", "ability", "strong", "ai", "ml"
    }

    if keybert_model is None:
        from keybert import KeyBERT
        keybert_model = KeyBERT(model='all-MiniLM-L6-v2')

    keywords = keybert_model.extract_keywords(jd_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=20)
    for kw, score in keywords:
        phrase_lower = kw.lower().strip()
        tokens = set(phrase_lower.split())
        
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