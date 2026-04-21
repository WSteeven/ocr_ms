import cv2
import numpy as np
import pytesseract
import re

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)[1]
    return thresh

def find_odometer_roi(img):
    h, w, _ = img.shape

    # 🔥 1. eliminar overlay inferior (GPS, texto)
    img = img[0:int(h * 0.85), :]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []

    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)

        if ch == 0:
            continue

        aspect_ratio = cw / ch

        # 🔍 filtro tipo display digital
        if 2 < aspect_ratio < 6 and 80 < cw < 500 and 30 < ch < 200:
            candidates.append((x, y, cw, ch))

    if not candidates:
        return None

    # elegir el más ancho
    x, y, cw, ch = max(candidates, key=lambda c: c[2])

    return img[y:y+ch, x:x+cw]

def extract_km(text):
    match = re.search(r'\d{5,7}', text)
    return int(match.group()) if match else None

def process_image(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 🔥 2. detectar ROI
    roi = find_odometer_roi(img)

    if roi is None:
        return {
            "km": None,
            "error": "No se detectó odómetro"
        }

    processed = preprocess(roi)

    # 🔥 3. OCR optimizado
    text = pytesseract.image_to_string(
        processed,
        config='--psm 7 -c tessedit_char_whitelist=0123456789'
    )

    km = extract_km(text)

    return {
        "km": km,
        "raw_text": text.strip()
    }