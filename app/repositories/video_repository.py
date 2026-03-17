
from app.db.models import VideoProcessingResult, VideoRequest


def find_by_idempotency(db, key):
    return db.query(VideoRequest).filter(VideoRequest.idempotency_key == key).first()

def create_video_request(db, url, key):
    req = VideoRequest(video_url=url, status="PENDING", idempotency_key=key)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

def update_status(db, req, status):
    req.status = status
    db.commit()

def save_result(db, request_id, title, duration):
    result = VideoProcessingResult(
        video_request_id=request_id,
        title=title,
        duration_seconds=duration
    )
    db.add(result)
    db.commit()
