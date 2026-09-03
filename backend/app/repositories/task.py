import sqlite3

def insert_task(
    connection: sqlite3.Connection,
    day_id: int,
    description: str,
    completed: int,
):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tarefas (dia_id, descricao, cumprida) VALUES (?, ?, ? )", (day_id, description, completed))
    return cursor.lastrowid


def delete_task_by_id(
    connection: sqlite3.Connection,
    task_id: int,
):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (task_id,))
    return cursor.rowcount

def update_task_completion(
        connection: sqlite3.Connection,
        task_id: int, 
        completed: int,  
):
    cursor = connection.cursor()
    cursor.execute("UPDATE tarefas SET cumprida = ? WHERE id = ?", (completed, task_id))
    return cursor.rowcount