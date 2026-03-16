from .base import AppError


class QueueError(AppError):
    error_code = "queue_error"
    http_status = 500


class QueuePublishError(QueueError):
    error_code = "queue_publish_failed"
    message = "Failed to publish message to queue"


class QueueReceiveError(QueueError):
    error_code = "queue_receive_failed"
    message = "Failed to receive message from queue"


class QueueDeleteError(QueueError):
    error_code = "queue_delete_failed"
    message = "Failed to delete message from queue"


class InvalidQueueMessageError(QueueError):
    error_code = "invalid_queue_message"
    http_status = 400
    message = "Invalid queue message payload"