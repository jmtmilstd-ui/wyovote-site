"""Profile sections shared by tools/gen.py (2014-2025 Profile pages) and tools/stamp_profiles_2026.py (current Profiles).
Ranks and band labels only; coefficients are internal and never printed.

issue_rows(Y, chamber, label) -> [(category, chamber_rank, overall_rank, band) or (category, None, None, note)]
    Method (matches the published 2026 Profiles exactly): roll-call issue tags from criteria/y<Y>/rollcallcriterion_<Y>.csv
    (groups from criteria_table_v4.csv); per category, an internal average of signed bill scores over the legislator's Aye/Nay
    votes on tagged roll calls; ranked members only (ranking.py) with at least 3 votes in the category; ties broken by overall
    rank; bands by natural breaks (bands.jenks3) within the category. Fewer than 3 votes: 'too few votes in category'.
committee_rows(Y, chamber, label) -> [(committee title, role, site PDF path or None)]
    Committees with a WyoVote 112 report that year (committees_<Y>/manifest_data.json), members from the LSO rosters
    (committees_<Y>/inputs), matched to the ratings file the same way the 112 builder does.
missed(Y, chamber, label) -> (aye_nay, session_roll_calls, missed, pct) ; session roll calls = that year's maximum counted votes.
"""
import csv, json, os, re, sys, collections, functools, glob
W = '/workspace/wyoleg'
sys.path.insert(0, W)
import ranking, bands as B
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS = []; G = {}
for r in csv.DictReader(open(f'{W}/criteria/criteria_table_v4.csv')):
    G[r['crit_ID']] = r['group_name']
    if r['group_name'] not in GROUPS: GROUPS.append(r['group_name'])
MIN_CAT = 3
NOBAND = []   # (year, category) where natural breaks could not be computed

@functools.lru_cache(None)
def RK(Y): return ranking.load(Y)

@functools.lru_cache(None)
def _issue(Y):
    Y = int(Y); d = RK(Y)
    tags = collections.defaultdict(set)
    for r in csv.DictReader(open(f'{W}/criteria/y{Y}/rollcallcriterion_{Y}.csv')): tags[int(r['v_ID'])].add(G[r['crit_ID']])
    sc = {int(r['VoteID']): float(r['Score']) for r in csv.DictReader(open(f'{W}/y{Y}/scores_{Y}.csv'))}
    ranked = {(r['chamber'], r['legislator']): r for r in d['ranked']}
    agg = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0]))
    for v in csv.DictReader(open(f'{W}/y{Y}/wy_{Y}_legislator_votes.csv')):
        if v['Vote'] not in ('Aye', 'Nay'): continue
        vid = int(v['VoteID']); s = sc[vid] * (1 if v['Vote'] == 'Aye' else -1)
        for g in tags.get(vid, ()): a = agg[(v['Chamber'], v['Legislator'])][g]; a[0] += s; a[1] += 1
    tagged = {g for t in tags.values() for g in t}
    out = {}
    for g in GROUPS:
        rows = [(k, agg[k][g][0] / agg[k][g][1]) for k in ranked if agg[k][g][1] >= MIN_CAT]
        rows.sort(key=lambda x: (-x[1], ranked[x[0]]['rank_all']))
        res = {}
        if len(rows) >= 3:
            try: hi, lo, _ = B.jenks3([c for _, c in rows])
            except ValueError: hi = lo = None; NOBAND.append((Y, g))      # fewer than 3 distinct values: ranks only, no band
            ks = [k for k, _ in rows]
            per = {'H': [k for k in ks if k[0] == 'H'], 'S': [k for k in ks if k[0] == 'S']}
            for i, (k, c) in enumerate(rows, 1): res[k] = (per[k[0]].index(k) + 1, i, B.band_of(c, hi, lo) if hi is not None else None)
        out[g] = (res, g in tagged)
    return out

def issue_rows(Y, chamber, label):
    k = (chamber, label); rows = []
    for g in GROUPS:
        res, tagged = _issue(Y)[g]
        if k in res: rows.append((g,) + res[k])
        elif not tagged: rows.append((g, None, None, f'no roll calls tagged in {Y}'))
        else: rows.append((g, None, None, 'too few votes in category'))
    return rows

def _nrm(x): return re.sub(r'[^a-z]', '', x.lower())
ALIAS = {2138: 'Laura Taliaferro'}
def _old_alias(Y): return {2018: 'JoAnn Dayton-Selman' if int(Y) >= 2019 else 'JoAnn Dayton', 2057: 'Andi Clifford'}
def _role(m):
    n = m.get('notes') or ''
    def dt(txt):
        g = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:\d{1,2},?\s+)?(\d{4})', txt)
        return f'{g.group(1)} {g.group(2)}' if g else None
    if m['chair']:
        d = dt(n) if 'Appointed Chairman' in n else None
        return 'Chair' + (f' (from {d})' if d else '')
    if m['vice']: return 'Vice Chair'
    if 'Chairman through' in n:
        d = dt(n); return 'Former chair' + (f' (through {d})' if d else '')
    if n.startswith('Appointed'):
        d = dt(n); return 'Member (appointed' + (f' {d})' if d else ')')
    return 'Member' + (' (alternate)' if m.get('alt') else '')

UNMATCHED = collections.defaultdict(list)   # Y -> [(committee, member name, chamber)]
@functools.lru_cache(None)
def _committees(Y):
    Y = int(Y); H = f'{W}/committees_{Y}'; ALLL = RK(Y)['all']; old = Y < 2021
    CM = json.load(open(f'{H}/inputs/committees_{Y}_all.json'))
    if os.path.exists(f'{H}/inputs/supplement_{Y}.json'): CM.update(json.load(open(f'{H}/inputs/supplement_{Y}.json')))
    man = {m['ownerID']: m for m in json.load(open(f'{H}/manifest_data.json'))}
    def find(m):
        nm = _nrm(ALIAS.get(m['id']) or (_old_alias(Y).get(m['id']) if old else None) or m['name']); ch = m['chamber']
        ex = [r for r in ALLL if _nrm(r['full_name']) == nm]
        if ex:
            same = [r for r in ex if r['chamber'] == ch]; return (same or ex)[0]
        for pool in ([r for r in ALLL if r['chamber'] == ch], ALLL):
            c = [r for r in pool if nm.endswith(_nrm(r['full_name'].split()[-1]))]
            if len(c) == 1: return c[0]
            if len(c) > 1:
                c2 = [r for r in c if _nrm(r['full_name'])[:2] == nm[:2]]
                if len(c2) == 1: return c2[0]
        return None
    out = collections.defaultdict(list)
    for o, c in CM.items():
        if o not in man: continue
        num = man[o]['num']; title = man[o]['title']
        pdf = sorted(glob.glob(f'{SITE}/reports/{Y}/wyovote_{Y}_Committee_{num}_*_112_v*.pdf'))
        href = os.path.relpath(pdf[-1], SITE) if pdf else None
        for m in c['members']:
            if m['id'] == 0: continue
            r = find(m)
            if r is None: UNMATCHED[Y].append((title, m['name'], m['chamber'])); continue
            out[(r['chamber'], r['legislator'])].append((int(num), title, _role(m), href))
    return {k: [x[1:] for x in sorted(v)] for k, v in out.items()}

def committee_rows(Y, chamber, label): return _committees(Y).get((chamber, label), [])

def missed(Y, nv):
    mx = RK(Y)['max_votes']; m = mx - nv
    return nv, mx, m, f'{100 * m / mx:.1f}%'
