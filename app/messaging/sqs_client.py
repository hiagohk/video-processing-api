import json
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import (
    AWS_REGION,
    SQS_QUEUE_URL,
    DLQ_QUEUE_URL,
    AWS_ENDPOINT_URL,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
)

from app.exceptions.queue import (
    QueueReceiveError,
    QueueDeleteError,
    QueuePublishError,
    InvalidQueueMessageError,
)

logger = logging.getLogger(__name__)


class SQSClient:
    def __init__(self):
        self.queue_url = SQS_QUEUE_URL
        self.dlq_url = DLQ_QUEUE_URL
        self.sqs = boto3.client(
            "sqs",
            region_name=AWS_REGION,
            endpoint_url=AWS_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    # ----------------------------
    # Receber mensagens
    # ----------------------------
    def receive_message(self, max_messages: int = 1, wait_time: int = 10):
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
            )
            messages = response.get("Messages", [])
            # Deserializa JSON automaticamente
            for msg in messages:
                try:
                    msg["Body"] = json.loads(msg["Body"])
                except json.JSONDecodeError:
                    logger.warning("Invalid message body, moving to DLQ", extra={"body": msg["Body"]})
                    self.send_to_dlq({"raw_message": msg["Body"]})
                    self.delete_message(msg["ReceiptHandle"])
                    raise InvalidQueueMessageError()
            return messages
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to receive messages from SQS")
            raise QueueReceiveError() from e

    # ----------------------------
    # Deletar mensagens
    # ----------------------------
    def delete_message(self, receipt_handle: str):
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            logger.info("Deleted message from queue", extra={"receipt_handle": receipt_handle})
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to delete message from SQS")
            raise QueueDeleteError() from e

    # ----------------------------
    # Enviar mensagem
    # ----------------------------
    def send_message(self, body: dict, delay_seconds: int = 0):
        try:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(body),
                DelaySeconds=delay_seconds,
            )
            logger.info("Sent message to SQS", extra={"body": body})
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to send message to SQS")
            raise QueuePublishError() from e

    # ----------------------------
    # Enviar para DLQ
    # ----------------------------
    def send_to_dlq(self, body: dict):
        try:
            self.sqs.send_message(
                QueueUrl=self.dlq_url,
                MessageBody=json.dumps(body),
            )
            logger.error("Sent message to DLQ", extra={"body": body})
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to send message to DLQ")
            raise QueuePublishError() from e