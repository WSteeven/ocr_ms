"""
Main OCR service that orchestrates text extraction and parsing.
"""
import traceback
from .client import OCRClient
from .utils import ensure_python_data
from .parser import parse_receipt, extract_description


class OCRService:
    """Main OCR service for extracting and parsing receipt data."""

    def __init__(self):
        self.client = OCRClient()

    def _extract_and_parse(self, ocr_result: object) -> dict:
        """
        Normalize OCR result and parse receipt fields.

        Args:
            ocr_result: Raw PaddleOCR result

        Returns:
            Dict with raw_text and parsed fields, or error info
        """
        if ocr_result is None:
            return {"error": "NO_RESULT"}

        # Normalize all NumPy arrays to Python lists
        result = ensure_python_data(ocr_result)

        # Handle both dict and list return formats
        if isinstance(result, dict):
            data = result
        elif isinstance(result, list) and len(result) > 0:
            data = next((item for item in result if isinstance(item, dict)), result[0])
        else:
            return {"error": "NO_TEXT_FOUND"}

        if not isinstance(data, dict):
            return {"error": "UNSUPPORTED_FORMAT"}

        # Normalize OCR data fields
        texts = ensure_python_data(data.get('rec_texts', []))

        # Build full text from all extracted text lines
        raw_text_list = [str(text).strip() for text in texts]
        raw_full_text = " ".join(raw_text_list)

        if not raw_full_text.strip():
            return {"error": "NO_TEXT_EXTRACTED"}

        # Parse receipt fields
        parsed = parse_receipt(raw_full_text)

        # Extract description with full data dict
        desc, c_desc = extract_description(data, raw_full_text)
        parsed["descripcion"] = desc
        parsed["confidence"] = (parsed["confidence"] + c_desc) / 2

        return {
            "raw_text": raw_full_text,
            "parsed": parsed
        }

    def extract_text(self, image_path: str) -> dict:
        """
        Extract and parse text from an image file.

        Args:
            image_path: Path to image file

        Returns:
            Dict with raw_text and parsed fields, or error info
        """
        try:
            result = self.client.predict(image_path)
            return self._extract_and_parse(result)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error in OCRService.extract_text: {e}\n{tb}")
            return {"error": str(e), "traceback": tb}

    def process_image(self, image_bytes: bytes) -> dict:
        """
        Extract and parse text from raw image bytes.

        Args:
            image_bytes: Raw bytes of the image

        Returns:
            Dict with raw_text and parsed fields, or error info
        """
        try:
            result = self.client.predict_bytes(image_bytes)
            return self._extract_and_parse(result)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"Error in OCRService.process_image: {e}\n{tb}")
            return {"error": str(e), "traceback": tb}


# Singleton instance
_service = None


def get_ocr_service() -> OCRService:
    """Get or create the OCR service singleton."""
    global _service
    if _service is None:
        _service = OCRService()
    return _service


def extract_text(image_path: str) -> dict:
    """
    Convenience function to extract text from an image file.

    Args:
        image_path: Path to image file

    Returns:
        Dict with extraction results
    """
    service = get_ocr_service()
    return service.extract_text(image_path)


def process_image(image_bytes: bytes) -> dict:
    """
    Convenience function to process image bytes.

    Args:
        image_bytes: Raw bytes of the image

    Returns:
        Dict with extraction results
    """
    service = get_ocr_service()
    return service.process_image(image_bytes)
