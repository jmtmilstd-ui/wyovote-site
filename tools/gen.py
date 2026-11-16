"""Officials archive generator (single tree: writes live paths; review on a Cloudflare branch preview). Templates = the published officials/2025 pages; ranks from ranking.py.
Deep pages carry the rank-history chart (tools/rank_chart.py). Run: python3 tools/gen.py BASE OUT 2008,...,2024 (OA_FIRST=2008)."""
import csv, json, re, sys, os, html, math, datetime
sys.path.insert(0, '/workspace/wyoleg'); sys.path.insert(0, '/workspace/name-index/tools'); sys.path.insert(0, os.path.dirname(__file__))
import ranking, namelib as N, rolls, match2021, rank_chart
BASE = sys.argv[1] if len(sys.argv) > 1 else '/workspace/officials-archive/base'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/workspace/officials-archive/site'
YEARS = [int(y) for y in (sys.argv[3].split(',') if len(sys.argv) > 3 else ['2021', '2022', '2023', '2024'])]
BUILT = '2026-11-15'
FIRST = int(os.environ.get('OA_FIRST', '2008'))
REVIEW = []
CONFIRMED = {'WY-WALTERS-THOMAS', 'WY-LEBEAU-ANDI'}
W = '/workspace/wyoleg'
E = html.escape
T = lambda p: open(f'{BASE}/officials/2025/{p}', encoding='utf-8').read()
TPL = {k: T(f) for k, f in (('idx', 'index.html'), ('pg', 'allemand.html'), ('dp', 'allemand-deep.html'))}
def split(t):
    a = t.index('    <main'); b = t.index('    </main>') + len('    </main>\n')
    return t[:a], t[b:]
PARTY = {'Rep': ('R', 'Republican', 'party-r'), 'Dem': ('D', 'Democrat', 'party-d'), 'Lib': ('L', 'Libertarian', 'party-l'), 'Ind': ('I', 'Independent', 'party-i')}
CH = {'H': ('House', 'Representative'), 'S': ('Senate', 'Senator')}
def fdate(s):
    d = datetime.date.fromisoformat(s); return f"{d.strftime('%b')} {d.day}, {d.year}"
# ---------- person ids per year ----------
def pid_rows(Y):
    Y = int(Y)
    if Y <= 2021:
        A = list(csv.DictReader(open(f'{W}/y{Y}/legislators_{Y}.csv')))
        match2021.YEAR = str(Y)
        for r in A:
            pid, how, cand = match2021.match(r['full_name'], r['district'])
            if how != 'name match': REVIEW.append(dict(year=Y, full_name=r['full_name'], roster_label=r['legislator'], chamber=r['chamber'], district=r['district'], reason=how, matched_person_id=pid, candidates=cand, ratings_file_person_id=r['person_id']))
            # unmatched: provisional key from the ratings file, prefixed so it never links to a Name Index person
            if not pid and r['person_id'] in CONFIRMED:   # errata E060/E061: owner-confirmed same person, link by the ratings-file ID
                pid = r['person_id']; REVIEW.pop()
            r['pid'] = pid or ('PROV:' + r['person_id'])
        import collections
        cnt = collections.Counter(r['pid'] for r in A)
        for r in A:
            if cnt[r['pid']] > 1:   # two people in one roster matched the same Name Index person: don't guess
                REVIEW.append(dict(year=Y, full_name=r['full_name'], roster_label=r['legislator'], chamber=r['chamber'], district=r['district'], reason='two roster members matched the same person', matched_person_id='', candidates=r['pid'], ratings_file_person_id=r['person_id']))
                r['pid'] = 'PROV:' + r['person_id']
        return A
    if Y in (2022, 2023):
        A = list(csv.DictReader(open(f'{W}/y{Y}/legislators_{Y}.csv')))
        for r in A: r['pid'] = r['person_id']
        return A
    A = list(csv.DictReader(open(f'{W}/persons/legislators_{Y}_pid.csv')))
    for r in A: r['pid'] = r['person_id']
    return A
PID = {}   # (Y, chamber, label) -> pid
for Y in range(FIRST, 2027):
    for r in pid_rows(Y): PID[(Y, r['chamber'], r['legislator'])] = r['pid']
RK = {Y: ranking.load(Y) for Y in range(FIRST, 2027) if Y <= max(YEARS)}
BYP = {}   # pid -> {Y: row}
YEARS_OF = {}
for Y in range(FIRST, 2027):
    for r in pid_rows(Y): YEARS_OF.setdefault(r['pid'], set()).add(Y)
for Y, d in RK.items():
    for r in d['all']:
        p = PID[(Y, r['chamber'], r['legislator'])]; r['pid'] = p; BYP.setdefault(p, {})[Y] = r
# ---------- 2026 slugs and wyoleg links ----------
S26 = {}
p26 = {(r['district'], r['full_name']): r['person_id'] for r in csv.DictReader(open(f'{W}/persons/legislators_2026_pid.csv'))}
for f in os.listdir(f'{BASE}/officials'):
    if not f.endswith('.html') or f.endswith('-deep.html'): continue
    t = open(f'{BASE}/officials/{f}', encoding='utf-8').read()
    nm = re.search(r'<h1 id="h-name">([^<]*)</h1>', t); ds = re.search(r'District (\d+)', t); ch = 'S' if 'Senator ·' in t else 'H'
    if not nm: continue
    key = (f'{ch}{ds.group(1)}', html.unescape(nm.group(1)))
    url = re.search(r'href="(https://www\.wyoleg\.gov/Legislators/2026/[HS]/\d+)"', t)
    if key in p26: S26[p26[key]] = (f[:-5], url.group(1) if url else None)
def slugs(Y, A):
    out = {}; base = {}
    for r in A:
        b = re.sub(r'[^a-z]', '', N.parse(r['full_name'])['last']); base.setdefault(b, []).append(r)
    for b, rs in base.items():
        for r in rs:
            s26 = S26.get(r['pid'], (None,))[0]
            if s26 and re.sub(r'[^a-z]', '', s26.split('-')[0]) == b: out[r['pid']] = s26
            elif len(rs) == 1: out[r['pid']] = b
            else: out[r['pid']] = f"{b}-{re.sub(r'[^a-z]', '', N.parse(r['full_name'])['first'])}"
    assert len(set(out.values())) == len(out), Y
    return out
BANDS_OF = {y: rank_chart.bands_from_ranking(d) for y, d in RK.items()}
def rank_series(p, Y):
    return [(y, BYP[p][y]['rank_all'], RK[y]['n_ranked'], BYP[p][y]['band']) for y in range(FIRST, Y + 1) if y in BYP.get(p, {})]
def band_span(b): return f'<span class="pf-band pf-band-{b.lower()}">{b}</span>'
def change(Y, p):
    cur = BYP[p][Y]; prev = BYP[p].get(Y - 1)
    if cur['rank_all'] is None: return 'Not ranked, too few votes.'
    if Y == FIRST: return f'No comparison: {FIRST} is the earliest year shown.'
    if prev is None:
        if any(y < Y for y in BYP[p]): return f"Not in the {Y-1} report; #{cur['rank_all']} in {Y}."
        return f'New in {Y}.'
    if prev['rank_all'] is None: return f"Not ranked in {Y-1} (too few votes); #{cur['rank_all']} in {Y}."
    d = prev['rank_all'] - cur['rank_all']; n = abs(d)
    if d > 0: s = f"Moved up {n} place{'s' if n != 1 else ''} overall: #{prev['rank_all']} in {Y-1}, #{cur['rank_all']} in {Y}."
    elif d < 0: s = f"Moved down {n} place{'s' if n != 1 else ''} overall: #{prev['rank_all']} in {Y-1}, #{cur['rank_all']} in {Y}."
    else: s = f"No change: #{cur['rank_all']} both years."
    if prev['chamber'] != cur['chamber']: s += f" The {Y-1} rank was in the {CH[prev['chamber']][0]}."
    return s
def ind(n, t): return '\n'.join((' ' * n + l) if l else l for l in t.split('\n'))
def build_year(Y):
    d = RK[Y]; A = d['all']; mx = d['max_votes']
    nH = sum(1 for r in d['ranked'] if r['chamber'] == 'H'); nS = sum(1 for r in d['ranked'] if r['chamber'] == 'S'); nA = d['n_ranked']
    SL = slugs(Y, A)
    # roll calls json
    rws = sorted(rolls.build(Y), key=lambda r: (r[0], r[1]), reverse=True)
    rolls_json = [r[2] for r in rws]; pos = {r[1]: i for i, r in enumerate(rws)}
    votes = {}
    for v in csv.DictReader(open(f'{W}/y{Y}/wy_{Y}_legislator_votes.csv')):
        votes.setdefault((v['Chamber'], v['Legislator']), []).append((pos[int(v['VoteID'])], 'No' if v['Vote'] == 'Nay' else v['Vote']))
    lv = fdate(d['LV'])
    asof_tail = {2021: 'the last voting day of 2021 (regular and special sessions)', 2020: 'the last voting day of 2020 (regular and special sessions)'}.get(Y, f'the last voting day of the {Y} session')
    src = f'published {Y} reports' if Y >= 2021 else f'approved {Y} WyoVote ratings'
    pages = {}
    ih, ifo = split(TPL['idx']); ph, pfo = split(TPL['pg']); dh, dfo = split(TPL['dp'])
    for r in A:
        p = r['pid']; s = SL[p]; nm = E(r['full_name']); party = PARTY[r['party']]; chn, title = CH[r['chamber']]
        dist = r['district'][1:]; last = max(YEARS_OF[p])
        served = f' · Served through {last}' if 2026 not in YEARS_OF[p] else ''
        url = S26.get(p, (None, None))[1] if 2026 in YEARS_OF[p] else None
        ranked = r['rank_all'] is not None
        if ranked:
            rk = f'<span class="pf-rankline">{chn} {r["rank_ch"]} of {nH if r["chamber"]=="H" else nS}</span><span class="pf-rankline">All {nA}: {r["rank_all"]} of {nA}</span>'
            bd = f'<b class="pf-mid">{band_span(r["band"])}</b>'
        else:
            rk = '<span class="pf-rankline">Not ranked, too few votes</span><span class="pf-rankline">Not ranked, too few votes</span>'
            bd = '<b class="pf-mid">Not ranked, too few votes</b>'
        miss = mx - r['nv']; pct = f'{100*miss/mx:.1f}'
        ch_s = change(Y, p)
        links = (f'<a class="pf-btn btn-out" href="{url}">Official wyoleg.gov page ↗</a> ' if url else '') + f'<span class="pf-asof">Results through {lv}, {asof_tail}</span>'
        outkey = '        <p class="out-key"><span class="out-swatch btn-out" aria-hidden="true"></span> Gold-ringed buttons go to other websites (leaves WyoVote); use Back to return.</p>\n' if url else ''
        main = f'''    <main id="main" class="profile">
      <div class="wrap">
        <p class="back-row"><a class="back-btn" href="index.html">← Back to {Y} Officials</a></p>
{outkey}        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{nm}</h1>
          <p class="pf-sub">{title} · {chn} District {dist} · {party[1]}{served}</p>
          <p class="pf-links">{links}</p>
        </section>
        <p class="pf-dive"><a class="pf-dive-btn" href="{s}-deep.html">Profile →</a></p>
        <section class="pf-card" aria-labelledby="h-num">
          <h2 id="h-num">{Y} numbers <small>as of {lv}</small></h2>
          <div class="pf-tiles pf-tiles-4">
            <div class="pf-tile"><div class="pf-tl">Rank</div><div class="pf-tv">{rk}</div></div>
            <div class="pf-tile"><div class="pf-tl">Band</div><div class="pf-tv">{bd}<span class="pf-of">rank 1 = MOST Conservative, last = Most Liberal</span></div></div>
            <div class="pf-tile"><div class="pf-tl">Votes counted</div><div class="pf-tv"><b class="pf-big">{r["nv"]}</b> <span class="pf-of">Aye and Nay votes scored</span></div></div>
            <div class="pf-tile"><div class="pf-tl">Missed votes</div><div class="pf-tv"><b class="pf-big">{miss}</b> <span class="pf-of">{pct}% of {mx} roll calls</span></div></div>
          </div>
        </section>
        <section class="pf-card" aria-labelledby="h-chart">
          <h2 id="h-chart">{"Overall rank change" if Y == FIRST else f"Overall rank change, {Y-1} to {Y}"}</h2>
          <p class="pf-none">{ch_s}</p>
          <p class="deep-note">This compares overall rank only. Chamber ranks are not compared across years.</p>
        </section>
<section class="pf-card" aria-labelledby="h-news">
          <h2 id="h-news">Views and News</h2>
          <p class="pf-none">No recent coverage found.</p>
        </section>
        <p class="pf-deeper"><a href="{s}-deep.html">Profile</a></p>
        <p class="pf-foot">Ranks and bands are {'copied from the ' if Y >= 2021 else 'from the '}{src}. Preview page, built {BUILT}.</p>
      </div>
    </main>
'''
        head = ph.replace('<title>Bill Allemand — 2025 Session — WyoVote</title>', f'<title>{nm} — {Y} Session — WyoVote</title>') \
                 .replace('content="Bill Allemand, House District 58: 2025 rank, votes and band."', f'content="{nm}, {chn} District {dist}: {Y} rank, votes and band."') \
                 .replace('class="pf pf-2025"', f'class="pf pf-{Y}"')
        pages[f'{s}.html'] = head + main + pfo
        # deep page
        hist = []
        for y in range(FIRST, Y + 1):
            q = BYP[p].get(y)
            if not q: continue
            if q['rank_all'] is None: hist.append(f'                <tr><td>{y}</td><td colspan="2">Not ranked, too few votes</td></tr>')
            else: hist.append(f'                <tr><td>{y}</td><td>{q["rank_all"]} of {RK[y]["n_ranked"]}</td><td>{band_span(q["band"])}</td></tr>')
        pr = sorted(votes.get((r['chamber'], r['legislator']), []))
        pairs = json.dumps([[i, v] for i, v in pr], separators=(',', ':'))
        dmain = f'''    <main id="main" class="profile">
      <div class="wrap">
        <p class="back-row"><a class="back-btn" href="{s}.html">← Back to {nm}</a></p>
        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{nm}</h1>
          <p class="pf-sub">Profile · {chn} District {dist} · {Y}</p>
        </section>
        <section class="pf-card" aria-labelledby="h-rank">
          <h2 id="h-rank">Rank history</h2>
          <p class="deep-note">{ch_s} Chamber ranks are not compared across years.</p>
{rank_chart.chart_block(r['full_name'], rank_series(p, Y), BANDS_OF)}          <div class="deep-scroll">
            <table class="deep-table">
              <thead><tr><th scope="col">Year</th><th scope="col">Overall rank</th><th scope="col">Band</th></tr></thead>
              <tbody>
{chr(10).join(hist)}
              </tbody>
            </table>
          </div>
        </section>
        <section class="pf-card" aria-labelledby="h-issue">
          <h2 id="h-issue">Issue areas</h2>
          <p class="deep-note">Category data not available for {Y}.</p>
        </section>
        <section class="pf-card" aria-labelledby="h-miss">
          <h2 id="h-miss">Missed votes</h2>
          <div class="deep-scroll">
            <table class="deep-table">
              <thead><tr><th scope="col">Year</th><th scope="col">Votes counted</th><th scope="col">Missed</th></tr></thead>
              <tbody>
                <tr><td>{Y}</td><td>{r["nv"]}</td><td>{miss} ({pct}% of {mx} roll calls)</td></tr>
              </tbody>
            </table>
          </div>
        </section>
        <section class="pf-card" aria-labelledby="h-votes">
          <h2 id="h-votes">Scored votes</h2>
          <p class="deep-note">Each row is one roll call. Category is Uncategorized because {Y} roll calls are not tagged. Bill lean is Conservative, Liberal, or Neutral.</p>
          <details class="vote-details" data-rolls="../../data/roll-calls-{Y}.json">
            <summary>{len(pr)} roll calls, newest first</summary>
            <div class="deep-scroll">
              <p class="vote-wait">Loading the roll calls.</p>
              <table class="deep-table deep-votes" hidden>
                <thead><tr><th scope="col">Date</th><th scope="col">Bill</th><th scope="col">Title</th><th scope="col">Stage</th><th scope="col">Vote</th><th scope="col">Category</th><th scope="col">Bill lean</th></tr></thead>
                <tbody></tbody>
              </table>
            </div>
            <noscript><p class="vote-noscript">This vote list needs JavaScript. <a href="../../data/roll-calls-{Y}.json">Open the {Y} roll-call file</a>.</p></noscript>
          </details>
          <script type="application/json" id="vote-ids">{pairs}</script>
          <script src="../votes.js"></script>
        </section>
        <p class="pf-foot">Session page: <a href="{s}.html">{nm}, {Y}</a>.</p>
      </div>
    </main>
'''
        dhead = dh.replace('<title>Bill Allemand — 2025 Profile — WyoVote</title>', f'<title>{nm} — {Y} Profile — WyoVote</title>') \
                  .replace('content="Bill Allemand: 2025 ranks, bands and scored votes."', f'content="{nm}: {Y} ranks, bands and scored votes."') \
                  .replace('class="pf pf-2025"', f'class="pf pf-{Y}"')
        pages[f'{s}-deep.html'] = dhead + dmain + dfo
    # index
    def li(r):
        party = PARTY[r['party']]; nm = N.sort_name(r['full_name'])
        return f'''            <li>
              <a class="official-btn {party[2]}" href="{SL[r['pid']]}.html">{E(nm)} ({party[0]}) {r['district']}</a>
            </li>'''
    order = lambda r: (re.split(r'[ ,]', r['legislator'])[0].lower(), N.parse(r['full_name'])['first'], r['full_name'].lower())
    H = sorted([r for r in A if r['chamber'] == 'H'], key=order); Sn = sorted([r for r in A if r['chamber'] == 'S'], key=order)
    pl = sorted({r['party'] for r in A}, key=lambda k: ['Rep', 'Dem', 'Lib', 'Ind'].index(k))
    pltxt = ', '.join(f'({PARTY[k][0]}) {PARTY[k][1]}' for k in pl)
    imain = f'''    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="../../archive/officials.html">← Back to Archive</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>Officials, {Y}</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap">
          <p class="year-choice">{Y} roster. The current year is on the <a href="../../officials.html">Officials</a> page.</p>
          <p class="intro">{Y} House and Senate. Ranks and bands are from the {src}. Party letter: {pltxt}.</p>
          <nav class="officials-jump" aria-label="On this page">
            <a class="jump-btn" href="#house-heading">House</a>
            <a class="jump-btn" href="#senate-heading">Senate</a>
          </nav>
          <section class="officials-section" aria-labelledby="house-heading">
            <h2 id="house-heading">House</h2>
            <ul class="officials-grid">
{chr(10).join(li(r) for r in H)}
            </ul>
          </section>
          <section class="officials-section" aria-labelledby="senate-heading">
            <h2 id="senate-heading">Senate</h2>
            <ul class="officials-grid">
{chr(10).join(li(r) for r in Sn)}
            </ul>
          </section>
        </div>
      </section>
    </main>
'''
    ihead = ih.replace('<title>Officials, 2025 — WyoVote</title>', f'<title>Officials, {Y} — WyoVote</title>') \
              .replace('content="2025 Wyoming legislators, with links to each WyoVote session page."', f'content="{Y} Wyoming legislators, with links to each WyoVote session page."')
    pages['index.html'] = ihead + imain + ifo
    return pages, rolls_json
if __name__ == '__main__':
    import shutil
    for Y in YEARS:
        pages, rj = build_year(Y)
        od = f'{OUT}/officials/{Y}'; os.makedirs(od, exist_ok=True)
        for f, t in pages.items(): open(f'{od}/{f}', 'w', encoding='utf-8').write(t)
        os.makedirs(f'{OUT}/data', exist_ok=True)
        json.dump(rj, open(f'{OUT}/data/roll-calls-{Y}.json', 'w', encoding='utf-8'), ensure_ascii=False)
        print(Y, 'pages', len(pages), 'list', len([f for f in pages if f != 'index.html' and not f.endswith('-deep.html')]), 'deep', len([f for f in pages if f.endswith('-deep.html')]), 'rolls', len(rj))
