#!/usr/bin/env python3
"""Put the rank-history chart (tools/rank_chart.py) on every legislator Profile page (the *-deep.html pages, formerly "Deeper dive"), and make each
rank-history row match ranking.py (counts = ranked members only). Idempotent: re-running replaces the chart.

    python3 tools/stamp_rank_chart.py [SITE_ROOT]      # default: the repo this file is in

2008-2024 deep pages also get the chart from tools/gen.py on a rebuild; 2025 and 2026 deep pages are
hand-built, so this stamp is how they get it. Prints a summary of every row it corrected.
"""
import os, re, sys, glob, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rank_chart

def load_gen():
    sys.argv = ['gen.py', ROOT, '/tmp/stamp-rank-chart-unused', '2026']
    os.environ.setdefault('OA_FIRST', '2008')
    g = {'__file__': f'{HERE}/gen.py', '__name__': 'gen_lib'}
    exec(compile(open(f'{HERE}/gen.py').read(), f'{HERE}/gen.py', 'exec'), g)
    return g
G = load_gen()
RK, BYP, slugs, S26, rank_series, BANDS_OF, band_span = G['RK'], G['BYP'], G['slugs'], G['S26'], G['rank_series'], G['BANDS_OF'], G['band_span']
OVERRIDE_2026 = {'taliaferro': 'WY-PEARSON-LAURA'}   # page h1 reads "Laura Taliaferro (formerly Pearson)"
FIX = []; STATS = collections.Counter(); CHECKS = []

def strip_chart(t):
    i = t.find('<div id="rank-chart">')
    if i < 0: return t
    a = t.rfind('\n', 0, i) + 1; b = t.index('</div>\n', i) + len('</div>\n')
    return t[:a] + t[b:]

def name_of(t):
    return re.search(r'<h1 id="h-name">([^<]*)</h1>', t).group(1)

def fix_rows_archive(rel, t, p, Y):
    i = t.index('aria-labelledby="h-rank"'); j = t.index('</section>', i); sec = t[i:j]; new = sec
    for y in range(G['FIRST'], Y + 1):
        q = BYP[p].get(y)
        if not q: continue
        exp = (f'<tr><td>{y}</td><td colspan="2">Not ranked, too few votes</td></tr>' if q['rank_all'] is None
               else f'<tr><td>{y}</td><td>{q["rank_all"]} of {RK[y]["n_ranked"]}</td><td>{band_span(q["band"])}</td></tr>')
        m = re.search(rf'<tr><td>{y}</td>.*?</tr>', new)
        assert m, (rel, y)
        if m.group(0) != exp:
            FIX.append((rel, y, re.sub('<[^>]+>', ' ', m.group(0)).split(), re.sub('<[^>]+>', ' ', exp).split()))
            new = new.replace(m.group(0), exp, 1)
    rows = re.findall(r'<tr><td>(\d{4})</td>', new)
    assert [int(x) for x in rows] == [y for y in range(G['FIRST'], Y + 1) if y in BYP[p]], (rel, rows)
    return t[:i] + new + t[j:]

def fix_rows_2026(rel, t, p):
    i = t.index('aria-labelledby="h-band"'); j = t.index('</section>', i); sec = t[i:j]; new = sec
    for y in range(G['FIRST'], 2027):
        q = BYP[p].get(y)
        if not q: continue
        m = re.search(rf'<tr><td>{y}</td>(.*?)</tr>', new); assert m, (rel, y)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', m.group(1))
        if q['rank_all'] is None:
            ok = cells == ['Not ranked, too few votes']
            exp = f'<tr><td>{y}</td><td colspan="4">Not ranked, too few votes</td></tr>'
        else:
            nC = sum(1 for r in RK[y]['ranked'] if r['chamber'] == q['chamber'])
            want = [f'{q["rank_all"]} of {RK[y]["n_ranked"]}', f'{q["rank_ch"]} of {nC}', band_span(q['band'])]
            ok = cells[:3] == want
            exp = f'<tr><td>{y}</td>' + ''.join(f'<td>{c}</td>' for c in want + cells[3:]) + '</tr>'
        if not ok:
            FIX.append((rel, y, [re.sub('<[^>]+>', '', c) for c in cells[:3]], [re.sub('<[^>]+>', '', c) for c in re.findall(r'<td[^>]*>(.*?)</td>', exp)[1:4]]))
            new = new.replace(m.group(0), exp, 1)
    return t[:i] + new + t[j:]

def stamp_archive(rel, t, p, Y):
    t = strip_chart(t)
    t = fix_rows_archive(rel, t, p, Y)
    ser = rank_series(p, Y); chk = {}
    blk = rank_chart.chart_block(G['BYP'][p][Y]['full_name'], ser, BANDS_OF, check=chk)
    if blk:
        i = t.index('aria-labelledby="h-rank"'); k = t.index('          <div class="deep-scroll">', i)
        t = t[:k] + blk + t[k:]; CHECKS.append((rel, chk)); STATS['chart'] += 1
    else:
        STATS['no chart (fewer than 2 ranked years)'] += 1
    return t

H2026 = re.compile(r'(        <section class="pf-card" aria-labelledby="h-rank">\n          <h2 id="h-rank">)Rank history[^<]*(</h2>\n)(.*?)(        </section>\n)', re.S)
def stamp_2026(rel, t, p):
    t = fix_rows_2026(rel, t, p)
    ser = rank_series(p, 2026); chk = {}
    q = BYP[p][2026]
    blk = rank_chart.chart_block(q['full_name'], ser, BANDS_OF, table_hint='The Band history table below repeats the same ranks, with chamber ranks.', check=chk)
    first = ser[0][0]
    yrs = f'{first}–2026' if first < 2026 else '2026'
    if blk:
        body = blk; CHECKS.append((rel, chk)); STATS['chart'] += 1
    else:
        body = '          <p class="deep-note">Only one ranked year so far, so there is no chart yet. The Band history table below shows the rank.</p>\n'
        STATS['no chart (fewer than 2 ranked years)'] += 1
    m = H2026.search(t); assert m, rel
    return t[:m.start()] + m.group(1) + f'Rank history, {yrs}' + m.group(2) + body + m.group(4) + t[m.end():]

def main():
    changed = []
    for Y in range(G['FIRST'], 2026):
        s2p = {v: k for k, v in slugs(Y, RK[Y]['all']).items()}
        for f in sorted(glob.glob(f'{ROOT}/officials/{Y}/*-deep.html')):
            rel = os.path.relpath(f, ROOT); p = s2p.get(os.path.basename(f)[:-10]); assert p, rel
            t = open(f, encoding='utf-8').read(); n = stamp_archive(rel, t, p, Y)
            if n != t: open(f, 'w', encoding='utf-8').write(n); changed.append(rel)
            STATS['pages'] += 1
    s2p = {v[0]: k for k, v in S26.items()}; s2p.update(OVERRIDE_2026)
    for f in sorted(glob.glob(f'{ROOT}/officials/*-deep.html')):
        rel = os.path.relpath(f, ROOT); p = s2p.get(os.path.basename(f)[:-10]); assert p, rel
        t = open(f, encoding='utf-8').read(); n = stamp_2026(rel, t, p)
        if n != t: open(f, 'w', encoding='utf-8').write(n); changed.append(rel)
        STATS['pages'] += 1
    print(dict(STATS)); print('changed files', len(changed))
    bad = [(r, c) for r, c in CHECKS if not c.get('labels_ok') or c.get('overlap') or not c.get('arrow_clear', True)]
    print('label problems', len(bad), bad[:10])
    fx = collections.Counter((r.split('/')[1] if r.count('/') == 2 else '2026', y, tuple(a), tuple(b)) and (r.split('/')[1] if r.count('/') == 2 else '2026', y) for r, y, a, b in FIX)
    print('row corrections (page year, row year): count', sorted(fx.items()))
    json.dump(FIX, open('/tmp/rank_chart_fixes.json', 'w'), indent=0, ensure_ascii=False)
    open('/tmp/rank_chart_changed.txt', 'w').write('\n'.join(changed) + '\n')
if __name__ == '__main__':
    main()
