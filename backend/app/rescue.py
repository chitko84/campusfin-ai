"""Phase 3: deterministic, conditional student funding rescue simulations.

No external transfer, payment, message sending or automatically authorized ledger update.
A plan may solve a *scenario*, but is never presented as confirmed funding.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, ROUND_UP, ROUND_DOWN, ROUND_HALF_UP
from .finance import forecast, net_myr, money, amount

QUOTES = (
    {'id': 'digital_sample', 'name': 'Sample Digital Transfer', 'rate': '4.20', 'flat_fee': '5.00', 'percent_fee': '0', 'fee_mode': 'deducted', 'arrival_min_days': 1, 'arrival_max_days': 2},
    {'id': 'bank_sample', 'name': 'Sample Bank Wire', 'rate': '4.12', 'flat_fee': '8.00', 'percent_fee': '0.01', 'fee_mode': 'separate', 'arrival_min_days': 2, 'arrival_max_days': 5},
    {'id': 'remittance_sample', 'name': 'Sample Remittance App', 'rate': '4.16', 'flat_fee': '2.00', 'percent_fee': '0.01', 'fee_mode': 'deducted', 'arrival_min_days': 1, 'arrival_max_days': 4},
)
QUOTE_BY_ID = {q['id']: q for q in QUOTES}


def _positive(value, max_value='1000000'):
    result = money(value)
    if result <= 0 or result > Decimal(max_value):
        raise ValueError('Amount must be positive and at most ' + max_value)
    return result


def quote_for_budget(quote: dict, total_sender_budget) -> dict:
    """Same total sender budget for deducted and separately paid fee cases.

    For separate fees, convert only a principal that can be covered within
    the TOTAL budget: principal + fixed + percentage * principal <= budget.
    """
    budget = _positive(total_sender_budget)
    rate = Decimal(quote['rate']); fixed = money(quote['flat_fee'])
    pct = Decimal(quote['percent_fee'])
    if pct < 0 or pct > Decimal('1') or rate <= 0:
        raise ValueError('Invalid simulated quote')
    if quote['fee_mode'] == 'deducted':
        principal = budget
        fee = (fixed + principal * pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        transfer = principal - fee
        spent = budget
    elif quote['fee_mode'] == 'separate':
        principal = ((budget - fixed) / (1 + pct)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        fee = (fixed + principal * pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        spent = principal + fee
        while spent > budget:  # rounding guard
            principal -= Decimal('0.01')
            fee = (fixed + principal * pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            spent = principal + fee
        transfer = principal
    else:
        raise ValueError('Unsupported fee mode')
    if transfer < 0 or principal <= 0:
        raise ValueError('Budget too small to cover simulated transfer fees')
    received = (transfer * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return {
        'id': quote['id'], 'name': quote['name'], 'rate_myr_per_usd': quote['rate'],
        'fee_mode': quote['fee_mode'], 'flat_fee_usd': quote['flat_fee'],
        'percentage_fee': quote['percent_fee'], 'fee_usd': amount(fee),
        'total_sender_budget_usd': amount(budget), 'actual_sender_cost_usd': amount(spent),
        'principal_usd': amount(principal), 'converted_usd': amount(transfer),
        'recipient_myr': amount(received),
        'arrival_days': [quote['arrival_min_days'], quote['arrival_max_days']],
        'source': 'SIMULATED', 'is_live': False,
        'assumptions': ['Fictional quote for demonstrating arithmetic; not a live provider offer.',
                        'All options compared at equal total sender budgets.',
                        'Arrival days are illustrative estimates, not guarantees.'],
    }


def compare_quotes(budget) -> dict:
    _positive(budget)
    rows = []
    for q in QUOTES:
        try:
            rows.append(quote_for_budget(q, budget))
        except ValueError as ex:
            rows.append({'id': q['id'], 'name': q['name'], 'available': False, 'reason': str(ex), 'source': 'SIMULATED'})
    rows.sort(key=lambda r: Decimal(r.get('recipient_myr', '-1')), reverse=True)
    return {'source': 'SIMULATED', 'currency_pair': 'USD/MYR', 'sender_budget_usd': amount(money(budget)),
            'quotes': rows, 'best_quote_id': next((r['id'] for r in rows if r.get('recipient_myr')), None),
            'disclaimer': 'Not live exchange rates, recommendations, guarantees or payment integrations.'}


def required_sender_budget(target_myr, quote_id='digital_sample') -> dict:
    target = _positive(target_myr)
    if quote_id not in QUOTE_BY_ID:
        raise ValueError('Unknown simulated quote')
    q = QUOTE_BY_ID[quote_id]
    # Find the minimum sender budget in CENTS via monotone integer search.
    low = 1
    high = 1
    target_cents = int(target * 100)
    def net_cents(cents):
        try:
            r = quote_for_budget(q, Decimal(cents) / 100)
            return int(Decimal(r['recipient_myr']) * 100)
        except ValueError:
            return -1
    while net_cents(high) < target_cents:
        high *= 2
        if high > 100_000_000:
            raise ValueError('Funding target exceeds supported simulated transfer sizes')
    while low < high:
        mid = (low+high)//2
        if net_cents(mid) >= target_cents: high = mid
        else: low = mid+1
    row = quote_for_budget(q, Decimal(low)/100)
    return {'recipient_target_myr': amount(target), 'required_sender_budget_usd': amount(Decimal(low)/100),
            'quote': row, 'confirmed': False, 'source': 'SIMULATED'}


def _simulation_result(data, scenario, overrides):
    result = forecast(data, scenario, overrides)
    return {'next_shortfall': result['next_shortfall'],
            'all_obligations_covered': len(result['shortfalls']) == 0,
            'timeline_final': result['timeline'][-1]['projected_available']}


def generate_rescue(data: dict, scenario='stress', overrides=None, capabilities=None) -> dict:
    overrides = overrides or {}
    caps = {'earlier_transfer': True, 'extension_request': True, 'family_topup': True}
    if capabilities: caps.update(capabilities)
    initial = forecast(data, scenario, overrides)
    gap = initial['next_shortfall']
    if not gap:
        return {'scenario': scenario, 'status': 'covered', 'shortfall': None, 'options': [],
                'gap_summary': None, 'disclaimer': 'Projected coverage does not mean received funds are confirmed.'}
    due = date.fromisoformat(gap['due_date']); as_of = date.fromisoformat(data['as_of'])
    target = Decimal(gap['amount'])
    gap_summary = {'amount_myr': amount(target), 'need_by': due.isoformat(),
                   'obligation': gap['name'], 'available_before_myr': gap['available_before'],
                   'explanation': 'Minimum additional amount needed at the flagged obligation, under current assumptions.',
                   'confirmed_solution': False, 'source': 'DETERMINISTIC_FORECAST'}
    options = []

    family = next((f for f in data['funding'] if f['id'] == 'family' and f['status'] != 'settled'), None)
    family_arrival = date.fromisoformat(overrides.get('family', family['arrivals'][scenario])) if family else None
    if caps['earlier_transfer'] and family and family_arrival > due:
        # Do not claim permission or availability: we only compare a possible earlier arrival.
        new_arrival = max(as_of + timedelta(days=1), due - timedelta(days=1))
        o = dict(overrides, family=new_arrival.isoformat())
        simulated = _simulation_result(data, scenario, o)
        options.append({'id':'early_transfer', 'title':'Request an earlier family transfer',
            'category':'timing', 'status':'conditional' if simulated['all_obligations_covered'] else 'insufficient',
            'is_confirmed':False, 'solves_scenario':simulated['all_obligations_covered'],
            'requirements':['Family confirms funds are available and can be sent.',
                            'Actual transfer arrives before the payment deadline.'],
            'assumption':'Family remittance arrives '+new_arrival.isoformat(),
            'scenario_change':{'arrival_overrides':o}, 'outcome':simulated,
            'cta':'Draft a funding request'})
    if caps['extension_request']:
        updated = deepcopy(data)
        # Move the flagged obligation two weeks later, only as a HYPOTHETICAL institution approval.
        new_due = (due + timedelta(days=14)).isoformat()
        for item in updated['obligations']:
            if item['id']==gap['obligation_id']:
                item['due_date']=new_due
        simulated = _simulation_result(updated, scenario, overrides)
        options.append({'id':'extension_request', 'title':'Request a university payment extension',
            'category':'deadline', 'status':'conditional' if simulated['all_obligations_covered'] else 'insufficient',
            'is_confirmed':False, 'solves_scenario':simulated['all_obligations_covered'],
            'requirements':['The university must explicitly approve the extension.',
                            'An unapproved request never changes the real deadline.'],
            'assumption':'Tuition due date hypothetically extended to '+new_due,
            'scenario_change':{'proposed_due_date':new_due}, 'outcome':simulated,
            'cta':'Draft an extension request'})
    if caps['family_topup']:
        sizing = required_sender_budget(target)
        updated = deepcopy(data)
        candidate_arrival = max(as_of+timedelta(days=1), due-timedelta(days=1))
        updated['funding'].append({'id':'simulated_topup','name':'Hypothetical family top-up',
            'amount':amount(target), 'currency':'MYR', 'fee_deducted':'0', 'status':'expected',
            'arrivals':{s:candidate_arrival.isoformat() for s in ('best','base','stress')}})
        simulated = _simulation_result(updated, scenario, overrides)
        options.append({'id':'family_topup','title':'Request additional family support',
            'category':'amount', 'status':'conditional' if simulated['all_obligations_covered'] else 'insufficient',
            'is_confirmed':False,'solves_scenario':simulated['all_obligations_covered'],
            'requirements':['A family member must confirm ability to send the additional amount.',
                            'Transfer amount, fees and arrival time must be checked before use.'],
            'assumption':'Hypothetical additional RM '+amount(target)+' received by '+candidate_arrival.isoformat(),
            'scenario_change':{'hypothetical_topup_myr':amount(target)}, 'outcome':simulated,
            'sender_estimate':sizing, 'cta':'Draft a funding request'})
    has_conditional = any(o['solves_scenario'] for o in options)
    return {'scenario':scenario, 'status':'conditional_options' if has_conditional else 'no_feasible_option',
            'shortfall':gap, 'gap_summary':gap_summary,'options':options,
            'confirmed_solution':False,
            'disclaimer':'All recovery options are simulations, not approved arrangements or completed payments. No funds move.'}


def draft_text(gap_summary, kind='family', option_id=None):
    due = gap_summary['need_by']; amount_myr=gap_summary['amount_myr']
    if kind=='university':
        return (f'Hello Student Finance Office, I am requesting an extension for my {gap_summary["obligation"].lower()} '
                f'currently due on {due}. Under my current funding assumptions, the projected uncovered amount '
                f'is RM {amount_myr}. Please let me know whether an extension or payment arrangement is possible. '
                'I understand no extension is approved until your office confirms it. Thank you.')
    return (f'Hi, I am planning for my {gap_summary["obligation"].lower()} due on {due}. '
            f'Under the current scenario, I may need an additional RM {amount_myr} before that deadline. '
            'Could we discuss whether support can be arranged in time? This is an estimated need, not a completed transfer. Thank you.')
