import os
import re
from pathlib import Path
import pypdf
from docx import Document
from datetime import datetime

def estimate_candidate_yoe(cv_text_or_sections):
    exp_text = ""
    if isinstance(cv_text_or_sections, dict):
        exp_text = cv_text_or_sections.get("experience", "")
        if not exp_text.strip():
            exp_text = " ".join(cv_text_or_sections.values())
    else:
        exp_text = str(cv_text_or_sections)

    explicit_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
        r'(?:experience|exp)(?:\s+of)?\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)'
    ]
    for pat in explicit_patterns:
        match = re.search(pat, exp_text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 0 < val < 40:
                    return val
            except ValueError:
                pass

    lines = exp_text.split('\n')
    filtered_exp_lines = []
    academic_keywords = ['university', 'college', 'school', 'b.s', 'bs ', 'b.sc', 'bachelor', 'project', 'semester', 'a-levels', 'education']
    for line in lines:
        line_lower = line.lower()
        if not any(kw in line_lower for kw in academic_keywords):
            filtered_exp_lines.append(line)
            
    clean_exp_text = "\n".join(filtered_exp_lines)

    date_range_pattern = re.compile(
        r'(0[1-9]|1[0-2])/(\d{4})\s*[-–to]+\s*(?:(0[1-9]|1[0-2])/(\d{4})|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})\s*[-–to]+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])|'
        r'(\d{4})\s*[-–to]+\s*(\d{4}|[Pp]resent|[Cc][Uu][Rr][Rr][Ee][Nn][Tt])',
        re.IGNORECASE
    )

    current_year = datetime.now().year
    current_month = datetime.now().month

    matches = date_range_pattern.findall(clean_exp_text)
    total_months = 0

    for match in matches:
        start_yr, end_yr = None, None
        start_mo, end_mo = 1, 1

        if match[1]:
            start_mo = int(match[0])
            start_yr = int(match[1])
            if match[3]:
                end_mo = int(match[2])
                end_yr = int(match[3])
            else:
                end_yr = current_year
                end_mo = current_month
        elif match[5]:
            start_yr = int(match[5])
            if match[6]:
                end_yr = int(match[6])
            else:
                end_yr = current_year
                end_mo = current_month
        elif match[7]:
            try:
                start_yr = int(match[7])
                end_str = match[8]
                if re.match(r'pres|curr', end_str, re.IGNORECASE):
                    end_yr = current_year
                    end_mo = current_month
                else:
                    end_yr = int(end_str)
            except ValueError:
                continue

        if start_yr and end_yr:
            duration = (end_yr - start_yr) * 12 + (end_mo - start_mo)
            if 0 < duration <= 120:
                total_months += duration

    if total_months > 0:
        return round(total_months / 12.0, 1)
    return 0.0

def parse_cv_simple(file_path):
    path = Path(file_path)
    text = ""
    if path.suffix.lower() == '.pdf':
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    elif path.suffix.lower() == '.docx':
        doc = Document(path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
    sections = {"experience": "", "education": "", "other": ""}
    current = "other"
    for line in text.split('\n'):
        lower = line.strip().lower()
        if "experience" in lower or "work history" in lower or "employment" in lower:
            current = "experience"
        elif "education" in lower:
            current = "education"
        if current in sections:
            sections[current] += line + "\n"
    return sections

if __name__ == "__main__":
    cv_folder = Path("sample_cvs")
    if not cv_folder.exists():
        cv_folder = Path(".")

    files = list(cv_folder.glob("*.pdf")) + list(cv_folder.glob("*.docx"))
    print(f"\n{'Candidate File':<45} | {'Est. YOE':<10}")
    print("-" * 60)
    for f in files:
        secs = parse_cv_simple(f)
        yoe = estimate_candidate_yoe(secs)
        print(f"{f.name[:45]:<45} | {yoe:<10} yrs")