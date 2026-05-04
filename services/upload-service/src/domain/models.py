import uuid
from datetime import datetime
from shared.schemas import AnalysisStatus

class UploadRecord:
    def __init__(self, process_id: uuid.UUID, filename: str):
        self.id = process_id
        self.filename = filename
        self.status = AnalysisStatus.RECEBIDO
        self.created_at = datetime.utcnow()
        self.blob_url = None
