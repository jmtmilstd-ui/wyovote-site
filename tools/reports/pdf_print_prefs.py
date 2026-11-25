#!/usr/bin/env python3
"""Add print ViewerPreferences to WyoVote report PDFs.

Sets:
    /ViewerPreferences << /PrintScaling /None /PickTrayByPDFSize true >>

Page content and page size are left unchanged. Use this after a ReportLab
build (and after booklet padding) so a rebuild keeps the preferences, and
to tag existing report PDFs already on the site.

  python3 -B tools/reports/pdf_print_prefs.py [repo]

Skips guide/ PDFs. Refuses to write if page count or MediaBox would change,
or if a file that was at or under 500 KB would go over that limit.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

FILE_LIMIT = 500 * 1024


def _mediabox(page) -> tuple[float, float, float, float]:
    box = page.mediabox
    return (float(box[0]), float(box[1]), float(box[2]), float(box[3]))


def _prefs_are_set(reader: PdfReader) -> bool:
    vp = reader.viewer_preferences
    if vp is None:
        return False
    scaling = vp.get("/PrintScaling")
    tray = vp.get("/PickTrayByPDFSize")
    scaling_ok = scaling is not None and str(scaling) in ("/None", "None")
    tray_ok = tray is True or str(tray) in ("true", "True", "/true")
    return bool(scaling_ok and tray_ok)


def apply_viewer_prefs(path: Path) -> dict:
    """Write ViewerPreferences onto path in place. Returns a small status dict."""
    path = Path(path)
    before_bytes = path.stat().st_size
    reader = PdfReader(str(path))
    before_pages = len(reader.pages)
    before_boxes = [_mediabox(p) for p in reader.pages]
    if _prefs_are_set(reader):
        return {
            "path": path,
            "changed": False,
            "pages": before_pages,
            "bytes_before": before_bytes,
            "bytes_after": before_bytes,
        }

    writer = PdfWriter(clone_from=reader)
    prefs = writer.create_viewer_preferences()
    prefs.print_scaling = NameObject("/None")
    prefs.pick_tray_by_pdfsize = True

    tmp = path.with_name(path.name + ".prefs-tmp")
    try:
        writer.write(str(tmp))
        check = PdfReader(str(tmp))
        if len(check.pages) != before_pages:
            raise RuntimeError(f"{path}: page count changed {before_pages} -> {len(check.pages)}")
        after_boxes = [_mediabox(p) for p in check.pages]
        if after_boxes != before_boxes:
            raise RuntimeError(f"{path}: MediaBox changed")
        if not _prefs_are_set(check):
            raise RuntimeError(f"{path}: ViewerPreferences missing after write")
        after_bytes = tmp.stat().st_size
        if before_bytes <= FILE_LIMIT < after_bytes:
            raise RuntimeError(
                f"{path}: would exceed 500 KB ({before_bytes} -> {after_bytes})"
            )
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()

    return {
        "path": path,
        "changed": True,
        "pages": before_pages,
        "bytes_before": before_bytes,
        "bytes_after": path.stat().st_size,
    }


def iter_report_pdfs(root: Path) -> list[Path]:
    paths = sorted(root.joinpath("reports").rglob("*.pdf"))
    paths += sorted(root.joinpath("people", "pdf").glob("*.pdf"))
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", nargs="?", default=".")
    args = ap.parse_args()
    root = Path(args.repo).resolve()
    paths = iter_report_pdfs(root)
    if not paths:
        print("no report PDFs found", file=sys.stderr)
        return 2
    changed = 0
    skipped = 0
    max_delta = 0
    for path in paths:
        rec = apply_viewer_prefs(path)
        delta = rec["bytes_after"] - rec["bytes_before"]
        if abs(delta) > abs(max_delta):
            max_delta = delta
        if rec["changed"]:
            changed += 1
        else:
            skipped += 1
    print(
        f"tagged {changed} PDFs, already set {skipped}, "
        f"total {len(paths)}, max byte delta {max_delta:+d}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
