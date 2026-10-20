from fastapi import APIRouter, Depends, HTTPException, Response
from app.database.connection import get_database_connection
from app.repositories import learning
from app.schemas.learning import LearningCreate, LearningUpdate, LearningNotesUpdate

router = APIRouter(prefix='/learning-nodes', tags=['learning'])


@router.get('')
def list_nodes(connection=Depends(get_database_connection)):
    return learning.list_nodes(connection)


@router.post('', status_code=201)
def create_node(payload: LearningCreate, connection=Depends(get_database_connection)):
    with connection:
        connection.execute('BEGIN IMMEDIATE')
        parent_id = payload.parent_id
        depth = 1
        while parent_id is not None:
            parent = learning.find_node(connection, parent_id)
            if parent is None:
                raise HTTPException(404, 'Tópico pai não encontrado')
            depth += 1
            if depth > 32:
                raise HTTPException(422, 'Limite de 32 níveis atingido')
            parent_id = parent[1]
        node_id = learning.insert_node(connection, payload.title, payload.parent_id)
    return {'id': node_id, **payload.model_dump(), 'completed': False, 'notes': '', 'notes_version': 1}


@router.put('/{node_id}/notes')
def update_notes(node_id: int, payload: LearningNotesUpdate, connection=Depends(get_database_connection)):
    with connection:
        if not learning.update_notes(connection, node_id, payload.notes, payload.version):
            if learning.find_node(connection, node_id) is None:
                raise HTTPException(404, 'Tópico não encontrado')
            raise HTTPException(409, 'A nota foi alterada em outra aba. Copie seu texto antes de recarregar.')
    return {'notes': payload.notes, 'notes_version': payload.version + 1}


@router.put('/{node_id}')
def update_node(node_id: int, payload: LearningUpdate, connection=Depends(get_database_connection)):
    with connection:
        if not learning.update_node(connection, node_id, payload.title, payload.completed):
            raise HTTPException(404, 'Tópico não encontrado')
    return {'id': node_id, **payload.model_dump()}


@router.delete('/{node_id}', status_code=204)
def delete_node(node_id: int, connection=Depends(get_database_connection)):
    with connection:
        if not learning.delete_node(connection, node_id):
            raise HTTPException(404, 'Tópico não encontrado')
    return Response(status_code=204)
