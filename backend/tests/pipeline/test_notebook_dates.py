import pytest
from pipeline.dates import normalize_notebook_date
from pipeline.payloads import build_import_payload


@pytest.mark.parametrize('value', ['12/10/2020', '12-10-2020', '2020/10/12', '2020-10-12'])
def test_normalizes_explicit_date(value):
    assert normalize_notebook_date(value) == '2020-10-12'


@pytest.mark.parametrize('value', [None, '12/10', '31/02/2020'])
def test_missing_or_invalid_date_is_quarantined_not_replaced_with_today(value):
    result = build_import_payload({'dias': [{'data': value, 'minutos_estudados': 60,
                                           'itens': [{'texto': 'SQL', 'status': 'feito'}]}]})
    assert result['days'] == []
    assert result['quarantine_days'][0]['data'] == value
