"""
OCR package for text extraction and parsing from bank receipt images.
"""

from .service import extract_text, process_image, get_ocr_service, OCRService
from .parser import (
    parse_receipt,
    extract_amount,
    extract_date,
    extract_recipient,
    extract_description,
)
from .utils import normalize_text, build_lines, detect_bank
from .client import OCRClient

__all__ = [
    # Service
    "extract_text",
    "process_image",
    "get_ocr_service",
    "OCRService",
    # Parser
    "parse_receipt",
    "extract_amount",
    "extract_date",
    "extract_recipient",
    "extract_description",
    # Utils
    "normalize_text",
    "build_lines",
    "detect_bank",
    # Client
    "OCRClient",
]
