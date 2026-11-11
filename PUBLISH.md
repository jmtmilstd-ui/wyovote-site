# Publishing the preview

Work in progress lives in `preview/`. GitHub Pages serves that folder at:

- https://jmtmilstd-ui.github.io/wyovote-site/preview/
- later, https://wyovote.com/preview/

Those pages use relative links. Shared PDFs stay in `reports/`, and shared images stay in `assets/`. `preview/` does not contain its own copies.

Do not add a `CNAME` file until DNS for wyovote.com is ready.

## Publish to the live pages

The live pages are the HTML files in the repository root. Publish by copying the preview pages over those root pages in a pull request to `main`, then taking the preview-only pieces back out.

1. Copy each `preview/*.html` file to the repository root, replacing the root file of the same name.
2. Remove these from the copied pages:
   - the `PREVIEW, not the live site` banner
   - `<meta name="robots" content="noindex">`
   - the `preview.css` stylesheet link
3. Point shared files at the repository root again. In the copied pages, change `../assets/` to `assets/`, `../css/` to `css/`, and `../reports/` to `reports/`. Links from one page to another (`index.html`, `reports.html`, and the rest) stay as they are.
4. Do not copy `preview/preview.css` onto the live pages. Do not add a `CNAME` file.
5. Open a pull request to `main`. The root pages update when that pull request is merged. Leave `preview/` in place for the next round of work.

Last preview update: 2026-11-11 (2024 and 2022 candidate archives published).
