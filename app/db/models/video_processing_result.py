
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class VideoProcessingResult(Base):
    __tablename__ = "video_processing_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_request_id = Column(UUID(as_uuid=True), ForeignKey("video_requests.id"))
    title = Column(String)
    duration_seconds = Column(Integer)
    processed_at = Column(DateTime, default=func.now())
