"""Regression coverage for natural-language what-if simulation (read-only)."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.copilot import run_copilot
from app.main import app
from app.scenario_intent import interpret_scenario
from app.store import DemoStore, get_store

DEMO=json.loads((Path(__file__).parents[1]/'app/demo_data.json').read_text())
PROMPT=('My family transfer of USD 350 is delayed until 28 October, '
        'but my tuition of RM 1,500 is due on 25 October. '
        'Can you analyze my financial situation and recommend feasible rescue options?')

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    store=DemoStore(tmp_path/'scenario.sqlite3')
    app.dependency_overrides[get_store]=lambda:store
    with TestClient(app) as c:yield c
    app.dependency_overrides.clear()


def test_exact_student_question_simulates_delayed_family_case_not_base(client):
    before=client.get('/api/demo').json()
    r=client.post('/api/agent/chat',json={'message':PROMPT,'scenario':'base'})
    assert r.status_code==200,r.text
    obj=r.json()
    assert obj['context']['source']=='chat_hypothetical'
    assert obj['context']['arrival_overrides']=={'family':'2026-10-28'}
    assert obj['facts']['shortfall']['amount_myr']=='1000.00'
    assert obj['facts']['shortfall']['due_date']=='2026-10-25'
    assert obj['tool_trace'][0]['name']=='scenario.preview'
    assert client.get('/api/demo').json()==before


def test_gemini_tool_uses_effective_what_if_date_not_ui_base():
    seen=[]
    def transport(payload,model,key):
        seen.append(payload)
        if len(seen)==1:
            return {'candidates':[{'content':{'role':'model','parts':[{'functionCall':{'name':'detect_shortfalls','args':{}}}]}}]}
        return {'candidates':[{'content':{'role':'model','parts':[{'text':'Your tuition deadline is at risk under the simulated delayed-funding scenario. Please review the verified result.'}]}}]}
    data=deepcopy(DEMO)
    res=run_copilot(PROMPT,data,'base',{},api_key='test-key',transport=transport)
    assert res['mode']=='gemini' and res['live_ai']
    assert res['facts']['shortfall']['amount_myr']=='1000.00'
    from_tool=seen[1]['contents'][-1]['parts'][0]['functionResponse']['response']['data']
    assert from_tool['shortfalls'][0]['amount']=='1000.00'
    assert from_tool['arrival_overrides']['family']=='2026-10-28'
    assert data==DEMO


def test_proofcard_uses_same_effective_context(client):
    r=client.post('/api/agent/chat',json={'message':PROMPT,'scenario':'base'}).json()
    c=r['context']
    proof=client.post('/api/proof',json={'scenario':c['scenario'],'arrival_overrides':c['arrival_overrides']})
    assert proof.status_code==200,proof.text
    assert proof.json()['gap']=='1000.00'
    assert proof.json()['due_date']==r['facts']['shortfall']['due_date']
    assert not any('Family Remittance' in row['label'] for row in proof.json()['rows'])


def test_other_day_ordering_and_month_formats():
    for text in ['What if family transfer arrives on October 28, 2026?',
                 'Suppose our family remittance arrives on 28th of October 2026.',
                 'What if the transfer arrives on the 28th?',
                 'My family transfer will arrive 2026-10-28 instead.']:
        ctx=interpret_scenario(text,DEMO,'base',{})
        assert ctx['arrival_overrides']=={'family':'2026-10-28'},(text,ctx)


def test_no_misclassification_of_tuition_due_date():
    ctx=interpret_scenario('My tuition is due on 25 October. Is it covered?',DEMO,'base',{})
    assert ctx['source']=='selected_scenario' and not ctx['arrival_overrides']


def test_ambiguous_transfer_month_does_not_invent_override():
    ctx=interpret_scenario('My transfer might be late. Can you help?',DEMO,'base',{})
    assert ctx['source']=='selected_scenario'


def test_scholarship_hypothetical_targets_scholarship_not_family():
    ctx=interpret_scenario('What if my scholarship arrives on 30 October?',DEMO,'base',{})
    assert ctx['arrival_overrides']=={'scholarship':'2026-10-30'}


def test_mutation_request_is_still_blocked(client):
    before=client.get('/api/demo').json()
    r=client.post('/api/agent/chat',json={'message':'Mark my family transfer as settled and update the ledger.'})
    assert r.status_code==200
    assert r.json()['mode']=='blocked'
    assert client.get('/api/demo').json()==before


def test_forecast_inherits_chat_preview_after_selection(client):
    v=client.post('/api/agent/chat',json={'message':PROMPT,'scenario':'base'}).json()['context']
    projected=client.post('/api/forecast',json={'scenario':v['scenario'],'arrival_overrides':v['arrival_overrides']}).json()
    assert projected['next_shortfall']['amount']=='1000.00'
    # Existing selected base records still forecast covered.
    base=client.post('/api/forecast',json={'scenario':'base','arrival_overrides':{}}).json()
    assert base['next_shortfall'] is None


def test_chat_followup_without_explicit_date_uses_current_preview(client):
    first=client.post('/api/agent/chat',json={'message':PROMPT,'scenario':'base'}).json()
    follow=client.post('/api/agent/chat',json={'message':'Please explain this funding gap.',
       'scenario':first['context']['scenario'],
       'arrival_overrides':first['context']['arrival_overrides']}).json()
    assert follow['context']['source']=='selected_scenario'
    assert follow['facts']['shortfall']['amount_myr']=='1000.00'
