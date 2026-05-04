from pydantic import BaseModel
from shared.schemas import TechnicalReport

class ReportRecord(BaseModel):
    process_id: str
    report_data: TechnicalReport
