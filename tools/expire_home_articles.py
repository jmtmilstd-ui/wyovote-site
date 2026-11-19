#!/usr/bin/env python3
"""Daily check for the home Articles stack (Denver date).

  python3 -B tools/expire_home_articles.py [repo] [--date YYYY-MM-DD] [--dry-run]

Prints 'no change' and exits 0 when nothing needs expiring.
Otherwise lists the articles leaving the home page, rebuilds the block in
index.html (unless --dry-run), and exits 0. Exit 2 means the check failed.
The page still has to be committed and deployed after a rebuild; until then,
news-box.js hides expired articles in the browser on the same Denver date.

The 7-day rule covers every home item: normal, feature and research
articles, the News box and a Special. The News box and a Special come from
data/news.json and are hidden by news-box.js; this check names them when
they are past the limit so data/news.json can be tidied.
"""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_home_articles as b


def stale_boxes(repo, today, max_age):
    """Report a News box or Special in data/news.json older than max_age days."""
    try:
        news = json.load(open(os.path.join(repo, 'data', 'news.json'), encoding='utf-8'))
    except (OSError, ValueError):
        return
    max_age = int(news.get('home_max_age_days', max_age))
    for key, name in (('current_news', 'News box'), ('special', 'Special')):
        item = news.get(key)
        if not item or not item.get('date'):
            continue
        age = (today - datetime.date.fromisoformat(item['date'])).days
        if age > max_age:
            print('%s past %d days (hidden on home by news-box.js): %s  (dated %s)'
                  % (name, max_age, item.get('title', ''), item['date']))


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
    stale_boxes(a.repo, today, int(data.get('max_age_days', 7)))
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
