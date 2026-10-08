import sqlite3
import pytest

from app.repositories.image_import import insert_image_import, start_image_import, find_image_import_by_hash
from app.schemas.image_import import ImageImportPublish
from app.services.image_import import publish_image_import
from app.schemas.image_import import ImageImportDayCreate, ImageImportQuarantineDayCreate
from app.services.image_import import save_import_day, save_import_quarantine_day

def test_save_import_day_links_tasks(database_connection):
    day = ImageImportDayCreate(
        data="2026-10-05",
        minutos_estudados=60,
        frase_do_dia="",
        autor_frase="",
        tipo="normal",
        tarefas=[
            {"descricao": "Estudar SQL", "cumprida": 1},
            {"descricao": "Revisar Python", "cumprida": 0},
        ],
    )

    day_id = save_import_day(database_connection, day)

    tasks = database_connection.execute(
        "SELECT dia_id, descricao, cumprida FROM tarefas ORDER BY id"
    ).fetchall()

    assert tasks == [
        (day_id, "Estudar SQL", 1),
        (day_id, "Revisar Python", 0),
    ]

def test_save_import_quarantine_day_preserves_task_error(database_connection):
    day = ImageImportQuarantineDayCreate(
        motivo_erro="tarefa_invalida",
        tarefas=[
            {
                "descricao": None,
                "cumprida": None,
                "motivo_erro": "tarefa_invalida",
            }
        ],
    )

    day_id = save_import_quarantine_day(database_connection, day)

    tasks = database_connection.execute(
        "SELECT erro_quarentena_id, descricao, cumprida, motivo_erro "
        "FROM tarefas_quarentena"
    ).fetchall()

    assert tasks == [
        (day_id, None, None, "tarefa_invalida")
    ]

def test_publish_image_import_rolls_back_on_failure(database_connection):
    import_id = insert_image_import(database_connection, "a" * 64)
    start_image_import(database_connection, import_id)
    database_connection.commit()

    payload = ImageImportPublish(
        quarantine_days=[
            {"data": "2026-10-07", "motivo_erro": "tarefas_ausentes"},
            {"data": "2026-10-07", "motivo_erro": "tarefas_ausentes"},
        ]
    )

    with pytest.raises(sqlite3.IntegrityError):
        publish_image_import(database_connection, import_id, payload)

    count = database_connection.execute(
        "SELECT COUNT(*) FROM erros_quarentena"
    ).fetchone()[0]
    row = find_image_import_by_hash(database_connection, "a" * 64)

    assert count == 0
    assert row[2] == "processing"

def test_publish_image_import_commits_success(database_connection):
    import_id = insert_image_import(database_connection, "a" * 64)
    start_image_import(database_connection, import_id)
    database_connection.commit()

    payload = ImageImportPublish(
        quarantine_days=[
            {"data": "2026-10-07", "motivo_erro": "tarefas_ausentes"}
        ]
    )

    publish_image_import(database_connection, import_id, payload)
    database_connection.rollback()

    count = database_connection.execute(
        "SELECT COUNT(*) FROM erros_quarentena"
    ).fetchone()[0]
    row = find_image_import_by_hash(database_connection, "a" * 64)

    assert count == 1
    assert row[2] == "completed"
