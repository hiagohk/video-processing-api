import pytest
from unittest.mock import MagicMock
from app.services.video_service import create_video


def test_create_video_success(mocker):

    db = MagicMock()

    mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=None
    )

    req = MagicMock()
    req.id = "123"

    mocker.patch(
        "app.services.video_service.create_video_request",
        return_value=req
    )

    send = mocker.patch(
        "app.services.video_service.sqs_client.send_message"
    )

    result = create_video(db, "video.mp4", "abc")

    assert result == req
    send.assert_called_once()


def test_create_video_idempotent(mocker):

    db = MagicMock()

    existing = MagicMock()
    existing.id = "existing"

    mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=existing
    )

    result = create_video(db, "video.mp4", "same-key")

    assert result == existing


def test_create_video_queue_error(mocker):

    db = MagicMock()

    mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=None
    )

    req = MagicMock()
    req.id = "123"

    mocker.patch(
        "app.services.video_service.create_video_request",
        return_value=req
    )

    mocker.patch(
        "app.services.video_service.sqs_client.send_message",
        side_effect=Exception("queue error")
    )

    with pytest.raises(Exception):
        create_video(db, "video.mp4", "key")


def test_create_video_calls_repository(mocker):

    db = MagicMock()

    find = mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=None
    )

    create = mocker.patch(
        "app.services.video_service.create_video_request"
    )

    mocker.patch(
        "app.services.video_service.sqs_client.send_message"
    )

    create_video(db, "video.mp4", "key")

    find.assert_called_once()
    create.assert_called_once()


def test_create_video_sends_sqs(mocker):

    db = MagicMock()

    mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=None
    )

    req = MagicMock()
    req.id = "abc"

    mocker.patch(
        "app.services.video_service.create_video_request",
        return_value=req
    )

    send = mocker.patch(
        "app.services.video_service.sqs_client.send_message"
    )

    create_video(db, "video.mp4", "key")

    send.assert_called_once()


def test_create_video_returns_existing(mocker):

    db = MagicMock()

    existing = MagicMock()
    existing.id = "xyz"

    mocker.patch(
        "app.services.video_service.find_by_idempotency",
        return_value=existing
    )

    result = create_video(db, "video.mp4", "key")

    assert result.id == "xyz"