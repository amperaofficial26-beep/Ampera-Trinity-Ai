#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pemeriksa tautan untuk situs hasil build (_site/).

Memastikan tidak ada tautan yang menggantung sebelum situs diterbitkan:
  - tautan .md yang lupa diubah jadi .html
  - berkas tujuan yang tidak ada
  - jangkar (#anchor) yang menunjuk id yang tidak pernah dibuat
  - gambar / skrip / stylesheet yang hilang

Dipakai otomatis oleh alur kerja GitHub Actions, tapi bisa juga dijalankan
manual setelah `python tools/build_site.py`:

    python tools/check_links.py
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"

EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:")


def main() -> int:
    if not SITE.exists():
        print("✗ Folder _site/ belum ada. Jalankan dulu: python tools/build_site.py")
        return 1

    pages = sorted(SITE.glob("*.html"))
    if not pages:
        print("✗ Tidak ada berkas HTML di _site/")
        return 1

    files = {p.name for p in SITE.iterdir() if p.is_file()}
    ids: dict[str, set[str]] = {}
    for page in pages:
        text = page.read_text(encoding="utf-8")
        ids[page.name] = set(re.findall(r'id="([^"]+)"', text))

    problems: list[str] = []

    for page in pages:
        text = page.read_text(encoding="utf-8")
        name = page.name

        # ---- href ----
        for raw in re.findall(r'href="([^"]+)"', text):
            href = html.unescape(raw)
            if href.startswith(EXTERNAL):
                continue

            if href.startswith("#"):
                anchor = href[1:]
                if anchor and anchor not in ids[name]:
                    problems.append(f"[jangkar] {name} → {href}")
                continue

            target, _, anchor = href.partition("#")

            if target.endswith(".md"):
                problems.append(f"[markdown] {name} → {href}  (belum diubah ke .html)")
                continue

            if target and target not in files and not (SITE / target).exists():
                problems.append(f"[hilang]   {name} → {href}")
                continue

            if anchor and target in ids and anchor not in ids[target]:
                problems.append(f"[jangkar]  {name} → {href}")

        # ---- src ----
        for raw in re.findall(r'src="([^"]+)"', text):
            src = html.unescape(raw)
            if src.startswith(EXTERNAL):
                continue
            if not (SITE / src).exists():
                problems.append(f"[aset]     {name} → {src}")

        # ---- stylesheet ----
        for raw in re.findall(r'<link[^>]+href="([^"]+)"', text):
            css = html.unescape(raw)
            if css.startswith(EXTERNAL):
                continue
            if not (SITE / css).exists():
                problems.append(f"[css]      {name} → {css}")

    if problems:
        print(f"✗ Ditemukan {len(problems)} tautan bermasalah:\n")
        for item in problems:
            print("   " + item)
        return 1

    total_links = sum(
        len(re.findall(r'href="([^"]+)"', p.read_text(encoding="utf-8"))) for p in pages
    )
    print(f"✓ Semua tautan valid — {len(pages)} halaman, {total_links} tautan diperiksa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
