# Reports

PDF reports for WyoVote belong in this folder. During a legislative session they may be updated every day. GitHub Pages serves each file directly, so a new or replaced PDF is published with the rest of the site.

## Organization

Keep one folder per year:

```text
reports/
  2025/
    house-ratings.pdf
    senate-ratings.pdf
  2026/
    house-ratings.pdf
```

Add a new year folder when that session’s reports begin. Use clear, stable filenames. If a daily update should replace yesterday’s file, keep the same name so links already on the site do not break.

`reports/2025/` is the first year folder. It is empty until PDFs are added.

## Adding a PDF

1. Copy the PDF into the year folder, for example `reports/2025/house-ratings.pdf`.
2. From a page in the site root, link to it with a relative address:

```html
<p><a href="reports/2025/house-ratings.pdf">House ratings (PDF)</a></p>
```

3. Commit both the PDF and the page that links to it, then push to `main`.

No build step is involved. The PDF is the file you committed.
