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

    async def upload_blob(self, filename: str, data: bytes) -> str:
        async with self.blob_service_client:
            container_client = self.blob_service_client.get_container_client(CONTAINER_NAME)
            try:
                await container_client.create_container()
            except Exception:
                pass # Already exists
            blob_client = container_client.get_blob_client(filename)
            await blob_client.upload_blob(data, overwrite=True)
            return blob_client.url

    async def send_to_queue(self, message: dict):
        async with self.queue_client:
            try:
                await self.queue_client.create_queue()
            except Exception:
                pass
            msg_str = json.dumps(message)
            await self.queue_client.send_message(msg_str)
