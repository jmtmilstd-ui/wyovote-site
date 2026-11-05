# Reports

PDF reports for WyoVote belong in this folder, one directory per year. GitHub Pages serves each file directly.

```text
reports/
  2025/
    25-all-rank.pdf
    25-all-alpha.pdf
  2024/
  2023/
  2022/
  2021/
```

`reports/2025/` holds the current session. Older years are linked from Historical Ratings.

## File names

Use lowercase letters, digits, and hyphens. Do not put spaces, commas, `#`, `@`, or brackets in a file name. Those characters break or complicate URLs. The page that links the file keeps the original human-readable title as the link text.

Example: the original title `25, All, Rank` is stored as `reports/2025/25-all-rank.pdf`.

Keep one copy of each report. If a later file is byte-for-byte the same as one already stored, link the existing file instead of adding a second copy.

## Adding a PDF

1. Copy the PDF into the year folder, for example `reports/2025/25-house-rank.pdf`.
2. From a page in the site root, link to it with a relative address:

```html
<p><a href="reports/2025/25-house-rank.pdf">25, House, Rank</a></p>
```

3. Commit both the PDF and the page that links to it, then push to `main`.

No build step is involved. The PDF is the file you committed. Current 2025 reports belong on `reports.html` (and the two all-legislator files also on the home page). Older reports belong on `historical-ratings.html`.
