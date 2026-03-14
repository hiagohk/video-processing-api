
from app.repositories.video_repository import create_video_request, find_by_idempotency
from app.messaging.sqs_client import send_message

def create_video(db, url, key):

    existing = find_by_idempotency(db, key)
    if existing:
        return existing

    req = create_video_request(db, url, key)

    send_message({
        "video_request_id": str(req.id),
        "video_url": url
    })

    return req
