#!/usr/bin/env python3
"""
Test script to verify OCR text extraction for Produbanco and Pichincha receipts.
"""

import sys

sys.path.insert(0, "/home/steeven/Documents/ocr_ms")

from app.ocr.parser import (
    parse_receipt,
    extract_amount,
    extract_date,
    extract_recipient,
    extract_description,
)
from app.ocr.utils import normalize_text, detect_bank


# Sample data from the images
PRODUBANCO_SAMPLE = """
Transferencia local
Produbanco Grupo Promerica
Transferencia exitosa
$70.00
Mto Veh 7423 Banda
Martes 27 Ene. 2026 - 02:20 pm
Terceros Produbanco
Comprobante Nro. 101174880
Para: Aguilar Fernandez Pedro Moroni
Produbanco
Ahorros Nro. 1•••••••729
De: Solange Carolina Romero
Cuenta Digital Nro. 2•••••••713
"""

PICHINCHA_SAMPLE = """
BANCO PICHINCHA
¡Transferencia exitosa!
$30.00
A Orellana Marca John David
El 09 de marzo de 2026
De Orellana Fernandez Ashley Milena
Cuenta destino •••••0253
Banco destino Banco Pichincha
Cuenta origen 220 905 4350
N° de comprobante 138276502
Verificar la transacción con este QR
"""


def test_extraction(name: str, sample_text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"{'=' * 60}")

    # Detect bank
    bank = detect_bank(sample_text)
    print(f"✓ Detected Bank: {bank.upper()}")

    # Normalize text
    normalized = normalize_text(sample_text)
    print(f"\n✓ Normalized Text:\n{normalized[:200]}...")

    # Extract fields
    print("\n📊 Extracted Fields:")

    monto, c_monto = extract_amount(normalized)
    if monto is not None:
        print(f"  • Amount (Monto): ${monto:.2f}")
    else:
        print("  • Amount (Monto): NOT FOUND")
    print(f"    Confidence: {c_monto:.2f}")

    fecha, c_fecha = extract_date(normalized)
    if fecha is not None:
        print(f"  • Date (Fecha): {fecha}")
    else:
        print("  • Date (Fecha): NOT FOUND")
    print(f"    Confidence: {c_fecha:.2f}")

    # Extract recipient from RAW text (before normalization)
    destinatario, c_dest = extract_recipient(sample_text)
    if destinatario is not None:
        print(f"  • Recipient (Destinatario): {destinatario}")
    else:
        print("  • Recipient (Destinatario): NOT FOUND")
    print(f"    Confidence: {c_dest:.2f}")

    # Mock data structure for description extraction
    lines = sample_text.split("\n")
    mock_data = {
        "rec_texts": lines,
        "rec_boxes": [
            [[0, i * 50, 100, i * 50 + 30], [0, i * 50], [100, i * 50 + 30], [100, i * 50]]
            for i in range(len(lines))
        ],
        "rec_scores": [0.95] * len(lines),
    }

    descripcion, c_desc = extract_description(mock_data, sample_text)
    if descripcion is not None:
        print(f"  • Description (Descripción): {descripcion}")
    else:
        print("  • Description (Descripción): NOT FOUND")
    print(f"    Confidence: {c_desc:.2f}")

    # Parse full receipt (extracts recipient from raw text internally)
    parsed = parse_receipt(sample_text)

    print("\n✅ Final Parsed Receipt:")
    print(f"  Monto: {parsed['monto']}")
    print(f"  Fecha: {parsed['fecha']}")
    print(f"  Destinatario: {parsed['destinatario']}")
    print(f"  Descripción: {parsed['descripcion']}")
    print(f"  Confidence: {parsed['confidence']:.2f}")


if __name__ == "__main__":
    test_extraction("PRODUBANCO", PRODUBANCO_SAMPLE)
    test_extraction("BANCO PICHINCHA", PICHINCHA_SAMPLE)

    print(f"\n{'=' * 60}")
    print("✨ Test Complete!")
    print(f"{'=' * 60}\n")
