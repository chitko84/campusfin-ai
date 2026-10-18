from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient
from app.finance import forecast, compare, net_myr, money
from app.main import app

DATA = json.loads((Path(__file__).parents[1] / 'app' / 'demo_data.json').read_text())
client = TestClient(app)


def at_day(result, date):
    return next(x for x in result['timeline'] if x['date'] == date)


def test_normal_case_all_bills_covered():
    r=forecast(DATA,'base')
    assert r['shortfalls']==[]
    assert at_day(r,'2026-10-25')['projected_available']=='449.00'


def test_delayed_funding_causes_1000_gap():
    r=forecast(DATA,'stress')
    assert r['next_shortfall']['obligation_id']=='tuition'
    assert r['next_shortfall']['amount']=='1000.00'
    assert at_day(r,'2026-10-18')['projected_available']=='500.00'
    assert at_day(r,'2026-10-25')['projected_available']=='-1000.00'


def test_settled_wages_not_counted_twice():
    a=forecast(DATA,'base')
    changed=deepcopy(DATA)
    changed['funding']=[f for f in changed['funding'] if f['id'] != 'wages']
    b=forecast(changed,'base')
    assert a['timeline']==b['timeline']


def test_normal_funding_fee_math():
    assert net_myr(DATA['funding'][0],DATA['rates']) == Decimal('1449.00')


def test_date_override_updates_scenario_without_mutating_fixture():
    a=forecast(DATA,'base',{'family':'2026-10-28'})
    b=forecast(DATA,'base')
    assert a['next_shortfall']['amount']=='1000.00'
    assert b['shortfalls']==[]


def test_expenses_are_counted_once_and_no_real_payment_executes():
    r=forecast(DATA,'stress')
    assert at_day(r,'2026-10-25')['obligations_due']=='1500.00'
    assert r['opening_cash']=='1200.00'
    assert r['rates_kind']=='SIMULATED'


def test_reject_negative_values_and_unknown_currency():
    bad=deepcopy(DATA); bad['obligations'][0]['amount']='-1'
    with pytest.raises(ValueError): forecast(bad)
    bad=deepcopy(DATA); bad['funding'][0]['currency']='EUR'
    with pytest.raises(ValueError): forecast(bad)


def test_unknown_item_and_invalid_scenario_rejected():
    with pytest.raises(ValueError): forecast(DATA,'base',{'unknown':'2026-10-28'})
    with pytest.raises(ValueError): forecast(DATA,'unknown')


def test_float_money_rejected():
    with pytest.raises(ValueError): money(0.1)


def test_api_health_and_forecast():
    assert client.get('/api/health').json()['real_money_enabled'] is False
    r=client.post('/api/forecast',json={'scenario':'stress'})
    assert r.status_code==200
    assert r.json()['next_shortfall']['amount']=='1000.00'
    assert client.post('/api/forecast',json={'scenario':'unknown'}).status_code==422
    assert client.post('/api/forecast',json={'arrival_overrides':{'x':'2026-10-18'}}).status_code==422


def test_scenario_compare():
    j=client.get('/api/compare').json()
    assert set(j)=={'best','base','stress'}
    assert j['base']['next_shortfall'] is None
    assert j['stress']['next_shortfall']['amount']=='1000.00'
