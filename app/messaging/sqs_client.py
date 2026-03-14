
import boto3, json
from app.core.config import AWS_REGION, SQS_QUEUE_URL

sqs = boto3.client("sqs", region_name=AWS_REGION, endpoint_url="http://localstack:4566")

def send_message(payload):
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(payload)
    )
