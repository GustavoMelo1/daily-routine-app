import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.quarantine import QuarantineDayCreate, QuarantineTaskCreate


router = APIRouter(tags=["quarantine"])

@router.post("/erros-quarentena", status_code=201)
def create_quarantine_day(dia: QuarantineDayCreate, con = Depends(get_database_connection)):
    """Envia um dia para o quarentena pro BANCO"""
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO erros_quarentena (data, minutos_estudados,frase_do_dia , autor_frase, tipo, motivo_erro) VALUES(?, ?, ?, ?, ?, ?)", (dia.data, dia.minutos_estudados, dia.frase_do_dia, dia.autor_frase, dia.tipo, dia.motivo_erro))
        con.commit()
        erro_id = cur.lastrowid
        con.close()
        return {"id": erro_id, "Status": "Dia enviado para quarentena"}
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=400, detail="Dia já está na quarentena")

@router.post("/tarefas-quarentena", status_code=201)
def create_quarantine_task(tarefa: QuarantineTaskCreate, con = Depends(get_database_connection)):
    """Cria a TAREFA em QUARENTENA no Banco"""
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas_quarentena (erro_quarentena_id, descricao, cumprida, motivo_erro) VALUES (?, ?, ?, ?)", (tarefa.erro_quarentena_id, tarefa.descricao, tarefa.cumprida, tarefa.motivo_erro))
    con.commit()
    tarefa_id = cur.lastrowid
    con.close()
    return {"id": tarefa_id, "Status": "Tarefa em Quarentena"}