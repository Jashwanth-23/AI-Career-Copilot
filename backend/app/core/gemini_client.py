"""Centralized Google Gemini Client & Health Diagnostic Module.

Provides singleton-like initialization for Google GenAI SDK (`google.genai`),
centralized model and API key configuration, exception mapping for HTTP 429 rate limits,
and backend diagnostic health checks.
"""

import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai.errors import APIError

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Hierarchy
# ============================================================================


class GeminiServiceError(Exception):
    """Base exception for Gemini service operations."""

    pass


class GeminiQuotaExhaustedError(GeminiServiceError):
    """Raised when Gemini returns HTTP 429 RESOURCE_EXHAUSTED."""

    pass


class GeminiAuthError(GeminiServiceError):
    """Raised when Gemini API authentication fails (401/403)."""

    pass


class GeminiModelNotFoundError(GeminiServiceError):
    """Raised when the requested Gemini model is invalid or unavailable (404)."""

    pass


# ============================================================================
# Centralized Configuration & Client Factory
# ============================================================================


def get_gemini_model() -> str:
    """Return configured Gemini model name from settings or default."""
    model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
    return model_name if model_name and model_name.strip() else "gemini-2.5-flash"


def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """Initialize and return a Google GenAI SDK client.

    Args:
        api_key: Optional API key override. Defaults to settings.GEMINI_API_KEY.

    Returns:
        genai.Client instance.

    Raises:
        GeminiAuthError: If no API key is configured or client initialization fails.
    """
    effective_api_key = api_key if api_key is not None else settings.GEMINI_API_KEY

    if not effective_api_key or not effective_api_key.strip():
        logger.error("Gemini API key is not configured in settings or parameters.")
        raise GeminiAuthError(
            "Gemini API key is missing. Please configure GEMINI_API_KEY in environment variables."
        )

    try:
        client = genai.Client(api_key=effective_api_key)
        return client
    except Exception as exc:
        logger.error("Failed to initialize Google Gen AI client: %s", exc, exc_info=True)
        raise GeminiAuthError(f"Failed to initialize Gemini client: {exc}") from exc


def handle_gemini_api_error(exc: Exception, operation: str = "Gemini operation") -> None:
    """Classify and raise domain-specific Gemini exceptions from SDK APIError.

    Args:
        exc: Exception caught during Gemini SDK calls.
        operation: Descriptive context string for logging.

    Raises:
        GeminiQuotaExhaustedError: On HTTP 429 / RESOURCE_EXHAUSTED.
        GeminiAuthError: On HTTP 401 / 403.
        GeminiModelNotFoundError: On HTTP 404 model not found.
        GeminiServiceError: On other API errors.
    """
    err_str = str(exc)
    logger.error("Gemini API error during %s: %s", operation, err_str)

    if isinstance(exc, APIError):
        code = getattr(exc, "code", None)
        status_code = getattr(exc, "status_code", None)

        if code == 429 or status_code == 429 or "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            raise GeminiQuotaExhaustedError(
                "Gemini API quota is temporarily exhausted. Please wait and try again."
            ) from exc
        if code in (401, 403) or status_code in (401, 403) or "PERMISSION_DENIED" in err_str or "UNAUTHENTICATED" in err_str:
            raise GeminiAuthError("Gemini API authentication failed. Please check the API key configuration.") from exc
        if code == 404 or status_code == 404 or "NOT_FOUND" in err_str:
            raise GeminiModelNotFoundError(f"Configured Gemini model is unavailable or invalid: {get_gemini_model()}") from exc

    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
        raise GeminiQuotaExhaustedError(
            "Gemini API quota is temporarily exhausted. Please wait and try again."
        ) from exc

    raise GeminiServiceError(f"Gemini API error: {err_str}") from exc


# ============================================================================
# Health Check Diagnostic
# ============================================================================


def check_gemini_health() -> Dict[str, Any]:
    """Perform a diagnostic check on the Gemini API integration.

    Returns:
        Diagnostic report dictionary outlining key status, client status, model, and generation result.
    """
    model_name = get_gemini_model()
    raw_key = settings.GEMINI_API_KEY or ""
    key_configured = bool(raw_key.strip())
    masked_key = f"{raw_key[:4]}...{raw_key[-4:]}" if len(raw_key) >= 8 else "Not configured"

    health_status = {
        "status": "error",
        "api_key_configured": key_configured,
        "api_key_snippet": masked_key,
        "configured_model": model_name,
        "client_initialized": False,
        "test_generation": "failed",
        "message": "Initialization failed.",
    }

    if not key_configured:
        health_status["message"] = "Gemini API key is missing from backend environment configuration."
        return health_status

    try:
        client = get_gemini_client()
        health_status["client_initialized"] = True
    except Exception as exc:
        health_status["message"] = f"Failed to initialize Gemini client: {exc}"
        return health_status

    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Respond with 'OK' to confirm service connection.",
        )
        if response and hasattr(response, "text") and response.text:
            health_status["status"] = "ok"
            health_status["test_generation"] = "success"
            health_status["message"] = f"Gemini API client and model '{model_name}' are healthy and operational."
        else:
            health_status["status"] = "degraded"
            health_status["test_generation"] = "empty_response"
            health_status["message"] = f"Gemini model '{model_name}' connected but returned empty test response."
    except Exception as exc:
        err_str = str(exc)
        logger.warning("Gemini health check test request failed: %s", err_str)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            health_status["status"] = "quota_exhausted"
            health_status["test_generation"] = "429_quota_exhausted"
            health_status["message"] = "Gemini API key and client initialized successfully, but quota is temporarily exhausted (HTTP 429)."
        elif "PERMISSION_DENIED" in err_str or "401" in err_str or "403" in err_str:
            health_status["status"] = "auth_failed"
            health_status["test_generation"] = "auth_failed"
            health_status["message"] = "Gemini API key authentication failed."
        elif "NOT_FOUND" in err_str or "404" in err_str:
            health_status["status"] = "model_not_found"
            health_status["test_generation"] = "model_not_found"
            health_status["message"] = f"Configured model '{model_name}' was not found or is unavailable."
        else:
            health_status["status"] = "error"
            health_status["test_generation"] = "api_error"
            health_status["message"] = f"Gemini API request failed: {err_str}"

    return health_status
