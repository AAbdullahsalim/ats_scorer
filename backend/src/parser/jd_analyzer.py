"""
Job Description analyzer.
Extracts must-have skills, nice-to-have skills, and required YOE from JD text.
Uses a technical vocabulary whitelist + KeyBERT for discovery.
"""

import re
from typing import Any, Optional


# Technical Vocabulary Whitelist — maps lowercase variants to display names
TECH_WHITELIST: dict[str, str] = {
    # Languages
    "python": "Python", "java": "Java", "javascript": "JavaScript",
    "typescript": "TypeScript", "c++": "C++", "c#": "C#",
    "go": "Go", "golang": "Go", "rust": "Rust", "ruby": "Ruby",
    "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
    "scala": "Scala", "r": "R", "dart": "Dart",
    # Frontend
    "react": "React", "react.js": "React", "reactjs": "React",
    "next.js": "Next.js", "nextjs": "Next.js",
    "vue": "Vue.js", "vue.js": "Vue.js", "vuejs": "Vue.js",
    "angular": "Angular", "svelte": "Svelte",
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    # Backend
    "node.js": "Node.js", "nodejs": "Node.js",
    "express": "Express.js", "expressjs": "Express.js",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "nestjs": "NestJS", "nest.js": "NestJS",
    "spring boot": "Spring Boot", "spring": "Spring",
    "fastify": "Fastify", "gin": "Gin",
    # Cloud & DevOps
    "aws": "AWS", "gcp": "GCP", "azure": "Azure",
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "terraform": "Terraform", "ansible": "Ansible",
    "jenkins": "Jenkins", "ci/cd": "CI/CD",
    "github actions": "GitHub Actions",
    # Databases
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "mysql": "MySQL", "mongodb": "MongoDB", "redis": "Redis",
    "dynamodb": "DynamoDB", "elasticsearch": "Elasticsearch",
    "cassandra": "Cassandra", "sqlite": "SQLite",
    # Data & ML
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "keras": "Keras", "scikit-learn": "Scikit-Learn",
    "pandas": "Pandas", "numpy": "NumPy", "opencv": "OpenCV",
    "hugging face": "Hugging Face", "langchain": "LangChain",
    "llm": "LLM", "transformers": "Transformers",
    # Messaging & Streaming
    "kafka": "Kafka", "rabbitmq": "RabbitMQ",
    "celery": "Celery",
    # Tools & Protocols
    "git": "Git", "github": "GitHub", "gitlab": "GitLab",
    "linux": "Linux", "graphql": "GraphQL",
    "rest apis": "REST APIs", "restful": "REST APIs",
    "websockets": "WebSockets", "microservices": "Microservices",
    "grpc": "gRPC", "socket.io": "Socket.io",
    # Practices
    "agile": "Agile", "scrum": "Scrum", "jira": "Jira",
    "tdd": "TDD", "unit testing": "Unit Testing",
    "sql": "SQL",
}

# Words to filter out from KeyBERT results (too generic)
NOISE_WORDS: set[str] = {
    "engineer", "developer", "developing", "develop", "cloud",
    "apis", "api", "backend", "frontend", "system", "systems",
    "team", "candidate", "experience", "work", "working", "using",
    "role", "position", "company", "skills", "knowledge", "ability",
    "strong", "ai", "ml", "data", "software", "application",
    "building", "build", "design", "years", "year", "responsible",
    "understanding", "requirements", "job", "looking", "ideal",
}


def extract_skills_from_jd(
    jd_text: str,
    keybert_model: Optional[Any] = None,
) -> tuple[list[str], list[str]]:
    """
    Extract (must_have_skills, nice_to_have_skills) from JD text.

    Must-haves: tech whitelist matches found in JD.
    Nice-to-haves: KeyBERT-extracted terms NOT in whitelist.
    """
    if not jd_text or not jd_text.strip():
        return (["Python", "AWS", "Docker"], [])

    text_lower = jd_text.lower()
    found_canonical: dict[str, str] = {}

    # Step 1: Scan against whitelist
    for tech_key, display in TECH_WHITELIST.items():
        pattern = r"(?<!\w)" + re.escape(tech_key) + r"(?!\w)"
        if re.search(pattern, text_lower):
            found_canonical[display.lower()] = display

    # Step 2: KeyBERT discovery (if model available)
    nice_to_haves: dict[str, str] = {}

    if keybert_model is not None:
        try:
            keywords = keybert_model.extract_keywords(
                jd_text,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=20,
            )

            for kw, _score in keywords:
                phrase_lower = kw.lower().strip()
                tokens = set(phrase_lower.split())

                if tokens.intersection(NOISE_WORDS):
                    continue

                # Check if it matches whitelist
                matched_whitelist = False
                for tech_key, display in TECH_WHITELIST.items():
                    if tech_key in phrase_lower:
                        found_canonical[display.lower()] = display
                        matched_whitelist = True

                if not matched_whitelist and phrase_lower not in found_canonical:
                    nice_to_haves[phrase_lower] = kw.strip().title()
        except Exception:
            pass  # KeyBERT failure is non-fatal

    must_have_list = sorted(found_canonical.values())
    nice_to_have_list = sorted(nice_to_haves.values())

    if not must_have_list:
        must_have_list = ["Python", "JavaScript", "SQL"]

    return (must_have_list, nice_to_have_list)


def extract_required_yoe(jd_text: str) -> float:
    """Extract required years of experience from JD text."""
    text_lower = jd_text.lower()

    patterns = [
        r"(\d+)\+?\s*(?:to|-)\s*(?:\d+)?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"(?:minimum|at\s+least|min)\s+(\d+)\s*(?:years?|yrs?)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue

    return 1.0
