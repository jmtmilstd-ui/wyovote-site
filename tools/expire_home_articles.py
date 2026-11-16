#!/usr/bin/env python3
"""Daily check for the home Articles stack (Denver date).

  python3 -B tools/expire_home_articles.py [repo] [--date YYYY-MM-DD] [--dry-run]

Prints 'no change' and exits 0 when nothing needs expiring.
Otherwise lists the articles leaving the home page, rebuilds the block in
index.html (unless --dry-run), and exits 0. Exit 2 means the check failed.
The page still has to be committed and deployed after a rebuild; until then,
news-box.js hides expired articles in the browser on the same Denver date.
"""
import argparse, datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_home_articles as b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', nargs='?', default='.')
    ap.add_argument('--date')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    today = datetime.date.fromisoformat(a.date) if a.date else b.denver_today()
    try:
        data, page, new = b.build(a.repo, today)
    except SystemExit as e:
        print('check failed:', e); return 2
    if b.stack_part(page) == b.stack_part(new):
        print('no change'); return 0
    shown, gone = b.select(data, today)
    on_page = set(__import__('re').findall(r'<li data-date="[^"]*">\s*<h3>.*?<a href="([^"]+)"', page, __import__('re').S))
    for d, art in gone:
        if art['url'] in on_page:
            print('expire: %s  %s  (dated %s)' % (art['url'], art['title'], d.isoformat()))
    print('home now shows %d article(s)%s' % (len(shown), '' if shown else '; News-only, archive prompt shown'))
    if not a.dry_run:
        open(os.path.join(a.repo, 'index.html'), 'w', encoding='utf-8').write(new)
        print('rebuilt index.html')
    return 0


if __name__ == '__main__':
    sys.exit(main())
