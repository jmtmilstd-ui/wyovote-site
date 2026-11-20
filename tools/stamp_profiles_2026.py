#!/usr/bin/env python3
"""Extend the 93 current (2026) Profiles (officials/<slug>-deep.html) back through the first year of the current window: add earlier missed-vote and committee rows
for the years each person served in that window, and keep the header and description
in timeless wording. Band history and the rank chart already
cover the current window (tools/stamp_rank_chart.py). Also replace the 2026 issue-area rank/band columns with vote counts, and add the candidate Research section when a record exists. Idempotent: years already in a table are left alone; issue-area and Research are rewritten to the current builder output.

    python3 -B tools/stamp_profiles_2026.py [SITE_ROOT]
"""
import os, re, sys, glob, html, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
sys.path.insert(0, HERE)
import profile_data
sys.argv = ['gen.py', ROOT, '/tmp/stamp-profiles-unused', '2026']; os.environ.setdefault('OA_FIRST', '2015')
G = {'__file__': f'{HERE}/gen.py', '__name__': 'gen_lib'}
exec(compile(open(f'{HERE}/gen.py').read(), f'{HERE}/gen.py', 'exec'), G)
BYP, S26, FIRST = G['BYP'], G['S26'], G['FIRST']
OVERRIDE_2026 = {'taliaferro': 'WY-PEARSON-LAURA'}
EARLY = 2021            # the hand-built 2026 tables start here
STATS = collections.Counter()

def section(t, sid):
    i = t.index(f'aria-labelledby="{sid}"'); j = t.index('</section>', i); return i, j

def add_missed(t, p, rel):
    i, j = section(t, 'h-missed'); sec = t[i:j]
    have = [int(y) for y in re.findall(r'<tr><td>(\d{4})</td>', sec)]
    yrs = [y for y in range(EARLY - 1, FIRST - 1, -1) if y in BYP[p] and y not in have]
    if not yrs: return t
    rows = {y: '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(y, *profile_data.missed(y, BYP[p][y]['nv'])) for y in yrs}
    asc = len(have) > 1 and have[0] < have[-1]
    tb0 = sec.index('<tbody>') + len('<tbody>'); tb1 = sec.index('</tbody>')
    body = sec[tb0:tb1]
    one_line = body.strip().count('\n') == 0
    if asc:
        k = sec.index('<tr>', tb0); ind = sec[sec.rfind('\n', 0, k) + 1:k]
        ins = (''.join(rows[y] for y in sorted(yrs)) if one_line else ''.join(rows[y] + '\n' + ind for y in sorted(yrs)))
        sec = sec[:k] + ins + sec[k:]
    else:
        k = sec.rindex('</tr>', 0, tb1) + len('</tr>'); ind = re.search(r'\n( *)<tr>', sec[tb0:]).group(1)
        ins = (''.join(rows[y] for y in yrs) if one_line else ''.join('\n' + ind + rows[y] for y in yrs))
        sec = sec[:k] + ins + sec[k:]
    STATS['missed rows'] += len(yrs); STATS['pages with missed rows added'] += 1
    return t[:i] + sec + t[j:]

def add_comm(t, p, rel):
    i, j = section(t, 'h-comm'); sec = t[i:j]
    have = {int(y) for y in re.findall(r'<tr><td>(\d{4})</td>', sec)}
    rows = []
    for y in range(FIRST, EARLY):
        if y not in BYP[p] or y in have: continue
        q = BYP[p][y]
        for title, role, href in profile_data.committee_rows(y, q['chamber'], q['legislator']):
            name = f'<a href="../{href}">{html.escape(title)}</a>' if href else html.escape(title)
            rows.append(f'<tr><td>{y}</td><td>{name}</td><td>{html.escape(role)}</td></tr>')
    if not rows: return t
    if '<tbody>' in sec:
        k = sec.index('<tr>', sec.index('<tbody>')); sec = sec[:k] + '\n'.join(rows) + '\n' + sec[k:]
    else:
        m = re.search(r'          <p class="pf-none">.*?</p>\n', sec); assert m, rel
        tbl = ('          <div class="deep-scroll">\n            <table class="deep-table">\n'
               '              <thead><tr><th scope="col">Year</th><th scope="col">Committee</th><th scope="col">Role</th></tr></thead>\n'
               '              <tbody>\n                ' + '\n'.join(rows) + '\n              </tbody>\n            </table>\n          </div>\n')
        sec = sec[:m.start()] + tbl + sec[m.end():]; STATS['pages with new committee table'] += 1
    old_note = 'Committees whose published WyoVote report lists this legislator.'
    if old_note in sec: sec = sec.replace(old_note, 'Committees whose WyoVote committee data lists this legislator. Reports for 2021 and later are linked.', 1)
    STATS['committee rows'] += len(rows); STATS['pages with committee rows added'] += 1
    return t[:i] + sec + t[j:]

# Standing text stays timeless (no current-year numbers; no rolling start year).
RANGE_FIX = [('Ranks and bands are copied from the published WyoVote rating reports for 2021–2026.', 'Ranks and bands are copied from the published WyoVote rating reports.'),
             ('Ranks and bands are copied from the published WyoVote rating reports for 2008–2026.', 'Ranks and bands are copied from the published WyoVote rating reports.'),
             ('missed votes and committees from the published WyoVote reports, 2021–2026.', 'missed votes and committees from the published WyoVote reports.'),
             ('missed votes and committees from the published WyoVote reports, 2008–2026.', 'missed votes and committees from the published WyoVote reports.')]
def fix_ranges(t):
    for a, b in RANGE_FIX:
        if a in t: t = t.replace(a, b); STATS['range sentences'] += 1
    return t


ISSUE_START = '        <section class="pf-card" aria-labelledby="h-issue">'
VOTES_START = '        <section class="pf-card" aria-labelledby="h-votes">'
RESEARCH_MARK = 'aria-labelledby="h-research"'


def _section_span(t, start_marker):
    i = t.index(start_marker)
    j = t.index('</section>', i) + len('</section>')
    # include the trailing newline if present
    if j < len(t) and t[j:j+1] == '\n':
        j += 1
    return i, j


def stamp_issue_votes(t, p, rel):
    """Replace the Issue-area breakdown body with the 2026 vote-count table."""
    if ISSUE_START not in t:
        raise AssertionError(f'no issue-area section in {rel}')
    i, j = _section_span(t, ISSUE_START)
    block = (
        ISSUE_START + '\n'
        '          <h2 id="h-issue">Issue-area breakdown</h2>\n'
        + profile_data.issue_votes_block(2026, p) +
        '        </section>\n'
    )
    STATS['issue vote tables'] += 1
    return t[:i] + block + t[j:]


def stamp_research(t, p, rel, research):
    """Insert or replace the Research card. No section when this person has no record."""
    html = profile_data.research_section_html(research.get(p))
    if RESEARCH_MARK in t:
        marker = '        <section class="pf-card cand-research"'
        if marker not in t:
            marker = '        <section class="cand-research"'
        i, j = _section_span(t, marker)
        t = t[:i] + t[j:]
        # drop a leftover blank line
        t = t[:i] + t[i:].lstrip('\n')
        t = t[:i] + ('\n' if i and t[i-1] != '\n' else '') + t[i:]
    if not html:
        return t
    if VOTES_START not in t:
        raise AssertionError(f'no scored-votes section in {rel}')
    k = t.index(VOTES_START)
    STATS['research sections'] += 1
    return t[:k] + html + t[k:]


def main():
    s2p = {v[0]: k for k, v in S26.items()}; s2p.update(OVERRIDE_2026); changed = []
    research = profile_data.load_officials_research(ROOT)
    for f in sorted(glob.glob(f'{ROOT}/officials/*-deep.html')):
        rel = os.path.relpath(f, ROOT); p = s2p.get(os.path.basename(f)[:-10]); assert p, rel
        t = open(f, encoding='utf-8').read()
        if any(y < EARLY for y in BYP[p]): STATS['served before 2021'] += 1
        n = fix_ranges(add_comm(add_missed(t, p, rel), p, rel))
        n = stamp_issue_votes(n, p, rel)
        n = stamp_research(n, p, rel, research)
        if n != t: open(f, 'w', encoding='utf-8').write(n); changed.append(rel)
        STATS['pages'] += 1
    print(dict(STATS)); print('changed files', len(changed))
    print('research available', sum(1 for rec in research.values() if profile_data.research_has_content(rec)))
    open('/tmp/stamp_profiles_2026_changed.txt', 'w').write('\n'.join(changed) + '\n')
if __name__ == '__main__':
    main()
