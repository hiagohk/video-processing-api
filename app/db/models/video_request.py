
import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class VideoRequest(Base):
    __tablename__ = "video_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_url = Column(String)
    status = Column(String)
    idempotency_key = Column(String, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())