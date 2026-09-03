import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.quarantine import QuarantineDayCreate, QuarantineTaskCreate
from app.repositories.quarantine import insert_quarantine_day, insert_quarantine_task

router = APIRouter(tags=["quarantine"])

@router.post("/erros-quarentena", status_code=201)
def create_quarantine_day(dia: QuarantineDayCreate, con = Depends(get_database_connection)):
    """Envia um dia para o quarentena pro BANCO"""
    try:
        quarantine_day_id = insert_quarantine_day(
            connection=con,
            date=dia.data,
            studied_minutes=dia.minutos_estudados,
            daily_quote=dia.frase_do_dia,
            quote_author=dia.autor_frase,
            day_type=dia.tipo,
            error_reason=dia.motivo_erro,
        )
        con.commit()
        con.close()
        return {"id": quarantine_day_id, "Status": "Dia enviado para quarentena"}
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=400, detail="Dia já está na quarentena")

@router.post("/tarefas-quarentena", status_code=201)
def create_quarantine_task(tarefa: QuarantineTaskCreate, con = Depends(get_database_connection)):
    """Cria a TAREFA em QUARENTENA no Banco"""
    quarantine_task_id = insert_quarantine_task(
        connection=con,
        quarantine_day_id=tarefa.erro_quarentena_id,
        description=tarefa.descricao,
        completed=tarefa.cumprida,
        error_reason=tarefa.motivo_erro,
    )
    con.commit()
    con.close()
    return {"id": quarantine_task_id, "Status": "Tarefa em Quarentena"}