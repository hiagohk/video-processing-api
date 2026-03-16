
import boto3, json
from app.core.config import AWS_REGION, SQS_QUEUE_URL, AWS_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def send_message(payload):
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(payload)
    )
