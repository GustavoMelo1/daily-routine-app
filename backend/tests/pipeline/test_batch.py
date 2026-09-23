import pytest
import logging
from pipeline.batch import find_image_files, process_folder
from unittest.mock import Mock


def test_find_image_files_rejects_missing_folder(tmp_path):
    missing_folder = tmp_path / "missing"

    with pytest.raises(NotADirectoryError, match="Pasta de imagens inválida"):
        find_image_files(missing_folder)

def test_find_image_files_filters_images(tmp_path):
    (tmp_path / "foto.JPG").touch()
    (tmp_path / "pagina.jpeg").touch()
    (tmp_path / "outra.png").touch()
    (tmp_path / "notas.txt").touch()
    (tmp_path / "pasta.jpg").mkdir()

    image_files = find_image_files(tmp_path)

    assert {path.name for path in image_files} == {
        "foto.JPG",
        "pagina.jpeg",
        "outra.png",
    }

def test_process_folder_skips_empty_folder(tmp_path, monkeypatch, caplog):
    fake_extract = Mock()
    fake_publish = Mock()
    monkeypatch.setattr("pipeline.batch.extract", fake_extract)
    monkeypatch.setattr("pipeline.batch.publish_days", fake_publish)
    caplog.set_level(logging.INFO, logger="pipeline.batch")
    failures = process_folder(tmp_path)

    assert failures == []
    fake_extract.assert_not_called()
    fake_publish.assert_not_called()
    assert "Nenhuma imagem encontrada" in caplog.text

def test_process_folder_continues_after_ocr_failure(tmp_path, monkeypatch, caplog):
    image_paths = [
        tmp_path / "primeira.jpg",
        tmp_path / "segunda.jpg",
        tmp_path / "terceira.jpg",
    ]
    monkeypatch.setattr("pipeline.batch.find_image_files",Mock(return_value=image_paths),)
    caplog.set_level(logging.INFO, logger="pipeline.batch")

    first_result = {"dias": [{"data": "2026-08-25"}]}
    third_result = {"dias": [{"data": "2026-08-27"}]}

    fake_extract = Mock(side_effect=[
        first_result,
        ValueError("Falha no OCR"),
        third_result,
    ])
    fake_publish = Mock()

    monkeypatch.setattr("pipeline.batch.extract", fake_extract)
    monkeypatch.setattr("pipeline.batch.publish_days", fake_publish)
    failures = process_folder(tmp_path)

    assert failures == [{
        "image_path": str(image_paths[1]),
        "error": "Falha no OCR",
    }]
    assert fake_extract.call_count == 3
    assert fake_publish.call_count == 2
    assert fake_publish.call_args_list[0].args[0] == first_result
    assert fake_publish.call_args_list[1].args[0] == third_result

def test_process_folder_continues_after_publication_failure(tmp_path, monkeypatch):
    image_paths = [
        tmp_path / "primeira.jpg",
        tmp_path / "segunda.jpg",
        tmp_path / "terceira.jpg",
    ]
    monkeypatch.setattr(
        "pipeline.batch.find_image_files",
        Mock(return_value=image_paths),
    )
    first_result = {"dias": [{"data": "2026-08-25"}]}
    second_result = {"dias": [{"data": "2026-08-26"}]}
    third_result = {"dias": [{"data": "2026-08-27"}]}

    fake_extract = Mock(side_effect=[
        first_result,
        second_result,
        third_result,
    ])
    fake_publish = Mock(side_effect=[
        None,
        RuntimeError("Falha na publicação"),
        None,
    ])
    monkeypatch.setattr("pipeline.batch.extract", fake_extract)
    monkeypatch.setattr("pipeline.batch.publish_days", fake_publish)
    failures = process_folder(tmp_path)

    assert failures == [{
        "image_path": str(image_paths[1]),
        "error": "Falha na publicação",
    }]
    assert fake_extract.call_count == 3
    assert fake_publish.call_count == 3
    assert fake_publish.call_args_list[0].args[0] == first_result
    assert fake_publish.call_args_list[1].args[0] == second_result
    assert fake_publish.call_args_list[2].args[0] == third_result