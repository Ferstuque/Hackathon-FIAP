import json
import logging
from src.infrastructure.gemini_adapter import GeminiAdapter
from src.infrastructure.azure_adapter import AzureAdapter
from src.infrastructure.http_adapter import HttpAdapter
from shared.schemas import AnalysisStatus

logger = logging.getLogger(__name__)

class AnalyzeDiagramUseCase:
    def __init__(self, gemini: GeminiAdapter, storage: AzureAdapter, http_client: HttpAdapter):
        self.gemini = gemini
        self.storage = storage
        self.http = http_client

    async def execute(self, message):
        process_id = None
        try:
            # Pegando as infos da Queue
            payload = json.loads(message.content)
            process_id = payload["process_id"]
            filename = payload["filename"]
            blob_name = f"{process_id}-{filename}"
            mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"

            # 1. Notificar início do processamento
            logger.info(f"[{process_id}] Mudando status para PROCESSANDO...")
            await self.http.update_status(process_id, AnalysisStatus.PROCESSANDO)

            # 2. Obter imagem do Blob (AzureAdapter local)
            logger.info(f"[{process_id}] Fazendo download da Imagem...")
            image_data = await self.storage.get_blob_content(blob_name)

            # 3. Análise Multimodal via Gemini 3.1 Pro Preview
            logger.info(f"[{process_id}] Extraindo dados arquiteturais via IA...")
            report = await self.gemini.analyze_architecture(image_data, mime_type)

            # 4. Enviar para o Report Service (Persistência isolada do DB_REPORTS)
            logger.info(f"[{process_id}] Salvando relatório final...")
            await self.http.send_to_report_service(process_id, report)
            
            # 5. Finalizar status e consumir a mensagem com sucesso
            await self.http.update_status(process_id, AnalysisStatus.ANALISADO)
            await self.storage.delete_message(message)
            
            logger.info(f"[{process_id}] Análise concluída e gravada com sucesso.")

        except Exception as e:
            if process_id:
                await self.http.update_status(process_id, AnalysisStatus.ERRO)
            logger.error(f"Falha na IA ou integração: {e}")
