
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class VideoRequest(Base):
    __tablename__ = "video_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_url = Column(String)
    status = Column(String)
    idempotency_key = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class VideoProcessingResult(Base):
    __tablename__ = "video_processing_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_request_id = Column(UUID(as_uuid=True), ForeignKey("video_requests.id"))
    title = Column(String)
    duration_seconds = Column(Integer)
    processed_at = Column(DateTime, default=func.now())
