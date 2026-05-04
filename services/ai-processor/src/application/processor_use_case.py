import json
import httpx
import os
import logging
from src.infrastructure.azure_adapter import AzureAdapter
from src.infrastructure.gemini_adapter import GeminiAdapter
from shared.schemas import TechnicalReport

logger = logging.getLogger(__name__)
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://report-service:8003")

class ProcessorUseCase:
    def __init__(self, azure_adapter: AzureAdapter, gemini_adapter: GeminiAdapter):
        self.azure_adapter = azure_adapter
        self.gemini_adapter = gemini_adapter

    async def execute(self, message) -> bool:
        try:
            # 1. Decodificar mensagem da Queue
            payload = json.loads(message.content)
            process_id = payload["process_id"]
            filename = payload["filename"]
            
            # Determina o mimetype pelo final do arquivo
            mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"
            
            # 2. Download do Blob Storage
            blob_name = f"{process_id}-{filename}"
            logger.info(f"[{process_id}] Baixando blob {blob_name}...")
            image_bytes = await self.azure_adapter.get_blob_content(blob_name)
            
            # 3. Processamento via Gemini 3.1 Pro Preview (Core AI Workflow)
            logger.info(f"[{process_id}] Iniciando análise em lote via Gemini...")
            report: TechnicalReport = await self.gemini_adapter.analyze_architecture(image_bytes, mime_type)
            
            # 4. Enviar relatório consolidado para o Report Service
            logger.info(f"[{process_id}] Análise concluída [Score {report.confidence_score}]. Salvando laudo...")
            async with httpx.AsyncClient() as client:
                data_to_send = {
                    "process_id": process_id,
                    "report": report.model_dump()
                }
                res = await client.post(f"{REPORT_SERVICE_URL}/internal/reports", json=data_to_send)
                if res.status_code not in (200, 201):
                    logger.error(f"Falha ao enviar para o Repor Service. HTTP: {res.status_code}")
                    return False
            
            # 5. Sucesso: Remover mensagem da fila
            await self.azure_adapter.delete_message(message)
            logger.info(f"[{process_id}] Fluxo finalizado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do diagrama: {e}")
            return False
