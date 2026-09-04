import sqlite3


def insert_quarantine_day(
    connection: sqlite3.Connection,
    date: str | None,
    studied_minutes: int | None,
    daily_quote: str | None,
    quote_author: str | None,
    day_type: str | None,
    error_reason: str,
):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO erros_quarentena "
        "(data, minutos_estudados, frase_do_dia, autor_frase, tipo, motivo_erro) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            date,
            studied_minutes,
            daily_quote,
            quote_author,
            day_type,
            error_reason,
        ),
    )
    return cursor.lastrowid


def insert_quarantine_task(
    connection: sqlite3.Connection,
    quarantine_day_id: int,
    description: str | None,
    completed: int | None,
    error_reason: str | None,
):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO tarefas_quarentena "
        "(erro_quarentena_id, descricao, cumprida, motivo_erro) "
        "VALUES (?, ?, ?, ?)",
        (
            quarantine_day_id,
            description,
            completed,
            error_reason,
        ),
    )
    return cursor.lastrowid
