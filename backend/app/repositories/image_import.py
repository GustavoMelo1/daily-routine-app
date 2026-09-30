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