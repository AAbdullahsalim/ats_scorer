"""
LLM prompt templates for CV extraction and JD analysis.
All prompts return structured JSON for reliable parsing.
"""


def build_cv_extraction_prompt(cv_text: str, required_skills: list[str]) -> str:
    """
    Build a prompt that extracts ALL structured data from a CV in ONE call.
    Returns: name, contact, skills (with context), experience, YOE, education, summary.
    """
    skills_str = ", ".join(required_skills) if required_skills else "any relevant technical skills"

    return f"""You are a CV parser. Extract structured data from the CV below and return ONLY a single valid JSON object. No extra text before or after the JSON.

RULES:
- Return ONLY the JSON object, nothing else
- No trailing commas
- No comments
- Use empty string "" for missing string fields
- Use 0 for missing numeric fields
- Use [] for missing array fields
- If a field cannot be determined, use its default value

REQUIRED SKILLS TO CHECK: {skills_str}

For each skill found, classify its context:
- "project" = skill is USED in a described project, role, or achievement
- "mentioned" = skill is only LISTED in a skills section without usage context

CV TEXT:
---
{cv_text[:6000]}
---

Return EXACTLY this JSON structure with ALL fields filled:
{{
  "candidate_name": "Full Name Here",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "location": "",
  "skills_found": [
    {{"name": "SkillName", "context": "project", "evidence": "Brief quote showing usage"}},
    {{"name": "SkillName", "context": "mentioned", "evidence": "Listed in skills section"}}
  ],
  "experience_entries": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "start": "YYYY-MM",
      "end": "YYYY-MM or present",
      "months": 24,
      "key_work": "One-line description of main achievement"
    }}
  ],
  "total_yoe": 3.5,
  "current_role": "",
  "education": [
    {{"degree": "BS Computer Science", "institution": "University Name", "year": "2018-2022"}}
  ],
  "certifications": [],
  "candidate_summary": "2-3 sentence professional summary highlighting key strengths and main technologies."
}}"""


def build_jd_extraction_prompt(jd_text: str) -> str:
    """
    Build a prompt to extract structured requirements from a Job Description.
    """
    return f"""You are a job description parser. Extract structured requirements from the JD below and return ONLY a single valid JSON object. No extra text.

RULES:
- Return ONLY the JSON object
- No trailing commas, no comments
- Use [] for empty arrays, 1.0 for unknown YOE

JOB DESCRIPTION:
---
{jd_text[:4000]}
---

Return EXACTLY this JSON structure:
{{
  "must_have_skills": ["Skill1", "Skill2"],
  "nice_to_have_skills": ["Skill1", "Skill2"],
  "required_yoe": 3.0,
  "role_title": "Job Title",
  "key_requirements": ["Requirement 1", "Requirement 2"]
}}

Rules for skill extraction:
- must_have_skills: Technical skills explicitly required or repeatedly mentioned
- nice_to_have_skills: Skills mentioned as "preferred", "bonus", or "nice to have"
- required_yoe: Minimum years of experience mentioned (default 1.0 if not specified)
- Use canonical skill names (e.g., "React" not "ReactJS", "AWS" not "Amazon Web Services")"""
