"""Profile sections shared by tools/gen.py (2015-2025 Profile pages) and tools/stamp_profiles_2026.py (current Profiles).
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
import csv, json, os, re, sys, collections, functools, glob, html
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

# ---------- 2026 issue-area vote counts (ranks stay in issue_rows for earlier years) ----------
VOTES_ROOT = '/workspace/wyovote-data'
OFFICIALS_RESEARCH = VOTES_ROOT + '/officials-2026/officials-research-2026.json'
RESEARCH_CYCLE = '2026-primary'
ITEM_PREFIX = re.compile(r'^\d{2}[ab]\s+')


def _item_label(raw):
    if not raw:
        return ''
    return ITEM_PREFIX.sub('', raw).strip()


@functools.lru_cache(None)
def category_sides():
    paths = [f'{VOTES_ROOT}/officials-2026/category_sides.csv', f'{VOTES_ROOT}/category_sides.csv']
    path = next((x for x in paths if os.path.exists(x)), None)
    if path is None:
        raise FileNotFoundError('category_sides.csv not found under ' + VOTES_ROOT)
    out = {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            out[r['category']] = (_item_label(r['for_item']), _item_label(r['against_item']))
    return out


@functools.lru_cache(None)
def category_votes(Y):
    Y = int(Y)
    path = f'{VOTES_ROOT}/officials-{Y}/category_votes_{Y}.csv'
    out = collections.defaultdict(dict)
    if not os.path.exists(path):
        return out
    def cell(r, k):
        v = r.get(k, '')
        if v is None or str(v).strip() == '':
            return None
        return int(v)
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            out[r['person_id']][r['category']] = (
                cell(r, 'for_aye'), cell(r, 'for_no'),
                cell(r, 'against_aye'), cell(r, 'against_no'),
            )
    return out


def issue_vote_rows(Y, person_id):
    """(category, for_name, for_aye, for_no, against_name, against_aye, against_no).
    against_* is None when that side is blank (Legislating in Budget has no item b)."""
    sides = category_sides()
    person = category_votes(Y).get(person_id, {})
    rows = []
    for g in GROUPS:
        fa, fn, aa, an = person.get(g, (None, None, None, None))
        for_name, against_name = sides.get(g, ('', ''))
        rows.append((g, for_name, fa, fn, against_name, aa, an))
    return rows


def _fmt_count(v):
    return '—' if v is None else str(v)


def issue_votes_block(Y, person_id):
    """Notes + table for the 2026 issue-area vote counts. No ranks, bands, or coefficients."""
    E = html.escape
    rows = []
    for g, for_name, fa, fn, against_name, aa, an in issue_vote_rows(Y, person_id):
        rows.append(
            '                <tr>'
            f'<th scope="row">{E(g)}</th>'
            f'<td class="side-name">{E(for_name)}</td>'
            f'<td class="vote-num">{_fmt_count(fa)}</td>'
            f'<td class="vote-num">{_fmt_count(fn)}</td>'
            f'<td class="side-name">{E(against_name)}</td>'
            f'<td class="vote-num">{_fmt_count(aa)}</td>'
            f'<td class="vote-num">{_fmt_count(an)}</td>'
            '</tr>'
        )
    body = '\n'.join(rows)
    return f'''          <p class="cat-prelim">Categories preliminary</p>
          <p class="deep-note">Aye and No are this session’s roll calls tagged in each category. Each pair belongs to the side named in that row. Excused, absent, and conflict are not counted. A roll call tagged on both sides of a category is counted on both. Legislating in Budget has only one side.</p>
          <div class="deep-scroll">
            <table class="deep-table">
              <thead><tr><th scope="col">Category</th><th scope="col">Side</th><th scope="col">Aye</th><th scope="col">No</th><th scope="col">Side</th><th scope="col">Aye</th><th scope="col">No</th></tr></thead>
              <tbody>
{body}
              </tbody>
            </table>
          </div>
'''


def load_officials_research(site_root=None):
    """person_id -> research record. Cycle shards first, then general-only, then the optional officials fill-in file."""
    import json as _json
    site_root = site_root or SITE
    records = {}

    def take(rec, overwrite=False):
        if not isinstance(rec, dict):
            return
        pid = rec.get('person_id')
        if not pid:
            return
        if overwrite or pid not in records:
            records[pid] = rec

    folder = os.path.join(site_root, 'data', 'candidate-research', RESEARCH_CYCLE)
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if not (name.startswith('part-') and name.endswith('.json')):
                continue
            payload = _json.load(open(os.path.join(folder, name), encoding='utf-8'))
            for rec in (payload if isinstance(payload, list) else [payload]):
                take(rec)
        for extra in ('general-only.json',):
            path = os.path.join(folder, extra)
            if os.path.isfile(path):
                payload = _json.load(open(path, encoding='utf-8'))
                for rec in (payload if isinstance(payload, list) else [payload]):
                    take(rec)  # fill only if missing; parts win
        # general.json is an election-results file, not the research-record schema.
        # Read it so a person_id only present there is noticed, but do not invent a record.
        gpath = os.path.join(folder, 'general.json')
        if os.path.isfile(gpath):
            _json.load(open(gpath, encoding='utf-8'))

    if os.path.isfile(OFFICIALS_RESEARCH):
        payload = _json.load(open(OFFICIALS_RESEARCH, encoding='utf-8'))
        if isinstance(payload, dict) and 'person_id' not in payload:
            recs = payload.get('records') or payload.get('people') or list(payload.values())
        else:
            recs = payload if isinstance(payload, list) else [payload]
        for rec in recs:
            if isinstance(rec, dict):
                take(rec)  # fill the 26 who are not in the cycle files; do not overwrite them
    return records


def research_has_content(record):
    if not record:
        return False
    if record.get('sources'):
        return True
    for key in ('residence', 'occupation', 'background', 'education', 'military',
                'prior_offices', 'website', 'positions', 'endorsements', 'fundraising', 'result'):
        if record.get(key):
            return True
    return False


def research_section_html(record):
    """Same Research block as candidate detail pages, styled as a Profile card. Empty if no record."""
    if not research_has_content(record):
        return ''
    import build_candidate_pages as cand
    inner = cand.research_html(record).replace(
        '<section class="cand-research"',
        '<section class="pf-card cand-research"',
        1,
    )
    return '        ' + inner.replace('\n', '\n        ') + '\n'

