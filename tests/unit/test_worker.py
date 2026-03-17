import json
from unittest.mock import MagicMock

from app.exceptions.video import VideoDownloadError
from app.worker.worker import (
    handle_message,
    process_video,
    retry_with_backoff,
    run_with_timeout,
)


def test_retry_with_backoff_success():

    fn = MagicMock(return_value="ok")

    result = retry_with_backoff(fn)

    assert result == "ok"
    fn.assert_called_once()


def test_retry_with_backoff_retry_success(mocker):

    fn = MagicMock(side_effect=[VideoDownloadError(context={}), "success"])

    sleep = mocker.patch("app.worker.worker.time.sleep")

    result = retry_with_backoff(fn)

    assert result == "success"
    assert fn.call_count == 2
    sleep.assert_called_once()


def test_run_with_timeout_success():

    fn = MagicMock(return_value="done")

    result = run_with_timeout(fn)

    assert result == "done"


def test_process_video_success(mocker):

    fake_info = {"title": "Test Video", "duration": 120}

    ydl_mock = MagicMock()
    ydl_mock.extract_info.return_value = fake_info

    mocker.patch(
        "app.worker.worker.yt_dlp.YoutubeDL",
        return_value=MagicMock(__enter__=lambda s: ydl_mock, __exit__=lambda *a: None),
    )

    title, duration = process_video("http://video.com")

    assert title == "Test Video"
    assert duration == 120


def test_handle_message_success(mocker):

    message = {
        "ReceiptHandle": "abc",
        "Body": json.dumps(
            {"video_request_id": "1", "video_url": "http://video.com", "retries": 0}
        ),
    }

    db = MagicMock()
    req = MagicMock()
    req.status = "PENDING"

    mocker.patch("app.worker.worker.SessionLocal", return_value=db)
    db.query.return_value.filter.return_value.first.return_value = req

    mocker.patch("app.worker.worker.run_with_timeout", return_value=("title", 100))
    save = mocker.patch("app.worker.worker.save_result")
    update = mocker.patch("app.worker.worker.update_status")
    delete = mocker.patch("app.worker.worker.sqs.delete_message")

    handle_message(message)

    save.assert_called_once()
    update.assert_called_once()
    delete.assert_called_once()


def test_handle_message_retry(mocker):

    message = {
        "ReceiptHandle": "abc",
        "Body": json.dumps(
            {"video_request_id": "1", "video_url": "http://video.com", "retries": 1}
        ),
    }

    db = MagicMock()
    req = MagicMock()
    req.status = "PENDING"

    mocker.patch("app.worker.worker.SessionLocal", return_value=db)
    db.query.return_value.filter.return_value.first.return_value = req

    mocker.patch("app.worker.worker.run_with_timeout", side_effect=Exception("fail"))

    send = mocker.patch("app.worker.worker.sqs.send_message")
    delete = mocker.patch("app.worker.worker.sqs.delete_message")

    handle_message(message)

    send.assert_called_once()
    delete.assert_called_once()
