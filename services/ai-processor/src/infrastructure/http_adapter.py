import httpx
import os
import logging
from shared.schemas import AnalysisStatus, TechnicalReport

logger = logging.getLogger(__name__)

class HttpAdapter:
    def __init__(self):
        self.upload_service_url = os.getenv("UPLOAD_SERVICE_URL", "http://upload-service:8001")
        self.report_service_url = os.getenv("REPORT_SERVICE_URL", "http://report-service:8003")

    async def update_status(self, analysis_id: str, status: AnalysisStatus):
        """Notifica o serviço responsável (Upload/Status Service) sobre a mudança de estado."""
        async with httpx.AsyncClient() as client:
            try:
                # Dispara patch para atualizar via Upload Service (que tem o DB db_upload)
                await client.patch(f"{self.upload_service_url}/internal/status/{analysis_id}", json={"status": status.value})
                logger.info(f"Status do {analysis_id} atualizado para {status.value}")
            except Exception as e:
                logger.error(f"Falha ao atualizar status do {analysis_id}: {e}")

    async def send_to_report_service(self, analysis_id: str, report: TechnicalReport):
        """Dispara o JSON extraído guardrailed para a persistência no banco do Report Service."""
        async with httpx.AsyncClient() as client:
            payload = {
                "process_id": str(analysis_id),
                "report": report.model_dump(by_alias=True)
            }
            res = await client.post(f"{self.report_service_url}/internal/reports", json=payload)
            res.raise_for_status()
