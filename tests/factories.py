from uuid import uuid4

from faker import Faker

fake = Faker()


def video_payload():
    return {"video_url": fake.url()}


def idempotency_key():
    return str(uuid4())
