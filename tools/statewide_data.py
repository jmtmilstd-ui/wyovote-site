"""Statewide elected officials (Governor, Secretary of State, State Auditor, State Treasurer, Superintendent of
Public Instruction), 2007 terms to the Nov. 2026 elects, from /workspace/wyoleg/statewide/ (see its README.md).
Shared by tools/build_statewide_profiles.py and tools/gen.py (the cross-link on legislator Profiles)."""
import csv, os, re, collections
SRC = os.environ.get('WY_STATEWIDE', '/workspace/wyoleg/statewide')
OFFICES = ['Governor', 'Secretary of State', 'State Auditor', 'State Treasurer', 'Superintendent of Public Instruction']
ELECT_LABEL = 'Official-elect, takes office Jan 4, 2027'
# Statewide person_id -> the key the legislator Profiles use (tools/gen.py). Same person, same roster person_id:
# roster_2008..2018 list Curt Meier S03 as WY-MEIER-CURT (site key WY-MEIER-CURTIS from the Name Index);
# Edward Buchanan H04 2008-2012 has a provisional site key (not in the Name Index).
SITE_KEY = {'WY-MEIER-CURT': 'WY-MEIER-CURTIS', 'WY-BUCHANAN-EDWARD': 'PROV:WY-BUCHANAN-EDWARD'}
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

def fmt_date(d):
    if not d: return ''
    y, m, dd = d.split('-'); return f'{MON[int(m) - 1]} {int(dd)}, {y}'

TERMS = list(csv.DictReader(open(f'{SRC}/statewide_officials_2008_2026.csv', encoding='utf-8')))
VETOES = list(csv.DictReader(open(f'{SRC}/statewide_governor_vetoes_2008_2026.csv', encoding='utf-8')))
RESULTS = list(csv.DictReader(open(f'{SRC}/statewide_election_results_2006_2026.csv', encoding='utf-8')))
BY_PERSON = collections.OrderedDict()
for r in TERMS: BY_PERSON.setdefault(r['person_id'], []).append(r)

def last_name(r):
    n = re.sub(r',\s*(Jr\.|Sr\.|III|II)$', '', r['full_name']).split()
    return n[-1]
def _slugs():
    base = {p: last_name(rs[0]).lower() for p, rs in BY_PERSON.items()}
    c = collections.Counter(base.values())
    return {p: (s if c[s] == 1 else f'{s}-{rs[0]["full_name"].split()[0].lower()}') for (p, rs), s in zip(BY_PERSON.items(), base.values())}
SLUG = _slugs()

def is_elect_only(p): return all(r['elect_not_yet_sworn'] == 'yes' for r in BY_PERSON[p])
def offices_of(p):
    seen = []
    for r in BY_PERSON[p]:
        if r['office'] not in seen: seen.append(r['office'])
    return seen
def link_label(p):
    """Button text on a legislator Profile."""
    o = ' and '.join(offices_of(p))
    return f'Statewide Profile: {o}, official-elect →' if is_elect_only(p) else f'Statewide Profile: {o} →'
def site_key(p): return SITE_KEY.get(p, p)
LEG_PEOPLE = [p for p, rs in BY_PERSON.items() if rs[0]['prior_leg_years']]
