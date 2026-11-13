#!/usr/bin/env python3
"""Scan a WyoVote working tree before publish.

Python 3, standard library only. Exit 0 when every check passes, 1 when a
check fails, and 2 when the command itself cannot run.

Checks:

  (a) any working-tree file is over 500 KB (512,000 bytes)
  (b) any asset other than HTML, CSS, or JS is not referenced by an HTML
      href/src or a CSS url()
  (c) any href or src in an .html file points at a local file that is missing
  (d) any root page (not under preview/) links into preview/ or contains the
      PREVIEW banner
  (e) the total size of tracked files is over 200 MB (209,715,200 bytes)
  (f) a top-level label in the preview or live site nav is missing from the site map
  (g) a line in the preview or live site map cuts through a box or crosses another line

The report always includes the tracked size, the 10 largest tracked files,
and the counts. Exceptions belong in tools/publish_check_allow.txt, or in
the file passed with --allow-list.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

FILE_LIMIT = 500 * 1024
TREE_LIMIT = 200 * 1024 * 1024

# Pages, stylesheets, and scripts are not assets. Everything else must be
# referenced. .docx, .csv, and .json are included, along with PDFs and images.
CODE_EXTENSIONS = {".html", ".htm", ".css", ".js", ".mjs", ".cjs"}

REMOTE_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}
ATTR_RE = re.compile(
    r"""(?is)\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))"""
)
COMMENT_RE = re.compile(r"(?s)<!--.*?-->")
CSS_COMMENT_RE = re.compile(r"(?s)/\*.*?\*/")
BANNER_MARKERS = ("PREVIEW, not the live site", "preview-banner")


def is_asset(path: Path) -> bool:
    return path.suffix.lower() not in CODE_EXTENSIONS


def norm(path: str) -> str:
    text = path.strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text.lstrip("/")


def comment_spans(text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in COMMENT_RE.finditer(text)]


def in_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file() and path.suffix.lower() != ".pyc":
            files.append(path)
    return files


def rel_posix(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def tracked_files(root: Path) -> tuple[list[str] | None, str | None]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        return None, f"could not run git: {exc}"
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        return None, message or f"git ls-files exited {result.returncode}"
    names = [name for name in result.stdout.decode("utf-8", "replace").split("\0") if name]
    return names, None


def parse_allow(path: Path) -> tuple[dict[str, set] | None, str | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return None, str(exc)
    rules: dict[str, set] = {
        "size": set(),
        "unreferenced": set(),
        "missing": set(),
        "root": set(),
    }
    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, rest = line.partition(":")
        if kind == "size" and rest.strip():
            rules["size"].add(norm(rest))
        elif kind == "unreferenced" and rest.strip():
            rules["unreferenced"].add(norm(rest))
        elif kind == "root" and rest.strip():
            rules["root"].add(norm(rest))
        elif kind == "missing" and rest.strip():
            html_path, separator, url = rest.strip().partition(" ")
            if not separator or not url.strip():
                return None, f"{path}:{lineno}: missing entries need an HTML path and a URL"
            rules["missing"].add((norm(html_path), url.strip()))
        elif ":" not in line:
            bare = norm(line)
            if not bare:
                return None, f"{path}:{lineno}: empty path"
            rules["size"].add(bare)
            rules["unreferenced"].add(bare)
        else:
            return None, f"{path}:{lineno}: unrecognized allow-list entry"
    return rules, None


def local_target(url: str) -> str | None:
    """Return the path portion of a local URL, or None when it is not a file."""
    text = html.unescape(url).strip()
    if not text or text.startswith("#"):
        return None
    if text.startswith("//"):
        return None
    parts = urlsplit(text)
    if parts.scheme.lower() in REMOTE_SCHEMES:
        return None
    if parts.scheme and parts.scheme.lower() != "file":
        return None
    path = unquote(parts.path)
    if not path:
        return None
    return path


def resolve_local(root: Path, html_file: Path, target: str) -> tuple[str | None, str | None]:
    """Resolve a local URL to a repo-relative path.

    Returns (relative path, error). The path is None when the URL leaves the repo.
    """
    if target.startswith("/"):
        candidate = (root / target.lstrip("/")).resolve()
    else:
        candidate = (html_file.parent / target).resolve()
    try:
        relative = candidate.relative_to(root.resolve())
    except ValueError:
        return None, "outside the repository"
    return relative.as_posix(), None


def points_at_preview(raw: str, relative: str | None) -> bool:
    if relative is not None and (relative == "preview" or relative.startswith("preview/")):
        return True
    path = unquote(urlsplit(html.unescape(raw).strip()).path or "")
    return (
        path == "/preview"
        or path.startswith("/preview/")
        or "/wyovote-site/preview/" in path
        or path.endswith("/wyovote-site/preview")
    )


def note_local(
    root: Path,
    source_file: Path,
    source: str,
    line: int,
    raw: str,
    target: str,
    referenced: set[str],
    missing: list[dict],
) -> str | None:
    """Record a local reference. Returns the repo-relative path when it stays in the repo."""
    relative, error = resolve_local(root, source_file, target)
    if error:
        missing.append(
            {
                "html": source,
                "line": line,
                "url": raw.strip(),
                "resolved": "",
                "reason": error,
            }
        )
        return None
    assert relative is not None
    destination = root / relative
    if destination.is_file():
        referenced.add(relative)
    elif not destination.exists():
        missing.append(
            {
                "html": source,
                "line": line,
                "url": raw.strip(),
                "resolved": relative,
                "reason": "file does not exist",
            }
        )
    return relative


def iter_css_urls(text: str):
    """Yield (start index, raw value) for each url() outside a CSS comment."""
    spans = [(match.start(), match.end()) for match in CSS_COMMENT_RE.finditer(text)]
    lower = text.lower()
    index = 0
    while True:
        start = lower.find("url(", index)
        if start < 0:
            return
        index = start + 4
        if in_span(start, spans):
            continue
        cursor = index
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text):
            return
        if text[cursor] in ("'", '"'):
            quote = text[cursor]
            cursor += 1
            end = text.find(quote, cursor)
            if end < 0:
                return
            raw = text[cursor:end]
            index = text.find(")", end)
            if index < 0:
                return
            index += 1
        else:
            end = text.find(")", cursor)
            if end < 0:
                return
            raw = text[cursor:end].strip()
            index = end + 1
        if raw:
            yield start, raw


def collect_css(
    root: Path,
    css_files: list[Path],
    referenced: set[str],
    missing: list[dict],
) -> None:
    for css_file in css_files:
        text = css_file.read_text(encoding="utf-8", errors="replace")
        source = rel_posix(root, css_file)
        for start, raw in iter_css_urls(text):
            target = local_target(raw)
            if target is None:
                continue
            line = text.count("\n", 0, start) + 1
            note_local(root, css_file, source, line, raw, target, referenced, missing)


def collect_links(root: Path, html_files: list[Path]) -> tuple[set[str], list[dict], list[dict]]:
    referenced: set[str] = set()
    missing: list[dict] = []
    preview_links: list[dict] = []
    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8", errors="replace")
        spans = comment_spans(text)
        source = rel_posix(root, html_file)
        is_root_page = PurePosixPath(source).parts[0] != "preview"
        for match in ATTR_RE.finditer(text):
            if in_span(match.start(), spans):
                continue
            raw = next(group for group in match.groups() if group is not None)
            line = text.count("\n", 0, match.start()) + 1
            target = local_target(raw)
            relative = None
            if target is not None:
                relative = note_local(
                    root, html_file, source, line, raw, target, referenced, missing
                )
            if is_root_page and points_at_preview(raw, relative):
                preview_links.append(
                    {
                        "html": source,
                        "line": line,
                        "url": raw.strip(),
                        "resolved": relative or "",
                    }
                )
    return referenced, missing, preview_links


def banner_hits(root: Path, html_files: list[Path]) -> list[dict]:
    hits: list[dict] = []
    for html_file in html_files:
        source = rel_posix(root, html_file)
        if PurePosixPath(source).parts[0] == "preview":
            continue
        text = html_file.read_text(encoding="utf-8", errors="replace")
        for marker in BANNER_MARKERS:
            if marker in text:
                hits.append({"html": source, "marker": marker})
                break
    return hits


def allowed_missing(rules: dict[str, set], item: dict) -> bool:
    for html_path, token in rules["missing"]:
        if html_path != item["html"]:
            continue
        if token in {item["url"], item["resolved"], norm(item["url"])}:
            return True
    return False


def format_bytes(size: int) -> str:
    return f"{size:,} bytes ({size / (1024 * 1024):.2f} MiB)"


def nav_labels(index_html: str) -> list[str]:
    nav = re.search(r'(?is)<nav class="site-nav".*?</nav>', index_html)
    if not nav:
        return []
    labels = []
    for raw in re.findall(r"(?is)<a\b[^>]*>(.*?)</a>", nav.group(0)):
        text = re.sub(r"(?is)<[^>]+>", "", raw)
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        if text:
            labels.append(text)
    return labels


def site_map_names(data: dict) -> list[str]:
    named = ["Home"]

    def walk(node: dict) -> None:
        named.append(node.get("label", ""))
        for child in node.get("children") or []:
            walk(child)

    for column in ("left", "right"):
        for node in data.get(column) or []:
            walk(node)
    return named


def site_map_gaps(root: Path) -> list[str]:
    """Nav sections that the preview or live site map does not name."""
    map_path = root / "data" / "site-map.json"
    if not map_path.is_file():
        return ["site map source is missing"]
    data = json.loads(map_path.read_text(encoding="utf-8"))
    named = site_map_names(data)
    missing = []
    for which, index_path, page_path in (
        ("live", root / "index.html", root / "site-map.html"),
    ):
        if not index_path.is_file() or not page_path.is_file():
            missing.append(f"{which} site map source is missing")
            continue
        page = page_path.read_text(encoding="utf-8")
        for label in nav_labels(index_path.read_text(encoding="utf-8")):
            if label not in named or label not in page:
                missing.append(f"{which}: {label}")
    return missing


def diagram_geometry(page: str) -> list[str]:
    """Lines in one site-map diagram must not cut through a box or cross."""
    match = re.search(r'(?s)<div class="map-diagram"><svg.*?</svg>', page)
    if not match:
        return ["site map diagram is missing"]
    chunk = match.group(0)
    boxes = [
        tuple(float(value) for value in item.groups())
        for item in re.finditer(
            r'<rect class="map-box[^"]*" x="([0-9.eE+-]+)" y="([0-9.eE+-]+)" '
            r'width="([0-9.eE+-]+)" height="([0-9.eE+-]+)"',
            chunk,
        )
    ]
    segments = [
        (*[float(value) for value in item.groups()], "")
        for item in re.finditer(
            r'<line class="map-line" x1="([0-9.eE+-]+)" y1="([0-9.eE+-]+)" '
            r'x2="([0-9.eE+-]+)" y2="([0-9.eE+-]+)"',
            chunk,
        )
    ]
    from build_site_map import geometry_errors

    return geometry_errors(boxes, segments)


def site_map_geometry(root: Path) -> list[str]:
    """Lines in the preview and live site-map diagrams must not cut a box or cross."""
    errors = []
    for which, page_path in (
        ("live", root / "site-map.html"),
    ):
        if not page_path.is_file():
            errors.append(f"{which}: site map page is missing")
            continue
        for item in diagram_geometry(page_path.read_text(encoding="utf-8")):
            errors.append(f"{which}: {item}")
    return errors


def check(root: Path, allow_path: Path | None, file_limit: int, tree_limit: int) -> tuple[int, str]:
    root = root.resolve()
    if not root.is_dir():
        return 2, f"repository path is not a directory: {root}"

    rules = {"size": set(), "unreferenced": set(), "missing": set(), "root": set()}
    allow_note = "allow list: none"
    if allow_path is not None:
        parsed, error = parse_allow(allow_path)
        if error:
            return 2, f"could not read allow list: {error}"
        rules = parsed
        count = sum(len(values) for values in rules.values())
        allow_note = f"allow list: {allow_path} ({count} entries)"

    files = iter_files(root)
    html_files = sorted(path for path in files if path.suffix.lower() in {".html", ".htm"})
    css_files = sorted(path for path in files if path.suffix.lower() == ".css")
    referenced, missing, preview_links = collect_links(root, html_files)
    collect_css(root, css_files, referenced, missing)
    banners = banner_hits(root, html_files)

    names, git_error = tracked_files(root)
    tracked_rows: list[tuple[int, str]] = []
    tracked_total = 0
    if names is not None:
        for name in names:
            path = root / name
            if path.is_file():
                size = path.stat().st_size
                tracked_total += size
                tracked_rows.append((size, name.replace("\\", "/")))
    tracked_rows.sort(key=lambda item: (-item[0], item[1]))

    oversized: list[tuple[int, str]] = []
    unreferenced: list[tuple[int, str]] = []
    suppressed = 0
    for path in files:
        relative = rel_posix(root, path)
        size = path.stat().st_size
        if size > file_limit and relative not in rules["size"]:
            oversized.append((size, relative))
        elif size > file_limit:
            suppressed += 1
        if is_asset(path):
            if relative not in referenced and relative not in rules["unreferenced"]:
                unreferenced.append((size, relative))
            elif relative not in referenced:
                suppressed += 1
    oversized.sort(key=lambda item: (-item[0], item[1]))
    unreferenced.sort(key=lambda item: item[1])

    missing_left = []
    for item in missing:
        if allowed_missing(rules, item):
            suppressed += 1
        else:
            missing_left.append(item)
    missing_left.sort(key=lambda item: (item["html"], item["line"], item["url"]))

    root_left = []
    for item in preview_links:
        if item["html"] in rules["root"]:
            suppressed += 1
        else:
            root_left.append(("link", item["html"], item["line"], item["url"], item["resolved"]))
    for item in banners:
        if item["html"] in rules["root"]:
            suppressed += 1
        else:
            root_left.append(("banner", item["html"], 0, item["marker"], ""))
    root_left.sort(key=lambda item: (item[1], item[2], item[0], item[3]))

    size_over = names is not None and tracked_total > tree_limit
    map_gaps = site_map_gaps(root)
    map_lines = site_map_geometry(root)
    failed = bool(
        oversized or unreferenced or missing_left or root_left or size_over or git_error or map_gaps or map_lines
    )

    lines: list[str] = []
    lines.append("WyoVote publish check")
    lines.append(f"Repository: {root}")
    lines.append(f"Result: {'FAIL' if failed else 'PASS'}")
    lines.append(allow_note)
    lines.append(f"Suppressed by the allow list: {suppressed}")
    lines.append("")
    if git_error:
        lines.append(f"Tracked size: unavailable ({git_error})")
        lines.append("Tracked size: FAIL")
    else:
        lines.append(f"Tracked size: {format_bytes(tracked_total)}")
        lines.append(f"Tracked size limit: {tree_limit:,} bytes (200 MB)")
        lines.append(f"Tracked size: {'FAIL' if size_over else 'OK'}")
    lines.append("")
    lines.append("10 largest tracked files:")
    if not tracked_rows:
        lines.append("  (none)")
    for index, (size, name) in enumerate(tracked_rows[:10], 1):
        lines.append(f"  {index:2}. {size:12,}  {name}")
    lines.append("")
    lines.append(f"Files over 500 KB ({file_limit:,} bytes): {len(oversized)}")
    for size, relative in oversized:
        lines.append(f"  {size:12,}  {relative}")
    if not oversized:
        lines.append("  (none)")
    lines.append("")
    lines.append(
        "Assets with no HTML href/src or CSS url() "
        f"(every file except HTML, CSS, and JS): {len(unreferenced)}"
    )
    for size, relative in unreferenced:
        lines.append(f"  {size:12,}  {relative}")
    if not unreferenced:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"HTML href/src and CSS url() targets that are not local files: {len(missing_left)}")
    for item in missing_left:
        resolved = item["resolved"] or item["reason"]
        lines.append(f"  {item['html']}:{item['line']}  {item['url']}  ->  {resolved}")
    if not missing_left:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Root pages linking into preview/ or showing the PREVIEW banner: {len(root_left)}")
    for kind, source, line, detail, resolved in root_left:
        if kind == "banner":
            lines.append(f"  {source}  contains {detail}")
        else:
            where = f":{line}" if line else ""
            lines.append(f"  {source}{where}  links to {detail}  ->  {resolved}")
    if not root_left:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Top-level nav labels missing from the site map: {len(map_gaps)}")
    for label in map_gaps:
        lines.append(f"  {label}")
    if not map_gaps:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Site map lines through a box or crossing another line: {len(map_lines)}")
    for item in map_lines[:12]:
        lines.append(f"  {item}")
    if not map_lines:
        lines.append("  (none)")
    lines.append("")
    lines.append(
        "Counts: "
        f"working_tree_files={len(files)} "
        f"html={len(html_files)} "
        f"css={len(css_files)} "
        f"tracked_files={len(tracked_rows)} "
        f"tracked_bytes={tracked_total} "
        f"oversized={len(oversized)} "
        f"unreferenced={len(unreferenced)} "
        f"missing={len(missing_left)} "
        f"root_preview={len(root_left)} "
        f"site_map={len(map_gaps)} "
        f"site_map_lines={len(map_lines)}"
    )
    return (1 if failed else 0), "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a WyoVote tree before publish.")
    parser.add_argument(
        "repo",
        nargs="?",
        help="Repository root to scan. Defaults to the repo that contains this script.",
    )
    parser.add_argument(
        "--allow-list",
        dest="allow_list",
        help="Allow-list file. Defaults to tools/publish_check_allow.txt in the scanned repository when that file exists.",
    )
    args = parser.parse_args(argv)
    if args.repo:
        root = Path(args.repo)
    else:
        root = Path(__file__).resolve().parent.parent
    if args.allow_list:
        allow_path: Path | None = Path(args.allow_list)
        if not allow_path.is_file():
            print(f"allow list not found: {allow_path}", file=sys.stderr)
            return 2
    else:
        default_allow = root / "tools" / "publish_check_allow.txt"
        allow_path = default_allow if default_allow.is_file() else None
    code, report = check(root, allow_path, FILE_LIMIT, TREE_LIMIT)
    stream = sys.stdout if code != 2 else sys.stderr
    print(report, end="", file=stream)
    return code


if __name__ == "__main__":
    sys.exit(main())
