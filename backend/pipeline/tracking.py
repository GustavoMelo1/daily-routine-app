import hashlib
import json
from pathlib import Path

def calculate_image_hash(image_path):
    with open(image_path, "rb") as image_file:
        return hashlib.file_digest(image_file, "sha256").hexdigest()

def load_processed_hashes(tracking_path):
    tracking_file = Path(tracking_path)
    if not tracking_file.exists():
        return set()

    with tracking_file.open("r", encoding="utf-8") as file:
        hashes = json.load(file)

    if not isinstance(hashes, list) or not all(isinstance(item, str) for item in hashes):
        raise ValueError("Histórico de imagens inválido")

    return set(hashes)