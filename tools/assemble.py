import os, glob, shutil, re
from to_preview import to_preview
B='/workspace/officials-archive/base'; S='/workspace/officials-archive/site'
YRS=[2024,2023,2022,2021]
for y in YRS:
    os.makedirs(f'{S}/preview/officials/{y}', exist_ok=True)
    for f in glob.glob(f'{S}/officials/{y}/*.html'):
        open(f'{S}/preview/officials/{y}/'+os.path.basename(f),'w').write(to_preview(open(f).read(),2))
    os.makedirs(f'{S}/preview/data', exist_ok=True)
    shutil.copy(f'{S}/data/roll-calls-{y}.json', f'{S}/preview/data/roll-calls-{y}.json')
# archive index
old='            <li class="archive-item"><a href="../officials/2025/index.html">2025</a> <span class="archive-meta">Session roster</span></li>\n'
new=old+''.join(f'            <li class="archive-item"><a href="../officials/{y}/index.html">{y}</a> <span class="archive-meta">Session roster</span></li>\n' for y in YRS)
for rel in ('archive/officials.html','preview/archive/officials.html'):
    t=open(f'{B}/{rel}').read(); assert t.count(old)==1; os.makedirs(os.path.dirname(f'{S}/{rel}'),exist_ok=True)
    open(f'{S}/{rel}','w').write(t.replace(old,new))
# CSS: extend the pf-2025 size rules to the archive years
sel=lambda pre: ', '.join(f'{pre}{y}' for y in (2021,2022,2023,2024,2025))
for rel in ('assets/css/site.css','preview/preview.css'):
    t=open(f'{B}/{rel}').read()
    o1='body.pf-2025 {\n'; o2='body.pf-2025 table.deep-table,\nbody.pf-2025 .deep-votes td {\n'
    assert t.count(o1)==1 and t.count(o2)==1
    t=t.replace(o1, ',\n'.join(f'body.pf-{y}' for y in (2021,2022,2023,2024,2025))+' {\n')
    t=t.replace(o2, ',\n'.join(f'body.pf-{y} table.deep-table,\nbody.pf-{y} .deep-votes td' for y in (2021,2022,2023,2024,2025))+' {\n')
    os.makedirs(os.path.dirname(f'{S}/{rel}'),exist_ok=True); open(f'{S}/{rel}','w').write(t)
for rel in ('officials/profile.css','preview/officials/profile.css'):
    t=open(f'{B}/{rel}').read(); o='body.pf.pf-2025 { font-size: 14pt; }'; assert t.count(o)==1
    open(f'{S}/{rel}','w').write(t.replace(o, ', '.join(f'body.pf.pf-{y}' for y in (2021,2022,2023,2024,2025))+' { font-size: 14pt; }'))
print('ok')
# --- follow-up 2026-11-15: party L/I button colors + 300 MB tree limit ---
LI = '''
.official-btn.party-l {
  background: #c99700;
  border-color: #5c4306;
  color: #142117;
}

.official-btn.party-l:hover,
.official-btn.party-l:focus-visible {
  background: #a87e00;
  color: #142117;
}

.official-btn.party-i {
  background: #4b2a7b;
  border-color: #2e1850;
  color: #ffffff;
}

.official-btn.party-i:hover,
.official-btn.party-i:focus-visible {
  background: #351c5a;
  color: #ffffff;
}
'''
anchor = '''.official-btn.party-d:hover,
.official-btn.party-d:focus-visible {
  background: #e8eef8;
  color: #1a4a8a;
}
'''
for rel in ('assets/css/site.css', 'preview/preview.css'):
    t = open(f'{S}/{rel}').read(); assert t.count(anchor) == 1
    open(f'{S}/{rel}', 'w').write(t.replace(anchor, anchor + LI))
t = open(f'{B}/tools/publish_check.py').read()
for o, n in (('over 200 MB (209,715,200 bytes)', 'over 300 MB (314,572,800 bytes)'), ('TREE_LIMIT = 200 * 1024 * 1024', 'TREE_LIMIT = 300 * 1024 * 1024'), ('bytes (200 MB)")', 'bytes (300 MB)")')):
    assert t.count(o) == 1, o; t = t.replace(o, n)
os.makedirs(f'{S}/tools', exist_ok=True); open(f'{S}/tools/publish_check.py', 'w').write(t)
print('followup ok')
