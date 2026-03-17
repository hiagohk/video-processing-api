import json
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.exceptions.queue import (
    InvalidQueueMessageError,
    QueueDeleteError,
    QueuePublishError,
    QueueReceiveError,
)
from app.messaging.sqs_client import SQSClient

VIDEO_MESSAGE = {
    "video_request_id": "547026cb-c6b4-4d10-af7e-c2a65236b918",
    "video_url": "https://example.com/video.mp4",
    "retries": 0,
}


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def mock_sqs(mocker):
    mock = MagicMock()
    mocker.patch("app.messaging.sqs_client.boto3.client", return_value=mock)
    return mock


@pytest.fixture
def client(mock_sqs):
    return SQSClient()


def build_message(body):
    return {
        "ReceiptHandle": "abc",
        "Body": body,
    }


# ----------------------------
# receive_message
# ----------------------------
def test_receive_message_success(client, mock_sqs):

    mock_sqs.receive_message.return_value = {
        "Messages": [build_message(json.dumps(VIDEO_MESSAGE))]
    }

    messages = client.receive_message()

    assert messages[0]["Body"]["video_url"] == VIDEO_MESSAGE["video_url"]
    mock_sqs.receive_message.assert_called_once()


def test_receive_message_invalid_json(client, mocker, mock_sqs):

    mock_sqs.receive_message.return_value = {
        "Messages": [build_message("invalid-json")]
    }

    dlq = mocker.patch.object(client, "send_to_dlq")
    delete = mocker.patch.object(client, "delete_message")

    with pytest.raises(InvalidQueueMessageError):
        client.receive_message()

    dlq.assert_called_once()
    delete.assert_called_once_with("abc")


def test_receive_message_boto_error(client, mock_sqs):

    mock_sqs.receive_message.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "receive_message"
    )

    with pytest.raises(QueueReceiveError):
        client.receive_message()


# ----------------------------
# delete_message
# ----------------------------
def test_delete_message_success(client, mock_sqs):

    client.delete_message("abc")

    mock_sqs.delete_message.assert_called_once_with(
        QueueUrl=client.queue_url,
        ReceiptHandle="abc",
    )


def test_delete_message_error(client, mock_sqs):

    mock_sqs.delete_message.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "delete_message"
    )

    with pytest.raises(QueueDeleteError):
        client.delete_message("abc")


# ----------------------------
# send_message
# ----------------------------
def test_send_message_success(client, mock_sqs):

    client.send_message(VIDEO_MESSAGE)

    mock_sqs.send_message.assert_called_once()

    args = mock_sqs.send_message.call_args[1]

    assert args["QueueUrl"] == client.queue_url
    assert json.loads(args["MessageBody"]) == VIDEO_MESSAGE


def test_send_message_error(client, mock_sqs):

    mock_sqs.send_message.side_effect = ClientError(
        {"Error": {"Code": "500"}}, "send_message"
    )

    with pytest.raises(QueuePublishError):
        client.send_message(VIDEO_MESSAGE)


# ----------------------------
# send_to_dlq
# ----------------------------
def test_send_to_dlq_success(client, mock_sqs):

    client.send_to_dlq(VIDEO_MESSAGE)

    mock_sqs.send_message.assert_called_once()

    args = mock_sqs.send_message.call_args[1]

    assert args["QueueUrl"] == client.dlq_url
    assert json.loads(args["MessageBody"]) == VIDEO_MESSAGE