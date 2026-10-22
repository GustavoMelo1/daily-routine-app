import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


def create_backup(database_path, output_directory):
    source = Path(database_path).resolve()
    if not source.is_file():
        raise FileNotFoundError('Banco de origem não encontrado')
    directory = Path(output_directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = directory / f'{source.stem}-{stamp}.sqlite3'
    with destination.open('xb'):
        pass
    original = sqlite3.connect(f'{source.as_uri()}?mode=ro', uri=True)
    backup = sqlite3.connect(destination)
    try:
        original.backup(backup)
        if backup.execute('PRAGMA integrity_check').fetchone() != ('ok',):
            raise RuntimeError('O backup não passou na verificação de integridade')
    finally:
        backup.close()
        original.close()
    return destination


def main():
    backend = Path(__file__).resolve().parents[1]
    load_dotenv(backend / '.env')
    parser = argparse.ArgumentParser(description='Criar uma cópia consistente do SQLite')
    parser.add_argument('--database', default=os.getenv('DB_URL', 'db/rotina.db'))
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(args.database)
    if not source.is_absolute():
        source = backend / source
    print(create_backup(source, args.output))


if __name__ == '__main__':
    main()
