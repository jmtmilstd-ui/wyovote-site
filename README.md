# WyoVote

Static website for WyoVote, which publishes Wyoming legislator ratings. The site is plain HTML and CSS. There is no build step. GitHub Pages can serve it directly from the repository root of the `main` branch.

Do not add a `CNAME` file. The custom domain is not being changed yet.

## Folder layout

| Path | Purpose |
| --- | --- |
| `index.html` | Home page |
| `legislative-ratings.html` | Legislative Ratings (placeholder) |
| `committee-ratings.html` | Committee Ratings (placeholder) |
| `county-ratings.html` | County Ratings (placeholder) |
| `archive.html` | Archive (placeholder) |
| `contact.html` | Contact (placeholder) |
| `css/styles.css` | All styles. The hero photo is the `--hero-background-image` variable at the top of this file. |
| `assets/img/surveyor-icon.png` | Header logo (green surveyor) |
| `assets/img/surveyor-banner.png` | Logo plus the WyoVote wordmark, kept for later use |
| `assets/img/owl-silhouette.jpg` | Kept for later use |
| `assets/img/backgrounds/` | Hero and other background photos |
| `reports/` | PDF reports, organized by year (for example `reports/2025/`) |
| `COPYRIGHT.md` | Copyright notice. Site content is not open source. |
| `.nojekyll` | Tells GitHub Pages to skip Jekyll and serve the files as they are |

## Hero background

Background photos are not in place yet. The hero uses a dark-green gradient so the heading stays easy to read.

To use a photo later:

1. Add the image under `assets/img/backgrounds/`.
2. In `css/styles.css`, set `--hero-background-image` to that file:

```css
--hero-background-image: url("../assets/img/backgrounds/wyoming.jpg");
```

That variable is the only place to change. A dark overlay stays on top of the photo so the white heading remains high contrast.

## How to add a PDF and link it

1. Put the file in a year folder. Create the folder if it does not exist yet:

```text
reports/2026/senate-ratings.pdf
```

2. Link it from the page where it should appear. From a page in the site root, the address is:

```html
<p><a href="reports/2026/senate-ratings.pdf">Senate ratings (PDF)</a></p>
```

3. Commit the PDF and the updated HTML, then push to `main`.

GitHub Pages serves the PDF at that same path. Replacing a file without renaming it keeps existing links working. More detail is in `reports/README.md`.

## Publishing

In the repository settings, set GitHub Pages to deploy from the `main` branch and the root folder (`/`). No build command is required. Leave the custom domain blank.

## Local preview

Open `index.html` in a browser, or from this folder run:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000/`.
