import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.day import DayCreate


router = APIRouter(prefix="/dias", tags=["days"])

@router.get("")
def list_days_by_month(ano: int, mes: int, con = Depends(get_database_connection)):
    """Lista os dias de um mes, com a primeira tarefa como marcador resumido"""
    cur = con.cursor()
    prefixo = f"{ano:04d}-{mes:02d}"
    cur.execute(
        "SELECT dias.data, "
        "(SELECT descricao FROM tarefas WHERE tarefas.dia_id = dias.id ORDER BY tarefas.id LIMIT 1) "
        "FROM dias WHERE dias.data LIKE ?",
        (f"{prefixo}%",),
    )
    linhas = cur.fetchall()
    con.close()
    return [{"data": linha[0], "marcador": linha[1]} for linha in linhas]
