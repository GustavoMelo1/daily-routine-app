import os
from pathlib import Path

from db.migrate import migrate


def main():
    database = Path(os.environ['DB_URL'])
    if not database.is_absolute():
        raise ValueError('DB_URL precisa ser absoluto na hospedagem')
    migrate(database)
    os.execvp('python', [
        'python', '-m', 'uvicorn', 'app.main:app',
        '--host', '0.0.0.0', '--port', '8000', '--workers', '1',
        '--root-path', '/api', '--no-access-log',
    ])


if __name__ == '__main__':
    main()
