"""
Utility functions for OCR processing.
"""
import re


def ensure_python_data(obj):
    """Convert NumPy arrays and tuples to plain Python lists recursively."""
    if isinstance(obj, dict):
        return {k: ensure_python_data(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return [ensure_python_data(v) for v in obj]
    if isinstance(obj, list):
        return [ensure_python_data(v) for v in obj]
    if hasattr(obj, "tolist") and not isinstance(obj, (str, bytes)):
        try:
            return ensure_python_data(obj.tolist())
        except Exception:
            return obj
    return obj


def normalize_text(text: str) -> str:
    """
    Normalize OCR text by fixing common OCR errors.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Normalized text
    """
    # Fix common OCR character mistakes
    text = text.replace("O", "0")
    text = text.replace("l", "1")
    text = text.replace("|", "1")
    
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s?-\s?', ' - ', text)
    
    return text.strip()


def build_lines(data: dict) -> list:
    """
    Build sorted text lines from OCR boxes and texts.
    
    Args:
        data: OCR data dict with rec_texts and rec_boxes
        
    Returns:
        List of text lines sorted by vertical position
    """
    texts = data.get('rec_texts') or []
    boxes = data.get('rec_boxes') or []
    
    lines = []
    for i in range(min(len(texts), len(boxes))):
        text = texts[i]
        box = boxes[i]
        
        if not isinstance(text, str):
            continue
        
        y = _get_y_position(box)
        lines.append((y, text.strip()))
    
    lines.sort(key=lambda x: x[0])
    return [t for _, t in lines]


def _get_y_position(box) -> float:
    """Extract average Y coordinate from a box."""
    try:
        # Polygon format: [[x,y],[x,y],[x,y],[x,y]]
        if isinstance(box, (list, tuple)) and len(box) > 0 and isinstance(box[0], (list, tuple)):
            return sum(p[1] for p in box) / len(box)
        
        # Flat array format: [x1,y1,x2,y2,...]
        if isinstance(box, (list, tuple)) and len(box) >= 8:
            return sum(box[1::2]) / len(box[1::2])
    except Exception:
        pass
    
    return 0


def detect_bank(text: str) -> str:
    """
    Detect which bank the receipt is from.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Bank identifier: 'produbanco', 'pichincha', or 'unknown'
    """
    t = text.lower()
    
    if "produbanco" in t:
        return "produbanco"
    if "pichincha" in t:
        return "pichincha"
    
    return "unknown"
