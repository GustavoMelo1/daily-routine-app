import json


def rows_as_dicts(cursor):
    keys = [column[0] for column in cursor.description]
    return [dict(zip(keys, row)) for row in cursor.fetchall()]


def list_reports(connection):
    return rows_as_dicts(connection.execute(
        'SELECT id,report_date,title,filename,version,created_at,updated_at FROM weekly_reports ORDER BY report_date DESC'
    ))


def find_report(connection, report_id):
    rows = rows_as_dicts(connection.execute('SELECT * FROM weekly_reports WHERE id=?', (report_id,)))
    return rows[0] if rows else None


def insert_report(connection, payload):
    return connection.execute(
        'INSERT INTO weekly_reports(report_date,title,filename,content) VALUES (?,?,?,?)',
        (payload.report_date.isoformat(), payload.title, payload.filename, payload.content),
    ).lastrowid


def update_report(connection, report_id, payload):
    changed = connection.execute(
        'UPDATE weekly_reports SET report_date=?,title=?,filename=?,content=?,version=version+1,updated_at=CURRENT_TIMESTAMP WHERE id=? AND version=?',
        (payload.report_date.isoformat(), payload.title, payload.filename, payload.content, report_id, payload.version),
    ).rowcount
    if changed:
        connection.execute('DELETE FROM weekly_comparisons WHERE previous_report_id=? OR current_report_id=?', (report_id, report_id))
    return changed


def delete_report(connection, report_id):
    return connection.execute('DELETE FROM weekly_reports WHERE id=?', (report_id,)).rowcount


def find_comparison(connection, previous, current):
    rows = rows_as_dicts(connection.execute(
        'SELECT * FROM weekly_comparisons WHERE previous_report_id=? AND current_report_id=? AND previous_version=? AND current_version=?',
        (previous['id'], current['id'], previous['version'], current['version']),
    ))
    if not rows:
        return None
    result = rows[0]
    result['result'] = json.loads(result.pop('result_json'))
    return result


def insert_comparison(connection, previous, current, result, model):
    connection.execute(
        'INSERT INTO weekly_comparisons(previous_report_id,current_report_id,previous_version,current_version,result_json,model) VALUES (?,?,?,?,?,?)',
        (previous['id'], current['id'], previous['version'], current['version'], result.model_dump_json(), model),
    )
