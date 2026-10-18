"""Phase 3 executable evidence: math integrity, conditional plans and safe local drafts."""
from copy import deepcopy
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import DemoStore, get_store
from app.rescue import compare_quotes, required_sender_budget, generate_rescue, quote_for_budget, QUOTE_BY_ID

@pytest.fixture
def client(tmp_path):
    store=DemoStore(tmp_path/'p3.sqlite3')
    app.dependency_overrides[get_store]=lambda: store
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()


def test_rescue_finds_shortfall_and_conditional_options(client):
    r=client.post('/api/rescue',json={'scenario':'stress'})
    assert r.status_code==200,r.text
    p=r.json()
    assert p['shortfall']['amount']=='1000.00'
    assert p['gap_summary']['amount_myr']=='1000.00'
    assert p['confirmed_solution'] is False
    assert len(p['options'])==3
    assert set(x['id'] for x in p['options'])=={'early_transfer','extension_request','family_topup'}
    assert all(x['is_confirmed'] is False for x in p['options'])
    assert all(x['status']=='conditional' for x in p['options'])
    assert all(x['solves_scenario'] for x in p['options'])
    assert p['options'][2]['sender_estimate']['required_sender_budget_usd']=='243.10'
    assert client.get('/api/demo').json()['funding'][0]['arrivals']['stress']=='2026-10-28'


def test_no_feasible_plan_yields_honest_gap(client):
    res=client.post('/api/rescue',json={'scenario':'stress','capabilities':{
        'earlier_transfer':False,'extension_request':False,'family_topup':False}})
    assert res.status_code==200
    p=res.json()
    assert p['status']=='no_feasible_option'
    assert p['options']==[]
    assert p['gap_summary']['amount_myr']=='1000.00'
    assert p['confirmed_solution'] is False


def test_covered_path_and_date_override(client):
    ok=client.post('/api/rescue',json={'scenario':'base'}).json()
    assert ok['status']=='covered' and ok['gap_summary'] is None
    late=client.post('/api/rescue',json={'scenario':'base','arrival_overrides':{'family':'2026-10-28'}}).json()
    assert late['shortfall']['amount']=='1000.00'


def test_simulated_comparison_equal_budget_and_correct_fees(client):
    r=client.post('/api/transfers/compare',json={'total_sender_budget_usd':'350.00'})
    assert r.status_code==200
    rows=r.json()['quotes']
    assert len(rows)==3
    digital=next(x for x in rows if x['id']=='digital_sample')
    assert digital['recipient_myr']=='1449.00'
    assert digital['converted_usd']=='345.00'
    assert digital['fee_usd']=='5.00'
    assert all(Decimal(x['actual_sender_cost_usd'])<=Decimal('350') for x in rows)
    assert all(x['source']=='SIMULATED' for x in rows)
    assert all(x['is_live'] is False for x in rows)


def test_required_sender_reverse_estimate_is_cent_accurate(client):
    r=client.post('/api/transfers/required-sender',json={'recipient_target_myr':'1000','quote_id':'digital_sample'})
    assert r.status_code==200,r.text
    assert r.json()['required_sender_budget_usd']=='243.10'
    assert Decimal(r.json()['quote']['recipient_myr'])>=Decimal('1000')
    assert Decimal(quote_for_budget(QUOTE_BY_ID['digital_sample'], '243.09')['recipient_myr'])<Decimal('1000')
    for qid in QUOTE_BY_ID:
        out=required_sender_budget('1000',qid)
        assert Decimal(out['quote']['recipient_myr'])>=Decimal('1000')
        assert Decimal(out['quote']['actual_sender_cost_usd'])<=Decimal(out['required_sender_budget_usd'])


def test_transfer_invalid_input_is_rejected(client):
    for invalid in ['0','-20','NaN','Infinity','1000001']:
        assert client.post('/api/transfers/compare',json={'total_sender_budget_usd':invalid}).status_code==422
    assert client.post('/api/transfers/required-sender',json={'recipient_target_myr':'50','quote_id':'fake'}).status_code==422
    assert client.post('/api/rescue',json={'scenario':'stress','capabilities':{'unsafe':True}}).status_code==422


def test_draft_edit_approval_does_not_modify_ledger(client):
    previous=client.get('/api/demo').json()
    creation=client.post('/api/drafts',json={'scenario':'stress','kind':'family'})
    assert creation.status_code==201,creation.text
    item=creation.json()
    assert 'RM 1000.00' in item['body']
    assert item['status']=='draft'
    edited=client.put('/api/drafts/'+item['id'],json={'body':'Please help with tuition fees before 25 October 2026.'})
    assert edited.status_code==200
    assert client.post('/api/drafts/'+item['id']+'/approve',json={'confirmed':False}).status_code==409
    assert client.get('/api/drafts').json()[0]['status']=='draft'
    approved=client.post('/api/drafts/'+item['id']+'/approve',json={'confirmed':True})
    assert approved.status_code==200
    assert approved.json()['status']=='approved'
    assert client.put('/api/drafts/'+item['id'],json={'body':'Try to change an approved draft.'}).status_code==409
    assert client.post('/api/drafts/'+item['id']+'/approve',json={'confirmed':True}).status_code==409
    assert client.get('/api/demo').json()==previous
    events=client.get('/api/audit').json()
    assert any(e['event']=='draft.approved' and e['details']['sent'] is False for e in events)
    assert all('funding.settled'!=e['event'] for e in events)


def test_no_draft_without_shortfall_and_reset_clears_logs(client):
    assert client.post('/api/drafts',json={'scenario':'base'}).status_code==409
    assert client.post('/api/drafts',json={'scenario':'stress','kind':'university'}).status_code==201
    assert len(client.get('/api/drafts').json())==1
    assert len(client.get('/api/audit').json())>=1
    reset=client.post('/api/reset')
    assert reset.status_code==200
    assert client.get('/api/drafts').json()==[]
    assert client.get('/api/audit').json()==[]


def test_client_never_exposes_money_movement_endpoints(client):
    paths=app.openapi()['paths']
    assert not any('/send' in p or '/pay' in p or '/transfer/execute' in p for p in paths)
