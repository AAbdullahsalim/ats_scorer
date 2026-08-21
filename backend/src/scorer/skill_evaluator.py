"""
Skill context evaluator.
Determines whether each required skill is:
  - Verified (used in experience/projects context)
  - Listed (mentioned in skills section or raw text only)
  - Missing (not found anywhere)

Includes an extensive synonym/alias resolution map and fuzzy normalization
so variants like git/github, react/reactjs/react.js, ai/ml/artificial intelligence
are seamlessly recognized.
"""

import re
from typing import Optional


# Comprehensive bidirectional synonym & ecosystem map
SYNONYM_MAP: dict[str, list[str]] = {
    # Version Control & Collaboration
    "git": ["git", "github", "gitlab", "bitbucket", "version control", "git/github", "git flow", "github actions"],
    "jira": ["jira", "atlassian", "confluence", "trello", "jira software"],
    "agile": ["agile", "scrum", "kanban", "sprint planning", "sprints", "scrum master", "agile methodologies"],

    # Cloud & DevOps
    "aws": ["aws", "amazon web services", "amazon cloud", "ec2", "s3", "lambda", "cloudformation", "dynamodb", "ecs", "eks"],
    "gcp": ["gcp", "google cloud", "google cloud platform", "bigquery", "gke", "cloud run"],
    "azure": ["azure", "microsoft azure", "azure devops"],
    "docker": ["docker", "dockerfile", "docker-compose", "containerization", "containers", "podman"],
    "k8s": ["k8s", "kubernetes", "helm", "kubectl", "k8s clusters"],
    "ci/cd": ["ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"],

    # Frontend
    "react": ["react", "reactjs", "react.js", "react-native", "react native", "create-react-app"],
    "next.js": ["next.js", "nextjs", "next js", "next", "next 13", "next 14", "next 15"],
    "vue.js": ["vue.js", "vuejs", "vue", "vue 3", "nuxt", "nuxtjs"],
    "angular": ["angular", "angularjs", "angular 2+"],
    "typescript": ["typescript", "ts", "type-script"],
    "javascript": ["javascript", "js", "es6", "es6+", "ecmascript", "vanilla js"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "redux": ["redux", "redux toolkit", "rtk", "zustand", "mobx"],

    # Backend
    "node.js": ["node.js", "nodejs", "node js", "node"],
    "nestjs": ["nestjs", "nest.js", "nest js", "nest"],
    "express.js": ["express.js", "expressjs", "express js", "express"],
    "python": ["python", "python3", "python 3", "py", "django", "fastapi", "flask"],
    "java": ["java", "j2ee", "spring", "spring boot", "springboot", "java 11", "java 17", "java 8"],
    "c++": ["c++", "cpp", "c/c++"],
    "c#": ["c#", "csharp", "c sharp", ".net", "dotnet", ".net core", "asp.net"],
    "golang": ["golang", "go", "go language"],
    "rest apis": ["rest apis", "restful apis", "rest api", "restful", "rest", "api integration", "web apis", "api development", "restful web services"],
    "graphql": ["graphql", "graph ql", "apollo", "apollo graphql"],
    "microservices": ["microservices", "microservice", "micro-services", "micro services", "distributed systems", "soa", "service-oriented architecture"],

    # Databases
    "postgres": ["postgres", "postgresql", "psql", "pg", "postgre sql"],
    "mongodb": ["mongodb", "mongo", "nosql", "mongoose"],
    "sql": ["sql", "structured query language", "mysql", "tsql", "t-sql", "relational database"],
    "redis": ["redis", "in-memory cache", "caching"],

    # AI / ML / Data Science
    "ai": ["ai", "artificial intelligence", "genai", "generative ai", "ai/ml", "ai ml", "applied ai"],
    "machine learning": ["machine learning", "ml", "deep learning", "dl", "supervised learning", "unsupervised learning"],
    "nlp": ["nlp", "natural language processing", "text processing"],
    "transformers": ["transformers", "transformer", "bert", "gpt", "llm", "llms", "large language models"],
    "hugging face": ["hugging face", "huggingface", "hf", "hugging face transformers"],
    "langchain": ["langchain", "lang chain", "llamaindex", "llama-index", "rag", "retrieval-augmented generation"],
    "pytorch": ["pytorch", "torch", "py-torch"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "scikit-learn": ["scikit-learn", "scikitlearn", "sklearn", "scikit learn", "scikit"],
}


def _generate_fuzzy_variants(name: str) -> set[str]:
    """Generate common morphological and punctuation variants for a skill name."""
    s = name.strip().lower()
    variants = {s}

    # Remove dots and hyphens: "next.js" -> "nextjs", "scikit-learn" -> "scikitlearn"
    no_punct = re.sub(r"[.\-_/]", "", s)
    variants.add(no_punct)

    # Replace dots/hyphens with spaces: "scikit-learn" -> "scikit learn", "next.js" -> "next js"
    space_punct = re.sub(r"[.\-_/]", " ", s)
    variants.add(space_punct)

    # Strip .js or js suffix: "react.js" -> "react", "reactjs" -> "react"
    if s.endswith(".js"):
        variants.add(s[:-3])
    elif s.endswith("js") and len(s) > 4:
        variants.add(s[:-2])

    # Singular / plural normalization: "microservices" -> "microservice", "apis" -> "api"
    if s.endswith("ies"):
        variants.add(s[:-3] + "y")
    elif s.endswith("s") and not s.endswith("ss") and not s.endswith("js"):
        variants.add(s[:-1])
    else:
        variants.add(s + "s")

    return variants


def get_aliases(skill: str) -> list[str]:
    """Get all known aliases for a skill (bidirectional lookup + algorithmic fuzzy rules)."""
    skill_lower = skill.strip().lower()
    aliases = {skill_lower}

    # Add algorithmic variants
    aliases.update(_generate_fuzzy_variants(skill_lower))

    # Match in synonym map
    for key, syn_list in SYNONYM_MAP.items():
        syn_lower = [s.lower() for s in syn_list]
        
        # Check if skill or any of its variants match key or syn_list
        is_match = (
            skill_lower == key 
            or skill_lower in syn_lower 
            or any(v in syn_lower or v == key for v in aliases)
        )

        if is_match:
            aliases.update(syn_lower)
            aliases.add(key)
            for item in syn_list:
                aliases.update(_generate_fuzzy_variants(item))

    return [a for a in aliases if a.strip()]


def _skill_in_text(skill: str, text: str) -> bool:
    """Check if any alias of a skill appears in text (word-boundary aware)."""
    text_lower = text.lower()
    for alias in get_aliases(skill):
        # Word boundary match (handles symbols like c++, c#, .net, ci/cd)
        pattern = r"(?<![\w])" + re.escape(alias) + r"(?![\w])"
        if re.search(pattern, text_lower):
            return True
    return False


def evaluate_skills(
    sections: dict[str, str],
    skills: list[str],
    llm_skills: Optional[list[dict]] = None,
) -> dict:
    """
    Evaluate each skill's presence and context in the candidate's CV.

    Returns:
        {
            "contextual": [skills verified in experience/projects],
            "stuffed": [skills only listed, not used in context],
            "missing": [skills not found at all],
            "ratio": float (0.0 to 1.0 — fraction of skills found),
            "detail": [{"name": ..., "context": ..., "evidence": ...}]
        }
    """
    if not skills:
        return {
            "contextual": [], "stuffed": [], "missing": [],
            "ratio": 1.0, "detail": [],
        }

    # If LLM already extracted skill data, use that as primary
    if llm_skills:
        return _evaluate_from_llm(skills, llm_skills)

    # Regex / synonym evaluation
    exp_text = (sections.get("experience", "") or "").lower()
    proj_text = (sections.get("projects", "") or "").lower()
    context_text = f"{exp_text} {proj_text}"

    full_text = " ".join(str(v) for v in sections.values() if v).lower()

    contextual = []
    stuffed = []
    missing = []
    detail = []

    for skill in skills:
        if _skill_in_text(skill, context_text):
            contextual.append(skill)
            detail.append({
                "name": skill, "context": "project",
                "evidence": "Found in experience/projects section",
            })
        elif _skill_in_text(skill, full_text):
            stuffed.append(skill)
            detail.append({
                "name": skill, "context": "mentioned",
                "evidence": "Found in text but not in experience/projects",
            })
        else:
            missing.append(skill)
            detail.append({
                "name": skill, "context": "missing", "evidence": "",
            })

    total_found = len(contextual) + len(stuffed)
    ratio = total_found / len(skills) if skills else 1.0

    return {
        "contextual": contextual,
        "stuffed": stuffed,
        "missing": missing,
        "ratio": ratio,
        "detail": detail,
    }


def _evaluate_from_llm(
    required_skills: list[str],
    llm_skills: list[dict],
) -> dict:
    """Use LLM-extracted skill data with synonym fallback for maximum accuracy."""
    # Build lookup: skill name (lowercase) → context info
    llm_lookup: dict[str, dict] = {}
    for entry in llm_skills:
        name_lower = entry.get("name", "").strip().lower()
        if name_lower:
            llm_lookup[name_lower] = entry
            # Also index all aliases and variants
            for alias in get_aliases(name_lower):
                llm_lookup[alias] = entry

    contextual = []
    stuffed = []
    missing = []
    detail = []

    for skill in required_skills:
        aliases = get_aliases(skill)

        matched_entry = None
        for alias in aliases:
            if alias in llm_lookup:
                matched_entry = llm_lookup[alias]
                break

        if matched_entry:
            ctx = matched_entry.get("context", "mentioned")
            evidence = matched_entry.get("evidence", "")

            if ctx == "project":
                contextual.append(skill)
            else:
                stuffed.append(skill)

            detail.append({
                "name": skill,
                "context": ctx,
                "evidence": evidence,
            })
        else:
            missing.append(skill)
            detail.append({
                "name": skill, "context": "missing", "evidence": "",
            })

    total_found = len(contextual) + len(stuffed)
    ratio = total_found / len(required_skills) if required_skills else 1.0

    return {
        "contextual": contextual,
        "stuffed": stuffed,
        "missing": missing,
        "ratio": ratio,
        "detail": detail,
    }
