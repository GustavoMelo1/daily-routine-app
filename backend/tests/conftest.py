import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database.connection import get_database_connection
from app.main import app

@pytest.fixture
def client(tmp_path):
    caminho_banco = tmp_path / "teste.db"
    caminho_schema = (
        Path(__file__).parent.parent / "db" / "schema.sql"
    )

    conexao_inicial = sqlite3.connect(caminho_banco)
    schema = caminho_schema.read_text(encoding="utf-8")
    conexao_inicial.executescript(schema)
    conexao_inicial.close()

    def conexao_teste():
        con = sqlite3.connect(caminho_banco)
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
        finally:
            con.close()

    app.dependency_overrides[get_database_connection] = conexao_teste

    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_database_connection, None)
