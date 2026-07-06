from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel

app = FastAPI()

class Dia(BaseModel):
    data: str
    minutos_estudados: int
    frase_do_dia: str
    autor_frase: str
    tipo: str

@app.get("/dias/{data}")
def dias(data: str):
    """Busca a tabela dias no BANCO pela DATA"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("SELECT dias.data,dias.frase_do_dia, tarefas.descricao, tarefas.cumprida FROM dias INNER JOIN tarefas ON dias.id = tarefas.dia_id WHERE dias.data = ? ", (data,))
    return cur.fetchall()

@app.post("/dias")
def create_dia(dia: Dia):
    """Cria um novo DIA no BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("INSERT INTO dias (data, minutos_estudados, frase_do_dia, autor_frase, tipo) VALUES(?, ?, ?, ?, ?)", (dia.data, dia.minutos_estudados, dia.frase_do_dia, dia.autor_frase, dia.tipo))
    con.commit()
    con.close()
    return {"Status": "Dia novo Criado"}

@app.delete("/dias/{data}")
def delete_dia(data: str):
    """Deleta o DIA do BANCO"""
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("DELETE FROM dias WHERE data = ?", (data,))
    con.commit()
    con.close()
    return {"Status": "Dia Deletado"}