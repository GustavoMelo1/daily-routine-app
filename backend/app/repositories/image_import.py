import sqlite3


def find_image_import_by_hash(
    connection: sqlite3.Connection,
    image_hash: str,
):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, image_hash, status, error_message "
        "FROM image_imports WHERE image_hash = ?",
        (image_hash,),
    )
    return cursor.fetchone()

def insert_image_import(
    connection: sqlite3.Connection,
    image_hash: str,
):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO image_imports (image_hash) VALUES (?)",
        (image_hash,),
    )
    return cursor.lastrowid