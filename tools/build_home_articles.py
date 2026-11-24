#!/usr/bin/env python3
"""Build the home-page Articles stack (middle column, under the News box).

Rule: at most max_items (4) articles, newest on top, and none older than
max_age_days (7) by article date, counted on the Denver calendar date.
An article dated D shows through D + 7 days and leaves the home page on
D + 8. Features and research articles follow the same rule; nothing is
exempt. It stays on archive/articles.html.

Source: data/home-articles.json. Target: the block between the
HOME-ARTICLES markers in index.html.

  python3 -B tools/build_home_articles.py [repo] [--date YYYY-MM-DD] [--out FILE] [--check]

--date   pretend today is this Denver date (testing)
--out    write the page here instead of rewriting index.html
--check  do not write; exit 1 if index.html is out of date, 0 if not
"""
import argparse, datetime, html, json, os, re, sys
from zoneinfo import ZoneInfo

START = '<!-- HOME-ARTICLES:START'
END = '<!-- HOME-ARTICLES:END -->'
KICKERS = {'feature': 'Feature', 'research': 'Research', 'news': 'News'}
MONTHS = ['Jan.', 'Feb.', 'March', 'April', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']


def denver_today():
    return datetime.datetime.now(ZoneInfo('America/Denver')).date()


def esc(s):
    return html.escape(s, quote=True)


def label(d):
    return '%s %d, %d' % (MONTHS[d.month - 1], d.day, d.year)


def select(data, today):
    """Return (shown, expired) lists of (date, article)."""
    max_items = int(data.get('max_items', 4))
    max_age = int(data.get('max_age_days', 7))
    items = [(datetime.date.fromisoformat(a['date']), i, a) for i, a in enumerate(data['articles'])]
    items.sort(key=lambda t: (-t[0].toordinal(), t[1]))  # newest first, file order for ties
    fresh = [(d, a) for d, _, a in items if 0 <= (today - d).days <= max_age]
    old = [(d, a) for d, _, a in items if (today - d).days > max_age]
    return fresh[:max_items], old + fresh[max_items:]


def render(data, today):
    shown, _ = select(data, today)
    max_items = int(data.get('max_items', 4)); max_age = int(data.get('max_age_days', 7))
    out = ['%s (built by tools/build_home_articles.py from data/home-articles.json for %s. Max %d, newest on top, none older than %d days. Do not edit by hand.) -->'
           % (START, today.isoformat(), max_items, max_age)]
    if shown:
        out.append('          <ul class="article-list" data-max-items="%d" data-max-age-days="%d">' % (max_items, max_age))
        for d, a in shown:
            k = a.get('kicker')
            kick = ('<span class="news-kicker news-kicker-%s">%s</span> ' % (k, KICKERS.get(k, k.title()))) if k else ''
            out += ['            <li data-date="%s">' % d.isoformat(),
                    '              <h3>%s<a href="%s">%s</a></h3>' % (kick, esc(a['url']), esc(a['title'])),
                    '              <p class="article-date"><time datetime="%s">%s</time></p>' % (d.isoformat(), label(d)),
                    '              <p class="article-excerpt">%s</p>' % esc(a['excerpt']),
                    '            </li>']
        out.append('          </ul>')
    out.append('          <p class="archive-prompt"%s><a class="archive-prompt-btn" href="archive/articles.html">Older articles are in the Archive&nbsp;&rarr;</a></p>' % ('' if not shown else ' hidden'))
    out.append('          <p class="column-foot"%s><a href="archive/articles.html">More articles in the Archive&nbsp;&rarr;</a></p>' % (' hidden' if not shown else ''))
    out.append('          ' + END)
    return '\n'.join(out)


def build(repo, today):
    data = json.load(open(os.path.join(repo, 'data', 'home-articles.json'), encoding='utf-8'))
    page = open(os.path.join(repo, 'index.html'), encoding='utf-8').read()
    m = re.search(re.escape(START) + r'.*?' + re.escape(END), page, re.S)
    if not m:
        sys.exit('index.html has no HOME-ARTICLES markers')
    new = page[:m.start()] + render(data, today) + page[m.end():]
    return data, page, new


def stack_part(page):
    """The block without its build-date comment, to compare content only."""
    m = re.search(re.escape(START) + r'.*?' + re.escape(END), page, re.S)
    return re.sub(r'for \d{4}-\d{2}-\d{2}\.', '', m.group(0)) if m else ''


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('repo', nargs='?', default='.')
    ap.add_argument('--date')
    ap.add_argument('--out')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args(argv)
    today = datetime.date.fromisoformat(a.date) if a.date else denver_today()
    data, page, new = build(a.repo, today)
    shown, _ = select(data, today)
    changed = stack_part(page) != stack_part(new)
    if a.check:
        print('out of date' if changed else 'up to date'); return 1 if changed else 0
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(new)
    elif changed:
        open(os.path.join(a.repo, 'index.html'), 'w', encoding='utf-8').write(new)
    print('%s: %d article(s) on home%s' % (today.isoformat(), len(shown), '' if changed or a.out else ' (no change)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
