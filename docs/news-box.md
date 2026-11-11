# News box and Special box

The home page middle column shows a News box, and a Special box when one is active. Both sit above Articles. The same boxes are on the preview home page.

The live files are:

- `data/news.json`
- `news-box.js`
- `news/YYYY-MM-DD-slug.html`
- `news/archive.html`

Keep the copies under `preview/` the same: `preview/data/news.json`, `preview/news-box.js`, and `preview/news/`. A weekly update edits both copies.

## The data file

```json
{
  "current_news": {
    "date": "2026-11-16",
    "date_label": "Week of Nov 16, 2026",
    "title": "Headline",
    "summary": "About five lines in the home column.",
    "url": "news/2026-11-16-slug.html"
  },
  "special": null,
  "archive": []
}
```

`url` is relative to the site root. `date` is `YYYY-MM-DD`. Optional `date_label` is the text shown on the box, such as `Week of Nov 16, 2026`. When it is omitted, the box shows the formatted `date`.

The `summary` is the text in the home-page box. Write it to about five lines at that column’s width. The page also clamps the summary at five lines. Keep the label, date, headline, Read more link, and Past news link.

`special` is either `null` or an object with `date`, `expires`, `title`, `summary`, and `url`. `expires` is the morning the box comes down. The check runs in the browser, so the box disappears on that morning even if the site is not redeployed.

## Monday news

Post one WyoVote news article each Monday, about Wyoming. Write 300 to 500 words in the WyoVote article voice: short sentences, the facts in hand, and no new claims. Use the standard article template (`article-body`, byline, date, deck, section headings, and a numbered Credits and Sources list). Put a News tag at the top. The Back button returns to Home. Body text stays 14 pt or larger, in `#142117`, with no light gray.

1. Add `news/YYYY-MM-DD-slug.html`, and the same page at `preview/news/YYYY-MM-DD-slug.html`.
2. In `data/news.json` and `preview/data/news.json`, move the current `current_news` object to the front of `archive`.
3. Set `current_news` to the new article.

The previous article then leaves the home box. On the preview home page, Past news goes to the Archive Articles page (`preview/archive/articles.html`). That page reads `news.json`, so the outgoing article and the new one appear in the same list as the other articles, newest first, with a News tag. You do not add those lines by hand. A special in the file appears there with a Special tag.

`preview/news/archive.html` redirects to the Archive Articles page so older links still land there.

A regular article, one that is not news or a special, is still added by hand in the article list inside `preview/archive/articles.html`. Title and date only.

## A special

A special is optional and can be posted any day. It appears above the News box with a Special label.

1. Add the article page the same way, with a Special tag instead of a News tag.
2. Set `special` in both JSON files. Set `expires` to the morning the box should come down.

To take a special down early, move that object into `archive`, add `"kind": "special"`, and set `special` to `null`.

After the expires date, the home box hides by itself and the archive page lists the special. When you next edit the file, move that object into `archive` with `"kind": "special"` and set `special` to `null`. Leaving it in `special` after it expires is safe: the home page keeps it hidden, and the archive page keeps showing it, until that cleanup.

## When a box is missing

- News only: the News box shows, and the Special box is not drawn.
- News and a current special: Special is on top, then News.
- No current news and no current special: neither box is drawn. If past items exist, the “Past news” link remains.

## Current items

The interim-committees article is the current news, published Nov. 11, 2026. Its dateline stays “Week of Nov 16, 2026.”

The next scheduled news article is Monday, Nov. 16, 2026. That article replaces this one. Move this one to the front of `archive`.

The special on certified election results shows from Nov. 11, 2026. It stays up through Nov. 18 and hides the morning of Nov. 19 (`expires` is `2026-11-19`).
