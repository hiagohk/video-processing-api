import time

import boto3
import pytest
import requests
from botocore.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():

    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_sqs():
    sqs = boto3.client(
        "sqs",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(
            signature_version="v4",
            retries={"max_attempts": 3},
        ),
    )

    # espera o LocalStack ficar pronto
    for _ in range(20):
        try:
            health = requests.get("http://localhost:4566/_localstack/health").json()
            if health.get("services", {}).get("sqs") == "running":
                break
        except Exception:
            pass
        time.sleep(3)

    # cria filas (idempotente)
    sqs.create_queue(QueueName="video-processing-queue")
    sqs.create_queue(QueueName="video-processing-dlq")
