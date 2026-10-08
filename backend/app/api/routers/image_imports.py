import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.repositories.image_import import insert_image_import
from app.schemas.image_import import ImageImportCreate
from app.repositories.image_import import insert_image_import, find_image_import_by_hash

router = APIRouter(
    prefix="/image-imports",
    tags=["image-imports"],
)

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