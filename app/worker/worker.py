
import boto3, json, yt_dlp
from app.core.config import AWS_REGION, SQS_QUEUE_URL
from app.db.session import SessionLocal
from app.repositories.video_repository import update_status, save_result
from app.db.models import VideoRequest

sqs = boto3.client("sqs", region_name=AWS_REGION, endpoint_url="http://localstack:4566")

def process_video(url):
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["title"], info.get("duration", 0)

while True:

    messages = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )

    if "Messages" not in messages:
        continue

    message = messages["Messages"][0]
    body = json.loads(message["Body"])

    request_id = body["video_request_id"]
    url = body["video_url"]

    db = SessionLocal()

    req = db.query(VideoRequest).filter(VideoRequest.id == request_id).first()

    if req.status == "PROCESSED":
        sqs.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=message["ReceiptHandle"]
        )
        continue

    title, duration = process_video(url)

    save_result(db, request_id, title, duration)
    update_status(db, req, "PROCESSED")

    sqs.delete_message(
        QueueUrl=SQS_QUEUE_URL,
        ReceiptHandle=message["ReceiptHandle"]
    )
