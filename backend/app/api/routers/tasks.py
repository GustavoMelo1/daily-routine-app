from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task import delete_task_by_id, insert_task, update_task_completion

router = APIRouter(prefix="/tarefas", tags=["tasks"])

@router.post("", status_code=201)
def create_task(tarefa: TaskCreate, con = Depends(get_database_connection)):
    """Cria uma nova TAREFA no BANCO"""
    task_id = insert_task(
        connection=con,
        day_id=tarefa.dia_id,
        description=tarefa.descricao,
        completed=tarefa.cumprida,
    )
    con.commit()
    con.close()
    return {"id": task_id, "Status": "Tarefa Criada"}

@router.delete("/{id}")
def delete_task(id: int, con = Depends(get_database_connection)):
    """Deleta a TAREFA do BANCO"""
    affected_rows = delete_task_by_id(
        connection=con,
        task_id=id,
    )
    if affected_rows == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    con.commit()
    con.close()
    return {"Status": "Tarefa Deletada"}

@router.patch("/{id}")
def update_task(id: int, tarefa: TaskUpdate, con = Depends(get_database_connection)):
    """Atualiza se uma tarefa foi cumprida ou nao"""
    affected_rows = update_task_completion(
        connection=con,
        task_id=id,
        completed=tarefa.cumprida,
    )
    if affected_rows == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    con.commit()
    con.close()
    return {"Status": "Tarefa Atualizada"}

