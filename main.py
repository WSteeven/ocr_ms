from fastapi import FastAPI
from pydantic import BaseModel
from app.ocr.service import extract_text

app = FastAPI(title="OCR Receipt Extractor", version="1.0.0")


class AnalyzeRequest(BaseModel):
    path: str


@app.post("/analyze")
def analyze(data: AnalyzeRequest):
    """Analyze a receipt image and extract structured data."""
    return extract_text(data.path)
