from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

class Dia(BaseModel):
    data: str
    minutos_estudados: int
    frase_do_dia: str
    autor_frase: str
    tipo: str

class Tarefa(BaseModel):
    dia_id: int
    descricao: str
    cumprida: int

@app.get("/dias/{data}")
def dias(data: str):
    """Busca a tabela DIAS no BANCO pela DATA"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("SELECT dias.data,dias.frase_do_dia, tarefas.descricao, tarefas.cumprida FROM dias LEFT JOIN tarefas ON dias.id = tarefas.dia_id WHERE dias.data = ? ", (data,))
    resultado = cur.fetchall()
    con.close()
    return resultado

@app.post("/dias")
def create_dia(dia: Dia):
    """Cria um novo DIA no BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO dias (data, minutos_estudados, frase_do_dia, autor_frase, tipo) VALUES(?, ?, ?, ?, ?)", (dia.data, dia.minutos_estudados, dia.frase_do_dia, dia.autor_frase, dia.tipo))
        con.commit()
        con.close()
        return {"Status": "Dia novo Criado"}
    except sqlite3.IntegrityError:
        con.close()
        raise HTTPException(status_code=400, detail="Dia ja existente")

@app.delete("/dias/{data}")
def delete_dia(data: str):
    """Deleta o DIA do BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("DELETE FROM dias WHERE data = ?", (data,))
    
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404,detail="Dia não encontrado")

    con.commit()
    con.close()
    return {"Status": "Dia Deletado"}

@app.post("/tarefas")
def create_tarefas(tarefa: Tarefa):
    """Cria uma nova TAREFA no BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas (dia_id, descricao, cumprida) VALUES (?, ?, ? )", (tarefa.dia_id, tarefa.descricao, tarefa.cumprida))
    con.commit()
    new_id = cur.lastrowid
    con.close()
    return {"id": new_id, "Status": "Tarefa Criada"}

@app.delete("/tarefas/{id}")
def delete_tarefa (id: int):
    """Deleta a TAREFA do BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404,detail="Tarefa não encontrada")

    con.commit()
    con.close()
    return {"Status": "Tarefa Deletada"}