# -*- coding: utf-8 -*-
"""
LOADING KHUSUS PEMBUATAN KODE / FILE.

Dipakai HANYA saat Yuki sedang menulis kode atau file (bukan chat biasa,
bukan pembuatan gambar). Muncul di ruang chat menggantikan animasi
"berpikir", lalu hilang dan digantikan kartu file begitu selesai.

SEMUA yang berkaitan dengan loader ini ada di satu file:
tampilan (HTML), gaya (CSS), dan teksnya. Jadi kalau nanti mau diganti
dengan desain lain, cukup timpa file ini.

CATATAN PENTING soal animasi:
    HTML di bawah dirender SEKALI saja lalu semua gerakannya dijalankan
    CSS di browser. Jangan me-render ulang di dalam loop - setiap
    markdown() baru mengganti node DOM sehingga animasi CSS ter-reset
    dari nol (loader akan terlihat diam/berkedip).
"""

from __future__ import annotations

import html

import streamlit as st

# ============================================================================
# >>> PENGATURAN LOADER — UBAH DI SINI <<<
# ============================================================================
TEKS_TAHAP = [                 # berganti otomatis, dikerjakan CSS
    "Menyusun struktur",
    "Menulis kode",
    "Merapikan format",
    "Memeriksa ulang",
]
TEKS_SELESAI = "Selesai"
DURASI_SIKLUS_DETIK = 8        # lama satu putaran penuh teks tahap
WARNA_KARTU = "#FFFFFF"        # latar kotak loader
WARNA_GARIS = "#E4D9C6"        # garis tepi
WARNA_TEKS = "#2C1F33"
WARNA_TEKS_REDUP = "#8E8398"
WARNA_AKSEN = "#2C1F33"        # bar progres & titik
LEBAR_MAKS_PX = 460
# ============================================================================


def inject_code_loading_css() -> None:
    """Suntik CSS loader. Dipanggil sekali sebelum loader dipakai."""
    n = max(1, len(TEKS_TAHAP))
    per = round(DURASI_SIKLUS_DETIK / n, 2)
    css = (
        "<style>"
        ".cl-box{"
        "background:" + WARNA_KARTU + ";"
        "border:1px solid " + WARNA_GARIS + ";"
        "border-radius:14px;"
        "padding:14px 16px;"
        "max-width:" + str(LEBAR_MAKS_PX) + "px;"
        "margin:6px 0 14px;"
        "position:relative;overflow:hidden;"
        "box-shadow:0 2px 10px rgba(44,31,51,0.05);"
        "animation:clIn .35s cubic-bezier(.32,.72,0,1) both;"
        "}"
        "@keyframes clIn{from{opacity:0;transform:translateY(8px) scale(.97);}"
        "to{opacity:1;transform:translateY(0) scale(1);}}"

        # baris atas: ikon berkas + nama file
        ".cl-top{display:flex;align-items:center;gap:9px;margin-bottom:10px;}"
        ".cl-ic{"
        "font-family:'JetBrains Mono',monospace;font-size:.76rem;font-weight:700;"
        "color:#FBF6EC;background:" + WARNA_AKSEN + ";border-radius:7px;"
        "padding:3px 7px;line-height:1.2;"
        "animation:clPulse 1.6s ease-in-out infinite;"
        "}"
        "@keyframes clPulse{0%,100%{opacity:1;}50%{opacity:.55;}}"
        ".cl-name{"
        "font-family:'JetBrains Mono',monospace;font-size:.9rem;font-weight:600;"
        "color:" + WARNA_TEKS + ";word-break:break-all;"
        "}"

        # baris teks tahap yang berganti-ganti
        ".cl-stage{position:relative;height:1.15rem;overflow:hidden;"
        "font-size:.85rem;color:" + WARNA_TEKS_REDUP + ";}"
        ".cl-stage span{position:absolute;left:0;top:0;white-space:nowrap;"
        "opacity:0;animation:clStage " + str(DURASI_SIKLUS_DETIK) + "s "
        "linear infinite;}"
        "@keyframes clStage{"
        "0%{opacity:0;transform:translateY(6px);}"
        "4%{opacity:1;transform:translateY(0);}"
        "20%{opacity:1;transform:translateY(0);}"
        "24%{opacity:0;transform:translateY(-6px);}"
        "100%{opacity:0;}"
        "}"

        # baris kode palsu yang berkedip seperti sedang diketik
        ".cl-lines{margin:11px 0 12px;display:flex;flex-direction:column;gap:6px;}"
        ".cl-line{height:8px;border-radius:99px;"
        "background:linear-gradient(90deg,#EFE6D6 0%,#E2D6C1 50%,#EFE6D6 100%);"
        "background-size:200% 100%;animation:clSweep 1.5s linear infinite;}"
        "@keyframes clSweep{0%{background-position:200% 0;}100%{background-position:-200% 0;}}"

        # bar progres tipis di dasar kotak
        ".cl-bar{height:3px;border-radius:99px;background:#EFE6D6;overflow:hidden;}"
        ".cl-fill{height:100%;width:35%;border-radius:99px;"
        "background:" + WARNA_AKSEN + ";animation:clRun 1.9s ease-in-out infinite;}"
        "@keyframes clRun{0%{margin-left:-38%;}100%{margin-left:100%;}}"

        # keadaan selesai: semua gerakan berhenti
        ".cl-box.is-done .cl-ic,"
        ".cl-box.is-done .cl-line,"
        ".cl-box.is-done .cl-fill{animation:none;}"
        ".cl-box.is-done .cl-fill{width:100%;margin-left:0;}"
        ".cl-box.is-done .cl-stage span{animation:none;opacity:0;}"
        ".cl-box.is-done .cl-stage span:first-child{opacity:1;}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader. Render SEKALI saja (lihat catatan di atas)."""
    judul = html.escape(nama_file or "Menyiapkan berkas…")
    if done:
        spans = '<span>' + html.escape(TEKS_SELESAI) + '…</span>'
    else:
        n = max(1, len(TEKS_TAHAP))
        per = DURASI_SIKLUS_DETIK / n
        spans = "".join(
            '<span style="animation-delay:' + str(round(i * per, 2)) + 's">'
            + html.escape(t) + "…</span>"
            for i, t in enumerate(TEKS_TAHAP)
        )

    garis = "".join(
        '<div class="cl-line" style="width:' + w + ';animation-delay:'
        + str(round(i * 0.18, 2)) + 's"></div>'
        for i, w in enumerate(("92%", "76%", "84%", "58%"))
    )

    kelas = "cl-box is-done" if done else "cl-box"
    return (
        '<div class="bubble-row ai"><div class="bubble-wrap">'
        '<div class="' + kelas + '">'
        '<div class="cl-top"><span class="cl-ic">&lt;/&gt;</span>'
        '<span class="cl-name">' + judul + "</span></div>"
        '<div class="cl-stage">' + spans + "</div>"
        '<div class="cl-lines">' + garis + "</div>"
        '<div class="cl-bar"><div class="cl-fill"></div></div>'
        "</div></div></div>"
    )
