"""Rank-history chart for the legislator Profile pages (*-deep.html, formerly "Deeper dive") (approved design, Michael t587u-t589u, "add it" t597u).

chart_svg(name, series, bands) -> inline SVG string
    series: [(year, rank_or_None, n_ranked, band_or_None), ...] one entry per year in the page's rank table.
            rank None = 'Not ranked, too few votes' (no dot that year; the table notes it).
    bands:  {year: {'Conservative': (lo, hi), 'Moderate': (lo, hi), 'Liberal': (lo, hi), 'n': n_ranked}}
chart_block(name, series, bands, table_hint) -> '<div id="rank-chart">note + svg + legend</div>' or '' (fewer than 2 ranked years)
bands_from_ranking(d) -> band ranges for one ranking.load(Y) result.

Rules: ranks and counts only (never coefficients); counts are ranked members only (ranking.py);
y-axis = rank as a percent of that year's list (Rank (% of list)), 0 (MOST Conservative, #1) at the top to 100 (Most Liberal) at the bottom,
gridlines every 20 (Michael t599u);
no light-gray text; type is 12 pt or larger when printed 7.5 in wide.
1 ranked year: no chart. 2+ ranked years: the year-to-year line plus a straight trend 'vector' (Michael t601u):
a dashed dark-brick line (t604u) from the first ranked year's point to the last ranked year's x at the average rank (% of list)
of all ranked years, ending in a filled arrowhead. The arrowhead never covers a point label.
"""
from __future__ import annotations

import html
import math

BAND_NAMES = ("Conservative", "Moderate", "Liberal")
# Medium-strength fills so the bands stay visible in print (booklet legal
# reduced to 5.5x8.5, and grayscale). Conservative is a bit darker than
# #5aa864 so it separates from the blue in black-and-white.
BAND_COLOR = {"Conservative": "#3e8c4a", "Moderate": "#ffffff", "Liberal": "#6f95d6"}
BAND_STROKE = "#142117"
COL_ALL = "#1f3a68"    # solid navy year-to-year line
COL_TREND = "#8a1f1b"  # dark brick trend vector (dashed shaft, solid arrowhead)
INK = "#142117"
FONT = "Arial, 'Helvetica Neue', 'Segoe UI', sans-serif"

# 26 user units = 12.3 pt when the 1140-wide figure prints 7.5 in wide.
W, H = 1140, 740
ML, MR, MT, MB = 88, 36, 86, 138
PLOT_Y = MT
PLOT_W_MAX, PLOT_H = W - ML - MR, H - MT - MB
COL_MAX = 150  # widest year column; short careers get a narrower, centered plot
FS = 26


def bands_from_ranking(d) -> dict:
    """{'Conservative': (lo, hi), ..., 'n': n_ranked} from one ranking.load(Y) result (ranked members only)."""
    out = {"n": d["n_ranked"]}
    for b in BAND_NAMES:
        rs = [r["rank_all"] for r in d["ranked"] if r["band"] == b]
        out[b] = (min(rs), max(rs)) if rs else None
    return out


def _halo_text(x, y, text, size=FS, anchor="middle", weight="700", fill=INK) -> str:
    common = (f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
              f'font-family="{FONT}" text-anchor="{anchor}"')
    return (f'<text {common} fill="#ffffff" stroke="#ffffff" stroke-width="5" stroke-linejoin="round">{text}</text>'
            f'<text {common} fill="{fill}">{text}</text>')


def _overlap(a, b, pad=3):
    return not (a["x"] + a["w"] + pad <= b["x"] or b["x"] + b["w"] + pad <= a["x"]
                or a["y"] + a["h"] + pad <= b["y"] or b["y"] + b["h"] + pad <= a["y"])


def _seg_hits_rect(x1, y1, x2, y2, r, pad=6) -> bool:
    rx, ry, rw, rh = r["x"] - pad, r["y"] - pad, r["w"] + 2 * pad, r["h"] + 2 * pad

    def inside(x, y):
        return rx <= x <= rx + rw and ry <= y <= ry + rh
    if inside(x1, y1) or inside(x2, y2):
        return True

    def cross(ax, ay, bx, by, cx, cy):
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    def hits(ax, ay, bx, by, cx, cy, dx, dy):
        d1 = cross(cx, cy, dx, dy, ax, ay); d2 = cross(cx, cy, dx, dy, bx, by)
        d3 = cross(ax, ay, bx, by, cx, cy); d4 = cross(ax, ay, bx, by, dx, dy)
        return ((d1 > 0 > d2) or (d1 < 0 < d2)) and ((d3 > 0 > d4) or (d3 < 0 < d4))
    edges = ((rx, ry, rx + rw, ry), (rx + rw, ry, rx + rw, ry + rh),
             (rx + rw, ry + rh, rx, ry + rh), (rx, ry + rh, rx, ry))
    return any(hits(x1, y1, x2, y2, *e) for e in edges)


def _hits_lines(r, segs, pad=6) -> bool:
    for seg in segs:
        for a, b in zip(seg, seg[1:]):
            if _seg_hits_rect(a["x"], a["y"], b["x"], b["y"], r, pad=pad):
                return True
    return False


def _frac(rank, n):
    return (rank - 0.5) / n


def _place_labels(points, segs, plot_x, plot_w, hard=(), soft=()):
    """Two-line '69' / 'of 90' labels, kept off the lines, off other dots, inside the plot, never overlapping.
    `hard` segments (the arrowhead) are never covered, even in the dense-chart fallback."""
    box_w, box_h = 96, 64

    def rect_for(x, y_pt, below, dx=0.0, gap=22.0):
        top = y_pt + gap if below else y_pt - gap - box_h
        return {"x": x + dx - box_w / 2, "y": top, "w": box_w, "h": box_h, "cx": x + dx,
                "line1_y": top + 22, "line2_y": top + 48, "below": below, "dx": dx, "gap": gap}

    def side_rect(x, y_pt, sx, dy=0.0):
        cx = x + sx * (box_w / 2 + 14); top = y_pt - box_h / 2 + dy
        return {"x": cx - box_w / 2, "y": top, "w": box_w, "h": box_h, "cx": cx,
                "line1_y": top + 22, "line2_y": top + 48, "below": False, "dx": 0.0, "gap": 0.0, "side": True}

    def in_view(r):
        return (r["y"] >= PLOT_Y + 2 and r["y"] + r["h"] <= PLOT_Y + PLOT_H - 2
                and r["x"] >= plot_x - 40 and r["x"] + r["w"] <= W - 2)

    def hits_other_point(r, self_pt):
        return any(q is not self_pt and r["x"] - 3 <= q["x"] <= r["x"] + r["w"] + 3
                   and r["y"] - 3 <= q["y"] <= r["y"] + r["h"] + 3 for q in points)

    def prefer_below_for(i, p):
        f = _frac(p["rank"], p["n"])
        if f < 0.22:
            return True
        if f > 0.75:
            return False
        ys = [points[j]["y"] for j in (i - 1, i + 1) if 0 <= j < len(points)]
        if ys:
            if p["y"] < min(ys) - 8:
                return False
            if p["y"] > max(ys) + 8:
                return True
        if i > 0:
            return points[i - 1]["y"] - p["y"] > 0
        return f < 0.45

    def candidates_for(i, p, line_pad):
        prefer = prefer_below_for(i, p)
        out = []
        gaps = (18, 24, 32, 42) if line_pad is not None else (18, 24, 32, 42, 54, 68, 84, 100, 120, 145)   # far labels only as a last resort
        for gi, gap in enumerate(gaps):
            for si, side in enumerate((prefer, not prefer)):
                for dx in (0, 12, -12, 22, -22, 30, -30):
                    r = rect_for(p["x"], p["y"], side, dx, gap)
                    if not in_view(r) or hits_other_point(r, p) or _hits_lines(r, hard, pad=4) or (line_pad is not None and _hits_lines(r, segs, pad=line_pad)):
                        continue
                    out.append((abs(dx) * 4 + si * 14 + gi * 7 + (30 if gap > 42 else 0) + (28 if _hits_lines(r, soft, pad=2) else 0), r))
        for sx in (1, -1):   # beside the dot, vertically centred (used when above/below are blocked)
            for dy in (0, -14, 14, -28, 28, -40, 40):
                r = side_rect(p["x"], p["y"], sx, dy)
                if not in_view(r) or hits_other_point(r, p) or _hits_lines(r, hard, pad=4) or (line_pad is not None and _hits_lines(r, segs, pad=line_pad)):
                    continue
                out.append((150 + abs(dy) * 2 + (0 if sx > 0 else 10) + (28 if _hits_lines(r, soft, pad=2) else 0), r))
        out.sort(key=lambda t: t[0])
        return out

    opts_all = []
    for i, p in enumerate(points):
        opts = candidates_for(i, p, 4) or candidates_for(i, p, 2) or candidates_for(i, p, 0)
        if not opts:   # last resort: may cross a line (white halo keeps it readable), never the arrowhead
            opts = [(s + 200, r) for s, r in candidates_for(i, p, None)]
        if not opts:
            opts = [(999, rect_for(p["x"], p["y"], prefer_below_for(i, p), 0, 24))]
        opts_all.append(opts)
    n = len(points)
    choice = [0] * n

    def valid_at(i):
        r = opts_all[i][choice[i]][1]
        return all(not _overlap(r, opts_all[j][choice[j]][1], pad=6) for j in range(i))
    i = guards = 0
    ok = True
    while i < n:
        guards += 1
        if guards > 100000:
            ok = False
            break
        while choice[i] < len(opts_all[i]) and not valid_at(i):
            choice[i] += 1
        if choice[i] < len(opts_all[i]):
            i += 1
            continue
        if i == 0:
            ok = False
            break
        choice[i] = 0
        i -= 1
        choice[i] += 1
    if ok:
        return [{**p, "lab": opts_all[k][choice[k]][1]} for k, p in enumerate(points)], True
    # Dense chart: dynamic programming over (previous label, this label) with a wider candidate set.
    # A label may then cross the line (penalized; the white halo keeps it readable) but never another label or dot.
    full = []
    for i, p in enumerate(points):
        prefer = prefer_below_for(i, p); out = []
        for gap in (14, 18, 24, 32, 42, 54, 68, 84, 100, 120, 145):
            for si, side in enumerate((prefer, not prefer)):
                for dx in (0, 12, -12, 22, -22, 32, -32, 44, -44):
                    r = rect_for(p["x"], p["y"], side, dx, gap)
                    if not in_view(r) or hits_other_point(r, p) or _hits_lines(r, hard, pad=4):
                        continue
                    pen = 0 if not _hits_lines(r, segs, pad=2) else (40 if not _hits_lines(r, segs, pad=0) else 90)
                    out.append((abs(dx) * 4 + si * 14 + gap * 1.5 + pen, r))
        out.sort(key=lambda t: t[0])
        full.append(out or [(999, rect_for(p["x"], p["y"], prefer, 0, 24))])
    wide = [f[:36] for f in full]
    INF = float("inf")

    def dp(wide):
        # state after i: (c_{i-1}, c_i) -> (cost, backpointer); checks neighbours i-1 and i-2
        best = {(None, c): (wide[0][c][0], None) for c in range(len(wide[0]))}
        hist = [best]
        for i in range(1, n):
            nb = {}
            for (a, b), (cost, _) in best.items():
                rb = wide[i - 1][b][1]
                ra = wide[i - 2][a][1] if a is not None else None
                for c, (sc, rc) in enumerate(wide[i]):
                    if _overlap(rc, rb, pad=6) or (ra is not None and _overlap(rc, ra, pad=6)):
                        continue
                    v = cost + sc
                    if v < nb.get((b, c), (INF,))[0]:
                        nb[(b, c)] = (v, (a, b))
            if not nb:
                return None
            best = nb; hist.append(best)
        state = min(best, key=lambda s: best[s][0])
        picks = [None] * n
        for i in range(n - 1, -1, -1):
            picks[i] = state[1]
            state = hist[i][state][1]
        return picks

    if dp(wide) is None:   # no layout among the 36 best options per label: widen the search once
        wide = [f[:90] for f in full]
    placed = None
    for _ in range(40):   # a clash 3+ labels apart is not seen by the DP: drop that option and solve again
        picks = dp(wide)
        if picks is None:
            break
        labs = [wide[k][picks[k]][1] for k in range(n)]
        clash = next(((a, b) for a in range(n) for b in range(a + 1, n) if _overlap(labs[a], labs[b], pad=0)), None)
        placed = [{**p, "lab": labs[k]} for k, p in enumerate(points)]
        if clash is None:
            return placed, True
        b = clash[1]
        if len(wide[b]) <= 1:
            break
        wide[b] = wide[b][:picks[b]] + wide[b][picks[b] + 1:]
    if placed is None:
        placed = [{**p, "lab": wide[k][0][1]} for k, p in enumerate(points)]
    return placed, False


def chart_svg(name, series, bands, check=None) -> str:
    years = list(range(min(s[0] for s in series), max(s[0] for s in series) + 1))
    k = len(years)
    col_w = min(PLOT_W_MAX / k, COL_MAX)
    plot_w = col_w * k
    plot_x = ML + (PLOT_W_MAX - plot_w) / 2
    bar_w = col_w * 0.90
    xs = {y: plot_x + col_w * (i + 0.5) for i, y in enumerate(years)}

    def y_frac(f):
        return PLOT_Y + f * PLOT_H

    by = {s[0]: s for s in series}
    points = []
    for y in years:
        s = by.get(y)
        if s and s[1] is not None:
            points.append({"year": y, "rank": s[1], "n": s[2], "x": xs[y], "y": y_frac(_frac(s[1], s[2]))})
    # year-to-year line: split wherever a year has no dot
    segs, cur = [], []
    for p in points:
        if cur and p["year"] != cur[-1]["year"] + 1:
            segs.append(cur); cur = []
        cur.append(p)
    if cur:
        segs.append(cur)
    # trend vector: first ranked point -> (last ranked year's x, average rank (% of list) of all ranked years)
    vector = None; hard = []
    if len(points) >= 2:
        avg = sum(_frac(p["rank"], p["n"]) for p in points) / len(points)
        x0, y0 = points[0]["x"], points[0]["y"]; x1, y1 = points[-1]["x"], y_frac(avg)
        L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
        AL, AW = 30.0, 13.0   # arrowhead length and half-width
        bx, by_ = x1 - ux * AL, y1 - uy * AL
        tri = [{"x": x1, "y": y1}, {"x": bx - uy * AW, "y": by_ + ux * AW}, {"x": bx + uy * AW, "y": by_ - ux * AW}]
        vector = {"x0": x0, "y0": y0, "bx": bx, "by": by_, "tri": tri, "avg": avg}
        hard = [tri + [tri[0]]]
        soft = [[{"x": x0, "y": y0}, {"x": bx, "y": by_}]]   # the shaft: labels avoid it when they can (penalty), never the arrowhead
    else:
        soft = []
    points, ok = _place_labels(points, segs, plot_x, plot_w, hard, soft)
    if check is not None:
        check["labels_ok"] = ok
        labs = [p["lab"] for p in points]
        check["overlap"] = any(_overlap(a, b, pad=0) for i, a in enumerate(labs) for b in labs[i + 1:])
        check["trend"] = vector is not None
        check["arrow_clear"] = not any(_hits_lines(p["lab"], hard, pad=0) for p in points)

    nm = html.escape(name, quote=False)
    parts = []
    for y in years:
        s = by.get(y)
        if not s:
            continue
        parts.append(f"{y}: {s[1]} of {s[2]}" if s[1] is not None else f"{y}: not ranked, too few votes")
    o = []
    o.append(f'<svg class="deep-chart" id="rank-history-chart" viewBox="0 0 {W} {H}" role="img" aria-labelledby="rt rd" '
             f'style="width:100%;height:auto;-webkit-print-color-adjust:exact;print-color-adjust:exact">')
    o.append(f'<title id="rt">{nm} overall rank, {years[0]} through {years[-1]}</title>')
    o.append(f'<desc id="rd">Overall rank by year: {"; ".join(parts)}. '
             'The scale is rank as a percent of that year’s list: 0 (MOST Conservative, #1) at the top, 100 (Most Liberal) at the bottom. '
             + ('The brick-red arrow runs from the first ranked year to the average rank (% of list) of all ranked years. ' if vector else '')
             + 'A year with no dot is a year this person did not serve or was not ranked.</desc>')
    for i, y in enumerate(years):
        b = bands[y]; n = b["n"]
        x = plot_x + col_w * i + (col_w - bar_w) / 2
        for bn in BAND_NAMES:
            if not b.get(bn):
                continue
            lo, hi = b[bn]
            y0 = PLOT_Y + ((lo - 1) / n) * PLOT_H; y1 = PLOT_Y + (hi / n) * PLOT_H
            o.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bar_w:.1f}" height="{y1 - y0:.1f}" fill="{BAND_COLOR[bn]}" stroke="{BAND_STROKE}" stroke-width="1.5"/>')
        for bn in ("Conservative", "Moderate"):
            if not b.get(bn):
                continue
            yc = PLOT_Y + (b[bn][1] / n) * PLOT_H
            o.append(f'<line x1="{x:.1f}" x2="{x + bar_w:.1f}" y1="{yc:.1f}" y2="{yc:.1f}" stroke="{INK}" stroke-width="1.75"/>')
    for pct in (0, 20, 40, 60, 80, 100):
        y = y_frac(pct / 100)
        o.append(f'<line x1="{plot_x:.1f}" x2="{plot_x + plot_w:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.75"/>')
        o.append(_halo_text(plot_x - 10, y + 9, str(pct), anchor="end"))
    o.append(_halo_text(plot_x, PLOT_Y - 16, "MOST Conservative", anchor="start"))
    o.append(_halo_text(plot_x, PLOT_Y + PLOT_H + 30, "Most Liberal", anchor="start"))
    tx, ty = plot_x - 70, PLOT_Y + PLOT_H / 2
    o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{FS}" font-weight="700" font-family="{FONT}" text-anchor="middle" '
             f'fill="{INK}" transform="rotate(-90 {tx:.1f} {ty:.1f})">Rank (% of list)</text>')
    o.append(f'<rect x="{plot_x:.1f}" y="{PLOT_Y}" width="{plot_w:.1f}" height="{PLOT_H}" fill="none" stroke="{INK}" stroke-width="2.25"/>')
    for seg in segs:
        if len(seg) >= 2:
            pts = " ".join(f'{p["x"]:.1f},{p["y"]:.1f}' for p in seg)
            o.append(f'<polyline points="{pts}" fill="none" stroke="{COL_ALL}" stroke-width="3.25" stroke-linejoin="round" stroke-linecap="round"/>')
    if vector:
        v = vector
        o.append(f'<line x1="{v["x0"]:.1f}" y1="{v["y0"]:.1f}" x2="{v["bx"]:.1f}" y2="{v["by"]:.1f}" stroke="{COL_TREND}" stroke-width="3" stroke-dasharray="10 6" stroke-linecap="butt"/>')
        o.append('<polygon points="' + " ".join(f'{q["x"]:.1f},{q["y"]:.1f}' for q in v["tri"]) + f'" fill="{COL_TREND}" stroke="{COL_TREND}" stroke-width="1" stroke-linejoin="miter"/>')
    for p in points:
        o.append(f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="5.2" fill="{COL_ALL}" stroke="#ffffff" stroke-width="1.75"/>')
    for p in points:
        lab = p["lab"]
        if abs(lab["dx"]) >= 12 or lab["gap"] >= 40:   # leader when the label sits sideways or far from its dot
            ly = lab["y"] - 1 if lab["below"] else lab["y"] + lab["h"] + 1
            o.append(f'<line x1="{p["x"]:.1f}" y1="{p["y"]:.1f}" x2="{lab["cx"]:.1f}" y2="{ly:.1f}" stroke="{INK}" stroke-width="1.25"/>')
        o.append(_halo_text(lab["cx"], lab["line1_y"], str(p["rank"])))
        o.append(_halo_text(lab["cx"], lab["line2_y"], f'of {p["n"]}'))
    for y in years:
        o.append(f'<text x="{xs[y]:.1f}" y="{PLOT_Y + PLOT_H + 72:.1f}" font-size="{FS}" font-weight="700" font-family="{FONT}" '
                 f'text-anchor="middle" fill="{INK}">\'{y % 100:02d}</text>')
    o.append(f'<text x="{plot_x + plot_w / 2:.1f}" y="{H - 18}" font-size="{FS}" font-weight="700" font-family="{FONT}" '
             f'text-anchor="middle" fill="{INK}">Year</text>')
    o.append("</svg>")
    return "".join(o)


def legend_html(trend=True) -> str:
    year_line = (f'<svg width="34" height="12" viewBox="0 0 34 12" aria-hidden="true"><line x1="0" y1="6" x2="34" y2="6" '
                 f'stroke="{COL_ALL}" stroke-width="3" stroke-linecap="round"/></svg>')
    trend_line = (f'<svg width="40" height="14" viewBox="0 0 40 14" aria-hidden="true"><line x1="0" y1="7" x2="28" y2="7" '
                  f'stroke="{COL_TREND}" stroke-width="3" stroke-dasharray="6 3"/><polygon points="40,7 27,1 27,13" fill="{COL_TREND}"/></svg>')
    return ('<ul class="pf-legend">'
            f'<li>{year_line} Each year</li>'
            + (f'<li>{trend_line} Trend (first year to average)</li>' if trend else '')
            + '<li><span class="pf-band pf-band-conservative">Conservative</span></li>'
            '<li><span class="pf-band pf-band-moderate">Moderate</span></li>'
            '<li><span class="pf-band pf-band-liberal">Liberal</span></li></ul>')


def ranked_years(series):
    return sum(1 for s in series if s[1] is not None)


def chart_block(name, series, bands, table_hint="", indent=10, check=None) -> str:
    """Note + chart + legend wrapped in <div id="rank-chart">. '' when fewer than 2 ranked years."""
    if ranked_years(series) < 2:
        return ""
    chk = {} if check is None else check
    svg = chart_svg(name, series, bands, check=chk)
    trend = chk.get("trend", False)
    note = ("Each point is overall rank shown as a percent of that year’s list, from 0 (MOST Conservative, #1) "
            "at the top to 100 (Most Liberal) at the bottom, so a year with 90 ranked legislators can be compared with a year with 93. "
            "Labels give the actual rank, such as 77 of 92. "
            "The solid line is each year’s rank. "
            + ("The brick-red arrow is the trend: it starts at the first ranked year and ends, at the last ranked year, "
               "at this person’s average rank (% of list) across all ranked years. " if trend else "")
            + "Shading behind each year is that year’s own Conservative, Moderate, and Liberal cutoffs. "
            "A year with no dot is a year this person did not serve or was not ranked."
            + ((" " + table_hint) if table_hint else ""))
    sp = " " * indent
    return (f'{sp}<div id="rank-chart">\n'
            f'{sp}  <p class="deep-note">{note}</p>\n'
            f'{sp}  {svg}\n'
            f'{sp}  {legend_html(trend)}\n'
            f'{sp}</div>\n')


# ---------- rank legend (Michael, Nov 16, t613u-t617u) ----------
LEGEND = '<p class="deep-note rank-legend">Rank: 1 = MOST Conservative.</p>'
LEGEND_SECTIONS = ('h-rank', 'h-issue', 'h-num')   # Profile chart, Issue areas; session/official Rank tiles
import re as _re
def add_legend(t):
    """Put the rank legend once, right under the heading, in each rank section that is present. Idempotent."""
    for sid in LEGEND_SECTIONS:
        m = _re.search(rf'( *)<h2 id="{sid}">.*?</h2>\n', t)
        if not m: continue
        end = t.find('</section>', m.end()); sec = t[m.end():end]
        if 'rank-legend' in sec: continue
        if sid == 'h-issue' and '<table' not in sec: continue        # no ranks shown (not ranked / no data)
        if sid == 'h-num' and 'pf-rankline' not in sec: continue
        t = t[:m.end()] + m.group(1) + LEGEND + '\n' + t[m.end():]
    return t
MOVED = _re.compile(r'Moved (up|down) (\d+) places? overall:')
def rank_wording(t):
    """'Moved up 3 places overall:' -> 'Overall rank moved up 3:' (keep the word rank; no place/position wording)."""
    return MOVED.sub(r'Overall rank moved \1 \2:', t)
