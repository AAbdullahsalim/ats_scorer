"""
LLM client with Groq primary (fast, high RPM) + Gemini fallback.
Handles rate limiting, retries, and graceful degradation.

Key design choices:
- Groq is primary (faster, higher RPM), Gemini is fallback
- Robust JSON repair handles trailing commas, comments, single quotes, etc.
- Rate limits are per-batch transient (not permanently disabling)
- Retry with backoff on transient failures
"""

import re
import time
import json
import logging
from typing import Optional

from config import (
    GEMINI_API_KEY, GROQ_API_KEY, LLM_DISABLED,
    LLM_RETRY_DELAY_SECONDS, LLM_INTER_CALL_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client.
    Uses Groq (Llama 3.3 70B) as primary for batch speed (30 RPM, 0.3s).
    Falls back to Gemini (2.0 Flash) if Groq fails.
    Falls back to None (regex-only) if both fail.
    """

    def __init__(self):
        self._groq_client = None
        self._gemini_model = None
        self._groq_available = False
        self._gemini_available = False
        self._last_call_time = 0.0
        self._consecutive_failures = 0
        self._max_failures_before_disable = 5
        # Temporary rate-limit cooldowns (timestamp until available again)
        self._groq_rate_limit_until = 0.0
        self._gemini_rate_limit_until = 0.0
        self._init_clients()

    def _init_clients(self):
        """Initialize LLM clients lazily."""
        if LLM_DISABLED:
            logger.info("LLM disabled via config")
            return

        # Init Groq - DISABLED AS PER USER REQUEST
        # if GROQ_API_KEY:
        #     try:
        #         from groq import Groq
        #         self._groq_client = Groq(api_key=GROQ_API_KEY)
        #         self._groq_available = True
        #         logger.info("Groq client initialized (primary)")
        #     except ImportError:
        #         logger.warning("groq package not installed")
        #     except Exception as e:
        #         logger.warning(f"Groq init failed: {e}")
        self._groq_client = None
        self._groq_available = False

        # Init Gemini (Now Primary)
        if GEMINI_API_KEY:
            try:
                import warnings
                import google.generativeai as genai
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    genai.configure(api_key=GEMINI_API_KEY)
                    self._gemini_model = genai.GenerativeModel("gemini-3.5-flash-lite")
                self._gemini_sdk = "old"
                self._gemini_available = True
                logger.info("Gemini client initialized (gemini-3.5-flash-lite primary)")
            except ImportError:
                logger.warning("google-generativeai package not installed")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        if LLM_DISABLED:
            return False
        if self._consecutive_failures >= self._max_failures_before_disable:
            return False
        # Check temporary rate-limit cooldowns
        now = time.time()
        groq_ok = self._groq_available and now >= self._groq_rate_limit_until
        gemini_ok = self._gemini_available and now >= self._gemini_rate_limit_until
        return groq_ok or gemini_ok

    @property
    def active_provider(self) -> str:
        """Return active LLM provider."""
        if not self.is_available:
            return "offline"
        now = time.time()
        if self._groq_available and now >= self._groq_rate_limit_until:
            return "groq"
        if self._gemini_available and now >= self._gemini_rate_limit_until:
            return "gemini"
        return "offline"

    def _throttle(self):
        """Enforce minimum delay between calls to respect RPM limits."""
        elapsed = time.time() - self._last_call_time
        if elapsed < LLM_INTER_CALL_DELAY_SECONDS:
            time.sleep(LLM_INTER_CALL_DELAY_SECONDS - elapsed)

    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API. Returns response text or None on failure."""
        if not self._groq_client:
            return None
        # Check temporary rate-limit cooldown
        if time.time() < self._groq_rate_limit_until:
            return None

        # Try models in order of preference
        groq_models = [
            "qwen/qwen3.6-27b",         # Best quality available
            "groq/compound",             # Groq's own compound model
            "groq/compound-mini",        # Smaller fallback
            "openai/gpt-oss-120b",       # OpenAI-compatible via Groq
            "llama-3.3-70b-versatile",   # Legacy check
        ]

        for model_name in groq_models:
            try:
                response = self._groq_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000,
                    response_format={"type": "json_object"},
                )
                result = response.choices[0].message.content
                if result and len(result.strip()) > 50:
                    logger.debug(f"Groq model used: {model_name}")
                    return result
                return None
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "rate" in error_str:
                    logger.warning("Groq rate limited, cooling down 60s")
                    self._groq_rate_limit_until = time.time() + 60
                    return None
                elif "404" in error_str or "not found" in error_str or "decommissioned" in error_str or "model_not_found" in error_str:
                    logger.warning(f"Groq model {model_name} unavailable, trying next...")
                    continue  # Try next model
                else:
                    logger.warning(f"Groq call failed with {model_name}: {e}")
                    return None

        # All models failed
        logger.warning("All Groq models unavailable, disabling Groq")
        self._groq_available = False
        return None

    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API. Returns response text or None on failure."""
        if not self._gemini_model:
            return None
        # Check temporary rate-limit cooldown
        if time.time() < self._gemini_rate_limit_until:
            logger.debug("Gemini in rate-limit cooldown, skipping")
            return None

        try:
            # Old google.generativeai SDK
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                response = self._gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 2000,
                        "response_mime_type": "application/json",
                    },
                )
            result_text = response.text

            if not result_text or len(result_text.strip()) < 80:
                logger.warning(f"Gemini response too short ({len(result_text or '')} chars)")
                return None
            logger.info(f"Gemini responded with {len(result_text)} chars")
            return result_text
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "quota" in error_str or "resource_exhausted" in error_str:
                logger.warning("Gemini rate limited, cooling down 90s")
                self._gemini_rate_limit_until = time.time() + 90
            elif "404" in error_str or "not found" in error_str:
                logger.warning(f"Gemini model not found, trying gemini-3.1-flash-lite: {e}")
                # Try a different model
                try:
                    import warnings, google.generativeai as genai
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self._gemini_model = genai.GenerativeModel("gemini-3.1-flash-lite")
                except Exception:
                    self._gemini_available = False
            else:
                logger.warning(f"Gemini call failed: {e}")
            return None

    def call(self, prompt: str) -> Optional[str]:
        """
        Call LLM — tries Groq first, falls back to Gemini.
        Returns raw JSON string response, or None if failed.
        """
        if not self.is_available:
            return None

        self._throttle()
        self._last_call_time = time.time()

        now = time.time()

        # Try Groq first (primary — faster, higher RPM)
        if self._groq_available and now >= self._groq_rate_limit_until:
            result = self._call_groq(prompt)
            if result:
                self._consecutive_failures = 0
                return result

        # Fall back to Gemini
        if self._gemini_available and time.time() >= self._gemini_rate_limit_until:
            result = self._call_gemini(prompt)
            if result:
                self._consecutive_failures = 0
                return result

        # Both failed
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._max_failures_before_disable:
            logger.error(
                f"LLM disabled after {self._max_failures_before_disable} "
                "consecutive failures"
            )

        return None

    def call_json(self, prompt: str) -> Optional[dict]:
        """
        Call LLM and parse response as JSON.
        Applies robust JSON repair before parsing to handle:
        - Trailing commas in arrays/objects
        - Python-style comments (// and #)
        - Single-quoted strings
        - Unquoted keys
        - Markdown code blocks wrapping the JSON
        Returns parsed dict or None on failure.
        """
        raw = self.call(prompt)
        if not raw:
            return None

        raw = raw.strip()

        # 1. Try parsing directly (works for Groq JSON mode responses)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 2. Extract from markdown code blocks if present
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL | re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
        else:
            # Strip to first { ... last }
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1:
                raw = raw[start:end + 1]

        # 3. Try after extraction
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # 4. Apply JSON repair transformations
        repaired = self._repair_json(raw)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return None

    @staticmethod
    def _repair_json(text: str) -> str:
        """
        Attempt to repair common LLM JSON output issues:
        - Trailing commas before } or ]
        - Single-line comments (// ...)
        - Hash comments (# ...)
        - Single-quoted strings
        - Ellipsis placeholders
        - Unquoted simple values
        """
        # Remove single-line comments: // ...
        text = re.sub(r'//[^\n"]*(?=\n|$)', '', text)
        # Remove hash comments that aren't inside strings: # ...
        text = re.sub(r'(?<!["])#[^\n"]*(?=\n|$)', '', text)
        # Remove trailing commas before ] or }
        text = re.sub(r',\s*([\]}])', r'\1', text)
        # Replace ellipsis placeholders
        text = re.sub(r'\.\.\.', '""', text)
        # Fix single-quoted strings to double-quoted
        # Only replace outer single quotes that wrap values
        text = re.sub(r"(?<=[{,:\[])\s*'([^']*)'(?=\s*[,:\]}])", r'"\1"', text)
        # Remove any remaining trailing commas (second pass for nested)
        text = re.sub(r',\s*([\]}])', r'\1', text)
        return text.strip()

    def reset_rate_limits(self):
        """Reset rate limit flags (call periodically or between batches)."""
        self._groq_available = bool(self._groq_client)
        self._gemini_available = bool(self._gemini_model)
        self._consecutive_failures = 0
        self._groq_rate_limit_until = 0.0
        self._gemini_rate_limit_until = 0.0
