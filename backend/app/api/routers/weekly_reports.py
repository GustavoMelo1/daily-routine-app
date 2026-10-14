import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Response
from app.database.connection import get_database_connection
from app.repositories import weekly_report as repository
from app.schemas.weekly_report import WeeklyReportCreate, WeeklyReportUpdate, ComparisonRequest
from app.services.weekly_comparison import (
    ComparisonUnavailable, generation_lock, get_comparison_generator, validate_evidence,
)

router = APIRouter(prefix='/weekly-reports', tags=['weekly-reports'])


def require_report(connection, report_id):
    report = repository.find_report(connection, report_id)
    if report is None:
        raise HTTPException(404, 'Relato não encontrado')
    return report


def select_pair(connection, report_id, previous_id):
    current = require_report(connection, report_id)
    if previous_id is None:
        earlier = [report for report in repository.list_reports(connection) if report['report_date'] < current['report_date']]
        if not earlier:
            raise HTTPException(422, 'Importe um relato anterior para comparar')
        previous_id = earlier[0]['id']
    previous = require_report(connection, previous_id)
    if previous['report_date'] >= current['report_date']:
        raise HTTPException(422, 'Escolha um relato com data anterior')
    return previous, current


@router.get('')
def list_reports(connection=Depends(get_database_connection)):
    return repository.list_reports(connection)


@router.post('', status_code=201)
def create_report(payload: WeeklyReportCreate, connection=Depends(get_database_connection)):
    try:
        with connection:
            report_id = repository.insert_report(connection, payload)
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, 'Já existe um relato nessa data. Abra-o para editar.') from error
    return require_report(connection, report_id)


@router.get('/{report_id}')
def get_report(report_id: int, connection=Depends(get_database_connection)):
    return require_report(connection, report_id)


@router.put('/{report_id}')
def update_report(report_id: int, payload: WeeklyReportUpdate, connection=Depends(get_database_connection)):
    require_report(connection, report_id)
    try:
        with connection:
            if not repository.update_report(connection, report_id, payload):
                raise HTTPException(409, 'O relato mudou em outra aba. Recarregue antes de editar.')
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, 'Já existe um relato nessa data.') from error
    return require_report(connection, report_id)


@router.delete('/{report_id}', status_code=204)
def delete_report(report_id: int, connection=Depends(get_database_connection)):
    with connection:
        if not repository.delete_report(connection, report_id):
            raise HTTPException(404, 'Relato não encontrado')
    return Response(status_code=204)


@router.get('/{report_id}/comparison')
def get_comparison(report_id: int, previous_report_id: int | None = None, connection=Depends(get_database_connection)):
    previous, current = select_pair(connection, report_id, previous_report_id)
    return repository.find_comparison(connection, previous, current)


@router.post('/{report_id}/compare')
def compare_reports(report_id: int, payload: ComparisonRequest,
                    connection=Depends(get_database_connection), generator=Depends(get_comparison_generator)):
    previous, current = select_pair(connection, report_id, payload.previous_report_id)
    cached = repository.find_comparison(connection, previous, current)
    if cached:
        return cached
    if not generation_lock.acquire(blocking=False):
        raise HTTPException(409, 'Uma comparação está sendo gerada. Aguarde e tente novamente.')
    try:
        cached = repository.find_comparison(connection, previous, current)
        if cached:
            return cached
        # No SQLite write transaction remains open during the external request.
        result, model = generator(previous['content'], current['content'])
        validate_evidence(result, previous['content'], current['content'])
        with connection:
            connection.execute('BEGIN IMMEDIATE')
            for original in (previous, current):
                fresh = repository.find_report(connection, original['id'])
                if fresh != original:
                    raise HTTPException(409, 'Um relato mudou durante a geração. Recarregue e compare novamente.')
            cached = repository.find_comparison(connection, previous, current)
            if cached:
                return cached
            repository.insert_comparison(connection, previous, current, result, model)
        return repository.find_comparison(connection, previous, current)
    except (ComparisonUnavailable, ValueError) as error:
        message = str(error) if isinstance(error, ComparisonUnavailable) else 'A comparação não citou evidências válidas. Tente novamente.'
        raise HTTPException(502, message) from error
    finally:
        generation_lock.release()
