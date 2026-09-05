# -*- coding: utf-8 -*-
"""
PANEL ARTEFAK (sidebar kanan) — ala Claude Artifacts.

Dua tampilan:
  DAFTAR : bagian "Artefak" (kartu file + unduh semua) dan "Konten"
           (petak gambar hasil buatan Yuki)
  ISI    : kode dengan nomor baris + pewarnaan sintaks, tombol Salin,
           perlebar, dan tutup

Alur: Yuki menulis blok kode ```...``` -> ambil_artefak() memotongnya dari
teks chat, menyimpannya sebagai file, lalu panel ini terbuka otomatis.

>>> ATUR LEBAR & PERILAKU PANEL DI BAGIAN "PENGATURAN" DI BAWAH <<<
"""

from __future__ import annotations

import base64
import html
import io
import re
import zipfile
from datetime import datetime
import streamlit.components.v1 as components
import streamlit as st

# ============================================================================
# PENGATURAN
# ============================================================================
MIN_BARIS_JADI_FILE = 3     # blok kode lebih pendek dari ini tetap di chat
MIN_KARAKTER_JADI_FILE = 40
BARIS_LANGSUNG_FILE = 5     # sebanyak ini baris ke atas: selalu jadi file
_EKSTENSI = {
    "python": "py", "py": "py", "javascript": "js", "js": "js",
    "typescript": "ts", "ts": "ts", "html": "html", "css": "css",
    "json": "json", "yaml": "yml", "yml": "yml", "sql": "sql",
    "bash": "sh", "sh": "sh", "shell": "sh", "java": "java",
    "kotlin": "kt", "swift": "swift", "php": "php", "dart": "dart",
    "go": "go", "rust": "rs", "c": "c", "cpp": "cpp", "csharp": "cs",
    "markdown": "md", "md": "md", "xml": "xml", "toml": "toml",
}

_KODE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.S)
_NAMA_RE = re.compile(r"([\w./-]+\.[A-Za-z0-9]{1,5})\s*:?\s*$")

# ============================================================================
# PENYIMPANAN
# ============================================================================
def daftar_artefak() -> list[dict]:
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []
    return st.session_state.artifacts


def _tebak_nama(lang: str, kode: str, sebelum: str) -> str:
    m = _NAMA_RE.search((sebelum or "").strip().splitlines()[-1]
                        if (sebelum or "").strip() else "")
    if m:
        return m.group(1)
    baris1 = (kode.splitlines() or [""])[0].strip()
    m2 = re.search(r"([\w./-]+\.[A-Za-z0-9]{1,5})", baris1)
    if m2 and baris1.startswith(("#", "//", "/*", "<!--")):
        return m2.group(1)
    ext = _EKSTENSI.get((lang or "").lower(), "txt")
    return f"file_{len(daftar_artefak()) + 1}.{ext}"

def ambil_artefak(teks: str) -> tuple[str, list[int]]:
    """Potong blok kode dari jawaban Yuki -> simpan sebagai file, 
    sekaligus merapikan teks dan menyisipkan kartu artefak di chat."""
    raw = teks or ""
    if "```" not in raw:
        return raw, []

    baru: list[int] = []
    potongan: list[str] = []
    posisi = 0

    for m in _KODE_RE.finditer(raw):
        lang = (m.group(1) or "").lower()
        kode = m.group(2).strip("\n")
        potongan.append(raw[posisi:m.start()])
        sebelum = raw[posisi:m.start()]
        posisi = m.end()

        n_baris = len(kode.splitlines())
        layak = (n_baris >= BARIS_LANGSUNG_FILE
                 or (n_baris >= MIN_BARIS_JADI_FILE
                     and len(kode) >= MIN_KARAKTER_JADI_FILE))
        if not layak:
            potongan.append(m.group(0))
            continue

        st.session_state["artifact_counter"] = (
            st.session_state.get("artifact_counter", 0) + 1
        )
        aid = st.session_state["artifact_counter"]
        daftar_artefak().insert(0, {
            "id": aid,
            "title": _tebak_nama(lang, kode, sebelum),
            "content": kode,
            "lang": lang or "text",
            "time": datetime.now().strftime("%H:%M"),
        })
        baru.append(aid)

    potongan.append(raw[posisi:])
    
    # Rapikan spasi atau baris kosong berlebih yang tertinggal
    bersih = re.sub(r"\n{3,}", "\n\n", "".join(potongan)).strip()

    # Jika ada file/artefak baru yang berhasil dibuat, 
    # sematkan kartu ringkasnya di akhir teks pesan chat
    if baru:
        bersih += "\n\n" + kartu_file_html(baru)

    return bersih, baru


def kartu_file_html(ids: list[int]) -> str:
    """Kartu ringkas pengganti kode di dalam chat."""
    kartu = ""
    for aid in ids:
        art = next((a for a in daftar_artefak() if a["id"] == aid), None)
        if not art:
            continue
        kartu += (
            '<div class="af-chip"><span class="af-chip-ic">&lt;/&gt;</span>'
            f'<span class="af-chip-name">{html.escape(art["title"])}</span>'
            f'<span class="af-chip-meta">{html.escape(art["lang"])} · '
            f'{len(art["content"].splitlines())} baris</span></div>'
        )
    return kartu
