from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_database_connection
from app.repositories.task import delete_task_by_id, insert_task, update_task_completion
from app.schemas.task import TaskCreate, TaskUpdate


router = APIRouter(prefix="/tarefas", tags=["tasks"])

@router.post("", status_code=201)
def create_task(task: TaskCreate, connection=Depends(get_database_connection)):
    """Cria uma nova TAREFA no BANCO"""
    task_id = insert_task(
        connection=connection,
        day_id=task.dia_id,
        description=task.descricao,
        completed=task.cumprida,
    )
    connection.commit()
    return {"id": task_id, "Status": "Tarefa Criada"}

@router.delete("/{id}")
def delete_task(id: int, connection=Depends(get_database_connection)):
    """Deleta a TAREFA do BANCO"""
    affected_rows = delete_task_by_id(
        connection=connection,
        task_id=id,
    )
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    connection.commit()
    return {"Status": "Tarefa Deletada"}

@router.patch("/{id}")
def update_task(
    id: int,
    task: TaskUpdate,
    connection=Depends(get_database_connection),
):
    """Atualiza se uma tarefa foi cumprida ou nao"""
    affected_rows = update_task_completion(
        connection=connection,
        task_id=id,
        completed=task.cumprida,
    )
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    connection.commit()
    return {"Status": "Tarefa Atualizada"}

