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
    elif parts[0] == "reports" and len(parts) >= 4:
        year, kind = parts[1], parts[2]
        place = title
        if year == "2026":
            if kind == "county":
                chain.extend(["Counties", place, "Report"])
            elif kind == "committee":
                chain.extend(["Committees", place, "Report"])
            else:
                chain.extend(["Ratings", place])
        else:
            section = {"county": "Counties", "committee": "Committees"}.get(kind, "Reports")
            chain.extend(["Archive", section, place])
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
    """Side-entry stair. A rail on the left enters each box's left end.

    Each box is as wide as its label. Labels are not shortened.
    """
    shown = [re.sub(r"\s+", " ", label).strip() for label in labels]
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


# Depth 0 is the section title (level 1). Depth 1 is the next page.
# Depth 2 is the leaf level. Sizes stay at least 12px in the diagram's own units.
LEVEL_FONT = {0: 18, 1: 15, 2: 12}
LEVEL_WEIGHT = {0: 700, 1: 400, 2: 400}
LEVEL_BOX = {0: 36, 1: 30, 2: 26}
CHAIN_GAP = 7
UNIT_GAP = 28
SECTION_GAP = 48
STEP = 26
NARROW = 16
RAIL = 15
PAD_X = 18


def _depth_key(depth: int) -> int:
    return min(depth, 2)


def level_widths(nodes: list[dict]) -> dict[int, float]:
    """One stair for the map. Each step is a bit narrower and still fits its label."""
    text = {0: 0.0, 1: 0.0, 2: 0.0}
    seen = {0: False, 1: False, 2: False}

    def walk(item: dict, depth: int) -> None:
        key = _depth_key(depth)
        seen[key] = True
        text[key] = max(text[key], text_width(item["label"], LEVEL_FONT[key]) + PAD_X)
        for child in item.get("children") or []:
            walk(child, depth + 1)

    for node in nodes:
        walk(node, 0)
    width0 = text[0]
    width1 = text[1]
    width2 = text[2]
    if seen[2]:
        width1 = max(width1, width2 + NARROW)
    if seen[1]:
        width0 = max(width0, width1 + NARROW)
    if seen[1]:
        width1 = width0 - NARROW
    else:
        width1 = max(width0 - NARROW, PAD_X)
    if seen[2]:
        width2 = width1 - NARROW
    else:
        width2 = max(width1 - NARROW, PAD_X)
    return {0: width0, 1: width1, 2: width2}


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


def layout_section(node: dict, side: str, y0: float, inner: float, widths: dict[int, float]) -> tuple[list, list, float]:
    """One section as a staircase. Each lower level steps right and is narrower.

    Even depths bracket on the outer side, odd depths on the inner side, so a
    rail never crosses a box. A chain stays tight. A child that is its own
    little stair (Archive's Articles, Reports, and the rest) gets a wider gap.
    The caller puts the large gap between sections.
    """
    boxes: list[dict] = []
    segs: list[tuple[float, float, float, float, str]] = []

    def place_box(item: dict, y: float, depth: int) -> dict:
        key = _depth_key(depth)
        width = widths[key]
        # Both columns indent to the right, as in the sketch. On the left the
        # stair walks toward the trunk. On the right it walks away from it.
        if side == "left":
            x = inner - widths[0] + depth * STEP
        else:
            x = inner + depth * STEP
        box = {
            "x": x,
            "y": y,
            "w": width,
            "h": LEVEL_BOX[key],
            "label": item["label"],
            "leaf": bool(item.get("leaf")),
            "font": LEVEL_FONT[key],
            "weight": LEVEL_WEIGHT[key],
            "depth": depth,
        }
        boxes.append(box)
        return box

    def connect(parent: dict, children: list[dict], depth: int) -> None:
        if not children:
            return
        outer = depth % 2 == 0
        use_left = outer if side == "left" else not outer
        cy = parent["y"] + parent["h"] / 2
        last = children[-1]["y"] + children[-1]["h"] / 2
        if use_left:
            rail = min(parent["x"], *(child["x"] for child in children)) - RAIL
            segs.append((parent["x"], cy, rail, cy, ""))
            segs.append((rail, cy, rail, last, ""))
            for child in children:
                ccy = child["y"] + child["h"] / 2
                segs.append((rail, ccy, child["x"], ccy, "arrow"))
        else:
            rail = max(parent["x"] + parent["w"], *(child["x"] + child["w"] for child in children)) + RAIL
            segs.append((parent["x"] + parent["w"], cy, rail, cy, ""))
            segs.append((rail, cy, rail, last, ""))
            for child in children:
                ccy = child["y"] + child["h"] / 2
                segs.append((rail, ccy, child["x"] + child["w"], ccy, "arrow"))

    def walk(item: dict, y: float, depth: int) -> tuple[dict, float]:
        current = place_box(item, y, depth)
        cursor = y + current["h"]
        children = []
        siblings = item.get("children") or []
        for index, child in enumerate(siblings):
            if index == 0:
                cursor += CHAIN_GAP
            elif child.get("children") or siblings[index - 1].get("children"):
                cursor += UNIT_GAP
            else:
                cursor += CHAIN_GAP
            placed, cursor = walk(child, cursor, depth + 1)
            children.append(placed)
        connect(current, children, depth)
        return current, cursor

    _root, end = walk(node, y0, 0)
    return boxes, segs, end


def geometry_errors(boxes: list[tuple], segments: list[tuple]) -> list[str]:
    """Segments may touch a box only at an endpoint on its border."""

    def hits_interior(x1, y1, x2, y2, rect) -> bool:
        left, top, right, bottom = rect
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
                if len(errors) > 16:
                    return errors
    return errors


def _draw_box(x, y, w, h, label, leaf, font: float, weight: int) -> str:
    radius = ' rx="11"' if leaf else ""
    style = ' font-style="italic"' if leaf else ""
    stroke = "2" if weight >= 700 and font >= LEVEL_FONT[0] else "1.5"
    return (
        f'<rect class="map-box{" is-leaf" if leaf else ""}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{radius} '
        f'fill="{WHITE}" stroke="{INK}" stroke-width="{stroke}"/>'
        f'<text class="map-label" x="{x + w / 2:.1f}" y="{y + h / 2:.1f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="{FONT_FAMILY}" font-weight="{weight}" font-size="{font:.0f}" '
        f'fill="{INK}"{style}>{esc(label)}</text>'
    )


def _column_layout(nodes: list[dict], side: str, inner: float, y0: float, section_gap: float, widths: dict[int, float]):
    boxes: list[dict] = []
    segs: list[tuple] = []
    roots: list[dict] = []
    y = y0
    for index, node in enumerate(nodes):
        if index:
            y += section_gap
        got_boxes, got_segs, end = layout_section(node, side, y, inner, widths)
        if got_boxes:
            roots.append(got_boxes[0])
        boxes.extend(got_boxes)
        segs.extend(got_segs)
        y = end
    return boxes, segs, roots, y


def _column_span(nodes: list[dict], gap: float, widths: dict[int, float]) -> float:
    if not nodes:
        return 0
    _boxes, _segs, _roots, end = _column_layout(nodes, "left", 0, 0, gap, widths)
    return end


def _extent_x(boxes: list[dict], segs: list[tuple]) -> tuple[float, float]:
    xs = [box["x"] for box in boxes] + [box["x"] + box["w"] for box in boxes]
    xs += [value for seg in segs for value in (seg[0], seg[2])]
    return min(xs), max(xs)


def _shift_x(boxes: list[dict], segs: list[tuple], dx: float) -> list[tuple]:
    for box in boxes:
        box["x"] += dx
    return [(x1 + dx, y1, x2 + dx, y2, kind) for x1, y1, x2, y2, kind in segs]


def render_diagram() -> str:
    """Home on a center trunk. Each section is its own stepped stair."""
    data = load_map()
    margin = 32
    trunk_gap = 26
    widths = level_widths(data["left"] + data["right"])

    left_h = _column_span(data["left"], SECTION_GAP, widths)
    right_h = _column_span(data["right"], SECTION_GAP, widths)
    left_gap = SECTION_GAP
    right_gap = SECTION_GAP
    if left_h < right_h and len(data["left"]) > 1:
        left_gap += (right_h - left_h) / (len(data["left"]) - 1)
    elif right_h < left_h and len(data["right"]) > 1:
        right_gap += (left_h - right_h) / (len(data["right"]) - 1)

    home_h = LEVEL_BOX[0]
    top = margin + home_h + 20
    left_boxes, left_segs, left_roots, left_end = _column_layout(data["left"], "left", 0, top, left_gap, widths)
    right_boxes, right_segs, right_roots, right_end = _column_layout(data["right"], "right", 0, top, right_gap, widths)

    left_min, left_max = _extent_x(left_boxes, left_segs)
    right_min, right_max = _extent_x(right_boxes, right_segs)
    shift_left = margin - left_min
    trunk = left_max + shift_left + trunk_gap
    shift_right = trunk + trunk_gap - right_min
    content_right = right_max + shift_right
    left_span = trunk - margin
    right_span = content_right - trunk
    # Equal outer margins, trunk in the middle, even when one stair steps outward.
    half = max(left_span, right_span) + margin
    center_shift = half - trunk
    left_segs = _shift_x(left_boxes, left_segs, shift_left + center_shift)
    right_segs = _shift_x(right_boxes, right_segs, shift_right + center_shift)
    trunk += center_shift
    total_w = half * 2

    home_w = max(text_width("Home", LEVEL_FONT[0]) + PAD_X, widths[0])
    home_x = trunk - home_w / 2
    home_y = margin
    drawn = [(home_x, home_y, home_w, home_h, "Home", False, LEVEL_FONT[0], LEVEL_WEIGHT[0])]
    for item in left_boxes + right_boxes:
        drawn.append(
            (item["x"], item["y"], item["w"], item["h"], item["label"], item["leaf"], item["font"], item["weight"])
        )

    segments = []
    root_centers = [item["y"] + item["h"] / 2 for item in left_roots + right_roots]
    trunk_bottom = max(root_centers) if root_centers else top
    segments.append((trunk, home_y + home_h, trunk, trunk_bottom, ""))
    for item in left_roots:
        cy = item["y"] + item["h"] / 2
        segments.append((trunk, cy, item["x"] + item["w"], cy, "arrow"))
    for item in right_roots:
        cy = item["y"] + item["h"] / 2
        segments.append((trunk, cy, item["x"], cy, "arrow"))
    segments.extend(left_segs)
    segments.extend(right_segs)

    bottom = max(left_end, right_end)
    total_h = bottom + margin
    rects = [(x, y, w, h) for x, y, w, h, _label, _leaf, _font, _weight in drawn]
    problems = geometry_errors(rects, segments)
    if problems:
        raise SystemExit("site map geometry:\n" + "\n".join(problems[:16]))

    parts = [f'<rect class="map-paper" width="{total_w:.1f}" height="{total_h:.1f}" fill="{PAPER}"/>']
    for x1, y1, x2, y2, kind in segments:
        if abs(y1 - y2) < 0.1:
            parts.append(_h_line(x1, x2, y1))
        else:
            parts.append(_v_line(x1, y1, y2))
        if kind == "arrow":
            parts.append(_arrow(x1, y1, x2, y2))
    for x, y, w, h, label, leaf, font, weight in drawn:
        parts.append(_draw_box(x, y, w, h, label, leaf, font, weight))
    body = "".join(parts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" '
        f'viewBox="0 0 {total_w:.1f} {total_h:.1f}" '
        f'role="img" aria-labelledby="site-map-title site-map-desc">'
        f'<title id="site-map-title">WyoVote site map</title>'
        f'<desc id="site-map-desc">Home at the top. Each section is a stepped stair. '
        f'A line leaves the side of a parent and enters the side of its child.</desc>'
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
            <li><a href="committees.html">Committees</a></li>
            <li><a href="counties.html">Counties</a></li>
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
    for name in ("election", "map", "report"):
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
