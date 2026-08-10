"""Resume parser service module for AI Career Copilot.

Provides high-level business logic to parse uploaded resume files (PDF, DOCX),
validate input files, extract plain text using text_extractor, clean whitespace,
normalize line breaks, and return sanitized plain text for AI processing pipelines.
"""

import logging
import re
from pathlib import Path
from typing import Union

from app.ai.text_extractor import (
    EmptyFileError,
    ExtractionFailedError,
    MissingFileError,
    TextExtractorError,
    UnsupportedFileTypeError,
    extract_text,
)

# Logger instance for parser service
logger = logging.getLogger(__name__)


def clean_resume_text(text: str) -> str:
    """Clean and normalize extracted resume text.

    - Normalizes carriage returns and line endings (\r\n -> \n).
    - Collapses multiple horizontal spaces/tabs within lines.
    - Strips leading and trailing whitespace per line.
    - Normalizes excessive blank lines (collapses 3+ consecutive newlines to \n\n).

    Args:
        text: Raw extracted text string.

    Returns:
        Cleaned and normalized text string.
    """
    if not text:
        return ""

    # Normalize carriage return characters to standard newlines
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Clean individual lines: collapse multiple spaces/tabs and strip line boundaries
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]

    # Rejoin lines with standard newline
    cleaned = "\n".join(lines)

    # Collapse 3 or more consecutive newlines down to 2 (paragraph break)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def parse_uploaded_resume(file_path: Union[str, Path]) -> str:
    """Parse an uploaded resume file, extract text, and clean content.

    Args:
        file_path: Absolute or relative path to the uploaded resume document.

    Returns:
        Cleaned, normalized plain text representation of the resume.

    Raises:
        MissingFileError: If the specified file does not exist or is invalid.
        EmptyFileError: If the resume contains no extractable text or is 0 bytes.
        UnsupportedFileTypeError: If the file format is not supported (.pdf, .docx).
        ExtractionFailedError: If an error occurs during text extraction or parsing.
    """
    path = Path(file_path)
    logger.info("Starting resume parsing service for file: %s", path)

    # 1. Validate file existence
    if not path.exists():
        logger.error("Resume file does not exist at path: %s", path)
        raise MissingFileError(f"Resume file not found: '{path}'")

    if not path.is_file():
        logger.error("Specified path is not a regular file: %s", path)
        raise MissingFileError(f"Specified path is not a regular file: '{path}'")

    # 2. Call text_extractor module to extract text
    try:
        raw_text = extract_text(path)
    except TextExtractorError as exc:
        logger.error("Text extraction failed for '%s': %s", path, exc)
        raise
    except Exception as exc:
        logger.error(
            "Unexpected error occurred during text extraction for '%s': %s",
            path,
            exc,
            exc_info=True,
        )
        raise ExtractionFailedError(
            f"Unexpected error parsing resume '{path}': {exc}"
        ) from exc

    # 3-5. Clean extracted text, remove unnecessary whitespace, normalize line breaks
    logger.debug("Cleaning extracted text for resume: %s", path)
    cleaned_text = clean_resume_text(raw_text)

    if not cleaned_text:
        logger.warning("Resume file resulted in empty text after cleaning: %s", path)
        raise EmptyFileError(
            f"Resume contains no text content after cleaning: '{path}'"
        )

    logger.info(
        "Successfully parsed resume '%s' (%d characters extracted & cleaned)",
        path,
        len(cleaned_text),
    )

    # 6. Return clean text
    return cleaned_text
