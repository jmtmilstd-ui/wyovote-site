#!/usr/bin/env python3
"""Stamp the Site Map and the small header trail, then promote preview to live.

The full diagram and the trail on each page come from the same page
structure. Run this after adding preview pages:

    python3 tools/build_site_map.py

tools/build_candidate_pages.py runs it at the end, so a candidate rebuild
picks up the trail on new pages. The same run copies every preview HTML
page to its live twin, following PUBLISH.md.
"""

from __future__ import annotations

import html
import json
import math
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

    levels = {
        "how-ratings-work.html": ["Ratings", "How the Ratings Work"],
        "reports.html": ["Ratings", "Current Reports"],
        "committee-ratings.html": ["Ratings", "Committee ratings"],
        "county-ratings.html": ["Ratings", "County ratings"],
        "legislative-ratings.html": ["Ratings", "Legislative ratings"],
        "historical-ratings.html": ["Ratings", "Historical ratings"],
        "historical-articles.html": ["Ratings", "Historical articles"],
        "historical-criteria.html": ["Ratings", "Historical criteria"],
        "about.html": ["About"],
        "privacy.html": ["Privacy"],
        "contact.html": ["Contact"],
        "contact-thanks.html": ["Contact", "Thanks"],
        "committees.html": ["Committees"],
        "counties.html": ["Counties"],
    }
    if rel in {"index.html"}:
        return chain
    if rel in levels:
        chain.extend(levels[rel])
        return chain[-4:]
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
        chain.extend(["Archive", "Articles", "Article"])
    elif parts[0] == "news":
        if name == "archive.html":
            chain.extend(["News", "Archive"])
        elif "certified-election" in name:
            chain.extend(["Special", "Article"])
        else:
            chain.extend(["News", "Article"])
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
                chain.append("Candidate")
            else:
                if not parts[1].startswith("2026"):
                    chain.append(year)
                chain.append(title.removesuffix(" County"))
    elif rel == "officials.html" or parts[0] == "officials":
        chain.append("Officials")
        if rel != "officials.html":
            if name == "index.html":
                chain.append("Year")
            elif name.endswith("-deep.html"):
                chain.append("Official")
                chain.append("Deeper Dive")
            else:
                chain.append("Official")
    else:
        chain.append(title)

    if len(chain) > 4:
        chain = chain[-4:]
    return chain


MAP_FILE = ROOT / "data" / "site-map.json"
MAP_FONT = 17
TRAIL_FONT = 14
BOX_H = 32
INK = "#142117"
LINE = "#146b31"
GOLD = "#b8860b"
WHITE = "#ffffff"
PAPER = "#f4f3ee"
FONT_FAMILY = "Liberation Sans, DejaVu Sans, sans-serif"
_FONTS: dict[int, object] = {}


def _font(size: int):
    if size not in _FONTS:
        try:
            from PIL import ImageFont
        except ImportError:
            _FONTS[size] = None
            return None
        for path in (
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ):
            if Path(path).is_file():
                _FONTS[size] = ImageFont.truetype(path, size)
                return _FONTS[size]
        _FONTS[size] = None
    return _FONTS[size]


def text_width(text: str, size: int) -> float:
    font = _font(size)
    if font is not None:
        return float(font.getlength(text))
    return len(text) * size * 0.56


def clip_label(label: str, limit: int = 22) -> str:
    label = re.sub(r"\s+", " ", label).strip()
    if len(label) <= limit:
        return label
    return label[: limit - 1].rstrip() + "…"


def load_map() -> dict:
    return json.loads(MAP_FILE.read_text(encoding="utf-8"))


def map_labels(data: dict | None = None) -> list[str]:
    data = data or load_map()
    found: list[str] = ["Home"]

    def walk(node: dict) -> None:
        found.append(node["label"])
        for child in node.get("children") or []:
            walk(child)

    for column in ("left", "right"):
        for node in data[column]:
            walk(node)
    return found


def trail_label(label: str) -> str:
    """Year-index labels follow the Primary/General switch, the same as the h1."""
    match = re.fullmatch(r"(\d{4}) Primary", label)
    if not match:
        return esc(label)
    year = match.group(1)
    return (
        f'<span class="cand-view-primary">{year} Primary</span>'
        f'<span class="cand-view-general">{year} General</span>'
    )


def trail_html(labels: list[str]) -> str:
    """Side-entry stair. A rail on the left enters each box's left end."""
    shown = [clip_label(label) for label in labels]
    pad_x = 8
    step_x = 12
    pitch = BOX_H + 8
    rail = 10.0
    specs = []
    for label in shown:
        match = re.fullmatch(r"(\d{4}) Primary", label)
        if match:
            year = match.group(1)
            width = max(text_width(f"{year} Primary", TRAIL_FONT), text_width(f"{year} General", TRAIL_FONT))
            specs.append((width + pad_x * 2, label, True))
        else:
            specs.append((text_width(label, TRAIL_FONT) + pad_x * 2, label, False))
    total_w = rail + 16 + step_x * (len(specs) - 1) + max(width for width, _, _ in specs) + 4
    total_h = pitch * (len(specs) - 1) + BOX_H + 4
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
        f'viewBox="0 0 {total_w:.1f} {total_h:.1f}" role="img" aria-label="{esc(" / ".join(labels))}">'
    ]
    centers = []
    for index, (width, label, dual) in enumerate(specs):
        x = rail + 16 + step_x * index
        y = 2 + pitch * index
        current = index == len(specs) - 1
        stroke = GOLD if current else INK
        width_px = "2.5" if current else "1.5"
        parts.append(
            f'<rect class="trail-box{" is-current" if current else ""}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{width:.1f}" height="{BOX_H:.1f}" fill="{WHITE}" stroke="{stroke}" stroke-width="{width_px}"/>'
        )
        cy = y + BOX_H / 2
        centers.append((x, cy))
        cx = x + width / 2
        if dual:
            year = label.split()[0]
            parts.append(
                f'<text class="trail-label cand-view-primary" x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" font-size="{TRAIL_FONT}" '
                f'fill="{INK}">{year} Primary</text>'
                f'<text class="trail-label cand-view-general" x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" font-size="{TRAIL_FONT}" '
                f'fill="{INK}">{year} General</text>'
            )
        else:
            parts.append(
                f'<text class="trail-label" x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" font-size="{TRAIL_FONT}" '
                f'fill="{INK}">{esc(label)}</text>'
            )
    if len(centers) > 1:
        y0 = centers[0][1]
        y1 = centers[-1][1]
        parts.append(
            f'<line class="map-line" x1="{rail:.1f}" y1="{y0:.1f}" x2="{rail:.1f}" y2="{y1:.1f}" '
            f'stroke="{LINE}" stroke-width="1.75"/>'
        )
        for x, cy in centers:
            parts.append(
                f'<line class="map-line" x1="{rail:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{cy:.1f}" '
                f'stroke="{LINE}" stroke-width="1.75"/>'
            )
            parts.append(_arrow(rail, cy, x, cy))
    parts.append("</svg>")
    return '<div class="page-trail">\n' + "".join(parts) + "\n</div>"


def _elbow(x1: float, y1: float, x2: float, y2: float, mid: float) -> str:
    """Down, across, then an arrow into the next box."""
    tip = y2 - 1
    line = (
        f'<polyline class="map-line" points="{x1:.1f},{y1:.1f} {x1:.1f},{mid:.1f} {x2:.1f},{mid:.1f} {x2:.1f},{tip:.1f}" '
        f'fill="none" stroke="{LINE}" stroke-width="1.75" stroke-linecap="butt" stroke-linejoin="miter"/>'
    )
    return line + _arrow(x2, mid, x2, tip)


def _arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 8
    spread = 0.5
    bx = x2 - size * math.cos(angle)
    by = y2 - size * math.sin(angle)
    p2 = (bx + spread * size * math.sin(angle), by - spread * size * math.cos(angle))
    p3 = (bx - spread * size * math.sin(angle), by + spread * size * math.cos(angle))
    return (
        f'<polygon class="map-arrow" points="{x2:.1f},{y2:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" '
        f'fill="{LINE}"/>'
    )


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


PITCH = 46
RAIL = 16
GUTTER = 36
MAP_BOX_H = 28


def section_width(node: dict) -> float:
    labels = []

    def walk(item: dict) -> None:
        labels.append(item["label"])
        for child in item.get("children") or []:
            walk(child)

    walk(node)
    return max(text_width(label, MAP_FONT) for label in labels) + 22


def row_count(node: dict) -> int:
    return 1 + sum(row_count(child) for child in node.get("children") or [])


def _h_line(x1: float, x2: float, y: float) -> str:
    return (
        f'<line class="map-line" x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" '
        f'stroke="{LINE}" stroke-width="1.75"/>'
    )


def _v_line(x: float, y1: float, y2: float) -> str:
    return (
        f'<line class="map-line" x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" '
        f'stroke="{LINE}" stroke-width="1.75"/>'
    )


def layout_section(node: dict, side: str, y0: float, inner: float, width: float) -> tuple[list, list, float]:
    """Place one section. Children use a side rail, never a top or bottom edge.

    Left column: inner is the right edge (near the trunk). The parent rail is
    on the outer (left) side. A nested child rail is on the inner (right) side.
    The right column is the mirror.
    """
    boxes: list[dict] = []
    segs: list[tuple[float, float, float, float, str]] = []

    def box_at(y: float) -> tuple[float, float]:
        if side == "left":
            return inner - width, inner
        return inner, inner + width

    def walk(item: dict, y: float, depth: int) -> tuple[dict, float]:
        x, right = box_at(y)
        current = {
            "x": x,
            "y": y,
            "w": width,
            "h": MAP_BOX_H,
            "label": item["label"],
            "leaf": bool(item.get("leaf")),
        }
        boxes.append(current)
        cursor = y + PITCH
        children = []
        for child in item.get("children") or []:
            placed, cursor = walk(child, cursor, depth + 1)
            children.append(placed)
        if children:
            cy = current["y"] + MAP_BOX_H / 2
            # Depth 0 rail is on the outer side. Deeper rails sit toward the trunk
            # so they do not cross the parent rail.
            outer = depth == 0
            if side == "left":
                rail = (current["x"] - RAIL) if outer else (right + RAIL)
                side_x = current["x"] if outer else right
                segs.append((side_x, cy, rail, cy, ""))
                last = children[-1]["y"] + MAP_BOX_H / 2
                segs.append((rail, cy, rail, last, ""))
                for child in children:
                    ccy = child["y"] + MAP_BOX_H / 2
                    enter = child["x"] if outer else child["x"] + child["w"]
                    segs.append((rail, ccy, enter, ccy, "arrow"))
            else:
                rail = (right + RAIL) if outer else (current["x"] - RAIL)
                side_x = right if outer else current["x"]
                segs.append((side_x, cy, rail, cy, ""))
                last = children[-1]["y"] + MAP_BOX_H / 2
                segs.append((rail, cy, rail, last, ""))
                for child in children:
                    ccy = child["y"] + MAP_BOX_H / 2
                    enter = child["x"] + child["w"] if outer else child["x"]
                    segs.append((rail, ccy, enter, ccy, "arrow"))
        return current, cursor

    walk(node, y0, 0)
    return boxes, segs, y0 + PITCH * row_count(node)


def geometry_errors(boxes: list[tuple], segments: list[tuple]) -> list[str]:
    """Segments may touch a box only at an endpoint on its border."""

    def hits_interior(x1, y1, x2, y2, rect) -> bool:
        left, top, right, bottom = rect
        # Shrink so a mere touch of the border is allowed.
        pad = 0.8
        left, top, right, bottom = left + pad, top + pad, right - pad, bottom - pad
        if right <= left or bottom <= top:
            return False
        dx, dy = x2 - x1, y2 - y1
        p = (-dx, dx, -dy, dy)
        q = (x1 - left, right - x1, y1 - top, bottom - y1)
        u1, u2 = 0.0, 1.0
        for pi, qi in zip(p, q):
            if abs(pi) < 1e-9:
                if qi < 0:
                    return False
                continue
            t = qi / pi
            if pi < 0:
                if t > u2:
                    return False
                u1 = max(u1, t)
            else:
                if t < u1:
                    return False
                u2 = min(u2, t)
        return u1 <= u2

    def crosses(a, b) -> bool:
        (x1, y1), (x2, y2) = a
        (x3, y3), (x4, y4) = b

        def orient(ax, ay, bx, by, cx, cy) -> float:
            return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

        o1 = orient(x1, y1, x2, y2, x3, y3)
        o2 = orient(x1, y1, x2, y2, x4, y4)
        o3 = orient(x3, y3, x4, y4, x1, y1)
        o4 = orient(x3, y3, x4, y4, x2, y2)
        if o1 * o2 < -1e-6 and o3 * o4 < -1e-6:
            return True
        return False

    rects = [(x, y, x + w, y + h) for x, y, w, h in boxes]
    errors = []
    for index, (x1, y1, x2, y2, _kind) in enumerate(segments):
        for rect in rects:
            if hits_interior(x1, y1, x2, y2, rect):
                errors.append(f"segment {index} ({x1:.1f},{y1:.1f})-({x2:.1f},{y2:.1f}) cuts a box")
                break
    for i in range(len(segments)):
        a = ((segments[i][0], segments[i][1]), (segments[i][2], segments[i][3]))
        for j in range(i + 1, len(segments)):
            b = ((segments[j][0], segments[j][1]), (segments[j][2], segments[j][3]))
            if crosses(a, b):
                errors.append(f"segments {i} and {j} cross")
                if len(errors) > 12:
                    return errors
    return errors


def _draw_box(x, y, w, h, label, leaf) -> str:
    radius = ' rx="11"' if leaf else ""
    style = ' font-style="italic"' if leaf else ""
    return (
        f'<rect class="map-box{" is-leaf" if leaf else ""}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{radius} '
        f'fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
        f'<text class="map-label" x="{x + w / 2:.1f}" y="{y + h / 2:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="700" font-size="{MAP_FONT}" '
        f'fill="{INK}"{style}>{esc(label)}</text>'
    )


def render_diagram() -> str:
    """Home on a center trunk. Children join the side of the parent."""
    data = load_map()
    column_w = max(section_width(node) for node in data["left"] + data["right"])
    home_w = text_width("Home", MAP_FONT) + 22

    def column(nodes: list[dict], side: str, inner: float, y0: float):
        boxes, segs = [], []
        y = y0
        for node in nodes:
            placed, links, _end = None, None, None
            got_boxes, got_segs, end = layout_section(node, side, y, inner, column_w)
            boxes.extend(got_boxes)
            segs.extend(got_segs)
            y = end
        return boxes, segs, y

    # Provisional vertical extent, then center the trunk between the columns.
    probe_left = sum(row_count(node) for node in data["left"])
    probe_right = sum(row_count(node) for node in data["right"])
    rows = max(probe_left, probe_right)
    margin = 28
    top = margin + MAP_BOX_H + 20
    trunk_clear = GUTTER
    # Place columns after we know their outer reach. Inner edges sit GUTTER from the trunk.
    # Width is fixed, so inner edges can be chosen now.
    left_inner = margin + RAIL + column_w
    # right inner is left_inner + 2*GUTTER, trunk between them
    right_inner = left_inner + 2 * trunk_clear
    trunk = (left_inner + right_inner) / 2
    total_w = right_inner + column_w + RAIL + margin
    total_h = top + rows * PITCH + margin

    left_boxes, left_segs, left_end = column(data["left"], "left", left_inner, top)
    right_boxes, right_segs, right_end = column(data["right"], "right", right_inner, top)
    home_x = trunk - home_w / 2
    home_y = margin
    home = (home_x, home_y, home_w, MAP_BOX_H, "Home", False)
    boxes = [home]
    for item in left_boxes + right_boxes:
        boxes.append((item["x"], item["y"], item["w"], item["h"], item["label"], item["leaf"]))

    segments = []
    # Trunk from the bottom center of Home. It is the one root stem.
    trunk_bottom = max(left_end, right_end) - PITCH + MAP_BOX_H / 2
    segments.append((trunk, home_y + MAP_BOX_H, trunk, trunk_bottom, ""))
    def section_rows_y(nodes, y0):
        marks = []
        y = y0
        for node in nodes:
            marks.append(y)
            y += row_count(node) * PITCH
        return marks

    for y in section_rows_y(data["left"], top):
        cy = y + MAP_BOX_H / 2
        segments.append((trunk, cy, left_inner, cy, "arrow"))
    for y in section_rows_y(data["right"], top):
        cy = y + MAP_BOX_H / 2
        segments.append((trunk, cy, right_inner, cy, "arrow"))
    segments.extend(left_segs)
    segments.extend(right_segs)

    rects = [(x, y, w, h) for x, y, w, h, _label, _leaf in boxes]
    problems = geometry_errors(rects, segments)
    if problems:
        raise SystemExit("site map geometry:\n" + "\n".join(problems[:12]))

    parts = [
        f'<rect class="map-paper" width="{total_w:.1f}" height="{total_h:.1f}" fill="{PAPER}"/>'
    ]
    for x1, y1, x2, y2, kind in segments:
        if abs(y1 - y2) < 0.1:
            parts.append(_h_line(x1, x2, y1))
        else:
            parts.append(_v_line(x1, y1, y2))
        if kind == "arrow":
            parts.append(_arrow(x1, y1, x2, y2))
    for x, y, w, h, label, leaf in boxes:
        parts.append(_draw_box(x, y, w, h, label, leaf))
    body = "".join(parts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w:.1f} {total_h:.1f}" '
        f'role="img" aria-labelledby="site-map-title site-map-desc">'
        f'<title id="site-map-title">WyoVote site map</title>'
        f'<desc id="site-map-desc">Home at the top. Sections branch from a center trunk. '
        f'Each child joins the side of its parent. Rounded boxes are the lowest page.</desc>'
        f"{body}</svg>"
    )
    return f'<div class="map-diagram">{svg}</div>'


def write_site_map_page() -> None:
    diagram = render_diagram()
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
          <p>This map reflects the current structure of the site. Repeating pages are shown once, by level. A rounded box is the lowest page in a stair. The boxes are information only. The structure is recorded in <a href="../data/site-map.json">data/site-map.json</a>.</p>
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
