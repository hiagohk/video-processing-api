import uuid

from app.repositories.video_repository import (
    find_by_idempotency,
    create_video_request,
    update_status,
    save_result,
)

from app.db.models import VideoRequest, VideoProcessingResult


def test_create_video_request(db_session):

    url = "https://example.com/video.mp4"
    key = str(uuid.uuid4())

    req = create_video_request(db_session, url, key)

    assert req.id is not None
    assert req.video_url == url
    assert req.status == "PENDING"
    assert req.idempotency_key == key


def test_find_by_idempotency(db_session):

    url = "https://example.com/video.mp4"
    key = str(uuid.uuid4())

    created = create_video_request(db_session, url, key)

    result = find_by_idempotency(db_session, key)

    assert result.id == created.id
    assert result.video_url == url


def test_find_by_idempotency_not_found(db_session):

    result = find_by_idempotency(db_session, "non-existent-key")

    assert result is None


def test_update_status(db_session):

    req = create_video_request(
        db_session,
        "https://example.com/video.mp4",
        str(uuid.uuid4()),
    )

    update_status(db_session, req, "PROCESSED")

    updated = db_session.query(VideoRequest).filter(VideoRequest.id == req.id).first()

    assert updated.status == "PROCESSED"


def test_save_result(db_session):

    req = create_video_request(
        db_session,
        "https://example.com/video.mp4",
        str(uuid.uuid4()),
    )

    save_result(
        db_session,
        request_id=req.id,
        title="Example Video",
        duration=120,
    )

    result = (
        db_session.query(VideoProcessingResult)
        .filter(VideoProcessingResult.video_request_id == req.id)
        .first()
    )

    assert result.title == "Example Video"
    assert result.duration_seconds == 120