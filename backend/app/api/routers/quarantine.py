import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.repositories.quarantine import insert_quarantine_day, insert_quarantine_task
from app.schemas.quarantine import QuarantineDayCreate, QuarantineTaskCreate


router = APIRouter(tags=["quarantine"])

@router.post("/erros-quarentena", status_code=201)
def create_quarantine_day(
    day: QuarantineDayCreate,
    connection=Depends(get_database_connection),
):
    """Envia um dia para o quarentena pro BANCO"""
    try:
        quarantine_day_id = insert_quarantine_day(
            connection=connection,
            date=day.data,
            studied_minutes=day.minutos_estudados,
            daily_quote=day.frase_do_dia,
            quote_author=day.autor_frase,
            day_type=day.tipo,
            error_reason=day.motivo_erro,
        )
        connection.commit()
        return {"id": quarantine_day_id, "Status": "Dia enviado para quarentena"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Dia já está na quarentena")

@router.post("/tarefas-quarentena", status_code=201)
def create_quarantine_task(
    task: QuarantineTaskCreate,
    connection=Depends(get_database_connection),
):
    """Cria a TAREFA em QUARENTENA no Banco"""
    quarantine_task_id = insert_quarantine_task(
        connection=connection,
        quarantine_day_id=task.erro_quarentena_id,
        description=task.descricao,
        completed=task.cumprida,
        error_reason=task.motivo_erro,
    )
    connection.commit()
    return {"id": quarantine_task_id, "Status": "Tarefa em Quarentena"}
