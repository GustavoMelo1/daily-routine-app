import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ErroQuarentena(BaseModel):
    data: str | None = None
    minutos_estudados: int | None = None
    frase_do_dia: str | None = None
    autor_frase: str | None = None
    tipo: str | None = None
    motivo_erro: str 

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

class AtualizarTarefa(BaseModel):
    cumprida: int

def conexao():
    """Conecta no db e retorna a conexão"""
    con = sqlite3.connect(os.getenv("DB_URL"))
    return con

def status(con, cur, mensagem):
    """Verifica o db se encontrou algo se nao lança erro 404 com a mensagem recebida"""
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail=mensagem)

@app.get("/dias")
def listar_dias_do_mes(ano: int, mes: int, con = Depends(conexao)):
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

@app.get("/dias/{data}")
def dias(data: str, con = Depends(conexao)):
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

@app.post("/dias", status_code=201)
def create_dia(dia: Dia, con = Depends(conexao)):
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

@app.delete("/dias/{data}")
def delete_dia(data: str, con = Depends(conexao)):
    """Deleta o DIA do BANCO"""
    cur = con.cursor()
    cur.execute("DELETE FROM dias WHERE data = ?", (data,))
    status(con, cur, "Dia não encontrado")

    con.commit()
    con.close()
    return {"Status": "Dia Deletado"}

@app.post("/tarefas", status_code=201)
def create_tarefas(tarefa: Tarefa, con = Depends(conexao)):
    """Cria uma nova TAREFA no BANCO"""
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas (dia_id, descricao, cumprida) VALUES (?, ?, ? )", (tarefa.dia_id, tarefa.descricao, tarefa.cumprida))
    con.commit()
    new_id = cur.lastrowid
    con.close()
    return {"id": new_id, "Status": "Tarefa Criada"}

@app.delete("/tarefas/{id}")
def delete_tarefa (id: int, con = Depends(conexao)):
    """Deleta a TAREFA do BANCO"""
    cur = con.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    status(con, cur, "Tarefa não encontrada")

    con.commit()
    con.close()
    return {"Status": "Tarefa Deletada"}

@app.patch("/tarefas/{id}")
def atualizar_tarefa(id: int, tarefa: AtualizarTarefa, con = Depends(conexao)):
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

