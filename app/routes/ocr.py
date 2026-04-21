from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import process_image

router = APIRouter()

@router.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, "Archivo inválido")
        
        
        contents = await file.read()
        result = process_image(contents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))