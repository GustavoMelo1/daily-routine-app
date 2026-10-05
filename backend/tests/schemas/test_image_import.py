import pytest
from pydantic import ValidationError

from app.schemas.image_import import ImageImportPublish


def test_image_import_publish_rejects_empty_payload():
    with pytest.raises(
        ValidationError,
        match="A importação precisa conter ao menos um registro",
    ):
        ImageImportPublish()

def test_image_import_publish_accepts_quarantine_only():
    payload = ImageImportPublish(
        quarantine_days=[
            {"motivo_erro": "tarefas_ausentes"}
        ]
    )

    assert payload.days == []
    assert len(payload.quarantine_days) == 1
    assert payload.quarantine_days[0].tarefas == []

def test_image_import_publish_accepts_valid_days_only():
    payload = ImageImportPublish(
        days=[{
            "data": "2026-10-05",
            "minutos_estudados": 60,
            "frase_do_dia": "",
            "autor_frase": "",
            "tipo": "normal",
            "tarefas": [
                {"descricao": "Estudar SQL", "cumprida": 1}
            ],
        }]
    )

    assert payload.quarantine_days == []
    assert len(payload.days) == 1
    assert payload.days[0].tarefas[0].descricao == "Estudar SQL"