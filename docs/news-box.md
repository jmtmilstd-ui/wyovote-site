# News box and home notices

The home page has three columns. The middle column and the right column each open with one solid dark green line, and neither column has a title. The News box sits under the middle line, then the article list. The right-hand column is for standing notices. “What is WyoVote?” sits at the top of that column. When no other notice is posted, the line under it reads “Standing notices appear here.”

The live files are:

- `data/news.json`
- `news-box.js`
- `news/YYYY-MM-DD-slug.html`
- `news/archive.html`

There is one copy of each file (single tree since 2026-11-15; there is no `preview/` copy). Review a change on a Cloudflare branch preview.

## The data file

```json
{
  "home_max_age_days": 7,
  "current_news": {
    "date": "2026-11-16",
    "date_label": "Week of Nov 16, 2026",
    "title": "Headline",
    "summary": "About five lines in the home column.",
    "url": "news/2026-11-16-slug.html"
  },
  "archive": []
}
```

`url` is relative to the site root. `date` is `YYYY-MM-DD`. Optional `date_label` is the text shown on the box, such as `Week of Nov 16, 2026`. When it is omitted, the box shows the formatted `date`.

The `summary` is the text in the home-page box. Write it to about five lines at that column’s width. The page also clamps the summary at five lines. Keep the label, date, headline, Read more link, and Past news link.

## Monday news

Post one WyoVote news article each Monday, about Wyoming. Write 300 to 500 words in the WyoVote article voice: short sentences, the facts in hand, and no new claims. Use the standard article template (`article-body`, byline, date, deck, section headings, and a numbered Credits and Sources list). Put a News tag at the top. The Back button returns to Home. Body text stays 14 pt or larger, in `#142117`, with no light gray.

1. Add `news/YYYY-MM-DD-slug.html`.
2. In `data/news.json`, move the current `current_news` object to the front of `archive`.
3. Set `current_news` to the new article.

The previous article then leaves the home box. Past news goes to the Archive Articles page (`archive/articles.html`). That page reads `news.json`, so the outgoing article and the new one appear in the same list as the other articles, newest first, with a News tag. You do not add those lines by hand.

`news/archive.html` redirects to the Archive Articles page so older links still land there.

A regular article, one that is not news, is still added by hand in the article list inside `archive/articles.html`. Title and date only. Its home-page line comes from `data/home-articles.json` (see the 7-day rule below).

## The 7-day rule (every home item)

Nothing older than 7 days shows on the home page. This covers every kind of item: normal articles, features, research articles, and the News box. Nothing is exempt. Age is counted on the Denver calendar date. An item dated D shows through D + 7 days and leaves the home page on the morning of D + 8, even when nothing new is posted.

- News box: hidden once `current_news` is more than 7 days old (`home_max_age_days` in `data/news.json`). The “Past news” link stays.
- Article list: see the next section.

Items that leave the home page stay on the Archive Articles page (`archive/articles.html`).

## Home Articles column

The article list under the News box follows two rules at once:

- At most 4 articles, newest on top. A new article pushes the oldest one down and off.
- No article older than 7 days (`max_age_days` in `data/home-articles.json`). Features and research articles follow the same rule.

Articles that leave the home page stay on the Archive Articles page (`archive/articles.html`) only.

The list is built, not typed into `index.html`:

- `data/home-articles.json` holds the articles that may appear on the home page (date, kicker, title, url, excerpt). `kicker` is `feature`, `research`, or `null`.
- `tools/build_home_articles.py` writes the block between the `HOME-ARTICLES` markers in `index.html`. `--date YYYY-MM-DD` renders a test date; `--check` exits 1 if the page is out of date.
- `tools/expire_home_articles.py` is the daily check. It prints `no change` and exits 0 when nothing needs expiring. Otherwise it lists the articles leaving the home page and rebuilds `index.html`, which then needs a commit and a deploy. It also names a News box in `data/news.json` that is past 7 days, so that file can be tidied.
- `news-box.js` applies the same rule in the browser on the Denver date, to the article list and the News box, so an item leaves on time even before the next deploy. The right-hand column keeps the standing-notices caption.

When no article is within 7 days, the News box is the only item in the column. A large dark green button, “Older articles are in the Archive →”, then shows under it and links to `archive/articles.html`. While articles are shown, a smaller “More articles in the Archive →” link sits at the bottom of the column instead.

To add a regular article:

1. Add the article page and its line in `archive/articles.html`, as before.
2. Add it at the top of `articles` in `data/home-articles.json`.
3. Run `python3 -B tools/build_home_articles.py .` and commit `index.html` with the data file.

## When a box is missing

- Current news within 7 days: the News box shows under the middle line. The right column keeps “What is WyoVote?” and the standing-notices caption.
- No current news: the News box is not drawn. The right column is unchanged. If past items exist, the “Past news” link remains in the middle column.

## Current items

The supplemental-budget article is the current news, published Nov. 23, 2026. Its dateline is “Week of Nov 23, 2026.”

The new-leaders article (Nov. 16, 2026) moved to the front of `archive`.

The next scheduled news article is Monday, Nov. 30, 2026. That article replaces this one.

The Nov. 11, 2026 certified election results article is a normal archived news article.

As of Nov. 19, 2026, three features are within 7 days, all dated Nov. 19, 2026, in this order: “How Yellowstone Became the First National Park,” “The Eaton Family's Long Ride on Wolf Creek,” and “The Long Fight That Finished Grand Teton National Park.” All three show through Nov. 26 and leave the home page the morning of Nov. 27. The four earlier articles are on the Archive Articles page only.
