"""Phase 4 WOW upgrade regressions: real deterministic calculations, no fake passes."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import DemoStore, get_store
from app.wow import essential_guard, enhanced_rescue, decision_xray, time_machine, fx_shock, chaos_lab

SEED=json.loads((Path(__file__).resolve().parents[1]/'app/demo_data.json').read_text())


def test_essential_guard_covered_bill_can_still_be_unsafe():
    guard=essential_guard(SEED,'best',reserve='500')
    rent,tuition=guard['checks']
    assert rent['meets_guard']
    assert not tuition['meets_guard']
    assert tuition['projected_after_myr']=='449.00'
    assert tuition['reserve_deficit_myr']=='51.00'


def test_essential_guard_rejects_unreasonable_reserves():
    for invalid in ('-1','10000.01','Infinity'):
        with pytest.raises(ValueError): essential_guard(SEED,reserve=invalid)


def test_rescue_solver_rejects_deceptive_plan_and_protects_essentials():
    r=enhanced_rescue(SEED,'stress',reserve='500.00')
    assert r['shortfall']['amount']=='1000.00'
    topup=next(o for o in r['enhanced_options'] if o['id']=='family_topup')
    assert topup['clears_all_bills'] and not topup['passes_essential_guard']
    assert topup['guard_decision']=='ESSENTIAL_RESERVE_BREACH'
    guarded=next(o for o in r['enhanced_options'] if o['id']=='reserve_protected_topup')
    assert guarded['clears_all_bills'] and guarded['passes_essential_guard']
    assert guarded['guard_decision']=='CONDITIONALLY_FEASIBLE'
    assert guarded['essential_reserve_myr']=='500.00'
    assert guarded['still_requires_confirmation'] is True


def test_guard_solver_no_external_confirmation_claimed():
    r=enhanced_rescue(SEED,'stress',reserve='300.00')
    assert not r['confirmed_solution']
    assert all(o.get('still_requires_confirmation') is True for o in r['enhanced_options'])


def test_xray_identifies_delayed_usd_family_transfer():
    result=decision_xray(SEED,'stress')
    assert result['gap_myr']=='1000.00'
    assert result['scenario_change_myr']=='-1449.00'
    causes=[x for x in result['causes'] if x['id']=='family']
    assert len(causes)==1 and causes[0]['affects_target_deadline']
    assert causes[0]['baseline_date']=='2026-10-18'
    assert causes[0]['scenario_date']=='2026-10-28'


def test_time_machine_variants_consistent_and_immutable():
    original=deepcopy(SEED)
    result=time_machine(SEED,reserve='250')
    assert [x['id'] for x in result['variants']]==['on_time','delayed','not_arriving','fx_drop']
    assert result['variants'][0]['gap_myr']=='0.00'
    assert result['variants'][1]['gap_myr']=='1000.00'
    assert SEED==original


def test_fx_shock_is_deterministic_and_not_forecast():
    result=fx_shock(SEED,'best',percent='-5')
    assert result['family_before_myr']=='1449.00'
    assert result['family_after_myr']=='1376.55'
    assert result['family_difference_myr']=='-72.45'
    assert 'not a currency prediction' in result['disclaimer']


def test_fx_shock_rejects_out_of_range():
    for pct in ('-21','21','NaN'):
        with pytest.raises(ValueError): fx_shock(SEED,'base',percent=pct)


def test_chaos_lab_executes_seven_real_checks():
    x=chaos_lab()
    assert x['total']==7 and x['passed']==7
    assert len(x['tests'])==7
    assert all(x['pass'] for x in x['tests'])
    assert {x['id'] for x in x['tests']}=={'ON_TIME','DELAY','ESSENTIALS','FEES','NO_MUTATION','FX_SHOCK','INVALID_RATE'}


@pytest.fixture
def client(tmp_path):
    demo=DemoStore(tmp_path/'wow-test.sqlite3')
    app.dependency_overrides[get_store]=lambda:demo
    with TestClient(app) as testclient:
        yield testclient,demo
    app.dependency_overrides.clear()


def test_wow_api_endpoints_are_callable_and_read_only(client):
    c,store=client
    prior=store.get()
    body={'scenario':'stress','arrival_overrides':{},'essential_reserve_myr':'500.00'}
    for name in ('essential-guard','rescue-solver','decision-xray','time-machine','fx-shock'):
        payload=body if name!='fx-shock' else {'scenario':'stress','percent_change':'-5'}
        r=c.post('/api/wow/'+name,json=payload)
        assert r.status_code==200, (name,r.text)
    assert store.get()==prior
    r=c.post('/api/wow/chaos-lab',json={})
    assert r.status_code==200 and r.json()['passed']==7
    assert store.get()==prior


def test_wow_api_input_validation(client):
    c,_=client
    assert c.post('/api/wow/essential-guard',json={'essential_reserve_myr':'-1'}).status_code==422
    assert c.post('/api/wow/fx-shock',json={'percent_change':'100'}).status_code==422
    assert c.post('/api/wow/decision-xray',json={'scenario':'future'}).status_code==422
