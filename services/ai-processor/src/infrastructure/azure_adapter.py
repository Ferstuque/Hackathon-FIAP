import os
import json
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.queue.aio import QueueClient
import logging

logger = logging.getLogger(__name__)

AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING", 
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
)
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "diagrams")
QUEUE_NAME = os.getenv("QUEUE_NAME", "analysis-queue")

class AzureAdapter:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        self.queue_client = QueueClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, QUEUE_NAME)

    async def get_blob_content(self, filename: str) -> bytes:
        """Faz o download do arquivo a partir do Blob Storage"""
        async with self.blob_service_client:
            blob_client = self.blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
            stream = await blob_client.download_blob()
            return await stream.readall()
            
    async def receive_messages(self):
        """Busca imagens a processar na Fila"""
        async with self.queue_client:
            # Tolerância para criar fila caso ainda não exista
            try:
                await self.queue_client.create_queue()
            except Exception:
                pass
            
            messages = self.queue_client.receive_messages(max_messages=1)
            async for msg in messages:
                yield msg

    async def delete_message(self, msg):
        """Remove a mensagem da fila indicando sucesso do processamento"""
        async with self.queue_client:
            await self.queue_client.delete_message(msg)
