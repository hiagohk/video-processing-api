
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.schemas.video_schema import VideoCreate
from app.db.session import SessionLocal
from app.services.video_service import create_video

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/videos")
def create(video: VideoCreate, db: Session = Depends(get_db), idempotency_key: str = Header(None)):
    req = create_video(db, video.video_url, idempotency_key)
    return {"id": req.id, "status": req.status}
