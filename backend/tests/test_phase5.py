from fastapi.testclient import TestClient
from app.main import app
from app.finance import money
import pytest

client=TestClient(app)

@pytest.mark.parametrize('bad', ['not-a-number', '99999999999999999999999', 'NaN', 'Infinity'])
def test_invalid_money_is_client_validation_error_not_server_crash(bad):
    with pytest.raises(ValueError):
        money(bad)

@pytest.mark.parametrize('bad', ['not-a-number', '99999999999999999999999', 'NaN'])
def test_invalid_funding_is_rejected_safely(bad):
    payload={'name':'Invalid Amount','currency':'MYR','amount':bad,'fee_deducted':'0','status':'expected',
             'arrivals':{'best':'2026-10-20','base':'2026-10-21','stress':'2026-10-22'}}
    r=client.post('/api/funding',json=payload)
    assert r.status_code==422


def test_demo_status_discloses_local_only():
    r=client.get('/api/health')
    assert r.status_code==200
    assert r.json()['real_money_enabled'] is False


def test_agent_status_never_discloses_key(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','secret-stays-on-server')
    r=client.get('/api/agent/status')
    assert r.status_code==200
    assert 'secret-stays-on-server' not in r.text
