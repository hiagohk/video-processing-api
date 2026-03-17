from sqlalchemy.orm import Session

from app.exceptions.queue import QueuePublishError
from app.messaging.sqs_client import SQSClient
from app.repositories.video_repository import create_video_request, find_by_idempotency

# Criar instância global do cliente SQS
sqs_client = SQSClient()


def create_video(db: Session, url: str, key: str):

    # Checar se já existe requisição com a mesma idempotência
    existing = find_by_idempotency(db, key)
    if existing:
        return existing

    # Criar nova requisição
    req = create_video_request(db, url, key)

    try:
        # Enviar para a fila SQS usando o SQSClient
        sqs_client.send_message(
            {
                "video_request_id": str(req.id),
                "video_url": url,
                "retries": 0,  # inicializa contagem de retries
            }
        )
    except Exception as e:
        db.rollback()
        raise QueuePublishError(context={"video_request_id": str(req.id)}) from e

    return req
