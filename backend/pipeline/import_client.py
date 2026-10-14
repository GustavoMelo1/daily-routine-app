"""HTTP operations for the image import lifecycle. No direct database access."""
import os
import requests


def request(method, path, **kwargs):
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
    return requests.request(method, f"{base_url}/image-imports{path}", timeout=(5, 60), **kwargs)


def require_response(response):
    response.raise_for_status()
    return response.json()


def check_import_api():
    require_response(request("GET", "/health"))


def get_or_create_import(image_hash):
    response = request("POST", "", json={"image_hash": image_hash})
    if response.status_code == 409:
        return require_response(request("GET", f"/by-hash/{image_hash}"))
    return require_response(response)


def retry_import(import_id):
    return require_response(request("POST", f"/{import_id}/retry"))


def start_import(import_id):
    return require_response(request("POST", f"/{import_id}/start"))["attempt_token"]


def get_payload(import_id):
    return require_response(request("GET", f"/{import_id}/payload"))["payload"]


def save_payload(import_id, token, payload):
    require_response(request("PUT", f"/{import_id}/payload", json=payload, headers={"X-Import-Token": token}))


def publish_import(import_id, token, payload):
    require_response(request("POST", f"/{import_id}/publish", json=payload, headers={"X-Import-Token": token}))


def fail_import(import_id, token, message):
    require_response(request("POST", f"/{import_id}/fail", json={"error_message": message[:2000]}, headers={"X-Import-Token": token}))
