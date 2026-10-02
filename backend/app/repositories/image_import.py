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

def start_image_import(
    connection: sqlite3.Connection,
    import_id: int,
):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE image_imports "
        "SET status = 'processing', updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'pending'",
        (import_id,),
    )
    return cursor.rowcount

def fail_image_import(
    connection: sqlite3.Connection,
    import_id: int,
    error_message: str,
):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE image_imports "
        "SET status = 'failed', error_message = ?, "
        "updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'processing'",
        (error_message, import_id),
    )
    return cursor.rowcount