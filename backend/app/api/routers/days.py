import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.repositories.day import delete_day_by_date, find_day_by_date, find_days_by_month, insert_day
from app.schemas.day import DayCreate

router = APIRouter(prefix="/dias", tags=["days"])

@router.get("")
def list_days_by_month(ano: int, mes: int, connection=Depends(get_database_connection)):
    """Lista os dias de um mes, com a primeira tarefa como marcador resumido"""
    day_rows = find_days_by_month(
        connection=connection,
        year=ano,
        month=mes,
    )
    return [{"data": row[0], "marcador": row[1]} for row in day_rows]

@router.get("/{data}")
def get_day_by_date(data: str, connection=Depends(get_database_connection)):
    """Busca a tabela DIAS no BANCO pela DATA, com as tarefas do dia"""
    day_rows = find_day_by_date(
        connection=connection,
        date=data,
    )
    if not day_rows:
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    first_row = day_rows[0]
    day_details = {
        "id": first_row[0],
        "data": first_row[1],
        "frase_do_dia": first_row[2],
        "autor_frase": first_row[3],
        "minutos_estudados": first_row[4],
        "tipo": first_row[5],
        "tarefas": [
            {"id": row[6], "descricao": row[7], "cumprida": row[8]}
            for row in day_rows
            if row[6] is not None
        ],
    }
    return day_details

@router.post("", status_code=201)
def create_day(day: DayCreate, connection=Depends(get_database_connection)):
    """Cria um novo DIA no BANCO"""
    try:
        new_day_id = insert_day(connection=connection, date=day.data, studied_minutes=day.minutos_estudados, daily_quote=day.frase_do_dia, quote_author=day.autor_frase, day_type=day.tipo,)
        connection.commit()
        return {"dia": new_day_id, "Status": "Dia novo Criado"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Dia ja existente")

@router.delete("/{data}")
def delete_day(data: str, connection=Depends(get_database_connection)):
    """Deleta o DIA do BANCO."""
    affected_rows = delete_day_by_date(connection=connection,date=data,)

    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    connection.commit()
    return {"Status": "Dia Deletado"}
