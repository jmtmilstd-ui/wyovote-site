#!/usr/bin/env python3
"""Stamp the Site Map and the header trail on the preview pages.

The diagram and the trail are drawn SVG figures in the same style as the
About page diagram. Run this after adding preview pages:

    python3 tools/build_site_map.py

tools/build_candidate_pages.py runs it at the end. Pass --publish to copy
the preview pages onto the live tree. The default run leaves live pages
untouched.
"""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
# Terms was removed from the live site on purpose. The preview copy stays.
SKIP_LIVE = {"terms.html"}

# Levels only. Repeating pages are one box, not one box per name.
TREE = (
    "Home",
    [
        (
            "Archive",
            [
                ("Articles", [("Article", [])]),
                ("Committees", []),
                ("Counties", []),
                ("Reports", []),
                ("Officials", []),
                ("Research", []),
                ("Candidates", []),
            ],
        ),
        (
            "Candidates",
            [("Year", [("County", [("Candidate", [])])])],
        ),
        (
            "Officials",
            [("Session", [("Official", [("Deeper Dive", [])])])],
        ),
        ("Research", []),
        ("News", [("Article", [])]),
        (
            "Ratings",
            [
                ("How the Ratings Work", []),
                ("Committee ratings", []),
                ("County ratings", []),
                ("Legislative ratings", []),
                ("Historical ratings", []),
            ],
        ),
        ("About", []),
        ("Privacy", []),
        ("Contact", []),
    ],
)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def page_h1(text: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if not match:
        return ""
    name = re.sub(r"<[^>]+>", "", match.group(1))
    return re.sub(r"\s+", " ", html.unescape(name)).strip()


def county_name(text: str) -> str:
    match = re.search(r"Back to ([A-Za-z][A-Za-z .'-]*?) County", text)
    return match.group(1) if match else ""


def year_label(folder: str) -> str:
    year = folder.split("-")[0]
    if folder.endswith("-primary"):
        return f"{year} Primary"
    return year


def crumbs(rel: str, text: str) -> list[str]:
    """Levels from Home down to this page. At most four, nearest the page."""
    path = Path(rel)
    parts = path.parts
    name = path.name
    title = page_h1(text) or path.stem.replace("-", " ").title()
    chain = ["Home"]

    if rel in {"index.html"}:
        return chain
    if rel == "site-map.html":
        chain.append("Site Map")
    elif rel == "404.html":
        chain.append("Page not found")
    elif parts[0] == "archive":
        chain.append("Archive")
        labels = {
            "articles.html": "Articles",
            "committees.html": "Committees",
            "counties.html": "Counties",
            "reports.html": "Reports",
            "officials.html": "Officials",
            "research.html": "Research",
            "candidates.html": "Candidates",
        }
        chain.append(labels.get(name, title))
    elif parts[0] == "articles":
        chain.extend(["Archive", "Articles", title])
    elif parts[0] == "news":
        chain.append("News")
        chain.append("Archive" if name == "archive.html" else title)
    elif rel == "candidates.html" or parts[0] == "candidates":
        chain.append("Candidates")
        if rel != "candidates.html":
            year = year_label(parts[1])
            if name == "index.html":
                chain.append(year)
            elif "c" in parts:
                if not parts[1].startswith("2026"):
                    chain.append(year)
                chain.append(county_name(text) or "County")
                chain.append(title)
            else:
                if not parts[1].startswith("2026"):
                    chain.append(year)
                chain.append(title.removesuffix(" County"))
    elif rel == "officials.html" or parts[0] == "officials":
        chain.append("Officials")
        if rel != "officials.html":
            if len(parts) > 2 and parts[1] != path.name:
                chain.append(parts[-2] if name == "index.html" else parts[1])
            if name == "index.html":
                pass
            elif name.endswith("-deep.html"):
                chain.append(title)
                chain.append("Deeper Dive")
            else:
                chain.append(title)
    else:
        chain.append(title)

    if len(chain) > 4:
        chain = chain[-4:]
    return chain


FONT_PATHS = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
FONT_FAMILY = "Liberation Sans, DejaVu Sans, sans-serif"
MAP_FONT = 26
TRAIL_FONT = 16
INK = "#142117"
PAPER = "#f4f3ee"
LINE = "#146b31"
GOLD = "#b8860b"
_FONTS: dict[int, object] = {}


def _font(size: int):
    if size not in _FONTS:
        from PIL import ImageFont

        for path in FONT_PATHS:
            if Path(path).is_file():
                _FONTS[size] = ImageFont.truetype(path, size)
                break
        else:
            _FONTS[size] = None
    return _FONTS[size]


def text_width(text: str, size: int) -> float:
    font = _font(size)
    if font is not None:
        return float(font.getlength(text))
    return len(text) * size * 0.56


def trail_html(labels: list[str]) -> str:
    """Small drawn trail: Home down to this page, current box in gold."""
    pad_x, pad_y = 12.0, 8.0
    line_h = TRAIL_FONT + 4
    join = 12.0
    max_text = 236.0
    items = []
    for label in labels:
        match = re.fullmatch(r"(\d{4}) Primary", label)
        if match:
            year = match.group(1)
            primary = f"{year} Primary"
            general = f"{year} General"
            width = max(text_width(primary, TRAIL_FONT), text_width(general, TRAIL_FONT))
            items.append((width + pad_x * 2, [primary], [general]))
            continue
        words = label.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if text_width(trial, TRAIL_FONT) <= max_text:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if not lines:
            lines = [label]
        width = max(text_width(line, TRAIL_FONT) for line in lines)
        items.append((width + pad_x * 2, lines, None))

    heights = [len(lines) * line_h + pad_y * 2 for _, lines, _ in items]
    total_w = max(width for width, _, _ in items)
    total_h = sum(heights) + join * (len(items) - 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
        f'viewBox="0 0 {total_w:.1f} {total_h:.1f}" role="img" aria-label="{esc(" / ".join(labels))}">'
    ]
    y = 0.0
    for index, ((width, lines, alt), height) in enumerate(zip(items, heights)):
        x = (total_w - width) / 2
        current = index == len(items) - 1
        fill = GOLD if current else "#ffffff"
        klass = "trail-box is-current" if current else "trail-box"
        parts.append(
            f'<rect class="{klass}" x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
        )
        text_y = y + height / 2 - (len(lines) - 1) * line_h / 2
        cx = total_w / 2

        def label_text(content: list[str], css: str, top: float) -> str:
            rows = []
            for line_index, line in enumerate(content):
                dy = 0 if line_index == 0 else line_h
                rows.append(f'<tspan x="{cx:.1f}" dy="{dy:.1f}">{esc(line)}</tspan>')
            return (
                f'<text class="trail-label {css}" x="{cx:.1f}" y="{top:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" '
                f'font-size="{TRAIL_FONT}" fill="{INK}">{"".join(rows)}</text>'
            )

        if alt:
            parts.append(label_text(lines, "cand-view-primary", text_y))
            parts.append(label_text(alt, "cand-view-general", text_y))
        else:
            parts.append(label_text(lines, "", text_y))
        y += height
        if index < len(items) - 1:
            parts.append(
                f'<line class="trail-line" x1="{total_w / 2:.1f}" y1="{y:.1f}" x2="{total_w / 2:.1f}" '
                f'y2="{y + join:.1f}" stroke="{GOLD}" stroke-width="2.5" stroke-linecap="butt"/>'
            )
            y += join
    parts.append("</svg>")
    return '<div class="page-trail">\n' + "".join(parts) + "\n</div>"


def root_prefix(rel: str) -> str:
    return "../" * (len(Path(rel).parts) - 1)


def insert_nav(text: str, rel: str) -> str:
    text = re.sub(r"\s*<li><a class=\"site-map-link\".*?</li>", "", text, flags=re.S)
    current = ' aria-current="page"' if rel == "site-map.html" else ""
    item = f'<li><a class="site-map-link" href="{root_prefix(rel)}site-map.html"{current}>Site Map</a></li>'
    match = re.search(r'(<a href="[^"]*research\.html"[^>]*>Research</a></li>)', text)
    if not match:
        return text
    return text[: match.end()] + "\n            " + item + text[match.end() :]


def insert_trail(text: str, labels: list[str]) -> str:
    block = trail_html(labels)
    text = re.sub(r"\s*<!-- page-trail -->.*?<!-- /page-trail -->", "", text, flags=re.S)
    wrapped = "<!-- page-trail -->\n" + block + "\n<!-- /page-trail -->"
    hero = re.search(r'(<section class="page-hero"[^>]*>\s*<div class="wrap">)', text)
    if hero:
        end = text.find("</div>", hero.end())
        if end != -1:
            return text[:end] + "\n" + wrapped + "\n        " + text[end:]
    profile = re.search(r'(<section class="pf-head"[^>]*>)', text)
    if profile:
        return text[: profile.end()] + "\n" + wrapped + text[profile.end() :]
    header = re.search(r'(<div class="wrap header-inner">)', text)
    if header:
        # Keep the trail with the header on pages that have no green title band.
        close = text.find("</div>", header.end())
        if close != -1:
            return text[:close] + "\n" + wrapped + "\n      " + text[close:]
    return text


# Drawn to match the About diagram: flat white boxes, dark stroke, green elbows.
MAP_PAD_X = 18
MAP_BOX_H = 54
MAP_H_GAP = 16
MAP_V_DROP = 36
MAP_ROW_GAP = 28
MAP_SECTION_GAP = 46
MAP_COL_GAP = 48
MAP_MARGIN = 22
MAP_TOP = 20
MAP_HOME_DROP = 32
MAP_MAX_ROW = 500
MAP_RAIL = 18
# Heights of these two groups match. Children still sit in rows under a parent.
LEFT_NAMES = ("Archive", "Candidates", "News", "Research")
RIGHT_NAMES = ("Officials", "Ratings", "About", "Privacy", "Contact")


def layout_node(node: tuple) -> dict:
    label, children = node
    width = text_width(label, MAP_FONT) + MAP_PAD_X * 2
    if not children:
        return {"label": label, "x": 0, "y": 0, "w": width, "h": MAP_BOX_H, "sub_w": width, "sub_h": MAP_BOX_H, "kids": []}
    laid = [layout_node(child) for child in children]
    rows: list[list[dict]] = []
    row: list[dict] = []
    row_w = 0.0
    for child in laid:
        extra = child["sub_w"] if not row else MAP_H_GAP + child["sub_w"]
        if row and row_w + extra > MAP_MAX_ROW:
            rows.append(row)
            row = [child]
            row_w = child["sub_w"]
        else:
            row.append(child)
            row_w += extra
    if row:
        rows.append(row)
    row_sizes = []
    for packed in rows:
        packed_w = sum(child["sub_w"] for child in packed) + MAP_H_GAP * (len(packed) - 1)
        packed_h = max(child["sub_h"] for child in packed)
        row_sizes.append((packed, packed_w, packed_h))
    # A left rail carries connectors to the second and later rows, so those
    # lines do not cut through the boxes above them.
    rail = MAP_RAIL if len(row_sizes) > 1 else 0
    content_w = rail + max([width] + [packed_w for _, packed_w, _ in row_sizes])
    kids = []
    y = MAP_BOX_H + MAP_V_DROP
    inner_w = content_w - rail
    for packed, packed_w, packed_h in row_sizes:
        x = rail + (inner_w - packed_w) / 2
        for child in packed:
            kids.append((child, x, y))
            x += child["sub_w"] + MAP_H_GAP
        y += packed_h + MAP_ROW_GAP
    return {
        "label": label,
        "x": rail + (inner_w - width) / 2,
        "y": 0,
        "w": width,
        "h": MAP_BOX_H,
        "sub_w": content_w,
        "sub_h": y - MAP_ROW_GAP,
        "kids": kids,
    }


def _rule(x1: float, y1: float, x2: float, y2: float) -> str:
    if abs(x1 - x2) < 0.5 and abs(y1 - y2) < 0.5:
        return ""
    return (
        f'<polyline class="map-line" points="{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}" '
        f'fill="none" stroke="{LINE}" stroke-width="2.5" stroke-linecap="butt" stroke-linejoin="miter"/>'
    )


def _box(x: float, y: float, w: float, h: float, label: str) -> str:
    text_y = y + h / 2
    return (
        f'<rect class="map-box" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="#ffffff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        f'<text class="map-label" x="{x + w / 2:.1f}" y="{text_y:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" '
        f'font-size="{MAP_FONT}" fill="{INK}">{esc(label)}</text>'
    )


def draw_node(node: dict, ox: float, oy: float, lines: list[str], boxes: list[str]) -> None:
    bx = ox + node["x"]
    by = oy + node["y"]
    boxes.append(_box(bx, by, node["w"], node["h"], node["label"]))
    if not node["kids"]:
        return
    parent_cx = bx + node["w"] / 2
    parent_bottom = by + node["h"]
    rows: dict[float, list[tuple]] = {}
    for child, x, y in node["kids"]:
        rows.setdefault(y, []).append((child, x))
    ordered = sorted(rows.items())
    rail_x = ox + 8
    previous_bus = None
    for index, (y, row) in enumerate(ordered):
        child_top = oy + y
        bus_y = child_top - 14
        centers = [ox + x + child["x"] + child["w"] / 2 for child, x in row]
        if index == 0:
            lines.append(_rule(parent_cx, parent_bottom, parent_cx, bus_y))
            lines.append(_rule(min(centers + [parent_cx]), bus_y, max(centers + [parent_cx]), bus_y))
            if len(ordered) > 1:
                lines.append(_rule(rail_x, bus_y, min(centers + [parent_cx]), bus_y))
                previous_bus = bus_y
        else:
            lines.append(_rule(rail_x, previous_bus, rail_x, bus_y))
            lines.append(_rule(rail_x, bus_y, max(centers), bus_y))
            previous_bus = bus_y
        for center in centers:
            lines.append(_rule(center, bus_y, center, child_top))
        for child, x in row:
            draw_node(child, ox + x, oy + y, lines, boxes)


def stack_column(nodes: list[dict]) -> tuple[list[tuple], float, float]:
    width = max(node["sub_w"] for node in nodes)
    # 14px above the first box is where its elbow meets the Home crossbar.
    y = 14.0
    placed = []
    for node in nodes:
        x = (width - node["sub_w"]) / 2
        placed.append((node, x, y))
        y += node["sub_h"] + MAP_SECTION_GAP
    return placed, width, y - MAP_SECTION_GAP


def render_diagram(tree: tuple) -> str:
    """Top-down org chart. Home over two even groups, elbows to every child."""
    label, children = tree
    by_name = {child[0]: child for child in children}
    left_nodes = [layout_node(by_name[name]) for name in LEFT_NAMES]
    right_nodes = [layout_node(by_name[name]) for name in RIGHT_NAMES]
    left, left_w, left_h = stack_column(left_nodes)
    right, right_w, right_h = stack_column(right_nodes)

    home_w = text_width(label, MAP_FONT) + MAP_PAD_X * 2
    home_h = MAP_BOX_H
    total_w = MAP_MARGIN + left_w + MAP_COL_GAP + right_w + MAP_MARGIN
    col_top = MAP_TOP + home_h + MAP_HOME_DROP
    total_h = col_top + max(left_h, right_h) + MAP_MARGIN
    left_x = MAP_MARGIN
    right_x = MAP_MARGIN + left_w + MAP_COL_GAP
    # One spine in the gap between the two halves. Elbows run out to each section.
    spine = left_x + left_w + MAP_COL_GAP / 2
    home_x = spine - home_w / 2
    home_bottom = MAP_TOP + home_h

    lines = [_rule(spine, home_bottom, spine, col_top)]
    boxes = [_box(home_x, MAP_TOP, home_w, home_h, label)]
    elbows = []
    for placed, origin_x in ((left, left_x), (right, right_x)):
        for node, x, y in placed:
            abs_y = col_top + y
            root_cx = origin_x + x + node["x"] + node["w"] / 2
            elbows.append((abs_y - 14, root_cx, node, origin_x + x, abs_y))
    if elbows:
        lines.append(_rule(spine, col_top, spine, max(item[0] for item in elbows)))
    for elbow_y, root_cx, node, origin_x, abs_y in elbows:
        lines.append(_rule(min(spine, root_cx), elbow_y, max(spine, root_cx), elbow_y))
        lines.append(_rule(root_cx, elbow_y, root_cx, abs_y))
        draw_node(node, origin_x, abs_y, lines, boxes)

    body = (
        f'<rect class="map-paper" width="{total_w:.1f}" height="{total_h:.1f}" fill="{PAPER}"/>'
        + "".join(lines)
        + "".join(boxes)
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w:.1f} {total_h:.1f}" '
        f'role="img" aria-labelledby="site-map-title site-map-desc">'
        f'<title id="site-map-title">WyoVote site map</title>'
        f'<desc id="site-map-desc">Home at the top. Pages sit in boxes on rows below their parent. '
        f'The boxes are information only and are not links.</desc>'
        f"{body}</svg>"
    )
    return f'<div class="map-diagram">{svg}</div>'


def write_site_map_page() -> None:
    diagram = render_diagram(TREE)
    page = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Site Map — WyoVote</title>
    <meta name="description" content="A diagram of the WyoVote pages and how they are nested.">
    <link rel="icon" href="assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="../css/styles.css">
    <link rel="stylesheet" href="preview.css">
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <p class="preview-banner" role="status">PREVIEW, not the live site</p>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="index.html">
          <img src="assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="archive.html">Archive</a></li>
            <li><a href="candidates.html">Candidates</a></li>
            <li><a href="archive/committees.html">Committees</a></li>
            <li><a href="archive/counties.html">Counties</a></li>
            <li><a href="officials.html">Officials</a></li>
            <li><a href="research.html">Research</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="index.html">← Back to Home</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>Site Map</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap page-prose">
          <p>This diagram shows how the pages are nested. Repeating pages are shown once, by level. The boxes are information only.</p>
          {diagram}
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="about.html">About</a></li>
            <li><a href="privacy.html">Privacy</a></li>
            <li><a href="contact.html">Contact</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""
    (PREVIEW / "site-map.html").write_text(page, encoding="utf-8")


def stamp(path: Path) -> None:
    rel = path.relative_to(PREVIEW).as_posix()
    text = path.read_text(encoding="utf-8")
    text = insert_nav(text, rel)
    text = insert_trail(text, crumbs(rel, text))
    path.write_text(text, encoding="utf-8")


def to_live(text: str, src: Path) -> str:
    """PUBLISH.md: drop preview chrome and retarget links that leave /preview."""
    text = re.sub(r"[ \t]*<meta name=\"robots\" content=\"noindex\">\n", "", text)
    text = re.sub(r"[ \t]*<p class=\"preview-banner\"[^>]*>.*?</p>\n", "", text)
    preview_root = PREVIEW.resolve()
    repo_root = ROOT.resolve()
    live_dir = (ROOT / src.relative_to(PREVIEW)).parent.resolve()

    def retarget(match: re.Match) -> str:
        raw = match.group(2)
        if re.match(r"^(?:https?:|mailto:|#|data:|javascript:)", raw, re.I):
            return match.group(0)
        path, query, frag = raw, "", ""
        if "#" in path:
            path, frag = path.split("#", 1)
            frag = "#" + frag
        if "?" in path:
            path, query = path.split("?", 1)
            query = "?" + query
        if not path or path.startswith("/"):
            return match.group(0)
        target = (src.parent / path).resolve()
        try:
            target.relative_to(preview_root)
            return match.group(0)
        except ValueError:
            pass
        try:
            target.relative_to(repo_root)
        except ValueError:
            return match.group(0)
        rewritten = Path(os.path.relpath(target, live_dir)).as_posix()
        return f'{match.group(1)}{rewritten}{query}{frag}"'

    text = re.sub(r'((?:href|src)=")([^"]*)"', retarget, text)
    text = text.replace('preview.css"', 'assets/css/site.css"')
    return text


def sync_live_styles() -> None:
    """Copy the promoted preview rules into the live stylesheet."""
    preview_css = (PREVIEW / "preview.css").read_text(encoding="utf-8")
    parts = []
    for name in ("election", "map"):
        match = re.search(
            rf"/\* PROMOTE_START {name} \*/\n(.*)/\* PROMOTE_END {name} \*/",
            preview_css,
            re.S,
        )
        if not match:
            raise SystemExit(f"missing promote block {name} in preview.css")
        parts.append(match.group(1).rstrip() + "\n")
    block = "/* PROMOTE_START */\n" + "\n".join(parts) + "/* PROMOTE_END */\n"
    site_path = ROOT / "assets" / "css" / "site.css"
    site = site_path.read_text(encoding="utf-8")
    if "/* PROMOTE_START */" in site:
        site = re.sub(r"/\* PROMOTE_START \*/.*?/\* PROMOTE_END \*/\n?", block, site, count=1, flags=re.S)
    else:
        if not site.endswith("\n"):
            site += "\n"
        site += "\n" + block
    site_path.write_text(site, encoding="utf-8")


def promote_live() -> int:
    sync_live_styles()
    count = 0
    for src in sorted(PREVIEW.rglob("*.html")):
        rel = src.relative_to(PREVIEW)
        if rel.as_posix() in SKIP_LIVE:
            continue
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(to_live(src.read_text(encoding="utf-8"), src), encoding="utf-8")
        count += 1
    return count


def main() -> None:
    write_site_map_page()
    pages = sorted(PREVIEW.rglob("*.html"))
    for path in pages:
        stamp(path)
    print(f"stamped {len(pages)} preview pages")
    if "--publish" in sys.argv:
        print(f"promoted {promote_live()} live pages")


if __name__ == "__main__":
    main()
