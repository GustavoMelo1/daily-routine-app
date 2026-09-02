import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.day import DayCreate


router = APIRouter(prefix="/dias", tags=["days"])

@router.get("")
def list_days_by_month(ano: int, mes: int, con= Depends(get_database_connection)):
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


@router.get("/{data}")
def get_day_by_date(data: str, con= Depends(get_database_connection)):
    """Busca a tabela DIAS no BANCO pela DATA, com as tarefas do dia"""
    cur = con.cursor()
    cur.execute(
        "SELECT dias.id, dias.data, dias.frase_do_dia, dias.autor_frase, dias.minutos_estudados, dias.tipo, "
        "tarefas.id, tarefas.descricao, tarefas.cumprida "
        "FROM dias LEFT JOIN tarefas ON dias.id = tarefas.dia_id WHERE dias.data = ?",
        (data,),
    )
    linhas = cur.fetchall()
    con.close()
    if not linhas:
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    primeira = linhas[0]
    resultado = {
        "id": primeira[0],
        "data": primeira[1],
        "frase_do_dia": primeira[2],
        "autor_frase": primeira[3],
        "minutos_estudados": primeira[4],
        "tipo": primeira[5],
        "tarefas": [
            {"id": linha[6], "descricao": linha[7], "cumprida": linha[8]}
            for linha in linhas
            if linha[6] is not None
        ],
    }
    return resultado

@router.post("", status_code=201)
def create_day(dia: DayCreate, con= Depends(get_database_connection)):
    """Cria um novo DIA no BANCO"""
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO dias (data, minutos_estudados, frase_do_dia, autor_frase, tipo) VALUES(?, ?, ?, ?, ?)", (dia.data, dia.minutos_estudados, dia.frase_do_dia, dia.autor_frase, dia.tipo))
        con.commit()
        new_day = cur.lastrowid
        con.close()
        return {"dia": new_day, "Status": "Dia novo Criado"}
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=400, detail="Dia ja existente")

@router.delete("/{data}")
def delete_day(data: str, con = Depends(get_database_connection)):
    """Deleta o DIA do BANCO."""
    cur = con.cursor()
    cur.execute("DELETE FROM dias WHERE data = ?", (data,))

    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Dia não encontrado")

    con.commit()
    con.close()
    return {"Status": "Dia Deletado"}