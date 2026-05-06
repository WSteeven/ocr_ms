"""
Text extraction and parsing functions for receipt fields.
"""
import re
from .utils import normalize_text, build_lines, detect_bank


MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "setiembre": "09", "octubre": "10",
    "noviembre": "11", "diciembre": "12",
    "ene": "01", "feb": "02", "mar": "03", "abr": "04", "may": "05", "jun": "06",
    "jul": "07", "ago": "08", "sep": "09", "oct": "10", "nov": "11", "dic": "12"
}


def extract_amount(text: str) -> tuple:
    """
    Extract amount from text with $ symbol.
    
    Args:
        text: Normalized text
        
    Returns:
        Tuple of (amount_float, confidence_score)
    """
    matches = re.findall(r'\$\s?([\d.,]+)', text)
    
    if not matches:
        return None, 0
    
    values = []
    for m in matches:
        try:
            normalized = m.replace(",", "")
            value = float(normalized)
            if value > 0:
                values.append(value)
        except ValueError:
            continue
    
    if not values:
        return None, 0
    
    return max(values), 1.0


def extract_date(text: str) -> tuple:
    """
    Extract date from text in various formats.
    
    Args:
        text: Normalized text
        
    Returns:
        Tuple of (date_str_YYYY-MM-DD, confidence_score)
    """
    text = text.lower()
    
    # Pichincha: "El 21 de abril de 2026"
    m = re.search(
        r'(?:el\s*)?(\d{1,2})\s+de\s+([a-záéíóúñ]+\.?)\s+de\s+(\d{4})',
        text,
        re.IGNORECASE
    )
    if m:
        day, mon, year = m.groups()
        month_str = mon.lower().rstrip('.')
        month = MESES.get(month_str, "01")
        return f"{year}-{month}-{int(day):02d}", 1.0
    
    # Produbanco: "Martes 27 Ene. 2026"
    m2 = re.search(
        r'(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+(\d{1,2})\s+([a-záéíóúñ]+\.?)\s+(\d{4})',
        text,
        re.IGNORECASE
    )
    if m2:
        day, mon, year = m2.groups()
        month_str = mon.lower().rstrip('.')
        month = MESES.get(month_str, "01")
        return f"{year}-{month}-{int(day):02d}", 1.0
    
    # Fallback: "Feb. 13 2026"
    m3 = re.search(r'(\d{1,2})\s*([a-z]{3})\.?\s*(\d{4})', text)
    if m3:
        day, mon, year = m3.groups()
        short = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        return f"{year}-{short.get(mon[:3], '01')}-{int(day):02d}", 0.9
    
    return None, 0


def extract_recipient(text: str) -> tuple:
    """
    Extract recipient/payee name from text (bank-specific).
    
    Args:
        text: Raw OCR text (before normalization to preserve letter accuracy)
        
    Returns:
        Tuple of (recipient_name, confidence_score)
    """
    text = re.sub(r'\s+', ' ', text)
    bank = detect_bank(text)
    
    if bank == "produbanco":
        return _extract_recipient_produbanco(text)
    elif bank == "pichincha":
        return _extract_recipient_pichincha(text)
    
    # Fallback
    m = re.search(r'\bA\s+([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)\s+(?:El|De|Cuenta|Banco|N°|Nro)', text)
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if len(name) > 3:
            return name, 0.8
    
    return None, 0


def _extract_recipient_produbanco(text: str) -> tuple:
    """Extract recipient from Produbanco receipt."""
    text = re.sub(r'\s+', ' ', text)
    
    # "Para: [Name]"
    m = re.search(
        r'\bPara\s*:\s*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?:\s+(?:Produbanco|Grupo|Producci[óo]n|Comprobante|Ahorros|Nro|N°|De:)|$)',
        text,
        re.IGNORECASE
    )
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if len(name) > 3:
            return name, 1.0
    
    # "De: [Name]"
    m = re.search(
        r'\bDe\s*:\s*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?:\s+(?:Produbanco|Grupo|Producci[óo]n|Comprobante|Ahorros|Nro|N°|Cuenta)|$)',
        text,
        re.IGNORECASE
    )
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if len(name) > 3:
            return name, 0.9
    
    return None, 0


def _extract_recipient_pichincha(text: str) -> tuple:
    """Extract recipient from Banco Pichincha receipt."""
    text = re.sub(r'\s+', ' ', text)
    
    # "A [Name] El [date/keywords]"
    m = re.search(
        r'\bA\s+([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)\s+(?:El|De|Cuenta|Banco|N°|Nro|Martes|Lunes|Miércoles|Jueves|Viernes|Sábado|Domingo)',
        text,
        re.IGNORECASE
    )
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if len(name) > 3:
            return name, 1.0
    
    # Fallback: "A [Name]"
    m = re.search(r'\bA\s+([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?:\s{2,}|$)', text)
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s+', ' ', name)
        if len(name) > 3 and name.lower() not in ['el', 'de', 'cuenta', 'banco']:
            return name, 0.8
    
    return None, 0


def extract_description(data: dict, raw_text: str) -> tuple:
    """
    Extract transaction description/status (bank-specific).
    
    Args:
        data: OCR data dict
        raw_text: Raw OCR text
        
    Returns:
        Tuple of (description, confidence_score)
    """
    bank = detect_bank(raw_text)
    
    if bank == "produbanco":
        return _extract_description_produbanco(data, raw_text)
    
    if bank == "pichincha":
        return _extract_description_pichincha(data, raw_text)
    
    # Fallback
    status_patterns = [
        r'(?:transferencia|transacci[ó]n)\s+(?:exitosa|realizada|completada)',
        r'¡?(?:exitosa|realizada|completada|procesada)\!?'
    ]
    
    for pattern in status_patterns:
        m = re.search(pattern, raw_text.lower())
        if m:
            return m.group(0).strip(), 0.8
    
    return "Transferencia Local", 0.6


def _extract_description_produbanco(data: dict, raw_text: str) -> tuple:
    """Extract description from Produbanco receipt."""
    texts = data.get('rec_texts', [])
    raw_text_lower = raw_text.lower()
    
    status_patterns = [
        r'transferencia\s+(?:exitosa|realizada|completada|procesada)',
        r'(?:exitosa|realizada|completada|procesada)',
        r'transacci[ó]n\s+(?:exitosa|realizada)',
    ]
    
    for pattern in status_patterns:
        m = re.search(pattern, raw_text_lower)
        if m:
            phrase = m.group(0).strip()
            phrase = phrase.replace("ó", "o").strip()
            return phrase.capitalize(), 1.0
    
    for text in texts:
        text_lower = str(text).lower().strip()
        if any(keyword in text_lower for keyword in ['exitosa', 'realizada', 'completada', 'procesada', 'transferencia']):
            return text.strip(), 0.9
    
    return "Transferencia Local", 0.7


def _extract_description_pichincha(data: dict, raw_text: str) -> tuple:
    """Extract description from Banco Pichincha receipt."""
    lines = build_lines(data)
    raw_text_lower = raw_text.lower()
    
    status_patterns = [
        r'¡?transferencia\s+(?:exitosa|realizada|completada|procesada)\!?',
        r'¡?(?:exitosa|realizada|completada|procesada)\!?',
    ]
    
    for pattern in status_patterns:
        m = re.search(pattern, raw_text_lower)
        if m:
            phrase = m.group(0).strip()
            phrase = phrase.replace("¡", "").replace("!", "").strip()
            return phrase.capitalize(), 1.0
    
    for i, t in enumerate(lines):
        if "$" in t or re.search(r'\d+[.,]\d{2}', t):
            for j in range(i+1, min(i+4, len(lines))):
                cand = lines[j].strip()
                
                if any(x in cand.lower() for x in [
                    "cuenta", "banco", "nro", "comprobante",
                    "origen", "destino", "digital", "numero",
                    "el de", "el 0", "mto veh"
                ]):
                    continue
                
                if any(keyword in cand.lower() for keyword in ['exitosa', 'realizada', 'completada', 'transferencia']):
                    return cand, 1.0
                
                if len(cand) > 5 and len(cand.split()) >= 1:
                    return cand, 0.8
    
    return "Transferencia Local", 0.7


def parse_receipt(raw_text: str) -> dict:
    """
    Parse receipt text and extract all fields.
    
    Args:
        raw_text: Complete OCR text from receipt
        
    Returns:
        Dict with parsed fields: monto, fecha, destinatario, descripcion, confidence
    """
    text = normalize_text(raw_text)
    
    # Extract from raw text to preserve names
    destinatario, c3 = extract_recipient(raw_text)
    
    # Extract from normalized text
    monto, c1 = extract_amount(text)
    fecha, c2 = extract_date(text)
    
    confidence = (c1 + c2 + c3) / 3
    
    return {
        "monto": monto,
        "fecha": fecha,
        "destinatario": destinatario,
        "descripcion": None,  # Filled later
        "confidence": confidence
    }
