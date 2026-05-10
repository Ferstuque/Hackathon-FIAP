import json
import httpx
import os
import logging
from src.infrastructure.azure_adapter import AzureAdapter
from src.infrastructure.gemini_adapter import GeminiAdapter
from shared.schemas import TechnicalReport

logger = logging.getLogger(__name__)
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://report-service:8003")
UPLOAD_SERVICE_URL = os.getenv("UPLOAD_SERVICE_URL", "http://upload-service:8001")

class ProcessorUseCase:
    def __init__(self, azure_adapter: AzureAdapter, gemini_adapter: GeminiAdapter):
        self.azure_adapter = azure_adapter
        self.gemini_adapter = gemini_adapter

    async def _update_status(self, process_id: str, status: str):
        async with httpx.AsyncClient() as client:
            try:
                await client.patch(
                    f"{UPLOAD_SERVICE_URL}/internal/status/{process_id}",
                    json={"status": status}
                )
            except Exception as e:
                logger.error(f"[{process_id}] Falha ao atualizar status para {status}: {e}")

    async def execute(self, message) -> bool:
        try:
            # 1. Decodificar mensagem da Queue
            payload = json.loads(message.content)
            process_id = payload["process_id"]
            filename = payload["filename"]
            
            # 1.1 Avaliar Status Inicial
            await self._update_status(process_id, "PROCESSANDO")
            
            # Determina o mimetype pelo final do arquivo
            mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"
            
            # 2. Download do Blob Storage
            blob_name = f"{process_id}-{filename}"
            logger.info(f"[{process_id}] Baixando blob {blob_name}...")
            image_bytes = await self.azure_adapter.get_blob_content(blob_name)
            
            # 3. Processamento via Gemini 3.1 Pro Preview (Core AI Workflow)
            logger.info(f"[{process_id}] Iniciando análise em lote via Gemini...")
            try:
                report: TechnicalReport = await self.gemini_adapter.analyze_architecture(image_bytes, mime_type)
            except Exception as ai_e:
                logger.error(f"[{process_id}] Falha na analise ({ai_e}), acionando Fallback...")
                report = self.gemini_adapter._get_fallback_report()
                
                # 3.1 Se acionou Fallback (Resiliência final), enviaremos cópia para a Dead Letter Queue (DLQ)
                logger.warning(f"[{process_id}] Enviando mensagem para a fila de mensagens mortas (DLQ) para investigação manual.")
                await self.azure_adapter.send_to_dlq({
                    "process_id": process_id,
                    "filename": filename,
                    "reason": str(ai_e)
                })
            
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
                    await self._update_status(process_id, "ERRO")
                    return False
            
            # 5. Sucesso: Remover mensagem da fila e atualizar status final
            await self.azure_adapter.delete_message(message)
            await self._update_status(process_id, "ANALISADO")
            logger.info(f"[{process_id}] Fluxo finalizado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do diagrama: {e}")
            await self._update_status(process_id, "ERRO")
            return False
