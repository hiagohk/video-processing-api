import concurrent.futures
import json
import logging
import time
from typing import Dict, List

import yt_dlp
from sqlalchemy.orm import Session

from app.db.models import VideoRequest
from app.db.session import SessionLocal
from app.exceptions.video import VideoDownloadError, VideoProcessingError
from app.messaging.sqs_client import SQSClient
from app.repositories.video_repository import save_result, update_status

logger = logging.getLogger(__name__)
sqs = SQSClient()

MAX_RETRIES = 3
PROCESSING_TIMEOUT = 60
POLL_INTERVAL = 2


def retry_with_backoff(fn, *args, retries: int = MAX_RETRIES, base_delay: int = 2):
    for attempt in range(1, retries + 1):
        try:
            return fn(*args)
        except VideoDownloadError as e:
            if attempt == retries:
                raise
            delay = base_delay**attempt
            logger.warning(
                "Retrying video processing",
                extra={
                    "attempt": attempt,
                    "delay": delay,
                    "context": getattr(e, "context", {}),
                },
            )
            time.sleep(delay)


def run_with_timeout(fn, *args, timeout: int = PROCESSING_TIMEOUT):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args)
        return future.result(timeout=timeout)


def process_video(url: str):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        raise VideoDownloadError(context={"url": url}) from e
    except Exception as e:
        raise VideoProcessingError(context={"url": url}) from e

    title = info.get("title")
    if not title:
        raise VideoProcessingError("Missing video title", context={"url": url})

    duration = info.get("duration", 0)
    return title, duration


def handle_message(message: Dict):
    receipt = message["ReceiptHandle"]

    try:
        body = message["Body"]
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid message JSON")
        sqs.delete_message(receipt_handle=receipt)
        return

    request_id = body.get("video_request_id")
    url = body.get("video_url")
    retries = body.get("retries", 0)

    db: Session = SessionLocal()
    try:
        req = db.query(VideoRequest).filter(VideoRequest.id == request_id).first()
        if not req:
            logger.warning("Video request not found", extra={"request_id": request_id})
            sqs.delete_message(receipt_handle=receipt)
            return

        # Idempotência
        if req.status == "PROCESSED":
            logger.info("Video already processed", extra={"request_id": request_id})
            sqs.delete_message(receipt_handle=receipt)
            return

        # Processamento
        try:
            title, duration = run_with_timeout(
                retry_with_backoff,
                process_video,
                url,
            )

            save_result(db, request_id, title, duration)
            update_status(db, req, "PROCESSED")

            logger.info(
                "Video processed",
                extra={"request_id": request_id, "title": title},
            )

        except Exception:
            logger.warning(
                "Video processing failed",
                extra={"request_id": request_id, "retries": retries},
            )

            if retries >= MAX_RETRIES:
                update_status(db, req, "FAILED")
                sqs.send_to_dlq({"video_request_id": request_id, "video_url": url})
            else:
                sqs.send_message(
                    {"video_request_id": request_id, "video_url": url, "retries": retries + 1}
                )

    finally:
        db.close()
        sqs.delete_message(receipt_handle=receipt)


def worker_loop():
    logger.info("Worker started")
    while True:
        messages: List[Dict] = sqs.receive_message(max_messages=1, wait_time=10)
        if not messages:
            time.sleep(POLL_INTERVAL)
            continue

        for message in messages:
            handle_message(message)


if __name__ == "__main__":
    worker_loop()
