import sqlite3
import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header
from app.repositories.image_import import find_image_import_by_id, start_image_import
from app.database.connection import get_database_connection
from app.repositories.image_import import get_import_attempt, retry_image_import, save_import_payload, fail_import_attempt
from app.schemas.image_import import ImageImportCreate, ImageImportFailure, ImageImportPublish
from app.services.image_import import publish_image_import
from app.repositories.image_import import insert_image_import, find_image_import_by_hash

router = APIRouter(
    prefix="/image-imports",
    tags=["image-imports"],
)


@router.get("/health")
def import_health(connection=Depends(get_database_connection)):
    connection.execute("SELECT attempt_token, extracted_payload, publication_digest FROM image_imports LIMIT 0")
    return {"status": "ready"}

@router.post("", status_code=201)
def create_image_import(
    payload: ImageImportCreate,
    connection=Depends(get_database_connection),
):
    try:
        import_id = insert_image_import(connection, payload.image_hash)
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        if error.sqlite_errorcode != sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise
        raise HTTPException(
            status_code=409,
            detail="Imagem já registrada",
        ) from error

    return {"id": import_id, "status": "pending"}

@router.get("/by-hash/{image_hash}")
def get_image_import_by_hash(
    image_hash: str,
    connection=Depends(get_database_connection),
):
    row = find_image_import_by_hash(connection, image_hash)

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Importação não encontrada",
        )

    return {
        "id": row[0],
        "image_hash": row[1],
        "status": row[2],
        "error_message": row[3],
    }

@router.post("/{import_id}/start")
def start_import(
    import_id: int,
    connection=Depends(get_database_connection),
):
    row = find_image_import_by_id(connection, import_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Importação não encontrada",
        )

    token = uuid4().hex
    affected_rows = start_image_import(connection, import_id, token)
    if affected_rows == 0:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="A importação não está pendente",
        )

    connection.commit()
    return {"id": import_id, "status": "processing", "attempt_token": token}


def require_import(connection, import_id):
    if find_image_import_by_id(connection, import_id) is None:
        raise HTTPException(status_code=404, detail="Importação não encontrada")


@router.post("/{import_id}/retry")
def retry_import(import_id: int, connection=Depends(get_database_connection)):
    require_import(connection, import_id)
    changed = retry_image_import(connection, import_id)
    if not changed:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Somente falhas ou tentativas paradas há uma hora podem ser retomadas")
    connection.commit()
    return {"id": import_id, "status": "pending"}


@router.get("/{import_id}/payload")
def get_payload(import_id: int, connection=Depends(get_database_connection)):
    require_import(connection, import_id)
    row = get_import_attempt(connection, import_id)
    return {"payload": json.loads(row[2]) if row[2] else None}


@router.put("/{import_id}/payload")
def checkpoint_payload(import_id: int, payload: ImageImportPublish,
                       x_import_token: str = Header(), connection=Depends(get_database_connection)):
    require_import(connection, import_id)
    changed = save_import_payload(connection, import_id, x_import_token, payload.model_dump_json())
    if not changed:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Tentativa não está ativa")
    connection.commit()
    return {"id": import_id, "status": "processing"}


@router.post("/{import_id}/fail")
def fail_import(import_id: int, payload: ImageImportFailure,
                x_import_token: str = Header(), connection=Depends(get_database_connection)):
    require_import(connection, import_id)
    changed = fail_import_attempt(connection, import_id, x_import_token, payload.error_message)
    if not changed:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Tentativa não está ativa")
    connection.commit()
    return {"id": import_id, "status": "failed"}


@router.post("/{import_id}/publish")
def publish_import(import_id: int, payload: ImageImportPublish,
                   x_import_token: str = Header(), connection=Depends(get_database_connection)):
    require_import(connection, import_id)
    try:
        publish_image_import(connection, import_id, payload, x_import_token)
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="Conflito com registros existentes. Nenhum dado desta publicação foi confirmado; revise as datas antes de tentar novamente.") from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"id": import_id, "status": "completed"}
