import uuid
from src.infrastructure.azure_adapter import AzureAdapter
from src.domain.models import UploadRecord
import logging

logger = logging.getLogger(__name__)

class UploadDiagramUseCase:
    def __init__(self, azure_adapter: AzureAdapter):
        self.azure_adapter = azure_adapter

    async def execute(self, filename: str, content: bytes) -> UploadRecord:
        process_id = uuid.uuid4()
        record = UploadRecord(process_id=process_id, filename=filename)
        
        # 1. Salvar no Blob Storage
        blob_name = f"{process_id}-{filename}"
        blob_url = await self.azure_adapter.upload_blob(blob_name, content)
        record.blob_url = blob_url
        
        # 2. Enviar mensagem para a Queue
        queue_message = {
            "process_id": str(process_id),
            "blob_url": blob_url,
            "filename": filename
        }
        await self.azure_adapter.send_to_queue(queue_message)
        
        logger.info(f"Processo {process_id} iniciado. Arquivo no blob: {blob_url}")
        return record
