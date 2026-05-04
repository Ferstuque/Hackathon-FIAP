import pytest
from unittest.mock import AsyncMock, patch
from src.application.upload_use_case import UploadDiagramUseCase

@pytest.mark.asyncio
class TestUploadDiagramUseCase:
    
    async def test_execute_failure_on_blob_upload(self):
        """Erro 1: Falha ao persistir arquivo no Azure Blob Storage."""
        mock_adapter = AsyncMock()
        mock_adapter.upload_blob.side_effect = Exception("Connection Timeout")

        use_case = UploadDiagramUseCase(mock_adapter)
        
        with pytest.raises(Exception) as excinfo:
            await use_case.execute("diagrama.png", b"conteudo_fake")
        
        assert "Connection Timeout" in str(excinfo.value)
        # Garante que a fila NÃO foi notificada se o upload falhou
        mock_adapter.send_to_queue.assert_not_called()

    async def test_execute_failure_on_queue_message(self):
        """Erro 2: Arquivo salvo, mas falha ao postar na fila assíncrona."""
        mock_adapter = AsyncMock()
        mock_adapter.upload_blob.return_value = "http://localhost:10000/devstoreaccount1/diagrams/diagrama.png"
        mock_adapter.send_to_queue.side_effect = Exception("Queue Unavailable")
        
        use_case = UploadDiagramUseCase(mock_adapter)

        with pytest.raises(Exception) as excinfo:
            await use_case.execute("diagrama.png", b"conteudo_fake")
        
        assert "Queue Unavailable" in str(excinfo.value)
        # Garante que o blob foi feito antes da falha
        mock_adapter.upload_blob.assert_called_once()
