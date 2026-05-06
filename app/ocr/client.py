"""
PaddleOCR client wrapper for text extraction from images.
"""
import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCRClient:
    """Singleton OCR client for text recognition."""

    _instance = None
    _ocr = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._ocr is None:
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                enable_mkldnn=False,
                det_db_thresh=0.3,
                det_db_box_thresh=0.5,
            )

    @property
    def engine(self):
        """Get the PaddleOCR engine instance."""
        return self._ocr

    def _preprocess(self, img):
        """Resize image for optimal OCR performance."""
        if img is None:
            return None
        target_width = 1024
        ratio = target_width / img.shape[1]
        target_height = int(img.shape[0] * ratio)
        return cv2.resize(img, (target_width, target_height))

    def predict(self, image_path: str):
        """
        Predict text from an image file path.

        Args:
            image_path: Path to the image file

        Returns:
            Raw PaddleOCR result or None if image cannot be loaded
        """
        img = cv2.imread(image_path)
        img = self._preprocess(img)
        if img is None:
            return None
        return self._ocr.ocr(img, cls=True)

    def predict_bytes(self, image_bytes: bytes):
        """
        Predict text from raw image bytes.

        Args:
            image_bytes: Raw bytes of the image

        Returns:
            Raw PaddleOCR result or None if image cannot be decoded
        """
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(array, cv2.IMREAD_COLOR)
        img = self._preprocess(img)
        if img is None:
            return None
        return self._ocr.ocr(img, cls=True)
