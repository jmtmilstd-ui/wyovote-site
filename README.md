# WyoVote

Static website for WyoVote, which publishes Wyoming legislator ratings. The site is plain HTML and CSS. There is no build step. GitHub Pages serves it from the repository root of the `main` branch at `https://jmtmilstd-ui.github.io/wyovote-site/`.

Links in the HTML are relative, so the same files work on that project site and in a local preview. Do not add a `CNAME` file. The custom domain is not being changed yet.

## Folder layout

| Path | Purpose |
| --- | --- |
| `index.html` | Home. Current material only: 2025 all-legislator ratings, a current-article placeholder, and a short “more items coming” note. |
| `reports.html` | Current Reports. The six 2025 rating PDFs. |
| `historical-ratings.html` | Older legislator, committee, and county rating PDFs, newest first. |
| `historical-articles.html` | Historical Articles. Empty until articles are archived. |
| `historical-criteria.html` | Historical Criteria Reports. Empty until a criteria or rating-guide document is archived. |
| `contact.html` | Contact email. No form. |
| `legislative-ratings.html`, `committee-ratings.html`, `county-ratings.html`, `archive.html` | Redirects to the new pages. |
| `css/styles.css` | All styles. The home hero photo is `--hero-background-image`. |
| `assets/img/surveyor-icon.png` | Surveyor logo, used in the header and footer. |
| `assets/img/surveyor-banner.png` | Logo plus the WyoVote wordmark, kept for later use. |
| `assets/img/owl-silhouette.jpg` | Kept for later use. |
| `assets/img/backgrounds/` | Hero photos. The home page uses the Black Hills red barn. Devils Tower is kept for later pages. |
| `reports/<year>/` | PDF reports. File names are lowercase and hyphenated. The pages show the original titles. |
| `COPYRIGHT.md` | Copyright notice. Site content is not open source. The hero photographs are public domain and are not WyoVote works. |
| `.nojekyll` | Tells GitHub Pages to skip Jekyll and serve the files as they are. |

## Hero background

The home hero uses `assets/img/backgrounds/red-barn-black-hills-1920.jpg`, and `red-barn-black-hills-1280.jpg` at viewports of 1280px and below. A dark gradient sits on top of the photo so the white heading stays readable. The Devils Tower images stay in the same folder for later pages.

To use a different photo later, change `--hero-background-image` at the top of `css/styles.css`. Interior pages keep the dark-green page header and do not use the photo.

## How to add a PDF and link it

1. Put the file in a year folder. Use a lowercase hyphenated name:

```text
reports/2026/senate-ratings.pdf
```

2. Link it from the page where it should appear. From a page in the site root, the address is:

```html
<p><a href="reports/2026/senate-ratings.pdf">Senate ratings</a></p>
```

Use the human-readable title as the link text. Keep the address relative. Do not start it with `/`.

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
