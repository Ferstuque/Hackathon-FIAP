import logging
from src.infrastructure.db_adapter import DatabaseAdapter
from shared.schemas import TechnicalReport

logger = logging.getLogger(__name__)

class SaveReportUseCase:
    def __init__(self, db: DatabaseAdapter):
        self.db = db

    async def execute(self, process_id: str, report: TechnicalReport):
        logger.info(f"Salvando o relatório da análise {process_id} no banco...")
        # Usa by_alias se quiser suportar names diferentes do Pydantic, caso contrario usa model_dump regular
        await self.db.save_report(process_id, report.model_dump(by_alias=True))
        return True

class GetReportUseCase:
    def __init__(self, db: DatabaseAdapter):
        self.db = db

    async def execute(self, process_id: str) -> TechnicalReport | None:
        data = await self.db.get_report(process_id)
        if data:
            return TechnicalReport(**data)
        return None

class GetAllReportsUseCase:
    def __init__(self, db: DatabaseAdapter):
        self.db = db

    async def execute(self) -> list[dict]:
        return await self.db.get_all_reports()