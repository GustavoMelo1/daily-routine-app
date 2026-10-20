from types import SimpleNamespace
import pytest
from app.services.weekly_comparison import generate_comparison, ComparisonUnavailable


def test_missing_key_does_not_call_provider(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with pytest.raises(ComparisonUnavailable, match='Configure'):
        generate_comparison('before', 'after')


def test_provider_uses_structured_output_and_closes_client(monkeypatch):
    from google import genai
    from app.schemas.weekly_report import WeeklyProgress
    monkeypatch.setenv('GEMINI_API_KEY', 'fictional-key')
    monkeypatch.setenv('GEMINI_COMPARISON_MODEL', 'test-model')
    calls = []
    class Client:
        def __init__(self, **kwargs):
            assert kwargs['http_options'].timeout == 90000
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            calls.append('closed')
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(text=WeeklyProgress(summary='Relatos diferentes', advances=[], consolidations=[], pending=[], limitations='Sem evidência suficiente').model_dump_json())
    monkeypatch.setattr(genai, 'Client', Client)
    result, model = generate_comparison('before', 'after')
    assert result.advances == []
    assert calls[0]['config'].response_schema is WeeklyProgress
    assert calls[0]['config'].response_mime_type == 'application/json'
    assert calls[-1] == 'closed'
    assert model == 'test-model'


@pytest.mark.parametrize('status, message', [(401, 'recusou a chave'), (403, 'Acesso negado'), (429, 'cota'), (404, 'HTTP 404'), (503, 'indisponível')])
def test_provider_errors_are_safe(monkeypatch, status, message, caplog):
    from google import genai
    from google.genai.errors import APIError
    monkeypatch.setenv('GEMINI_API_KEY', 'fictional-secret')
    class Client:
        def __init__(self, **kwargs):
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def generate_content(self, **kwargs):
            raise APIError(status, {'error': {'code': status, 'message': 'fictional-secret private-report'}})
    monkeypatch.setattr(genai, 'Client', Client)
    with pytest.raises(ComparisonUnavailable, match=message) as caught:
        generate_comparison('private-report', 'current')
    assert 'fictional-secret' not in str(caught.value) + caplog.text
    assert 'private-report' not in str(caught.value) + caplog.text


@pytest.mark.parametrize('invalid_evidence', [False, True])
def test_refusal_or_unverified_evidence_is_not_accepted(monkeypatch, invalid_evidence):
    from google import genai
    from app.schemas.weekly_report import WeeklyProgress
    monkeypatch.setenv('GEMINI_API_KEY', 'fictional-key')
    result = WeeklyProgress.model_validate({
        'summary': 'Resumo', 'advances': [{
            'title': 'Novo assunto', 'explanation': 'Explicação',
            'previous_evidence': None, 'current_evidence': 'citação inventada',
        }], 'consolidations': [], 'pending': [], 'limitations': 'Só relatos',
    }) if invalid_evidence else None
    class Client:
        def __init__(self, **kwargs):
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=result.model_dump_json() if result else None)
    monkeypatch.setattr(genai, 'Client', Client)
    with pytest.raises(ComparisonUnavailable, match='validação' if invalid_evidence else 'completa'):
        generate_comparison('before', 'after')
