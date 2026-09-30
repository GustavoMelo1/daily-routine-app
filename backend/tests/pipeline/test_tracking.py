import json
from pipeline.tracking import calculate_image_hash, load_processed_hashes


def test_same_content_has_same_hash(tmp_path):
    first_file = tmp_path / "foto.jpg"
    second_file = tmp_path / "copia.jpg"

    first_file.write_bytes(b"mesmo conteudo")
    second_file.write_bytes(b"mesmo conteudo")

    assert calculate_image_hash(first_file) == calculate_image_hash(second_file)

def test_changed_content_has_different_hash(tmp_path):
    image_file = tmp_path / "foto.jpg"
    image_file.write_bytes(b"conteudo original")
    original_hash = calculate_image_hash(image_file)

    image_file.write_bytes(b"conteudo alterado")
    updated_hash = calculate_image_hash(image_file)

    assert original_hash != updated_hash

def test_load_processed_hashes_returns_empty_when_missing(tmp_path):
    tracking_file = tmp_path / "processed_images.json"

    result = load_processed_hashes(tracking_file)

    assert result == set()
    assert not tracking_file.exists()

def test_load_processed_hashes_reads_existing_file(tmp_path):
    tracking_file = tmp_path / "processed_images.json"
    saved_hashes = ["a" * 64, "b" * 64]
    tracking_file.write_text(json.dumps(saved_hashes), encoding="utf-8")

    result = load_processed_hashes(tracking_file)

    assert result == set(saved_hashes)
