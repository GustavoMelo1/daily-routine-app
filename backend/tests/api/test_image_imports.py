import pytest

def test_create_image_import_returns_pending(client):
    response = client.post(
        "/image-imports",
        json={"image_hash": "a" * 64},
    )

    assert response.status_code == 201

    body = response.json()
    assert isinstance(body["id"], int)
    assert body["id"] > 0
    assert body["status"] == "pending"

def test_create_image_import_rejects_duplicate_hash(client):
    payload = {"image_hash": "a" * 64}

    first_response = client.post("/image-imports", json=payload)
    second_response = client.post("/image-imports", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Imagem já registrada"

@pytest.mark.parametrize("invalid_hash", [
    "",
    "a" * 63,
    "a" * 65,
    "g" * 64,
])
def test_create_image_import_rejects_invalid_hash(client, invalid_hash):
    response = client.post(
        "/image-imports",
        json={"image_hash": invalid_hash},
    )

    assert response.status_code == 422

def test_get_image_import_returns_registered_image(client):
    image_hash = "a" * 64
    created = client.post(
        "/image-imports",
        json={"image_hash": image_hash},
    )
    assert created.status_code == 201

    response = client.get(f"/image-imports/by-hash/{image_hash}")

    assert response.status_code == 200
    assert response.json() == {
        "id": created.json()["id"],
        "image_hash": image_hash,
        "status": "pending",
        "error_message": None,
    }