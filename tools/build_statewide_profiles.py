#!/usr/bin/env python3
"""Build the statewide-official Profiles (officials/statewide/<slug>.html) and the add-on index statewide-profiles.html
from /workspace/wyoleg/statewide/ (tools/statewide_data.py), and put a Statewide Profile button on the 2026 Profiles of
legislators who also hold or were elected to a statewide office. Idempotent.

Michael (Nov 15): statewide offices are not added piecemeal to the 2008-2025 archive year pages or Officials year lists;
these pages are reached only from legislator Profiles, statewide-profiles.html, and one link line on officials.html.

    python3 -B tools/build_statewide_profiles.py [SITE_ROOT]
"""
import os, re, sys, html, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
sys.path.insert(0, HERE)
import statewide_data as S
E = html.escape

def leg_profiles():
    """statewide person_id -> (href from site root of the canonical legislator Profile, list of all that person's Profile pages)."""
    sys.argv = ['gen.py', ROOT, '/tmp/statewide-unused', '2026']; os.environ.setdefault('OA_FIRST', '2008')
    g = {'__file__': f'{HERE}/gen.py', '__name__': 'gen_lib'}
    exec(compile(open(f'{HERE}/gen.py').read(), f'{HERE}/gen.py', 'exec'), g)
    out = {}
    for p in S.LEG_PEOPLE:
        k = S.site_key(p); yrs = sorted(g['BYP'][k]); pages = [f'officials/{y}/{g["slug_of"](k, y)}-deep.html' for y in yrs if y < 2026]
        if 2026 in yrs: canon = f'officials/{g["S26"][k][0]}-deep.html'; pages.append(canon)
        else: canon = pages[-1]
        for f in pages: assert os.path.exists(f'{ROOT}/{f}'), f
        out[p] = (canon, pages, yrs)
    return out

TPL = open(f'{ROOT}/officials/case-deep.html', encoding='utf-8').read()
HEAD = TPL[:TPL.index('    <main id="main" class="profile">')]
FOOT = TPL[TPL.index('    </main>'):TPL.index('      <script>')] + '\n  </body>\n</html>\n'
def page(depth, title, desc, body, current='officials'):
    up = '../' * depth
    h = HEAD.replace('href="../', f'href="{up}').replace('src="../', f'src="{up}')
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h)
    if depth == 0:
        h = h.replace('href="profile.css"', 'href="officials/profile.css"')
    elif depth == 2:
        h = h.replace('href="profile.css"', 'href="../profile.css"')
    f = FOOT.replace('href="../', f'href="{up}')
    return h + '    <main id="main" class="profile">\n      <div class="wrap">\n' + body + '      </div>\n' + f

def md_inline(s):
    s = E(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return s
README = open(f'{S.SRC}/README.md', encoding='utf-8').read()
GAPS = [b[2:].strip() for b in re.split(r'\n(?=- )', README.split('## Gaps and notes', 1)[1].strip())]
assert len(GAPS) == 9, len(GAPS)
GAP_PEOPLE = [  # README bullet -> people it is about (slugs)
    {'meyer-joseph', 'gordon'},
    {'meyer-joseph', 'gordon', 'murray', 'wheeler', 'buchanan', 'allred', 'balow', 'schroeder'},
    {'allred'}, {'hill'}, {'meier', 'buchanan', 'harshman', 'short'},
    {'freudenthal', 'maxfield', 'meyer-rita', 'meyer-joseph', 'mcbride'},
    {'mead'}, {'gordon'}, {'barlow', 'short', 'harshman', 'meier', 'racines'}]

def num(s): return f'{int(s):,}' if s else ''
def pct(s): return f'{float(s):.2f}%' if s else ''
def ext(url): return f'<a href="{E(url)}">{E(url)}</a> <span class="ext">(leaves WyoVote)</span> '   # same form as tools/mark_outside_links.py
def term_label(r):
    if r['elect_not_yet_sworn'] == 'yes': return S.ELECT_LABEL
    return f'{S.fmt_date(r["term_start"])} – {S.fmt_date(r["term_end"])}'
def how(r):
    h = r['how_took_office']
    return {'elected': 'Elected', 'appointed': f'Appointed {S.fmt_date(r["appointment_date"])}' if r['appointment_date'] else 'Appointed', 'acting': 'Acting'}.get(h, h)

def table(head, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    return ('          <div class="deep-scroll">\n            <table class="deep-table">\n'
            f'              <thead><tr>{th}</tr></thead>\n              <tbody>\n'
            + '\n'.join('                <tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
            + '\n              </tbody>\n            </table>\n          </div>\n')
def card(hid, title, inner, note=None):
    n = f'          <p class="deep-note">{note}</p>\n' if note else ''
    return f'        <section class="pf-card" aria-labelledby="{hid}">\n          <h2 id="{hid}">{title}</h2>\n{n}{inner}        </section>\n'

def vetoes_of(p):
    by = collections.OrderedDict()
    for v in S.VETOES:
        if v['governor_person_id'] == p: by.setdefault((v['year'], v['bill']), []).append(v)
    return by

def build_person(p, LP):
    rs = sorted(S.BY_PERSON[p], key=lambda r: r['term_start']); r0 = rs[0]; slug = S.SLUG[p]; name = r0['full_name']
    offices = S.offices_of(p)
    sub = 'Statewide Profile · ' + ' and '.join(offices) + f' · {r0["party"]}'
    body = f'        <p class="back-row"><a class="back-btn" href="../../statewide-profiles.html">← Back to Statewide Profiles</a></p>\n'
    body += f'        <section class="pf-head" aria-labelledby="h-name">\n          <h1 id="h-name">{E(name)}</h1>\n          <p class="pf-sub">{E(sub)}</p>\n'
    if S.is_elect_only(p):
        body += f'          <p class="pf-sub">{S.ELECT_LABEL}</p>\n'
    if p in LP:
        body += f'          <p class="pf-links"><a class="pf-btn" href="../../{LP[p][0]}">Legislator Profile →</a></p>\n'
    body += '          <p class="pf-links"><span class="pf-asof">From the official Wyoming Secretary of State rosters and election results, as of Nov 16, 2026. Gaps are shown as the source files note them.</span></p>\n        </section>\n'
    rows = [[E(r['office']), term_label(r), how(r), E(r['term_end_reason'])] for r in rs]
    body += card('h-terms', 'Terms in office', table(['Office', 'Term', 'Took office', 'Term end'], rows),
                 'One row per term, oldest first. Regular terms begin the first Monday in January after the election.')
    el = [r for r in rs if r['election_year']]
    if el:
        rows = []
        for r in el:
            pri = f'{E(r["primary_party"])}: {num(r["primary_votes"])} votes, {pct(r["primary_pct"])}' if r['primary_votes'] else ''
            gen = f'{num(r["general_votes"])} votes, {pct(r["general_pct"])}' if r['general_votes'] else ''
            ru = (f'{E(r["general_runner_up"])} ({E(r["general_runner_up_party"])}), {pct(r["general_runner_up_pct"])}' if r['general_runner_up'] else 'none listed')
            rows.append([r['election_year'], E(r['office']), pri, gen, ru])
        body += card('h-elect', 'Elections', table(['Year', 'Office', 'Primary', 'General', 'General runner-up'], rows),
                     'Percent is of votes for named candidates (write-ins, overvotes and undervotes left out). Official results.')
    else:
        body += card('h-elect', 'Elections', '          <p class="pf-none">No election for this office in these files: this person took office by appointment or as acting official.</p>\n')
    if 'Governor' in offices:
        vb = vetoes_of(p)
        if vb:
            rows = []
            for (y, b), vs in sorted(vb.items(), key=lambda kv: (-int(kv[0][0]), kv[0][1])):
                v = vs[0]; items = f' ({len(vs)} roll calls)' if v['veto_type'] == 'line-item' and len(vs) > 1 else ''
                rows.append([y, E(b), E(v['catch_title']), E(v['veto_type']) + items, E(v['bill_override_outcome'])])
            body += card('h-veto', f'Vetoes, {len(vb)} bills', table(['Year', 'Bill', 'Title', 'Veto type', 'Override outcome'], rows),
                         'Vetoes found in the wyoleg bill status (last action) and WyoVote roll calls, newest first. Override outcome is as the file records it.')
        else:
            body += card('h-veto', 'Vetoes', '          <p class="pf-none">No vetoes in these files for this governor’s years (2008 on).</p>\n')
    if r0['prior_leg_years'] or p in LP:
        rr = [r for r in rs if r['prior_leg_years']][0]
        inner = table(['Years', 'Chamber', 'District'], [[E(rr['prior_leg_years']), E(rr['prior_leg_chamber']), E(rr['prior_leg_district'])]])
        inner += f'          <p class="deep-note">{E(rr["prior_leg_note"])}</p>\n'
        if p in LP: inner += f'          <p class="pf-dive"><a class="pf-dive-btn" href="../../{LP[p][0]}">Legislator Profile →</a></p>\n'
        body += card('h-leg', 'Legislative service', inner, 'WyoVote rosters start in 2008.')
    notes = [r['notes'] for r in rs if r['notes']]
    if notes:
        body += card('h-notes', 'Notes', '          <ul class="pf-list">\n' + ''.join(f'            <li>{E(n)}</li>\n' for n in dict.fromkeys(notes)) + '          </ul>\n',
                     'Copied from the source file, one line per term note.')
    gaps = [GAPS[i] for i, ps in enumerate(GAP_PEOPLE) if slug in ps]
    if gaps:
        body += card('h-gaps', 'Gaps in the data', '          <ul class="pf-list">\n' + ''.join(f'            <li>{md_inline(g)}</li>\n' for g in gaps) + '          </ul>\n',
                     'Copied word for word from the source notes. Nothing here is filled in or estimated.')
    urls = list(dict.fromkeys(u.strip() for r in rs for u in r['source_urls'].split('|') if u.strip()))
    body += card('h-src', 'Sources', '          <ul class="pf-list">\n' + ''.join(f'            <li>{ext(u)}</li>\n' for u in urls) + '          </ul>\n')
    return page(2, f'{name} — Statewide Profile — WyoVote', f'{name}: statewide office terms, elections and sources, 2007 terms to 2027.', body)

def build_index():
    body = '        <p class="back-row"><a class="back-btn" href="officials.html">← Back to Officials</a></p>\n'
    body += ('        <section class="pf-head" aria-labelledby="h-name">\n          <h1 id="h-name">Statewide Profiles</h1>\n'
             '          <p class="pf-sub">Governor, Secretary of State, State Auditor, State Treasurer, Superintendent of Public Instruction · 2007 terms to the 2026 elects</p>\n'
             '          <p class="pf-links"><span class="pf-asof">From the official Wyoming Secretary of State rosters and election results, as of Nov 16, 2026.</span></p>\n        </section>\n')
    for o in S.OFFICES:
        rows = []
        for r in S.TERMS:
            if r['office'] != o: continue
            p = r['person_id']
            rows.append([f'<a href="officials/statewide/{S.SLUG[p]}.html">{E(r["full_name"])}</a>', E(r['party']), term_label(r), how(r)])
        hid = 'h-' + re.sub(r'[^a-z]+', '-', o.lower()).strip('-')
        body += card(hid, E(o), table(['Name', 'Party', 'Term', 'Took office'], rows), 'Oldest first. Each name opens that person’s Statewide Profile.')
    body += card('h-gaps', 'Gaps in the data', '          <ul class="pf-list">\n' + ''.join(f'            <li>{md_inline(g)}</li>\n' for g in GAPS) + '          </ul>\n',
                 'Copied word for word from the source notes. Nothing here is filled in or estimated.')
    return page(0, 'Statewide Profiles — WyoVote', 'Profiles of Wyoming statewide elected officials, 2007 terms to the 2026 elects.', body)

def stamp_2026_buttons(LP):
    n = 0
    for p, (canon, pages, yrs) in LP.items():
        if not canon.count('/') == 1: continue                  # only 2026 Profiles; gen.py writes the button on 2008-2025 pages
        f = f'{ROOT}/{canon}'; t = open(f, encoding='utf-8').read()
        line = f'          <p class="pf-links"><a class="pf-btn" href="statewide/{S.SLUG[p]}.html">{S.link_label(p)}</a></p>\n'
        if line in t: continue
        i = t.index('<section class="pf-head"'); j = t.index('        </section>', i)
        t = t[:j] + line + t[j:]; open(f, 'w', encoding='utf-8').write(t); n += 1
    return n

OFFICIALS_LINE = '          <p class="year-choice">Statewide Profiles for these five offices, 2007 terms to the 2026 elects: <a href="statewide-profiles.html">Statewide Profiles</a>.</p>\n'
def stamp_officials():
    f = f'{ROOT}/officials.html'; t = open(f, encoding='utf-8').read()
    if OFFICIALS_LINE in t: return 0
    i = t.index('aria-labelledby="state-heading"'); j = t.index('          </ul>\n', i) + len('          </ul>\n')
    t = t[:j] + OFFICIALS_LINE + t[j:]; open(f, 'w', encoding='utf-8').write(t); return 1

def main():
    LP = leg_profiles()
    os.makedirs(f'{ROOT}/officials/statewide', exist_ok=True)
    for p in S.BY_PERSON:
        open(f'{ROOT}/officials/statewide/{S.SLUG[p]}.html', 'w', encoding='utf-8').write(build_person(p, LP))
    open(f'{ROOT}/statewide-profiles.html', 'w', encoding='utf-8').write(build_index())
    print('statewide profiles', len(S.BY_PERSON), 'linked', {p: LP[p][0] for p in LP})
    print('2026 buttons added', stamp_2026_buttons(LP), 'officials.html line added', stamp_officials())
    # every year's Profile of a linked person must carry the button (gen.py for 2008-2025)
    for p, (canon, pages, yrs) in LP.items():
        for f in pages: assert f'statewide/{S.SLUG[p]}.html' in open(f'{ROOT}/{f}', encoding='utf-8').read(), f
if __name__ == '__main__':
    main()
