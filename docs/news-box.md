# News box and Special box

The preview home page middle column shows a News box, and a Special box when one is active. Both sit above Articles. The live home page is unchanged until a later publish.

The boxes read `preview/data/news.json`. A weekly update is a new article page plus an edit to that file.

## The data file

```json
{
  "current_news": {
    "date": "2026-11-09",
    "title": "Headline",
    "summary": "Two or three sentences.",
    "url": "news/2026-11-09-slug.html"
  },
  "special": null,
  "archive": []
}
```

`url` is relative to the `preview/` folder. `date` is `YYYY-MM-DD`.

`special` is either `null` or an object with `date`, `expires`, `title`, `summary`, and `url`. `expires` is the morning the box comes down, seven days after `date`. A special posted on November 11 uses `"expires": "2026-11-18"`. It shows on November 11 through November 17, and the home page hides it on November 18. That check runs in the browser from the dates in the file, so the box disappears on the expires date even if the site is not redeployed.

## Monday news

Post one WyoVote news article each Monday, about Wyoming.

1. Add `preview/news/YYYY-MM-DD-slug.html`. Use the preview header, the Back button to Home, and the footer. Body text is 14 pt or larger, in `#142117`. No light gray text.
2. In `preview/data/news.json`, move the current `current_news` object to the front of `archive`.
3. Set `current_news` to the new article.

The previous article then leaves the home box. It is listed on `preview/news/archive.html`, newest first. The News box links there as “Past news”.

## A special

A special is optional and can be posted any day. It appears above the News box with a Special label.

1. Add `preview/news/YYYY-MM-DD-slug.html` the same way as a news article.
2. Set `special` in the JSON. Set `expires` to seven days after `date`.

To take a special down early, move that object into `archive`, add `"kind": "special"`, and set `special` to `null`.

After the expires date, the home box hides by itself and the archive page lists the special. When you next edit the file, move that object into `archive` with `"kind": "special"` and set `special` to `null`. Leaving it in `special` after it expires is safe: the home page keeps it hidden, and the archive page keeps showing it, until that cleanup.

## When a box is missing

- News only: the News box shows, and the Special box is not drawn.
- News and a current special: Special is on top, then News.
- No current news and no current special: neither box is drawn. If past items exist, the “Past news” link remains.

## Sample

The file shipped with this change uses sample headlines, “SAMPLE news article - text coming” and “SAMPLE Special - text coming”. The special is dated November 11, 2026, so both boxes are visible through November 17, 2026. Replace the sample when the real text is ready.
