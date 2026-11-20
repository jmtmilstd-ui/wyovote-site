#!/usr/bin/env python3
"""Rebuild a candidate Level-3 page in the Officials Profile chrome.

Preview helper for the Profile standardization (t784u). Omits empty
sections. Research (or Results) and Sources share one pf-card when both
exist; a section with no data is left out entirely. Rank history and
other legislative blocks are not added here; a later pass should attach
them when the person has legislative data.

    python3 -B tools/render_candidate_profile.py PAGE.html [PAGE.html ...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def one(tag: str, html: str, flags=0) -> str | None:
    m = re.search(tag, html, flags)
    return m.group(1) if m else None


def rel_to_root(page: Path) -> str:
    depth = len(page.resolve().relative_to(ROOT).parts) - 1
    return "../" * depth


def convert(page: Path) -> bool:
    raw = page.read_text(encoding="utf-8")
    name = one(r"<h1[^>]*>([^<]+)</h1>", raw)
    if not name:
        raise SystemExit(f"no h1 in {page}")
    title_el = one(r"<title>([^<]+)</title>", raw) or ""
    desc = one(r'<meta name="description" content="([^"]*)"', raw) or ""
    back = one(r'(<p class="back-row">.*?</p>)', raw, re.S)
    blurb = one(r'(<p class="cand-blurb">.*?</p>)', raw, re.S)
    meta = one(r'<p class="cand-meta">([^<]*)</p>', raw) or ""
    results = re.findall(
        r'(<p class="cand-res(?: cand-general-line)?">.*?</p>)', raw, re.S
    )
    officials = one(
        r'(<p><a href="[^"]*officials/[^"]+-deep\.html">Officials profile</a></p>)',
        raw,
    )
    research_sec = one(
        r'(<section class="cand-research"[^>]*>.*?</section>)', raw, re.S
    )
    facts = None
    sources = None
    research_heading = None
    if research_sec:
        research_heading = one(r'<h2 id="h-research">([^<]+)</h2>', research_sec)
        facts = one(r'(<table class="cand-facts">.*?</table>)', research_sec, re.S)
        sources = one(r'(<ul class="cand-sources">.*?</ul>)', research_sec, re.S)
        # If the only heading in a sources-only block was h-sources, heading stays None
        if not sources:
            # some pages might have sources without the class? keep none
            pass

    # Cycle label from the existing title or the path
    cycle = "2026"
    m = re.search(r"(20\d{2})(?: (Primary|General|Local))?", title_el)
    if m:
        cycle = m.group(1)
        kind = m.group(2) or ""
    else:
        kind = ""
        if "local" in page.parts:
            kind = "Local"
            m2 = re.search(r"(20\d{2})-local", str(page))
            if m2:
                cycle = m2.group(1)
        elif "primary" in page.parts:
            kind = "Primary"
            m2 = re.search(r"(20\d{2})-primary", str(page))
            if m2:
                cycle = m2.group(1)

    meta_txt = re.sub(r"\s+", " ", meta).strip(" ·")
    # pf-sub: Profile · office/party · cycle
    sub_parts = ["Profile"]
    if meta_txt:
        sub_parts.append(meta_txt)
    if cycle:
        sub_parts.append(cycle if not kind else f"{cycle} {kind}")
    sub = " · ".join(sub_parts)

    # Research / Results / Sources card(s). Omit a heading when that part has no data.
    cards = []
    has_research = bool(facts) and research_heading == "Research"
    has_results = bool(facts) and research_heading == "Results"
    has_sources = bool(sources)

    def sources_block() -> str:
        if not has_sources:
            return ""
        return (
            '                    <div class="cand-sources-block">\n'
            '                      <h2 id="h-sources">Sources</h2>\n'
            f"                      {sources}\n"
            "                    </div>\n"
        )

    if has_research or has_results:
        heading = "Research" if has_research else "Results"
        hid = "h-research"
        cards.append(
            f'        <section class="pf-card cand-research" aria-labelledby="{hid}">\n'
            f'                    <h2 id="{hid}">{heading}</h2>\n'
            f"                    {facts}\n"
            f"{sources_block()}"
            "                  </section>"
        )
    elif has_sources:
        cards.append(
            '        <section class="pf-card cand-research" aria-labelledby="h-sources">\n'
            "                    " + sources_block().strip() + "\n"
            "                  </section>"
        )

    rel = rel_to_root(page)
    # Candidates tab current; keep sitting-legislator Officials link if present
    nav_candidates = f'{rel}candidates.html'
    extra = []
    if blurb:
        extra.append("          " + blurb)
    if results:
        extra.extend("          " + r for r in results)
    if officials:
        extra.append("          " + officials)
    extra_html = "\n".join(extra)
    cards_html = "\n".join(cards)

    # Keep the existing back-button script when present
    script = one(r"(<script>\s*\(function \(\) \{.*?cand-back.*?</script>)", raw, re.S) or ""
    if script:
        script = "    " + script.strip() + "\n"

    desc_attr = desc.replace('"', "&quot;")
    new = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{name} — Profile — WyoVote</title>
    <meta name="description" content="{desc_attr}">
    <link rel="icon" href="{rel}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{rel}css/styles.css">
    <link rel="stylesheet" href="{rel}assets/css/site.css">
    <link rel="stylesheet" href="{rel}officials/profile.css">
  </head>
  <body class="pf cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="{rel}index.html">
          <img src="{rel}assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="{rel}index.html">Home</a></li>
            <li><a href="{nav_candidates}" aria-current="page">Candidates</a></li>
            <li><a href="{rel}committees.html">Committees</a></li>
            <li><a href="{rel}counties.html">Counties</a></li>
            <li><a href="{rel}officials.html">Officials</a></li>
            <li><a href="{rel}people/index.html">Name Index</a></li>
            <li><a href="{rel}research.html">Research</a></li>
            <li><a href="{rel}archive.html">Archive</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main" class="profile">
      <div class="wrap">
        {back or ""}
        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{name}</h1>
          <p class="pf-sub">{sub}</p>
        </section>
{extra_html}
{cards_html}
      </div>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="{rel}about.html">About</a></li>
            <li><a href="{rel}privacy.html">Privacy</a></li>
            <li><a href="{rel}contact.html">Contact</a></li>
            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v2.0.pdf">User's Guide</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
{script}  </body>
</html>
"""
    # tidy leftover indent from the back-row capture
    new = re.sub(r"\n{3,}", "\n\n", new)
    if new == raw:
        return False
    page.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: render_candidate_profile.py PAGE.html ...", file=sys.stderr)
        return 2
    n = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        changed = convert(p)
        print(("updated" if changed else "unchanged"), p.relative_to(ROOT))
        n += int(changed)
    print("changed", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
