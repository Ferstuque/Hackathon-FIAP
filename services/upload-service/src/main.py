from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from src.infrastructure.azure_adapter import AzureAdapter
from src.application.upload_use_case import UploadDiagramUseCase
from shared.schemas import AnalysisProcess, AnalysisStatus

app = FastAPI(title="Upload Service")

azure_adapter = AzureAdapter()
upload_use_case = UploadDiagramUseCase(azure_adapter)

@app.post("/internal/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    content = await file.read()
    
    try:
        record = await upload_use_case.execute(file.filename, content)
        # Em um cenário real, persistir o record no banco (db_upload)
        
        return {
            "id": record.id,
            "filename": record.filename,
            "status": record.status.value,
            "created_at": record.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/internal/status/{process_id}")
async def get_status(process_id: UUID):
    # Mock para MVP
    return {
        "id": process_id,
        "status": AnalysisStatus.RECEBIDO.value
    }