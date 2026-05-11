from fastapi import FastAPI, status
import logging
from src.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from shared.telemetry import setup_telemetry_logger, TelemetryMiddleware
from prometheus_client import make_asgi_app

logger = setup_telemetry_logger("api-gateway")

app = FastAPI(
    title="API Gateway - Architecture Analyzer",
    description="Ponto de entrada único para o upload e consulta de análise de arquitetura",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Adiciona o Middleware de Telemetria / Monitoramento
app.add_middleware(TelemetryMiddleware, service_name="api-gateway")

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

