"""Safe, deliberately narrow chat-to-simulation interpreter.

Parses explicitly mentioned arrival dates for a uniquely identified *unsettled*
funding source. It NEVER writes to SQLite and does not invent funding entries,
exchange rates or obligation deadlines. Ambiguous requests stay on the selected
scenario. This is a deterministic convenience, not a general-purpose NLP model.
"""
from __future__ import annotations
from datetime import date, timedelta
import re

MONTHS = {name:i for i, names in enumerate([
    ('jan','january'),('feb','february'),('mar','march'),('apr','april'),
    ('may',),('jun','june'),('jul','july'),('aug','august'),('sep','sept','september'),
    ('oct','october'),('nov','november'),('dec','december')], 1) for name in names}
MON = r'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
DATE_PATTERNS = [
    re.compile(r'(?<!\d)(?P<iso>20\d{2}-\d{2}-\d{2})(?!\d)',re.I),
    re.compile(rf'\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?(?P<month>{MON})\b(?:[\s,]+(?P<year>20\d{{2}}))?',re.I),
    re.compile(rf'\b(?P<month>{MON})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\b(?:[\s,]+(?P<year>20\d{{2}}))?',re.I),
]
INTENT_RE = re.compile(r'\b(arriv\w*|delay\w*|postpon\w*|expect\w*|receiv\w*|lands?|comes?|coming|transfer\w*|remitt\w*|sent|send|fund\w*)\b',re.I)
DATE_ACTION_RE = re.compile(r'\b(arriv\w*|delay\w*|postpon\w*|expect\w*|receiv\w*|lands?|comes?|coming|send|sent)\b',re.I)
QUESTION_RE = re.compile(r'\b(what if|suppos\w*|simulat\w*|hypothetical|would|if|imagine|scenario|forecast)\b',re.I)
BARE_DAY = re.compile(r'\b(?:the\s+)?(?P<day>\d{1,2})(?:st|nd|rd|th)\b(?!\s*\d)',re.I)


def _date_in_fragment(fragment: str, reference: date) -> date|None:
    matches=[]
    for pat in DATE_PATTERNS:
        for m in pat.finditer(fragment):
            try:
                if m.groupdict().get('iso'):
                    d=date.fromisoformat(m.group('iso'))
                else:
                    month=MONTHS[m.group('month').lower()]
                    year=int(m.group('year')) if m.groupdict().get('year') else reference.year
                    d=date(year,month,int(m.group('day')))
                    # An omitted year on a clear month/day pair resolves forward.
                    if not m.groupdict().get('year') and d<reference: d=date(year+1,month,int(m.group('day')))
                matches.append((m.start(),d))
            except (ValueError,TypeError):
                pass
    if matches:
        return min(matches,key=lambda v:v[0])[1]
    # Bare ordinal is safe only when preceded by an arrival-related phrase.
    marker=re.search(r'\b(?:until|on|by|around|arrives?\s+on|delayed?\s+to)\s+(?:the\s+)?(\d{1,2})(st|nd|rd|th)\b',fragment,re.I)
    if marker:
        try:
            d=date(reference.year,reference.month,int(marker.group(1)))
            return d if d>=reference else date(reference.year+int(reference.month==12),(reference.month%12)+1,int(marker.group(1)))
        except ValueError:
            return None
    return None


def _funding_source(message: str, funding: list[dict]) -> dict|None:
    """Pick a source only if its identity is unambiguous in the user's text."""
    msg=message.lower()
    unsettled=[f for f in funding if f.get('status')!='settled']
    family_words=re.search(r'\b(family|parent|parents|mom|mother|dad|father|remittance)\b',msg)
    scholarship_words=re.search(r'\b(scholarship|stipend|grant)\b',msg)
    if family_words and scholarship_words:
        # Both may appear in the question; explicit arrival phrase decides below.
        return None
    if family_words:
        matches=[f for f in unsettled if re.search(r'family|remittance|parent',f.get('name',''),re.I) or f['id']=='family']
    elif scholarship_words:
        matches=[f for f in unsettled if re.search(r'scholarship|stipend|grant',f.get('name',''),re.I)]
    else:
        # Generic transfer when only one genuinely remittance-like funding source exists.
        if not re.search(r'\b(transfer|remittance)\b',msg):return None
        matches=[f for f in unsettled if re.search(r'transfer|remittance|family',f.get('name',''),re.I)]
    return matches[0] if len(matches)==1 else None


def interpret_scenario(message: str, data: dict, scenario: str, overrides: dict) -> dict:
    """Return an ephemeral context; no mutation or newly fabricated facts."""
    ctx={'source':'selected_scenario','scenario':scenario,'arrival_overrides':dict(overrides),
         'funding_id':None,'funding_name':None,'assumed_arrival':None,'label':f'{scenario.title()} scenario'}
    if not INTENT_RE.search(message):return ctx
    # Avoid treating tuition due dates alone as transfer arrival changes.
    item=_funding_source(message,data['funding'])
    if item is None:return ctx
    lower=message.lower()
    anchors=list(DATE_ACTION_RE.finditer(lower))
    if not anchors:return ctx
    # Extract date from the clause following its closest arrival/transfer verb;
    # never borrow a tuition/rent due date from the next clause.
    segments=[]
    for anchor in anchors:
        frag=message[anchor.end():anchor.end()+120]
        frag=re.split(r'\b(?:but|whereas|while|tuition|rent|bill|obligation|payment\s+due)\b',frag,maxsplit=1,flags=re.I)[0]
        d=_date_in_fragment(frag,date.fromisoformat(data['as_of']))
        if d:
            weight=3 if re.search(r'^(?:.{0,20}\b)(delayed?|arrive\w*|expected?|postpon\w*|receiv\w*)',anchor.group(),re.I) else 1
            segments.append((weight,anchor.start(),d))
    if not segments:return ctx
    _,_,when=max(segments,key=lambda x:(x[0],x[1]))
    ref=date.fromisoformat(data['as_of'])
    if not (ref<=when<=ref+timedelta(days=366)):
        return ctx
    ctx.update(source='chat_hypothetical',funding_id=item['id'],funding_name=item['name'],
        assumed_arrival=when.isoformat(),label=f'{item["name"]} arriving {when.strftime("%d %b %Y")}',
        arrival_overrides={**overrides,item['id']:when.isoformat()})
    return ctx
