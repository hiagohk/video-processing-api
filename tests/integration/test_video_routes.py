from tests.factories import idempotency_key, video_payload


def test_create_video(client):

    response = client.post(
        "/videos", json=video_payload(), headers={"idempotency-key": idempotency_key()}
    )

    assert response.status_code == 200
    assert "id" in response.json()


def test_create_video_without_idempotency(client):

    response = client.post("/videos", json=video_payload())

    assert response.status_code in (400, 422)


def test_idempotent_requests(client):

    payload = video_payload()
    key = idempotency_key()

    r1 = client.post("/videos", json=payload, headers={"idempotency-key": key})

    r2 = client.post("/videos", json=payload, headers={"idempotency-key": key})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_invalid_body(client):

    response = client.post("/videos", json={}, headers={"idempotency-key": idempotency_key()})

    assert response.status_code == 422
