from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import get_database_connection
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.quarantine import QuarantineDayCreate, QuarantineTaskCreate
from app.api.routers.days import router as days_router

import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(days_router)


def status(con, cur, mensagem):
    """Verifica o db se encontrou algo se nao lança erro 404 com a mensagem recebida"""
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail=mensagem)

@app.post("/erros-quarentena", status_code=201)
def create_erros(dia: QuarantineDayCreate, con = Depends(get_database_connection)):
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

@app.post("/tarefas-quarentena", status_code=201)
def create_tarefa_quarentena(tarefa: QuarantineTaskCreate, con = Depends(get_database_connection)):
    """Cria a TAREFA em QUARENTENA no Banco"""
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas_quarentena (erro_quarentena_id, descricao, cumprida, motivo_erro) VALUES (?, ?, ?, ?)", (tarefa.erro_quarentena_id, tarefa.descricao, tarefa.cumprida, tarefa.motivo_erro))
    con.commit()
    tarefa_id = cur.lastrowid
    con.close()
    return {"id": tarefa_id, "Status": "Tarefa em Quarentena"}

@app.post("/tarefas", status_code=201)
def create_tarefas(tarefa: TaskCreate, con = Depends(get_database_connection)):
    """Cria uma nova TAREFA no BANCO"""
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas (dia_id, descricao, cumprida) VALUES (?, ?, ? )", (tarefa.dia_id, tarefa.descricao, tarefa.cumprida))
    con.commit()
    new_id = cur.lastrowid
    con.close()
    return {"id": new_id, "Status": "Tarefa Criada"}

@app.delete("/tarefas/{id}")
def delete_tarefa (id: int, con = Depends(get_database_connection)):
    """Deleta a TAREFA do BANCO"""
    cur = con.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    status(con, cur, "Tarefa não encontrada")

    con.commit()
    con.close()
    return {"Status": "Tarefa Deletada"}

@app.patch("/tarefas/{id}")
def atualizar_tarefa(id: int, tarefa: TaskUpdate, con = Depends(get_database_connection)):
    """Atualiza se uma tarefa foi cumprida ou nao"""
    cur = con.cursor()

    cur.execute(
        "UPDATE tarefas SET cumprida = ? WHERE id = ?",
        (tarefa.cumprida, id)
    )

    status(con, cur, "Tarefa nao encontrada")

    con.commit()
    con.close()
    return {"Status": "Tarefa Atualizada"}
