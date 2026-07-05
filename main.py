from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/dias/{data}")
def dias(data: str):
    con = sqlite3.connect("db/rotina.db")
    cur = con.cursor()
    cur.execute("SELECT dias.data,dias.frase_do_dia, tarefas.descricao, tarefas.cumprida FROM dias INNER JOIN tarefas ON dias.id = tarefas.dia_id WHERE dias.data = ? ", (data,))
    return cur.fetchall()
