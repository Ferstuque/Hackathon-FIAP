import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.application.analyze_diagram_use_case import AnalyzeDiagramUseCase
from shared.schemas import AnalysisStatus, TechnicalReport, ArchitectureComponent

@pytest.fixture
def mock_sqs_message():
    message = MagicMock()
    message.content = json.dumps({
        "process_id": "1234-abcd",
        "filename": "diagrama.png"
    })
    return message

@pytest.fixture
def mock_technical_report():
    return TechnicalReport(
        identified_components=[],
        architectural_risks=["Spof"],
        recommendations=["Use Load Balancer"],
        confidence_score=0.9
    )

@pytest.mark.asyncio
class TestAnalyzeDiagramUseCase:
    
    async def test_execute_success(self, mock_sqs_message, mock_technical_report):
        """Teste de Fluxo Feliz: Desenha o ciclo completo, da queue à persistencia no Report."""
        mock_gemini = AsyncMock()
        mock_gemini.extract_architecture_facts.return_value = "fatos arquiteturais"
        mock_gemini.generate_report_from_facts.return_value = mock_technical_report
        
        mock_storage = AsyncMock()
        mock_storage.get_blob_content.return_value = b"fake_image_bytes"
        
        mock_http = AsyncMock()
        
        use_case = AnalyzeDiagramUseCase(mock_gemini, mock_storage, mock_http)
        
        # Ação
        await use_case.execute(mock_sqs_message)
        
        # Verifica se o status mudou para PROCESSANDO primeiro
        mock_http.update_status.assert_any_call("1234-abcd", AnalysisStatus.PROCESSANDO)
        
        # Verifica chamadas sequenciais
        mock_gemini.extract_architecture_facts.assert_called_once_with(b"fake_image_bytes", "image/jpeg")
        mock_gemini.generate_report_from_facts.assert_called_once_with("fatos arquiteturais", b"fake_image_bytes", "image/jpeg")
        
        # Verifica se enviou o relatório pro report_service

        mock_http.send_to_report_service.assert_called_once_with("1234-abcd", mock_technical_report)
        
        # Verifica trâmite final: ANALISADO e remoção da fila
        mock_http.update_status.assert_any_call("1234-abcd", AnalysisStatus.ANALISADO)
        mock_storage.delete_message.assert_called_once_with(mock_sqs_message)

    async def test_execute_failure_during_analysis(self, mock_sqs_message):
        """Erro 1: Falha na IA - Garante que o status no Gateway do DB reflita o erro."""
        mock_gemini = AsyncMock()
        mock_gemini.extract_architecture_facts.side_effect = Exception("API Unavailable")
        
        mock_storage = AsyncMock()

        mock_storage.get_blob_content.return_value = b"fake_image_bytes"
        
        mock_http = AsyncMock()
        
        use_case = AnalyzeDiagramUseCase(mock_gemini, mock_storage, mock_http)
        
        # Ação
        await use_case.execute(mock_sqs_message)
        
        # O Workflow deve absorver o Erro, e repassar com update para a Controller
        mock_http.update_status.assert_called_with("1234-abcd", AnalysisStatus.ERRO)
        
        # O arquivo NÃO deve ser apagado da Queue se deu erro crítico de infraestrutura (pra tentar novamente depois ou colocar na Dead Letter Queue)
        mock_storage.delete_message.assert_not_called()