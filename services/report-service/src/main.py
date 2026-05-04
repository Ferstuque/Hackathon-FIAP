from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

from src.infrastructure.db_adapter import DatabaseAdapter
from src.application.report_use_case import SaveReportUseCase, GetReportUseCase
from shared.schemas import TechnicalReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_adapter = DatabaseAdapter()
save_use_case = SaveReportUseCase(db_adapter)
get_use_case = GetReportUseCase(db_adapter)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria a tabela de relatórios caso ela não exista
    await db_adapter.init_db()
    yield

app = FastAPI(title="Report Service", lifespan=lifespan)

class ReportPayload(BaseModel):
    process_id: str
    report: TechnicalReport

@app.post("/internal/reports", status_code=status.HTTP_201_CREATED)
async def create_report(payload: ReportPayload):
    """(Interno) Recebe do AI Processor o relatório final para gravar no banco do Report Service."""
    try:
        await save_use_case.execute(payload.process_id, payload.report)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro salvando o Report {payload.process_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Report DB Save Failed")

@app.get("/internal/reports/{process_id}", response_model=TechnicalReport)
async def fetch_report(process_id: str):
    """(Interno) Consultado pelo API Gateway durante chamadas GET /report/{analysis_id}"""
    report = await get_use_case.execute(process_id)
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report
