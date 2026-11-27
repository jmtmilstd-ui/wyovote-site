"""Block outside voter-guide citations (iVoterGuide, LWV, Vote411, wyovoterguide.com)
and outside slate endorsements such as Nathaniel's Picks.

WyoVote states facts, not advice. This module is used when rendering official
and candidate pages so a rebuild does not put those citations back. Factual
biography that happens to name the League (employment, membership, or a
forum the person spoke at) is left in place.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

BLOCKED_HOSTS = {
    "wyominglwv.org",
    "www.wyominglwv.org",
    "ivoterguide.com",
    "www.ivoterguide.com",
    "wyovoterguide.com",
    "www.wyovoterguide.com",
    "vote411.org",
    "www.vote411.org",
}

# Mentions that are facts about the person, not a citation to a voter guide.
KEEP_PATTERNS = (
    re.compile(r"Casper League of Women Voters", re.I),
    re.compile(r"lobbying for the Wyoming League of Women Voters", re.I),
    re.compile(r"lobbyist for the League of Women Voters", re.I),
    re.compile(r"Told a League of Women Voters forum", re.I),
    re.compile(r"League of Women Voters of Fremont County forum", re.I),
)

TERM_RE = re.compile(
    r"iVoterGuide|ivoterguide|wyovoterguide|Vote\s*411|vote411|"
    r"League of Women Voters|\bLWV\b|wyominglwv",
    re.I,
)

_SOURCE_LI = re.compile(
    r"[ \t]*<li>\s*<a href=\"(https?://[^\"]+)\"[^>]*>.*?</a>\s*"
    r"(?:<span class=\"ext\">.*?</span>\s*)?</li>\s*",
    re.I | re.S,
)

_EMPTY_SOURCES_BLOCK = re.compile(
    r"[ \t]*<div class=\"cand-sources-block\">\s*"
    r"<h2 id=\"h-sources\">Sources</h2>\s*"
    r"<ul class=\"cand-sources\">\s*</ul>\s*"
    r"</div>\s*",
    re.I | re.S,
)

_EMPTY_ENDORSE_ROW = re.compile(
    r"[ \t]*<tr><th scope=\"row\">Endorsements</th><td>\s*</td></tr>\r?\n?",
    re.I,
)

# Outside slate endorsement (not a host; strip from endorsement text / HTML cells).
_NATHANIELS_PICKS = re.compile(
    r"(?:(?<=\s)|(?<=^)|(?<=>))"
    r"Nathaniel(?:&#x27;|&apos;|')s Picks\s*"
    r"\(\s*Sway voting group by Nathaniel Williams\s*\)",
    re.I,
)


def scrub_outside_endorsements(text: str) -> str:
    """Remove Nathaniel's Picks from endorsement text or an HTML cell."""
    if not text or not _NATHANIELS_PICKS.search(text):
        return text
    out = _NATHANIELS_PICKS.sub("", text)
    # Collapse leftover spaces in plain (non-HTML) endorsement strings only.
    if "<" not in out:
        out = re.sub(r"[ \t]{2,}", " ", out).strip()
    return out


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def is_blocked_source(url: str | None = None, name: str | None = None) -> bool:
    """True if this source is an outside voter guide we should not publish."""
    url = (url or "").strip()
    name = name or ""
    host = host_of(url)
    if host in BLOCKED_HOSTS or host.endswith(".ivoterguide.com") or host.endswith(".wyovoterguide.com"):
        # County 10 news about an LWV forum is not blocked (different host).
        return True
    # Name-only fallback if a guide is cited without a recognized host.
    if re.search(r"iVoterGuide|wyovoterguide|Nathaniel's Picks", name, re.I):
        return True
    if re.search(r"League of Women Voters.*(?:Voter Guide|Candidate Guide|Legislative Directory)|Vote\s*411", name, re.I):
        return True
    return False


def is_kept_factual(text: str) -> bool:
    return any(p.search(text) for p in KEEP_PATTERNS)


def leftover_terms(text: str) -> list[str]:
    """Terms that remain after scrub and are not in a kept factual phrase."""
    found = []
    for m in TERM_RE.finditer(text):
        start, end = m.span()
        window = text[max(0, start - 80) : min(len(text), end + 80)]
        if is_kept_factual(window):
            continue
        found.append(m.group(0))
    return found


def scrub_text(text: str) -> str:
    """Remove voter-guide attributions; keep the underlying facts."""
    if not text:
        return text
    s = scrub_outside_endorsements(text)
    if not TERM_RE.search(s):
        return s

    # --- specific leftover voter-guide typography ---
    s = s.replace(
        " Continued on page 5 H5H Wyoming State Auditor continued from page 4",
        "",
    )
    s = re.sub(
        r" Wyoming Governor Office: Salary is \$140,000 annually;.*?"
        r"the rest were posted by the candidates themselves on Vote411\.",
        "",
        s,
        flags=re.I | re.S,
    )
    s = re.sub(
        r"<p class=\"cand-topic\">DO YOU THINK THERE IS SUFFICIENT TRANSARENCY "
        r"IN WYOMING’S FINANCES\? PLEASE EXPLAIN\.</p>"
        r"<p>Transparency isn(?:'|&#x27;)t an end destination - it can always be improved\.</p>",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"<p>Wyoming has the highest rate of suicide deaths in the nation</p>"
        r"<p>Agree\. WY(?:'|&#x27;)s Constitution requires the state provide a complete "
        r".*?transparent for parents and the community\.</p>",
        "",
        s,
        flags=re.I | re.S,
    )
    s = re.sub(
        r"<p>and Sergio A\. Maldonado \(D\), no response to the other three questions "
        r"of the League of Women Voters, check Vote 411\.org to see if they have entered "
        r"responses now\. Other Ballot Measures</p>",
        "",
        s,
        flags=re.I,
    )
    # Same leftovers in JSON / plain-text background items:
    s = re.sub(
        r"^and Sergio A\. Maldonado \(D\), no response to the other three questions "
        r"of the League of Women Voters, check Vote 411\.org to see if they have entered "
        r"responses now\. Other Ballot Measures\s*$",
        "",
        s,
        flags=re.I,
    )

    # --- gap sentence ---
    s = re.sub(
        r", the 2022 League of Women Voters statewide primary voter guide, or",
        " or",
        s,
        flags=re.I,
    )

    # --- parenthetical citations ---
    s = re.sub(
        r" \(2022 League of Women Voters legislative directory; institution not named\)",
        " (institution not named)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(2022 LWV legislative directory; degree level not specified\)",
        " (degree level not specified)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(2022 League of Women Voters legislative directory\)",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(34 years, per his 2022 League of Women Voters statement\)",
        " (34 years, per his 2022 statement)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(2022 League of Women Voters statewide primary guide\)",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(self-described, 2024 iVoterGuide biography\)",
        " (self-described)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(self-described on his 2024 iVoterGuide biography:",
        " (self-described:",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(self-reported on his 2024 iVoterGuide biography\)",
        " (self-reported)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(self-reported on his 2024 iVoterGuide biography\)\.",
        " (self-reported).",
        s,
        flags=re.I,
    )
    # Mike Selmer occupation: WyoFile + LWV materials
    s = re.sub(
        r" \(2024 WyoFile questionnaire and the already-sourced campaign / League of Women Voters materials\)",
        " (2024 WyoFile questionnaire and already-sourced campaign materials)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"iVoterGuide lists 2012",
        "listed as 2012",
        s,
        flags=re.I,
    )

    # --- "in a statement for the LWV guide" ---
    s = re.sub(
        r"In a statement dictated by telephone for the League of Women Voters of Wyoming 2022 statewide primary voter guide,",
        "In a 2022 statement dictated by telephone,",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"In (?:her|his) statement for the League of Women Voters of Wyoming 2022 statewide primary voter guide,",
        "In a 2022 statement,",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"In a 2022 League of Women Voters of Fremont County primary questionnaire",
        "In a 2022 primary questionnaire",
        s,
        flags=re.I,
    )

    # --- "The 2022 LWV directory listed..." keep the facts ---
    s = re.sub(
        r"The 2022 LWV directory listed him as ",
        "He is ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" He was in his fourth year in the House at the time of the directory\.",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"The 2022 LWV directory lists his birth date as Jan\. 29, 1976, in Powell, a B\.S\.",
        "He was born Jan. 29, 1976, in Powell, and holds a B.S.",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(Street address, phone, and email in the directory were not stored\.\)",
        "",
        s,
        flags=re.I,
    )
    def _drop_cap(s, pattern):
        s = re.sub(pattern, "\x00", s, flags=re.I)
        s = re.sub(r"\x00([a-z])", lambda m: m.group(1).upper(), s)
        return s.replace("\x00", "")
    s = _drop_cap(s, r"The 2022 LWV directory listed ")
    s = _drop_cap(s, r"The 2022 LWV legislative directory listed ")
    s = _drop_cap(s, r"The 2022 LWV directory lists ")

    # --- iVoterGuide biography / form ---
    s = re.sub(
        r"That aligns with his 2022 LWV Fremont questionnaire, in which he identified himself as ",
        "That aligns with a 2022 questionnaire in which he identified himself as ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(2024 WyoFile questionnaire and the already-sourced campaign / League of Women Voters profile text on this record\)",
        " (2024 WyoFile questionnaire and already-sourced campaign materials)",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"Already-sourced profile text on this record, drawn from his campaign materials and the League of Women Voters of Albany County 2024 general-election voter guide, also describes him as ",
        "Already-sourced profile text on this record, drawn from his campaign materials, also describes him as ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"On (?:her|his) 2024 iVoterGuide biography (?:he|she) also listed ",
        lambda m: ("She also listed " if "she listed" in m.group(0).lower() or "biography she also" in m.group(0).lower() else "He also listed "),
        s,
        flags=re.I,
    )
    s = re.sub(
        r"On (?:her|his) 2024 iVoterGuide biography (?:he|she) listed ",
        lambda m: ("She listed " if "she listed" in m.group(0).lower() or "biography she listed" in m.group(0).lower() else "He listed "),
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(iVoterGuide; her résumé specifies ",
        " (her résumé specifies ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(iVoterGuide; her resume specifies ",
        " (her resume specifies ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"On her iVoterGuide form she wrote ",
        "She wrote ",
        s,
        flags=re.I,
    )
    s = re.sub(
        r" \(2024 voter-guide questionnaire\)",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(
        r"on a 2024 voter-guide form he wrote ",
        "he has written ",
        s,
        flags=re.I,
    )

    # --- Tom Kelly / official endorsements cell ---
    s = re.sub(
        r" Ratings Kelly received ratings or grades from the following organizations\. iVoterGuide",
        "",
        s,
        flags=re.I,
    )
    s = re.sub(r"\s+iVoterGuide\s*$", "", s, flags=re.I)

    # Do not collapse spaces globally: that would wipe HTML indentation
    # when scrub_html runs on a full page.
    s = re.sub(
        r" She was in her first House term \(two years\) at the time of the directory\.",
        " She was in her first House term (two years).",
        s,
        flags=re.I,
    )
    s = re.sub(r" \.", ".", s)
    return s


def drop_blocked_sources(sources: list) -> list:
    out = []
    for item in sources or []:
        if isinstance(item, dict) and is_blocked_source(item.get("url"), item.get("name")):
            continue
        if isinstance(item, str) and TERM_RE.search(item) and not is_kept_factual(item):
            continue
        out.append(item)
    return out


def scrub_obj(obj):
    """Recursively scrub strings and drop blocked source objects."""
    if isinstance(obj, dict):
        # A source object itself
        if "url" in obj and is_blocked_source(obj.get("url"), obj.get("name")):
            return None
        new = {}
        for k, v in obj.items():
            if k == "sources" and isinstance(v, list):
                new[k] = drop_blocked_sources(v)
                continue
            sv = scrub_obj(v)
            if sv is None:
                continue
            # Drop empty leftover background strings
            if isinstance(sv, str) and not sv.strip():
                if k in {"background", "text", "value", "blurb", "endorsements"}:
                    continue
            new[k] = sv
        return new
    if isinstance(obj, list):
        out = []
        for item in obj:
            sv = scrub_obj(item)
            if sv is None:
                continue
            if isinstance(sv, str) and not sv.strip():
                continue
            # Drop Degenfelder leftover background items that are only paste.
            if isinstance(sv, str) and sv.strip() in {
                "Wyoming has the highest rate of suicide deaths in the nation",
            }:
                continue
            if isinstance(sv, str) and sv.startswith("Agree. WY") and "basket of goods" in sv and "Superintendent I will advocate" in sv:
                # Duplicate of a Positions answer pasted into Background.
                continue
            out.append(sv)
        return out
    if isinstance(obj, str):
        return scrub_text(obj)
    return obj


def scrub_html(html: str) -> str:
    def _li(m: re.Match) -> str:
        return "" if is_blocked_source(m.group(1), m.group(0)) else m.group(0)

    out = _SOURCE_LI.sub(_li, html)
    out = scrub_text(out)
    out = _EMPTY_SOURCES_BLOCK.sub("", out)
    out = _EMPTY_ENDORSE_ROW.sub("", out)
    # If a sources ul is now empty but the wrapper regex missed (whitespace/indent)
    out = re.sub(
        r"[ \t]*<div class=\"cand-sources-block\">\s*<h2 id=\"h-sources\">Sources</h2>\s*"
        r"<ul class=\"cand-sources\">\s*</ul>\s*</div>\s*",
        "",
        out,
        flags=re.I | re.S,
    )
    return out
