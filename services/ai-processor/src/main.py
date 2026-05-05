import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.infrastructure.azure_adapter import AzureAdapter
from src.infrastructure.gemini_adapter import GeminiAdapter
from src.infrastructure.http_adapter import HttpAdapter
from src.application.analyze_diagram_use_case import AnalyzeDiagramUseCase

from shared.telemetry import setup_telemetry_logger, TelemetryMiddleware
logger = setup_telemetry_logger("ai-processor")

azure_adapter = AzureAdapter()
gemini_adapter = GeminiAdapter()
http_adapter = HttpAdapter()
processor_use_case = AnalyzeDiagramUseCase(gemini_adapter, azure_adapter, http_adapter)

async def poll_queue():
    """Worker que roda em background buscando os itens na Azure Queue"""
    logger.info("Iniciando AI Processor - Escutando fila Azure Storage Queue...")
    while True:
        try:
            async for message in azure_adapter.receive_messages():
                await processor_use_case.execute(message)
        except Exception as e:
            logger.error(f"Erro no polling loop: {e}")
        # Descansa por 5 segundos antes de buscar mais mensagens para não sobrecarregar as I/Os
        await asyncio.sleep(5) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Liga o background worker na inicialização da aplicação
    task = asyncio.create_task(poll_queue())
    yield
    # Desliga quando a aplicação FastAPI morre
    task.cancel()

app = FastAPI(
    title="AI Processor Worker",
    lifespan=lifespan
)

app.add_middleware(TelemetryMiddleware, service_name="ai-processor")

@app.get("/health")
async def health():
    return {"status": "Escutando mensagens da Fila"}
