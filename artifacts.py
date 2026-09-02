# -*- coding: utf-8 -*-
"""
PANEL ARTEFAK (sidebar kanan) — ala Claude Artifacts.

Alur kerjanya:
  1. Yuki menulis jawaban berisi blok kode ```...```
  2. ambil_artefak() memotong blok itu dari teks chat, menyimpannya sebagai
     "file", lalu menyisipkan kartu ringkas (nama file + bahasa + jumlah baris)
  3. Panel kanan otomatis terbuka menampilkan isi file lengkapnya

Jadi chat tetap ringkas, kode dibaca di panel khusus.

>>> ATUR LEBAR & PERILAKU PANEL DI BAGIAN "PENGATURAN" DI BAWAH <<<
"""

from __future__ import annotations

import html
import re
from datetime import datetime

import streamlit as st

# ============================================================================
# PENGATURAN
# ============================================================================
PANEL_LEBAR_PX = 460        # lebar panel kanan
BUKA_OTOMATIS = True        # panel langsung terbuka saat file baru dibuat
MIN_BARIS_JADI_FILE = 3     # blok kode lebih pendek dari ini tetap di chat
MIN_KARAKTER_JADI_FILE = 40 # ...begitu juga yang terlalu sedikit karakternya
BARIS_LANGSUNG_FILE = 5     # sebanyak ini baris ke atas: selalu jadi file
# ============================================================================

# ekstensi berkas menurut bahasa yang ditulis Yuki di pagar kode
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
# "nama file" kalau Yuki menyebutnya di baris sebelum blok kode
_NAMA_RE = re.compile(r"([\w./-]+\.[A-Za-z0-9]{1,5})\s*:?\s*$")


def daftar_artefak() -> list[dict]:
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []
    return st.session_state.artifacts


def _tebak_nama(lang: str, kode: str, sebelum: str) -> str:
    """Tebak nama file: dari teks sebelum blok, komentar di baris pertama,
    atau nama umum sesuai bahasanya."""
    m = _NAMA_RE.search((sebelum or "").strip().splitlines()[-1]
                        if (sebelum or "").strip() else "")
    if m:
        return m.group(1)

    baris1 = (kode.splitlines() or [""])[0].strip()
    m2 = re.search(r"([\w./-]+\.[A-Za-z0-9]{1,5})", baris1)
    if m2 and baris1.startswith(("#", "//", "/*", "<!--")):
        return m2.group(1)

    ext = _EKSTENSI.get((lang or "").lower(), "txt")
    n = len([a for a in daftar_artefak()]) + 1
    return f"file_{n}.{ext}"


def ambil_artefak(teks: str) -> tuple[str, list[int]]:
    """Potong blok kode dari jawaban Yuki -> simpan sebagai file.

    Mengembalikan (teks_tanpa_kode, daftar_id_file_baru).
    Blok pendek dibiarkan tetap di chat supaya cuplikan singkat tidak
    ikut jadi "file".
    """
    raw = teks or ""
    if "```" not in raw:
        return raw, []

    baru: list[int] = []
    potongan: list[str] = []
    posisi = 0

    for m in _KODE_RE.finditer(raw):
        lang = (m.group(1) or "").lower()
        kode = m.group(2).strip("\n")
        sebelum = raw[posisi:m.start()]
        potongan.append(sebelum)
        posisi = m.end()

        n_baris = len(kode.splitlines())
        cukup_panjang = (
            n_baris >= BARIS_LANGSUNG_FILE
            or (n_baris >= MIN_BARIS_JADI_FILE and len(kode) >= MIN_KARAKTER_JADI_FILE)
        )
        if not cukup_panjang:
            potongan.append(m.group(0))     # biarkan tetap di chat
            continue

        st.session_state["artifact_counter"] = (
            st.session_state.get("artifact_counter", 0) + 1
        )
        aid = st.session_state["artifact_counter"]
        nama = _tebak_nama(lang, kode, sebelum)
        daftar_artefak().insert(0, {
            "id": aid,
            "title": nama,
            "content": kode,
            "lang": lang or "text",
            "time": datetime.now().strftime("%H:%M"),
        })
        baru.append(aid)

    potongan.append(raw[posisi:])
    bersih = re.sub(r"\n{3,}", "\n\n", "".join(potongan)).strip()

    if baru and BUKA_OTOMATIS:
        st.session_state["artifact_panel_open"] = True
        st.session_state["artifact_panel_id"] = baru[0]

    return bersih, baru


def kartu_file_html(ids: list[int]) -> str:
    """Kartu ringkas pengganti kode di dalam chat."""
    kartu = ""
    for aid in ids:
        art = next((a for a in daftar_artefak() if a["id"] == aid), None)
        if not art:
            continue
        baris = len(art["content"].splitlines())
        kartu += (
            '<div class="af-chip">'
            '<span class="af-chip-ic">&lt;/&gt;</span>'
            f'<span class="af-chip-name">{html.escape(art["title"])}</span>'
            f'<span class="af-chip-meta">{html.escape(art["lang"])} · {baris} baris</span>'
            "</div>"
        )
    return kartu


def buka_panel(aid: int) -> None:
    st.session_state["artifact_panel_open"] = True
    st.session_state["artifact_panel_id"] = aid


def tutup_panel() -> None:
    st.session_state["artifact_panel_open"] = False


def render_panel() -> None:
    """Panel kanan berisi file/kode buatan Yuki.

    Dirender sebagai container biasa lalu DIPOSISIKAN ke kanan lewat CSS
    (Streamlit tidak punya sidebar kanan bawaan).
    """
    daftar = daftar_artefak()
    if not st.session_state.get("artifact_panel_open") or not daftar:
        return

    aktif_id = st.session_state.get("artifact_panel_id") or daftar[0]["id"]
    aktif = next((a for a in daftar if a["id"] == aktif_id), daftar[0])

    # CSS panel disuntik di sini supaya lebarnya mengikuti PANEL_LEBAR_PX
    st.markdown(
        "<style>"
        ".st-key-art_panel{"
        "position:fixed !important;"
        "top:3.2rem !important;right:0 !important;bottom:0 !important;"
        "width:" + str(PANEL_LEBAR_PX) + "px !important;"
        "background:#F7F1E6 !important;"
        "border-left:1px solid #DBCEB9 !important;"
        "padding:14px 16px 90px !important;"
        "overflow-y:auto !important;"
        "z-index:999990 !important;"
        "box-shadow:-8px 0 24px rgba(44,31,51,0.06) !important;"
        "animation:afSlideIn .34s cubic-bezier(.32,.72,0,1) both;"
        "}"
        "@keyframes afSlideIn{"
        "from{opacity:0;transform:translateX(28px);}"
        "to{opacity:1;transform:translateX(0);}"
        "}"
        "[data-testid='stMainBlockContainer']{"
        "padding-right:" + str(PANEL_LEBAR_PX + 40) + "px !important;"
        "}"
        "@media (max-width: 1100px){"
        ".st-key-art_panel{width:100% !important;top:0 !important;}"
        "[data-testid='stMainBlockContainer']{padding-right:1rem !important;}"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )

    with st.container(key="art_panel"):
        judul, tombol = st.columns([1.0, 0.16])
        with judul:
            st.markdown(
                '<div class="af-head">'
                '<div class="af-head-title">' + html.escape(aktif["title"]) + "</div>"
                '<div class="af-head-meta">' + html.escape(aktif["lang"])
                + " · " + str(len(aktif["content"].splitlines())) + " baris · "
                + html.escape(aktif.get("time", "")) + "</div></div>",
                unsafe_allow_html=True,
            )
        with tombol:
            st.button("✕", key="af_close", help="Tutup panel",
                      on_click=tutup_panel)

        # pemilih file bila ada lebih dari satu
        if len(daftar) > 1:
            pilihan = {f'{a["title"]}  ·  {a.get("time", "")}': a["id"]
                       for a in daftar[:12]}
            label_aktif = next((k for k, v in pilihan.items() if v == aktif["id"]),
                               list(pilihan)[0])
            dipilih = st.selectbox(
                "File", list(pilihan), index=list(pilihan).index(label_aktif),
                key="af_pick", label_visibility="collapsed",
            )
            if pilihan[dipilih] != aktif["id"]:
                st.session_state["artifact_panel_id"] = pilihan[dipilih]
                st.rerun()

        st.code(aktif["content"], language=aktif["lang"] or None)

        st.download_button(
            ":material/download:  Unduh " + aktif["title"],
            data=aktif["content"],
            file_name=aktif["title"],
            mime="text/plain",
            key=f"af_dl_{aktif['id']}",
            use_container_width=True,
        )
