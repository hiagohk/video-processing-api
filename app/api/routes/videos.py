from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.video_schema import VideoCreate
from app.services.video_service import create_video

router = APIRouter()


@router.post("/videos")
def create(
    video: VideoCreate,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(alias="idempotency-key"),
):
    req = create_video(db, video.video_url, idempotency_key)

    return {
        "id": req.id,
        "status": req.status
    }