"""CampusFin Horizon WOW Lab — deterministic, local-only student finance demonstrations.

This module does not mutate student data, fabricate live quotes, send messages or
invoke a model.  Every scenario and safety result is computed from existing
forecast/rescue primitives with Decimal money values.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
from .finance import amount, forecast, money, net_myr
from .rescue import generate_rescue, compare_quotes, required_sender_budget


def _reserve(value):
    reserve = money(value)
    if reserve < 0 or reserve > Decimal('10000'):
        raise ValueError('Essential living reserve must be between RM 0 and RM 10,000')
    return reserve


def _at(forecast_result, on_date):
    line = next((row for row in forecast_result['timeline'] if row['date'] == on_date), None)
    if not line:
        raise ValueError('Date is outside financial forecast window')
    return Decimal(line['projected_available'])


def _shortfall_summary(result):
    item = result['next_shortfall']
    return {'status': 'at_risk' if item else 'covered',
            'gap_myr': item['amount'] if item else '0.00',
            'due_date': item['due_date'] if item else None,
            'obligation': item['name'] if item else None}


def essential_guard(data, scenario='stress', overrides=None, reserve='250.00'):
    """A safety floor *after* an obligation; not an actual cost or prediction.

    Does not count the reserve as money spent, and does not change the ledger.
    """
    floor = _reserve(reserve)
    current = forecast(data, scenario, overrides or {})
    rows = []
    for bill in sorted(data['obligations'], key=lambda b: (b['due_date'], b.get('priority', 5))):
        if bill['due_date'] <= data['as_of']:
            continue
        after = _at(current, bill['due_date'])
        deficit = max(Decimal('0'), floor - after)
        rows.append({'id': bill['id'], 'obligation': bill['name'], 'due_date': bill['due_date'],
                     'projected_after_myr': amount(after), 'essential_reserve_myr': amount(floor),
                     'reserve_deficit_myr': amount(deficit),
                     'meets_guard': deficit == 0,
                     'reason_code': 'RESERVE_UNDER_MINIMUM' if deficit > 0 else 'RESERVE_PRESERVED'})
    return {'scenario': scenario, 'reserve_myr': amount(floor), 'checks': rows,
            'all_deadlines_protected': all(x['meets_guard'] for x in rows),
            'meaning': 'Student-selected minimum balance to preserve for essentials after each bill. Not a financial recommendation, statistical model, or charge.',
            'assumptions': current['assumptions']}


def enhanced_rescue(data, scenario='stress', overrides=None, reserve='250.00', capabilities=None):
    overrides = overrides or {}
    floor = _reserve(reserve)
    base = generate_rescue(data, scenario, overrides, capabilities)
    checks = essential_guard(data, scenario, overrides, reserve)
    if not base['shortfall']:
        base['essential_guard'] = checks
        base['enhanced_options'] = []
        return base
    gap = base['shortfall']; due = gap['due_date']
    options = []
    for option in base['options']:
        working = deepcopy(data)
        edits = dict(overrides)
        change = option['scenario_change']
        if option['id'] == 'early_transfer':
            edits = change['arrival_overrides']
        elif option['id'] == 'extension_request':
            for bill in working['obligations']:
                if bill['id'] == gap['obligation_id']:
                    bill['due_date'] = change['proposed_due_date']
            # Rescheduled tuition's own date is the relevant check date.
        elif option['id'] == 'family_topup':
            incoming_date = max(date.fromisoformat(data['as_of']) + timedelta(days=1), date.fromisoformat(due) - timedelta(days=1)).isoformat()
            working['funding'].append({'id': 'wow_topup', 'name': 'Hypothetical rescue support',
                 'amount': change['hypothetical_topup_myr'], 'currency': 'MYR', 'fee_deducted': '0',
                 'status': 'expected', 'arrivals': {s: incoming_date for s in ('best','base','stress')}})
        simulated = forecast(working, scenario, edits)
        bill = next(b for b in working['obligations'] if b['id'] == gap['obligation_id'])
        check_day = bill['due_date']
        after = _at(simulated, check_day)
        bills_covered = not simulated['shortfalls']
        essentials_covered = after >= floor
        options.append({**option, 'protected_amount_after_bill_myr': amount(after),
                        'essential_reserve_myr': amount(floor),
                        'essential_reserve_shortfall_myr': amount(max(Decimal('0'), floor-after)),
                        'passes_essential_guard': essentials_covered,
                        'clears_all_bills': bills_covered,
                        'guard_decision': 'CONDITIONALLY_FEASIBLE' if bills_covered and essentials_covered
                            else ('ESSENTIAL_RESERVE_BREACH' if bills_covered else 'BILLS_NOT_COVERED'),
                        'guard_check_date': check_day,
                        'still_requires_confirmation': True})
    # Add a meaningful stronger candidate, sized to protect both tuition and living needs.
    if floor > 0 and (capabilities is None or capabilities.get('family_topup', True)):
        gap_amount = Decimal(gap['amount'])
        missing_plus_reserve = gap_amount + floor
        arrival_date = max(date.fromisoformat(data['as_of']) + timedelta(days=1), date.fromisoformat(due) - timedelta(days=1)).isoformat()
        candidate = deepcopy(data)
        candidate['funding'].append({'id':'wow_reserve_topup', 'name':'Hypothetical tuition-and-essentials support',
            'amount': amount(missing_plus_reserve), 'fee_deducted':'0', 'currency':'MYR',
            'status':'expected', 'arrivals': {s: arrival_date for s in ('best','base','stress')}})
        simulated = forecast(candidate, scenario, overrides)
        after = _at(simulated, due)
        full = not simulated['shortfalls'] and after >= floor
        # If student obligations before tuition already consume part of the reserve,
        # the computed option may be insufficient. Never falsely mark as feasible.
        options.append({'id':'reserve_protected_topup', 'title':'Protect tuition AND essential living funds',
             'category':'amount', 'status':'conditional' if full else 'insufficient',
             'is_confirmed':False,'solves_scenario':full,
             'requirements':['Family/sponsor confirms additional funds are available.',
                             'Funding must actually arrive before the tuition deadline.',
                             'Quote and fee assumptions need independent verification.'],
             'assumption':f'Additional RM {amount(missing_plus_reserve)} arrives by {arrival_date} (hypothetical)',
             'sender_estimate': required_sender_budget(missing_plus_reserve),
             'protected_amount_after_bill_myr':amount(after),
             'essential_reserve_myr':amount(floor),
             'essential_reserve_shortfall_myr':amount(max(Decimal('0'), floor-after)),
             'passes_essential_guard':after>=floor, 'clears_all_bills': not simulated['shortfalls'],
             'guard_decision':'CONDITIONALLY_FEASIBLE' if full else 'INSUFFICIENT',
             'guard_check_date':due, 'still_requires_confirmation':True})
    base['essential_guard'] = checks
    base['enhanced_options'] = options
    base['planning_method'] = 'Rule-based option enumeration and deterministic verification, not mathematical optimization.'
    return base


def decision_xray(data, scenario='stress', overrides=None):
    overrides = overrides or {}
    baseline = forecast(data,'best')
    current = forecast(data,scenario,overrides)
    gap = current['next_shortfall']
    due = gap['due_date'] if gap else (max(b['due_date'] for b in data['obligations']))
    baseline_by_due = _at(baseline,due)
    selected_by_due = _at(current,due)
    causes = []
    for f in data['funding']:
        if f['status'] == 'settled':
            continue
        best = f['arrivals']['best']; actual = overrides.get(f['id'], f['arrivals'][scenario])
        if best != actual:
            received = net_myr(f,data['rates'])
            causes.append({'id':f['id'], 'label':f['name'], 'reason_code':'ARRIVAL_DATE_CHANGED',
                           'baseline_date':best,'scenario_date':actual,
                           'expected_myr':amount(received),
                           'affects_target_deadline': best <= due < actual,
                           'description': ('Funding would be available in the earliest-arrival scenario but not by this deadline.'
                               if best <= due < actual else 'Arrival changes, but may not directly explain this payment gap.')})
    contributing = []
    for bill in sorted(data['obligations'], key=lambda b:b['due_date']):
        if bill['due_date']<=due and bill['due_date']>data['as_of']:
            contributing.append({'label': bill['name'], 'due_date':bill['due_date'],
                                 'amount_myr':bill['amount'], 'reason_code':'OUTSTANDING_OBLIGATION'})
    for f in data['funding']:
        if f['status']!='settled':
            actual = overrides.get(f['id'],f['arrivals'][scenario])
            if data['as_of']<actual<=due:
                contributing.append({'label':f['name'], 'due_date':actual,
                                     'amount_myr':amount(net_myr(f,data['rates'])),
                                     'reason_code':'EXPECTED_NOT_CONFIRMED_FUNDING'})
    return {'status':'at_risk' if gap else 'covered',
            'reason_codes':['UNFUNDED_DEADLINE'] if gap else ['OBLIGATIONS_PROJECTED_COVERED'],
            'baseline':'best', 'scenario':scenario,
            'critical_date':due, 'critical_bill':gap['name'] if gap else None,
            'gap_myr':gap['amount'] if gap else '0.00',
            'opening_cash_myr':amount(money(data['opening_cash'])),
            'baseline_after_myr':amount(baseline_by_due),
            'selected_after_myr':amount(selected_by_due),
            'scenario_change_myr':amount(selected_by_due-baseline_by_due),
            'causes':causes, 'contributing_items':contributing,
            'assumptions':current['assumptions'],
            'disclaimer':'Explanations describe the selected synthetic scenario relative to the earliest-arrival scenario; they are not proofs of real-world causality.'}


def time_machine(data, reserve='250.00'):
    floor=_reserve(reserve)
    variants=[('on_time','On-time remittance','Family support arrives at the earliest declared date','best', None, None),
              ('delayed','Delayed remittance','Family support arrives at the latest declared date','stress',None,None),
              ('not_arriving','Support unavailable','Remove the family remittance in this what-if case','stress','remove',None),
              ('fx_drop','FX rate falls 5%','USD/MYR rate decreases 5% in an illustrative stress test','stress',None,'0.95')]
    results=[]
    for key,title,description,scenario,change,fx in variants:
        testdata=deepcopy(data)
        if change=='remove':testdata['funding']=[f for f in testdata['funding'] if f['id']!='family']
        if fx and 'USD' in testdata['rates']:
            testdata['rates']['USD'] = str(Decimal(testdata['rates']['USD'])*Decimal(fx))
        result=forecast(testdata,scenario)
        gap=_shortfall_summary(result)
        checks=essential_guard(testdata,scenario,reserve=amount(floor))
        results.append({'id':key, 'title':title,'description':description, 'scenario':scenario,
                        **gap,'essentials_protected':checks['all_deadlines_protected'],
                        'end_projected_myr':result['timeline'][-1]['projected_available'],
                        'points':[{'date':r['date'],'available_myr':r['projected_available']} for i,r in enumerate(result['timeline']) if i%3==0 or r['obligations_due']!='0.00'],
                        'source':'DETERMINISTIC_SIMULATION'})
    return {'variants':results,'reserve_myr':amount(floor),
            'disclaimer':'Four hypothetical futures, not probability forecasts. Each simulation is read-only and uses synthetic financial records.'}


def fx_shock(data, scenario='base', overrides=None, percent='0'):
    p=Decimal(str(percent))
    if not p.is_finite() or p < -20 or p>20:
        raise ValueError('FX scenario adjustment must be between -20% and +20%')
    if 'USD' not in data['rates']:
        raise ValueError('USD rate is not configured')
    original=Decimal(str(data['rates']['USD']))
    rate=(original*(Decimal('1')+p/Decimal('100')))
    if rate<=0:raise ValueError('FX rate scenario must remain positive')
    changed=deepcopy(data);changed['rates']['USD']=str(rate)
    baseline=forecast(data,scenario,overrides or {})
    stressed=forecast(changed,scenario,overrides or {})
    family=next((f for f in data['funding'] if f['id']=='family' and f['status']!='settled'),None)
    before=net_myr(family,data['rates']) if family else Decimal('0')
    after=net_myr(family,changed['rates']) if family else Decimal('0')
    return {'percent_change':str(p),'original_rate_myr_per_usd':str(original),
            'scenario_rate_myr_per_usd':format(rate.quantize(Decimal('0.0001')),'.4f'),
            'family_before_myr':amount(before), 'family_after_myr':amount(after),
            'family_difference_myr':amount(after-before),
            'baseline':_shortfall_summary(baseline),'stressed':_shortfall_summary(stressed),
            'source':'SYNTHETIC_FX_STRESS_TEST',
            'disclaimer':'This is a sensitivity test using fictional exchange-rate inputs, not a currency prediction or live quote.'}


def chaos_lab():
    """Execute reproducible independent assertions on canonical Amina fixtures.

    Does not assert these are real-world validations or modify persistent data.
    """
    fixture=json.loads(Path(__file__).with_name('demo_data.json').read_text(encoding='utf-8'))
    cases=[]
    def record(key,title,observed,expected,passed):
        cases.append({'id':key,'name':title,'observed':str(observed),'expected':str(expected),'pass':bool(passed)})
    f=forecast(fixture,'best')
    record('ON_TIME','On-time remittance covers listed bills',f['next_shortfall'] is None,True,f['next_shortfall'] is None)
    s=forecast(fixture,'stress');gap=s['next_shortfall']
    record('DELAY','Late remittance produces RM 1,000 gap',gap['amount'] if gap else 'none','1000.00',gap is not None and gap['amount']=='1000.00')
    e=essential_guard(fixture,'best',reserve='500');tuition=next(x for x in e['checks'] if x['id']=='tuition')
    record('ESSENTIALS','Covered tuition can still violate a living reserve',tuition['reserve_deficit_myr'],'51.00',tuition['reserve_deficit_myr']=='51.00')
    q=compare_quotes('350.00')['quotes']
    record('FEES','All compared quote costs fit equal USD 350 sender budget',all(Decimal(x['actual_sender_cost_usd'])<=350 for x in q if 'actual_sender_cost_usd' in x),True,all(Decimal(x['actual_sender_cost_usd'])<=350 for x in q if 'actual_sender_cost_usd' in x))
    original=json.dumps(fixture,sort_keys=True)
    generate_rescue(fixture,'stress')
    record('NO_MUTATION','Rescue planning cannot modify the input ledger',json.dumps(fixture,sort_keys=True)==original,True,json.dumps(fixture,sort_keys=True)==original)
    z=fx_shock(fixture,'best',percent='-5')
    record('FX_SHOCK','Five percent FX drop reduces USD transfer value',z['family_difference_myr'],'-72.45',z['family_difference_myr']=='-72.45')
    invalid=deepcopy(fixture);invalid['rates']['USD']='0'
    try:
        forecast(invalid,'base'); denied=False
    except ValueError:denied=True
    record('INVALID_RATE','Zero FX rate rejected rather than silently used',denied,True,denied)
    return {'passed':sum(1 for c in cases if c['pass']),'total':len(cases),'tests':cases,
            'scope':'Reproducible built-in tests on the canonical Amina synthetic fixture (not the current edited profile).',
            'disclaimer':'Real assertions executed on-demand; not security certification, real financial validation or independent user testing.'}
