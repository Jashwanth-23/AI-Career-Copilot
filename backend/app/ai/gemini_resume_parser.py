"""Gemini Resume Parser Module for AI Career Copilot.

Uses Google Gen AI SDK (google.genai) via app.core.gemini_client to extract
structured JSON data from raw resume text. Provides prompt engineering, JSON response cleaning,
error handling, 429 quota exhaustion mapping, and fallback schema normalization.
"""

import json
import logging
import re
from typing import Any, Dict, Optional

from google.genai import types
from google.genai.errors import APIError

from app.core.gemini_client import (
    GeminiAuthError as CoreGeminiAuthError,
    GeminiQuotaExhaustedError as CoreGeminiQuotaExhaustedError,
    get_gemini_client,
    get_gemini_model,
    handle_gemini_api_error,
)

logger = logging.getLogger(__name__)

# Target JSON Schema default template
DEFAULT_PARSED_RESUME_SCHEMA: Dict[str, Any] = {
    "personal_information": {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "website": "",
    },
    "education": [],
    "experience": [],
    "skills": [],
    "projects": [],
    "certifications": [],
    "languages": [],
    "summary": "",
}


# ============================================================================
# Exception Classes
# ============================================================================


class GeminiParserError(Exception):
    """Base exception class for Gemini resume parser operations."""

    pass


class GeminiAPIKeyError(GeminiParserError):
    """Raised when the Gemini API key is missing or invalid."""

    pass


class GeminiQuotaExhaustedError(GeminiParserError):
    """Raised when Gemini returns HTTP 429 RESOURCE_EXHAUSTED."""

    pass


class GeminiParsingFailedError(GeminiParserError):
    """Raised when Gemini fails to return valid structured JSON after retries."""

    pass


# ============================================================================
# Helper Functions
# ============================================================================


def clean_json_response(raw_response: str) -> str:
    """Clean markdown code block wrappers (```json ... ```) from AI response text.

    Args:
        raw_response: Raw string output from Gemini API.

    Returns:
        Stripped string containing pure JSON text.
    """
    if not raw_response:
        return ""

    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()


def normalize_resume_json(parsed_data: Any) -> Dict[str, Any]:
    """Ensure parsed JSON contains all required top-level keys with valid default values.

    Args:
        parsed_data: Parsed data returned by json.loads().

    Returns:
        Normalized dictionary adhering to DEFAULT_PARSED_RESUME_SCHEMA.
    """
    if not isinstance(parsed_data, dict):
        logger.warning(
            "Parsed Gemini response is not a dict (%s). Returning default schema.",
            type(parsed_data),
        )
        return dict(DEFAULT_PARSED_RESUME_SCHEMA)

    normalized = dict(DEFAULT_PARSED_RESUME_SCHEMA)

    for key, default_val in DEFAULT_PARSED_RESUME_SCHEMA.items():
        if key in parsed_data and parsed_data[key] is not None:
            normalized[key] = parsed_data[key]

    return normalized


def build_parser_prompt(resume_text: str, is_retry: bool = False) -> str:
    """Build a structured prompt instructing Gemini to parse resume text into JSON.

    Args:
        resume_text: Extracted raw resume plain text.
        is_retry: Flag indicating if this is a retry attempt following a malformed JSON error.

    Returns:
        Formatted prompt string.
    """
    retry_notice = ""
    if is_retry:
        retry_notice = (
            "\nCRITICAL: Previous response was NOT valid JSON. Output ONLY raw valid JSON matching schema.\n"
        )

    prompt = f"""You are an expert AI Resume Parser. Extract all details from the resume text into a structured JSON object matching EXACTLY this schema:

{retry_notice}SCHEMA:
{{
  "personal_information": {{
    "name": "Full Name or ''",
    "email": "Email Address or ''",
    "phone": "Phone Number or ''",
    "location": "City, State/Country or ''",
    "linkedin": "LinkedIn URL or ''",
    "github": "GitHub URL or ''",
    "website": "Portfolio URL or ''"
  }},
  "education": [
    {{
      "institution": "School Name",
      "degree": "Degree",
      "field_of_study": "Major",
      "start_date": "Start Date or ''",
      "end_date": "End Date or ''",
      "gpa": "GPA or ''"
    }}
  ],
  "experience": [
    {{
      "company": "Company",
      "position": "Title",
      "location": "Location or ''",
      "start_date": "Start Date or ''",
      "end_date": "End Date or ''",
      "description": ["Bullet points"],
      "technologies": ["Tools / Languages"]
    }}
  ],
  "skills": ["Technical skills"],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Summary",
      "technologies": ["Tools used"],
      "link": "URL or ''"
    }}
  ],
  "certifications": ["Certifications"],
  "languages": ["Languages spoken"],
  "summary": "Professional summary statement"
}}

STRICT INSTRUCTIONS:
1. Return ONLY valid JSON. No markdown wrappers.
2. Return empty string "", empty array [], or null for missing fields.

RESUME TEXT:
{resume_text}
"""
    return prompt


# ============================================================================
# Main API Parsing Function
# ============================================================================


def parse_resume_with_gemini(
    resume_text: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    max_retries: int = 1,
) -> Dict[str, Any]:
    """Parse extracted resume text into structured JSON using Google Gen AI SDK (google.genai).

    Args:
        resume_text: Cleaned plain text extracted from a resume document.
        api_key: Optional Gemini API key override (defaults to settings.GEMINI_API_KEY).
        model_name: Optional model identifier override (defaults to settings.GEMINI_MODEL).
        max_retries: Number of retry attempts for malformed JSON (default: 1).

    Returns:
        Structured dictionary matching the resume schema.

    Raises:
        ValueError: If resume_text is empty or invalid.
        GeminiAPIKeyError: If no valid Gemini API key is configured.
        GeminiQuotaExhaustedError: If Gemini returns HTTP 429 quota exhausted.
        GeminiParsingFailedError: If Gemini fails to produce valid JSON after retries.
    """
    if not resume_text or not resume_text.strip():
        logger.error("Empty resume_text provided to parse_resume_with_gemini")
        raise ValueError("Input resume_text cannot be empty.")

    target_model = model_name if model_name and model_name.strip() else get_gemini_model()

    try:
        client = get_gemini_client(api_key=api_key)
    except CoreGeminiAuthError as exc:
        raise GeminiAPIKeyError(str(exc)) from exc

    generation_config = types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
    )

    total_attempts = 1 + max(0, max_retries)

    for attempt in range(1, total_attempts + 1):
        is_retry = attempt > 1
        prompt = build_parser_prompt(resume_text, is_retry=is_retry)

        logger.info(
            "Sending resume text to Gemini API via google.genai (Model: %s, Attempt %d/%d)",
            target_model,
            attempt,
            total_attempts,
        )

        try:
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=generation_config,
            )
            raw_output = (
                response.text if response and hasattr(response, "text") else ""
            )
        except CoreGeminiQuotaExhaustedError as exc:
            logger.error("Gemini API quota exhausted (429) on attempt %d: %s", attempt, exc)
            raise GeminiQuotaExhaustedError(str(exc)) from exc
        except CoreGeminiAuthError as exc:
            logger.error("Gemini API auth failed on attempt %d: %s", attempt, exc)
            raise GeminiAPIKeyError(str(exc)) from exc
        except APIError as exc:
            err_str = str(exc)
            logger.error("Google Gen AI API error on attempt %d: %s", attempt, err_str)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                raise GeminiQuotaExhaustedError(
                    "Gemini API quota is temporarily exhausted. Please wait and try again."
                ) from exc
            if attempt == total_attempts:
                raise GeminiParsingFailedError(f"Gemini API request failed: {exc}") from exc
            continue
        except Exception as exc:
            err_str = str(exc)
            logger.error("Unexpected error invoking Gemini API on attempt %d: %s", attempt, err_str, exc_info=True)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                raise GeminiQuotaExhaustedError(
                    "Gemini API quota is temporarily exhausted. Please wait and try again."
                ) from exc
            if attempt == total_attempts:
                raise GeminiParsingFailedError(f"Unexpected error communicating with Gemini: {exc}") from exc
            continue

        if not raw_output or not raw_output.strip():
            logger.warning("Gemini API returned empty response on attempt %d", attempt)
            if attempt == total_attempts:
                raise GeminiParsingFailedError("Gemini API returned an empty response.")
            continue

        cleaned_json_str = clean_json_response(raw_output)

        try:
            parsed_data = json.loads(cleaned_json_str)
            normalized_data = normalize_resume_json(parsed_data)
            logger.info("Successfully parsed and normalized resume JSON with Gemini API (google.genai)")
            return normalized_data
        except json.JSONDecodeError as exc:
            logger.warning(
                "Failed to decode JSON from Gemini output on attempt %d/%d: %s. Output snippet: %.100s",
                attempt,
                total_attempts,
                exc,
                cleaned_json_str,
            )
            if attempt == total_attempts:
                raise GeminiParsingFailedError(
                    f"Gemini output could not be parsed as valid JSON after {total_attempts} attempts: {exc}"
                ) from exc

    raise GeminiParsingFailedError("Gemini parsing failed unexpectedly after all attempts.")
