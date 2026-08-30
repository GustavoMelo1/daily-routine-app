from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.task import TaskCreate, TaskUpdate


router = APIRouter(prefix="/tarefas", tags=["tasks"])

@router.post("", status_code=201)
def create_task(tarefa: TaskCreate, con = Depends(get_database_connection)):
    """Cria uma nova TAREFA no BANCO"""
    cur = con.cursor()
    cur.execute("INSERT INTO tarefas (dia_id, descricao, cumprida) VALUES (?, ?, ? )", (tarefa.dia_id, tarefa.descricao, tarefa.cumprida))
    con.commit()
    new_id = cur.lastrowid
    con.close()
    return {"id": new_id, "Status": "Tarefa Criada"}

@router.delete("/{id}")
def delete_task(id: int, con = Depends(get_database_connection)):
    """Deleta a TAREFA do BANCO"""
    cur = con.cursor()
    cur.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    con.commit()
    con.close()
    return {"Status": "Tarefa Deletada"}

@router.patch("/{id}")
def update_task(id: int, tarefa: TaskUpdate, con = Depends(get_database_connection)):
    """Atualiza se uma tarefa foi cumprida ou nao"""
    cur = con.cursor()

    cur.execute(
        "UPDATE tarefas SET cumprida = ? WHERE id = ?",
        (tarefa.cumprida, id)
    )
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    con.commit()
    con.close()
    return {"Status": "Tarefa Atualizada"}

