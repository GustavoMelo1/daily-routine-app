from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_dia_existente():
    resposta = client.get("/dias/2026-07-02")
    assert resposta.status_code == 200
    
def test_criar_dia_duplicado():
    resposta = client.post("/dias", json={
        "data": "2026-07-02",
        "minutos_estudados": 10,
        "frase_do_dia": "teste",
        "autor_frase": "teste",
        "tipo": "normal"
    })
    assert resposta.status_code == 400