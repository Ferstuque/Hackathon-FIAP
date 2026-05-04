import httpx
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from shared.schemas import AnalysisStatus, TechnicalReport

api_router = APIRouter()

# URLs dos serviços internos (definidas no docker-compose)
UPLOAD_SERVICE_URL = os.getenv("UPLOAD_SERVICE_URL", "http://upload-service:8001")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://report-service:8003")

@api_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_diagram(file: UploadFile = File(...)):
    """Recebe o diagrama e encaminha para o Upload Service."""
    async with httpx.AsyncClient() as client:
        # Repassa o arquivo para o microserviço de upload
        files = {"file": (file.filename, file.file, file.content_type)}
        response = await client.post(f"{UPLOAD_SERVICE_URL}/internal/upload", files=files)
        
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Erro no serviço de upload")
            
        return response.json()

@api_router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Consulta o status atual do processamento."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{UPLOAD_SERVICE_URL}/internal/status/{analysis_id}")
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
            
        return response.json()

@api_router.get("/report/{analysis_id}", response_model=TechnicalReport)
async def get_final_report(analysis_id: str):
    """Recupera o relatório técnico estruturado após a análise."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{REPORT_SERVICE_URL}/internal/reports/{analysis_id}")
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Relatório ainda não disponível ou ID inválido")
            
        return response.json()
