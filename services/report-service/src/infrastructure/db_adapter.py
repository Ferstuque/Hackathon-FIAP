import os
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/db_reports")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class ReportModel(Base):
    __tablename__ = "reports"
    process_id = Column(String, primary_key=True, index=True)
    report_data = Column(JSONB, nullable=False)

class DatabaseAdapter:
    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_report(self, process_id: str, report_data: dict):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_report = ReportModel(process_id=process_id, report_data=report_data)
                session.add(new_report)

    async def get_report(self, process_id: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.get(ReportModel, process_id)
            if result:
                return result.report_data
            return None
