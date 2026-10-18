"""Auditable, deterministic cash-flow calculations for the CampusFin demo.

All monetary values use Decimal; settled historical receipts are already included
in the opening balance. An obligation projection is NOT a payment execution.
"""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

PENNY = Decimal('0.01')


def money(value: Any) -> Decimal:
    if isinstance(value, float):
        raise ValueError('Money must be entered as a decimal string, not floating point')
    try:
        d = Decimal(str(value))
        if not d.is_finite():
            raise ValueError('Money must be finite')
        if abs(d) > Decimal('1000000000000'):
            raise ValueError('Money exceeds the demonstration range')
        return d.quantize(PENNY, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValueError('Enter a valid decimal money amount') from exc


def amount(value: Decimal) -> str:
    return format(value.quantize(PENNY), '.2f')


def arrival_for(item: dict, overrides: dict[str, str], scenario: str) -> date:
    if item['id'] in overrides:
        return date.fromisoformat(overrides[item['id']])
    return date.fromisoformat(item['arrivals'][scenario])


def validate(data: dict, overrides: dict[str, str], scenario: str):
    if scenario not in ('best', 'base', 'stress'):
        raise ValueError('scenario must be best, base or stress')
    funding = data['funding']; obligations = data['obligations']
    ids = {x['id'] for x in funding}
    if set(overrides).difference(ids):
        raise ValueError('Unknown funding item override')
    as_of = date.fromisoformat(data['as_of'])
    if money(data['opening_cash']) < 0:
        raise ValueError('Opening cash cannot be negative')
    for item in funding:
        if money(item['amount']) < 0:
            raise ValueError('Funding amount cannot be negative')
        if item['status'] not in ('expected', 'in_transit', 'settled'):
            raise ValueError('Invalid funding status')
        # A settled receipt dated on/before the as-of date belongs to opening cash.
        arr = arrival_for(item, overrides, scenario)
        if item['status'] == 'settled' and arr > as_of:
            raise ValueError('Settled receipt cannot have a future arrival')
        for key in ('best','base','stress'):
            date.fromisoformat(item['arrivals'][key])
        if item['currency'] not in data['rates']:
            raise ValueError('Missing conversion rate for funding currency')
    for item in obligations:
        if money(item['amount']) < 0:
            raise ValueError('Obligation cannot be negative')
        date.fromisoformat(item['due_date'])
    for rate in data['rates'].values():
        if Decimal(str(rate)) <= 0:
            raise ValueError('Exchange rate must be positive')


def net_myr(item: dict, rates: dict) -> Decimal:
    """Quotes are simplified: fixed sending fee is deducted before conversion.
    Formula is strictly labeled as simulated; no live transfer provider connection.
    """
    rate = Decimal(str(rates[item['currency']]))
    fx_fee = money(item.get('fee_deducted', '0'))
    net = money(item['amount']) - fx_fee
    if net < 0:
        raise ValueError('Deducted fee exceeds funding amount')
    return (net * rate).quantize(PENNY, rounding=ROUND_HALF_UP)


def forecast(data: dict, scenario: str = 'base', overrides: dict[str, str] | None = None) -> dict:
    overrides = overrides or {}
    validate(data, overrides, scenario)
    as_of = date.fromisoformat(data['as_of'])
    future_obligations = [o for o in data['obligations'] if date.fromisoformat(o['due_date']) > as_of]
    end = max([as_of+timedelta(days=14)] + [date.fromisoformat(o['due_date']) for o in future_obligations] +
              [arrival_for(f, overrides, scenario) for f in data['funding'] if f['status'] != 'settled'])
    cash = money(data['opening_cash'])
    balance = cash
    future_receipts: dict[date, list] = {}
    for f in data['funding']:
        # Settled funds were accounted for when the as-of opening balance was recorded.
        if f['status'] == 'settled':
            continue
        arrival = arrival_for(f, overrides, scenario)
        if arrival > as_of:
            future_receipts.setdefault(arrival, []).append(f)
    future_bills: dict[date, list] = {}
    for o in future_obligations:
        future_bills.setdefault(date.fromisoformat(o['due_date']), []).append(o)
    timeline = []
    shortfalls = []
    for daynum in range((end-as_of).days + 1):
        day = as_of + timedelta(days=daynum)
        incoming = Decimal('0')
        outflow = Decimal('0')
        for f in future_receipts.get(day, []):
            incoming += net_myr(f, data['rates'])
        balance += incoming
        for bill in sorted(future_bills.get(day, []), key=lambda b: (b.get('priority', 5), b['id'])):
            outflow += money(bill['amount'])
            before = balance
            balance -= money(bill['amount'])
            if balance < 0:
                shortfalls.append({'obligation_id':bill['id'], 'name':bill['name'], 'due_date':day.isoformat(),
                     'amount':amount(max(Decimal('0'), -balance)), 'available_before':amount(max(Decimal('0'),before)),
                     'status':'at_risk', 'explanation':'Projected amount needed to cover obligations by this deadline; no payment is executed.'})
        timeline.append({'date':day.isoformat(), 'projected_available':amount(balance),
                         'incoming': amount(incoming), 'obligations_due':amount(outflow)})
    first = shortfalls[0] if shortfalls else None
    return {'as_of':data['as_of'], 'scenario':scenario, 'opening_cash':amount(cash), 'currency':'MYR',
            'rates_kind':'SIMULATED', 'timeline':timeline,'shortfalls':shortfalls,
            'next_shortfall':first,
            'assumptions':['Funds expected on day D are available before obligations on the same day.',
                           'Funding arrivals are assumptions, not guarantees.',
                           'Already-settled income is included in opening cash and is never added twice.',
                           'Projected negative availability signifies unmet obligations, not overdrawn bank cash.',
                           'Living expenses beyond listed obligations are excluded from this fixture.']}


def compare(data: dict) -> dict:
    return {s:forecast(data,s) for s in ('best','base','stress')}
