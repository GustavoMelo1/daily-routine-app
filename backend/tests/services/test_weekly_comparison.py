from types import SimpleNamespace
import pytest
from app.services.weekly_comparison import generate_comparison, ComparisonUnavailable


def test_missing_key_does_not_call_provider(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with pytest.raises(ComparisonUnavailable, match='Configure'):
        generate_comparison('before', 'after')


def test_provider_uses_structured_output_and_closes_client(monkeypatch):
    from google import genai
    monkeypatch.setenv('GEMINI_API_KEY', 'fictional-key')
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
            return SimpleNamespace(text='{"summary":"Relatos diferentes","advances":[],"consolidations":[],"pending":[],"limitations":"Sem evidência suficiente"}')
    monkeypatch.setattr(genai, 'Client', Client)
    result, model = generate_comparison('before', 'after')
    assert result.advances == []
    assert calls[0]['config'].response_mime_type == 'application/json'
    assert calls[-1] == 'closed'
    assert model
