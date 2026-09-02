import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.day import DayCreate
from app.repositories.day import delete_day_by_date, find_day_by_date, find_days_by_month, insert_day

router = APIRouter(prefix="/dias", tags=["days"])

@router.get("")
def list_days_by_month(ano: int, mes: int, con= Depends(get_database_connection)):
    """Lista os dias de um mes, com a primeira tarefa como marcador resumido"""
    rows = find_days_by_month(
        connection=con,
        year=ano,
        month=mes,
    )
    con.close()
    return [{"data": row[0], "marcador": row[1]} for row in rows]


@router.get("/{data}")
def get_day_by_date(data: str, con= Depends(get_database_connection)):
    """Busca a tabela DIAS no BANCO pela DATA, com as tarefas do dia"""
    rows = find_day_by_date(
        connection=con,
        date=data,
    )
    con.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    first_row = rows[0]
    result = {
        "id": first_row[0],
        "data": first_row[1],
        "frase_do_dia": first_row[2],
        "autor_frase": first_row[3],
        "minutos_estudados": first_row[4],
        "tipo": first_row[5],
        "tarefas": [
            {"id": row[6], "descricao": row[7], "cumprida": row[8]}
            for row in rows
            if row[6] is not None
        ],
    }
    return result

@router.post("", status_code=201)
def create_day(dia: DayCreate, con= Depends(get_database_connection)):
    """Cria um novo DIA no BANCO"""
    try:
        new_day_id = insert_day(connection=con, date=dia.data, studied_minutes=dia.minutos_estudados, daily_quote=dia.frase_do_dia, quote_author=dia.autor_frase, day_type=dia.tipo,)
        con.commit()
        con.close()
        return {"dia": new_day_id, "Status": "Dia novo Criado"}
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=400, detail="Dia ja existente")

@router.delete("/{data}")
def delete_day(data: str, con = Depends(get_database_connection)):
    """Deleta o DIA do BANCO."""
    affected_rows = delete_day_by_date(connection=con,date=data,)

    if affected_rows == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    con.commit()
    con.close()
    return {"Status": "Dia Deletado"}