"""CampusFin synthetic-data prototype API. Protect deployments from public writes."""
from copy import deepcopy
import os
from datetime import date
from decimal import Decimal
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .finance import forecast, compare, money, validate, net_myr, amount
from .store import DemoStore, get_store

app = FastAPI(title='CampusFin AI — Prototype API', version='0.3.0',
              description='Synthetic financial data only; not production authenticated; protect deployment.')
# Add your exact Vercel frontend origin in FRONTEND_ORIGINS before deploying a separate API.
# This is a browser access policy, NOT authentication. Do not expose unauthenticated demo writes.
allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
allowed_origins += [origin.strip().rstrip('/') for origin in os.getenv('FRONTEND_ORIGINS', '').split(',') if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins,
                   allow_credentials=False, allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Content-Type'])

class ForecastRequest(BaseModel):
    scenario: str = 'base'
    arrival_overrides: dict[str, str] = Field(default_factory=dict)
    @field_validator('scenario')
    @classmethod
    def scenario_allowed(cls, value):
        if value not in ('best', 'base', 'stress'):
            raise ValueError('Choose best, base or stress')
        return value
    @field_validator('arrival_overrides')
    @classmethod
    def valid_dates(cls, value):
        if len(value)>20:
            raise ValueError('Too many overrides')
        for d in value.values():
            date.fromisoformat(d)
        return value

class FundingInput(BaseModel):
    name: str = Field(min_length=2, max_length=70)
    amount: str
    currency: str
    fee_deducted: str = '0'
    status: str = 'expected'
    arrivals: dict[str,str]
    @field_validator('amount','fee_deducted')
    @classmethod
    def monetary(cls, value):
        value = str(value)
        if money(value)<0:
            raise ValueError('Must be nonnegative')
        return amount(money(value))
    @field_validator('status')
    @classmethod
    def status_allowed(cls, value):
        if value not in ('expected','in_transit'):
            raise ValueError('Editing settled receipts is unavailable: already included in opening cash')
        return value
    @field_validator('arrivals')
    @classmethod
    def arrivals_allowed(cls, value):
        if set(value) != {'best','base','stress'}:
            raise ValueError('Exactly best, base, stress dates are required')
        dates = {k: date.fromisoformat(v) for k,v in value.items()}
        if not dates['best']<=dates['base']<=dates['stress']:
            raise ValueError('Dates must be ordered best <= base <= stress')
        return value

class ObligationInput(BaseModel):
    name: str = Field(min_length=2, max_length=70)
    amount: str
    currency: str = 'MYR'
    due_date: str
    priority: int = Field(default=3, ge=1, le=9)
    @field_validator('amount')
    @classmethod
    def positive_amount(cls, value):
        if money(value)<=0:
            raise ValueError('Amount must be greater than zero')
        return amount(money(value))
    @field_validator('due_date')
    @classmethod
    def valid_date(cls, value):
        date.fromisoformat(value)
        return value


def checked_save(store: DemoStore, data: dict):
    try:
        validate(data, {}, 'base')
        # Multi-currency obligations are not supported by Phase 2. Avoid silent mispricing.
        if any(o['currency']!='MYR' for o in data['obligations']):
            raise ValueError('Obligations must use MYR in this prototype')
        if any(date.fromisoformat(o['due_date'])<=date.fromisoformat(data['as_of']) for o in data['obligations']):
            raise ValueError('An unpaid obligation must be due after the demo as-of date')
        for item in data['funding']:
            if item['status'] != 'settled' and date.fromisoformat(item['arrivals']['base']) <= date.fromisoformat(data['as_of']):
                raise ValueError('Unsettled base arrival date must be after the demo as-of date')
            if item['status'] != 'settled':
                net_myr(item, data['rates'])
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    return store.save(data)

@app.get('/api/health')
def health():
    return {'status':'ok', 'demo':True, 'real_money_enabled':False,
            'storage_mode':'ephemeral_sqlite' if os.getenv('VERCEL') else 'local_sqlite'}

@app.get('/api/demo')
def demo(store: DemoStore=Depends(get_store)):
    return store.get()

@app.get('/api/compare')
def scenarios(store: DemoStore=Depends(get_store)):
    return compare(store.get())

@app.post('/api/forecast')
def calculate(body: ForecastRequest, store: DemoStore=Depends(get_store)):
    try:
        return forecast(store.get(), body.scenario, body.arrival_overrides)
    except (ValueError, KeyError) as exc:
        raise HTTPException(422, str(exc)) from exc

def _create_proof(data:dict,scenario:str,overrides:dict):
    try:
        result=forecast(data,scenario,overrides)
        gap=result['next_shortfall']
        remaining=[o for o in data['obligations'] if o['due_date']>data['as_of']]
        if not remaining:
            return {'status':'covered','scenario':scenario,'rows':[], 'currency':'MYR','projected_available':data['opening_cash'], 'assumptions':result['assumptions']}
        # Trace the first detected gap; if covered, trace through the last listed bill.
        due=gap['due_date'] if gap else max(x['due_date'] for x in remaining)
        rows=[{'label':'Opening cash (includes settled receipts)','date':data['as_of'],
               'signed_amount':data['opening_cash'],'kind':'confirmed'}]
        for o in data['obligations']:
            if data['as_of']<o['due_date']<=due:
                rows.append({'label':o['name'],'date':o['due_date'],
                             'signed_amount':amount(-money(o['amount'])),'kind':'obligation'})
        for f in data['funding']:
            if f['status']=='settled': continue
            arrival=overrides.get(f['id'],f['arrivals'][scenario])
            if data['as_of']<arrival<=due:
                rows.append({'label':f['name']+' (projected)','date':arrival,
                             'signed_amount':amount(net_myr(f,data['rates'])),'kind':'assumption'})
        total=sum((Decimal(x['signed_amount']) for x in rows),Decimal('0'))
        return {'status':'at_risk' if gap else 'covered','scenario':scenario,
                'obligation_id':gap['obligation_id'] if gap else None,
                'due_date':due,'rows':rows,'projected_available':amount(total),
                'gap':gap['amount'] if gap else '0.00','currency':'MYR','assumptions':result['assumptions']}
    except (ValueError,KeyError) as exc:
        raise HTTPException(422,str(exc)) from exc

@app.get('/api/proof')
def proof(scenario: str='base', arrival_date: str|None=None, store: DemoStore=Depends(get_store)):
    return _create_proof(store.get(),scenario,{'family':arrival_date} if arrival_date else {})

@app.post('/api/proof')
def proof_for_scenario(body:ForecastRequest,store:DemoStore=Depends(get_store)):
    # Ephemeral exact scenario proof. Does not save any user data.
    return _create_proof(store.get(),body.scenario,body.arrival_overrides)

@app.post('/api/funding',status_code=201)
def add_funding(item: FundingInput,store: DemoStore=Depends(get_store)):
    data=deepcopy(store.get())
    if item.currency not in data['rates']:
        raise HTTPException(422,'Unsupported currency in this demonstration')
    new={'id':'f_'+uuid4().hex[:12],**item.model_dump()}
    data['funding'].append(new)
    checked_save(store,data)
    store.audit('funding.created','success',{'record_id':new['id'],'user_ui_action':True,'synthetic':True})
    return new

@app.put('/api/funding/{item_id}')
def update_funding(item_id:str,item:FundingInput,store:DemoStore=Depends(get_store)):
    data=deepcopy(store.get())
    for i,old in enumerate(data['funding']):
        if old['id']==item_id:
            if old['status']=='settled':
                raise HTTPException(409,'Settled historical income is locked to prevent opening balance double-counting')
            if item.currency not in data['rates']:
                raise HTTPException(422,'Unsupported currency in this demonstration')
            data['funding'][i]={'id':item_id,**item.model_dump()}
            checked_save(store,data)
            store.audit('funding.edited','success',{'record_id':item_id,'user_ui_action':True,'synthetic':True})
            return data['funding'][i]
    raise HTTPException(404,'Funding not found')

@app.delete('/api/funding/{item_id}')
def remove_funding(item_id:str,store:DemoStore=Depends(get_store)):
    data=deepcopy(store.get())
    old=next((f for f in data['funding'] if f['id']==item_id),None)
    if not old: raise HTTPException(404,'Funding not found')
    if old['status']=='settled': raise HTTPException(409,'Cannot delete income included in opening cash')
    data['funding']=[f for f in data['funding'] if f['id']!=item_id]
    checked_save(store,data)
    store.audit('funding.deleted','success',{'record_id':item_id,'user_ui_action':True,'synthetic':True})
    return {'deleted':item_id}

@app.post('/api/obligations',status_code=201)
def add_obligation(item:ObligationInput,store:DemoStore=Depends(get_store)):
    data=deepcopy(store.get()); item_id='o_'+uuid4().hex[:12]
    new={'id':item_id,**item.model_dump()};data['obligations'].append(new)
    checked_save(store,data)
    store.audit('obligation.created','success',{'record_id':item_id,'user_ui_action':True,'synthetic':True})
    return new

@app.put('/api/obligations/{item_id}')
def update_obligation(item_id:str,item:ObligationInput,store:DemoStore=Depends(get_store)):
    data=deepcopy(store.get())
    for i,old in enumerate(data['obligations']):
        if old['id']==item_id:
            data['obligations'][i]={'id':item_id,**item.model_dump()}
            checked_save(store,data)
            store.audit('obligation.edited','success',{'record_id':item_id,'user_ui_action':True,'synthetic':True})
            return data['obligations'][i]
    raise HTTPException(404,'Obligation not found')

@app.delete('/api/obligations/{item_id}')
def remove_obligation(item_id:str,store:DemoStore=Depends(get_store)):
    data=deepcopy(store.get())
    if not any(o['id']==item_id for o in data['obligations']):raise HTTPException(404,'Obligation not found')
    data['obligations']=[o for o in data['obligations'] if o['id']!=item_id]
    checked_save(store,data)
    store.audit('obligation.deleted','success',{'record_id':item_id,'user_ui_action':True,'synthetic':True})
    return {'deleted':item_id}

@app.post('/api/reset')
def reset_demo(store:DemoStore=Depends(get_store)):
    return store.reset()

# -------- PHASE 3: SAFE, SIMULATED FINANCIAL RECOVERY ----------------------
from .rescue import generate_rescue, compare_quotes, required_sender_budget, draft_text

class RescueRequest(ForecastRequest):
    capabilities: dict[str, bool] = Field(default_factory=dict)
    @field_validator('capabilities')
    @classmethod
    def known_capabilities(cls, value):
        if set(value) - {'earlier_transfer','extension_request','family_topup'}:
            raise ValueError('Unknown rescue capability')
        return value

class TransferRequest(BaseModel):
    total_sender_budget_usd: str
    @field_validator('total_sender_budget_usd')
    @classmethod
    def valid_budget(cls, value):
        if money(value) <= 0 or money(value) > 1000000:
            raise ValueError('Budget must be positive and no more than USD 1,000,000')
        return str(value)

class SenderRequest(BaseModel):
    recipient_target_myr: str
    quote_id: str = 'digital_sample'
    @field_validator('recipient_target_myr')
    @classmethod
    def valid_target(cls,value):
        if money(value) <= 0 or money(value) > 1000000:
            raise ValueError('Target must be positive and no more than RM 1,000,000')
        return str(value)

class DraftRequest(RescueRequest):
    kind: str = 'family'
    @field_validator('kind')
    @classmethod
    def valid_kind(cls, value):
        if value not in ('family', 'university'):
            raise ValueError('Draft kind must be family or university')
        return value

class EditDraftRequest(BaseModel):
    body: str = Field(min_length=10, max_length=3000)

class ApprovalRequest(BaseModel):
    confirmed: bool

@app.post('/api/rescue')
def rescue(body:RescueRequest,store:DemoStore=Depends(get_store)):
    try:
        response=generate_rescue(store.get(), body.scenario, body.arrival_overrides, body.capabilities)
        store.audit('rescue.simulated','success',{'scenario':body.scenario,'status':response['status'],'no_money_moved':True})
        return response
    except (ValueError,KeyError,OverflowError) as exc:
        raise HTTPException(422,str(exc)) from exc

@app.post('/api/transfers/compare')
def transfers(body:TransferRequest):
    try: return compare_quotes(body.total_sender_budget_usd)
    except (ValueError,KeyError,OverflowError) as exc: raise HTTPException(422,str(exc)) from exc

@app.post('/api/transfers/required-sender')
def required_sender(body:SenderRequest):
    try: return required_sender_budget(body.recipient_target_myr,body.quote_id)
    except (ValueError,KeyError,OverflowError) as exc: raise HTTPException(422,str(exc)) from exc

@app.post('/api/drafts',status_code=201)
def create_draft(body:DraftRequest,store:DemoStore=Depends(get_store)):
    try:
        rescue_result=generate_rescue(store.get(),body.scenario,body.arrival_overrides,body.capabilities)
        gap=rescue_result['gap_summary']
        if not gap: raise HTTPException(409,'No identified shortfall in the selected simulation')
        return store.create_draft(draft_text(gap,body.kind),body.kind,body.scenario,gap)
    except (ValueError,KeyError,OverflowError) as exc:
        raise HTTPException(422,str(exc)) from exc

@app.get('/api/drafts')
def drafts(store:DemoStore=Depends(get_store)):
    return store.list_drafts()

@app.put('/api/drafts/{draft_id}')
def update_draft(draft_id:str,body:EditDraftRequest,store:DemoStore=Depends(get_store)):
    try:
        row=store.edit_draft(draft_id,body.body)
        if row is None: raise HTTPException(404,'Draft not found')
        return row
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@app.post('/api/drafts/{draft_id}/approve')
def approve_draft(draft_id:str,body:ApprovalRequest,store:DemoStore=Depends(get_store)):
    try:
        row=store.approve_draft(draft_id,body.confirmed)
        if row is None: raise HTTPException(404,'Draft not found')
        return row
    except ValueError as exc: raise HTTPException(409,str(exc)) from exc

@app.get('/api/audit')
def audit_events(store:DemoStore=Depends(get_store)):
    return store.list_events()

# No API endpoint sends an email, executes a transfer, or marks synthetic funding settled.

# -------- PHASE 4: BOUNDED GEMINI AI COPILOT (READ-ONLY TOOLS) -----------
import os
from .copilot import run_copilot, DEFAULT_MODEL

class ChatHistoryItem(BaseModel):
    role: str
    text: str = Field(max_length=500)
    @field_validator('role')
    @classmethod
    def valid_role(cls,value):
        if value not in ('user','assistant'):
            raise ValueError('Unsupported chat role')
        return value

class CopilotRequest(ForecastRequest):
    message: str = Field(min_length=2, max_length=1200)
    history: list[ChatHistoryItem] = Field(default_factory=list,max_length=4)

@app.get('/api/agent/status')
def agent_status():
    # Never return the API key, even partially.
    return {'gemini_configured':bool(os.getenv('GEMINI_API_KEY')),
            'model':os.getenv('GEMINI_MODEL',DEFAULT_MODEL),
            'mode_without_key':'offline_guide',
            'tool_permissions':'read_only',
            'supports_real_payments':False,
            'synthetic_data_only':True}

@app.post('/api/agent/chat')
def agent_chat(body:CopilotRequest,store:DemoStore=Depends(get_store)):
    try:
        # The caller controls a *scenario*, not a persistent record. Validate
        # against the finance engine before invoking the model or creating logs.
        data=store.get()
        forecast(data,body.scenario,body.arrival_overrides)
        response=run_copilot(
            message=body.message,data=data,scenario=body.scenario,
            overrides=body.arrival_overrides,
            history=[item.model_dump() for item in body.history],
            api_key=os.getenv('GEMINI_API_KEY'),
            model=os.getenv('GEMINI_MODEL',DEFAULT_MODEL))
        store.audit('agent.turn', 'blocked' if response['mode']=='blocked' else 'success',
                    {'mode':response['mode'],'scenario':body.scenario,
                     'tools':[t['name'] for t in response['tool_trace']],
                     'scenario_context':{'source':response.get('context',{}).get('source'),
                                         'arrival_overrides':response.get('context',{}).get('arrival_overrides',{})},
                     'no_ledger_mutation':True,'no_external_action':True})
        return response
    except (ValueError,KeyError,OverflowError) as exc:
        raise HTTPException(422,str(exc)) from exc

# -------- WOW LAB (Phase 4 enhancement): DETERMINISTIC & READ-ONLY --------
from .wow import essential_guard, enhanced_rescue, decision_xray, time_machine, fx_shock, chaos_lab

class WowRequest(ForecastRequest):
    essential_reserve_myr: str = '250.00'
    @field_validator('essential_reserve_myr')
    @classmethod
    def valid_reserve(cls, value):
        v = money(value)
        if v < 0 or v > 10000:
            raise ValueError('Reserve must be between RM 0 and RM 10,000')
        return amount(v)

class WowRescueRequest(WowRequest):
    capabilities: dict[str, bool] = Field(default_factory=dict)
    @field_validator('capabilities')
    @classmethod
    def wow_capabilities(cls,value):
        if set(value) - {'earlier_transfer', 'extension_request', 'family_topup'}:
            raise ValueError('Unknown rescue capability')
        return value

class WowFxRequest(ForecastRequest):
    percent_change: str = '0'
    @field_validator('percent_change')
    @classmethod
    def valid_fx_change(cls,value):
        change=Decimal(str(value))
        if not change.is_finite() or change < -20 or change > 20:
            raise ValueError('Shock must range from -20 to +20 percent')
        return str(change)

@app.post('/api/wow/essential-guard')
def essential_safety(body:WowRequest,store:DemoStore=Depends(get_store)):
    try: return essential_guard(store.get(),body.scenario,body.arrival_overrides,body.essential_reserve_myr)
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex

@app.post('/api/wow/rescue-solver')
def rescue_safety(body:WowRescueRequest,store:DemoStore=Depends(get_store)):
    try: return enhanced_rescue(store.get(),body.scenario,body.arrival_overrides,
                                body.essential_reserve_myr,body.capabilities)
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex

@app.post('/api/wow/decision-xray')
def decision_insights(body:ForecastRequest,store:DemoStore=Depends(get_store)):
    try: return decision_xray(store.get(),body.scenario,body.arrival_overrides)
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex

@app.post('/api/wow/time-machine')
def crisis_time_machine(body:WowRequest,store:DemoStore=Depends(get_store)):
    try: return time_machine(store.get(),body.essential_reserve_myr)
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex

@app.post('/api/wow/fx-shock')
def currency_shock(body:WowFxRequest,store:DemoStore=Depends(get_store)):
    try: return fx_shock(store.get(),body.scenario,body.arrival_overrides,body.percent_change)
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex

@app.post('/api/wow/chaos-lab')
def run_chaos_lab(store:DemoStore=Depends(get_store)):
    try:
        response=chaos_lab()
        store.audit('wow.chaos_lab_ran','success',{'passed':response['passed'],'total':response['total'],
                    'synthetic_fixture_only':True,'no_ledger_changes':True})
        return response
    except (ValueError, KeyError, OverflowError) as ex: raise HTTPException(422,str(ex)) from ex
