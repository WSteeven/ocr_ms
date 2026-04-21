from fastapi import FastAPI
from app.routes.ocr import router as ocr_router

app = FastAPI(title="OCR Service")

app.include_router(ocr_router, prefix="/api")