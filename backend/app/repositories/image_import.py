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
    attempt_token: str | None = None,
):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE image_imports "
        "SET status = 'processing', attempt_token = ?, error_message = NULL, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'pending'",
        (attempt_token, import_id),
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

def complete_image_import(
    connection: sqlite3.Connection,
    import_id: int,
):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE image_imports "
        "SET status = 'completed', error_message = NULL, "
        "updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'processing'",
        (import_id,),
    )
    return cursor.rowcount

def find_image_import_by_id(
    connection: sqlite3.Connection,
    import_id: int,
):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, image_hash, status, error_message "
        "FROM image_imports WHERE id = ?",
        (import_id,),
    )
    return cursor.fetchone()


def get_import_attempt(connection, import_id):
    return connection.execute(
        "SELECT status, attempt_token, extracted_payload, publication_digest "
        "FROM image_imports WHERE id = ?", (import_id,),
    ).fetchone()


def retry_image_import(connection, import_id):
    # A worker that was replaced loses its token and cannot publish afterwards.
    return connection.execute(
        "UPDATE image_imports SET status = 'pending', attempt_token = NULL, "
        "error_message = NULL, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND (status = 'failed' OR "
        "(status = 'processing' AND updated_at <= datetime('now', '-1 hour')))",
        (import_id,),
    ).rowcount


def save_import_payload(connection, import_id, token, payload):
    return connection.execute(
        "UPDATE image_imports SET extracted_payload = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'processing' AND attempt_token = ?",
        (payload, import_id, token),
    ).rowcount


def fail_import_attempt(connection, import_id, token, message):
    return connection.execute(
        "UPDATE image_imports SET status = 'failed', error_message = ?, "
        "updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'processing' "
        "AND attempt_token = ?", (message, import_id, token),
    ).rowcount
