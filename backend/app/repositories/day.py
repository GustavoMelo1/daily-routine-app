import sqlite3


def find_days_by_month(connection: sqlite3.Connection,
    year: int,
    month: int,
):
    cursor = connection.cursor()
    date_prefix = f"{year:04d}-{month:02d}"
    cursor.execute(
        "SELECT dias.data, "
        "(SELECT descricao FROM tarefas WHERE tarefas.dia_id = dias.id ORDER BY tarefas.id LIMIT 1) "
        "FROM dias WHERE dias.data LIKE ?",
        (f"{date_prefix}%",),
    )
    return cursor.fetchall()

def find_day_by_date(connection: sqlite3.Connection,
    date: str,
):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT dias.id, dias.data, dias.frase_do_dia, dias.autor_frase, dias.minutos_estudados, dias.tipo, "
        "tarefas.id, tarefas.descricao, tarefas.cumprida "
        "FROM dias LEFT JOIN tarefas ON dias.id = tarefas.dia_id WHERE dias.data = ?",
        (date,),
    )
    return cursor.fetchall()
