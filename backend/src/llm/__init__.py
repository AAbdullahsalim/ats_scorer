"""
LLM module — public API.
"""

from .client import LLMClient
from .prompts import build_cv_extraction_prompt, build_jd_extraction_prompt
from .extractor import parse_cv_extraction, parse_jd_extraction

__all__ = [
    "LLMClient",
    "build_cv_extraction_prompt",
    "build_jd_extraction_prompt",
    "parse_cv_extraction",
    "parse_jd_extraction",
]
