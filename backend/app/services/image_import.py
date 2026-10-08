import sqlite3

from app.repositories.day import insert_day
from app.repositories.task import insert_task
from app.schemas.image_import import ImageImportDayCreate
from app.repositories.quarantine import insert_quarantine_day, insert_quarantine_task
from app.schemas.image_import import ImageImportQuarantineDayCreate
from app.repositories.image_import import complete_image_import
from app.schemas.image_import import ImageImportPublish

def save_import_day(
    connection: sqlite3.Connection,
    day: ImageImportDayCreate,
):
    day_id = insert_day(
        connection=connection,
        date=day.data,
        studied_minutes=day.minutos_estudados,
        daily_quote=day.frase_do_dia,
        quote_author=day.autor_frase,
        day_type=day.tipo,
    )

    for task in day.tarefas:
        insert_task(
            connection=connection,
            day_id=day_id,
            description=task.descricao,
            completed=task.cumprida,
        )

    return day_id

def save_import_quarantine_day(
    connection: sqlite3.Connection,
    day: ImageImportQuarantineDayCreate,
):
    quarantine_day_id = insert_quarantine_day(
        connection=connection,
        date=day.data,
        studied_minutes=day.minutos_estudados,
        daily_quote=day.frase_do_dia,
        quote_author=day.autor_frase,
        day_type=day.tipo,
        error_reason=day.motivo_erro,
    )

    for task in day.tarefas:
        insert_quarantine_task(
            connection=connection,
            quarantine_day_id=quarantine_day_id,
            description=task.descricao,
            completed=task.cumprida,
            error_reason=task.motivo_erro,
        )

    return quarantine_day_id

def publish_image_import(
    connection: sqlite3.Connection,
    import_id: int,
    payload: ImageImportPublish,
):
    if connection.in_transaction:
        raise ValueError("A conexão já possui uma transação aberta")

    with connection:
        for day in payload.days:
            save_import_day(connection, day)

        for day in payload.quarantine_days:
            save_import_quarantine_day(connection, day)

        affected_rows = complete_image_import(connection, import_id)
        if affected_rows != 1:
            raise ValueError("A importação não está em processamento")

