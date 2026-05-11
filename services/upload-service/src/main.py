from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from src.infrastructure.azure_adapter import AzureAdapter
from src.infrastructure.db_adapter import DatabaseAdapter
from src.application.upload_use_case import UploadDiagramUseCase
from shared.telemetry import setup_telemetry_logger, TelemetryMiddleware
from prometheus_client import make_asgi_app
from shared.schemas import AnalysisStatus

logger = setup_telemetry_logger("upload-service")

app = FastAPI(title="Upload Service")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.add_middleware(TelemetryMiddleware, service_name="upload-service")

azure_adapter = AzureAdapter()
db_adapter = DatabaseAdapter()
upload_use_case = UploadDiagramUseCase(azure_adapter)

@app.on_event("startup")
async def startup_event():
    await db_adapter.init_db()

@app.post("/internal/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    content = await file.read()
    
    try:
        record = await upload_use_case.execute(file.filename, content)
        # Salva o status inicial no banco (db-upload)
        await db_adapter.save_process(str(record.id), record.filename, AnalysisStatus.RECEBIDO.value)
        
        return {
            "id": record.id,
            "filename": record.filename,
            "status": record.status.value,
            "created_at": record.created_at.isoformat()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/internal/status/{process_id}")
async def get_status(process_id: UUID):
    process = await db_adapter.get_process(str(process_id))
    if not process:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    
    return {
        "id": process.process_id,
        "filename": process.filename,
        "status": process.status,
        "created_at": process.created_at.isoformat()
    }

class StatusUpdate(BaseModel):
    status: AnalysisStatus

@app.patch("/internal/status/{process_id}")
async def patch_status(process_id: UUID, status_update: StatusUpdate):
    await db_adapter.update_status(str(process_id), status_update.status.value)
    return {"message": "Status atualizado com sucesso"}