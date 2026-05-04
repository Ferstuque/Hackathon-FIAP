from fastapi import FastAPI, status
import logging
from src.api.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway - Architecture Analyzer",
    description="Ponto de entrada único para o upload e consulta de análise de arquitetura",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

