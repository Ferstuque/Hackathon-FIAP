import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user_upload:password_upload@localhost:5432/upload_db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class UploadProcessModel(Base):
    __tablename__ = "upload_processes"
    process_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseAdapter:
    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_process(self, process_id: str, filename: str, status: str):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                new_process = UploadProcessModel(
                    process_id=process_id, 
                    filename=filename, 
                    status=status
                )
                session.add(new_process)

    async def update_status(self, process_id: str, status: str):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                process = await session.get(UploadProcessModel, process_id)
                if process:
                    process.status = status

    async def get_process(self, process_id: str):
        async with AsyncSessionLocal() as session:
            result = await session.get(UploadProcessModel, process_id)
            return result
