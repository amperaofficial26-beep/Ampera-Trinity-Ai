# -*- coding: utf-8 -*-
"""
DOK FILE — panel kecil pengganti panel artefak lama.

Konsep BARU (sengaja beda dari panel sebelumnya):
  - Bukan sidebar penuh setinggi layar, melainkan KARTU KECIL melayang
    di kanan-atas dengan tema gelap (ungu) + aksen emas.
  - TIDAK ada buka otomatis. Saat Yuki selesai membuat file, hanya muncul
    gelembung kecil "File kamu ada di sini" + titik merah penghitung di
    ikon foldernya. Gelembung hilang begitu dok dibuka.
  - Preview kode memakai st.popover + st.code bawaan Streamlit (bukan
    viewer nomor-baris buatan sendiri seperti dulu).

Pintu masuk: render_file_dock() dipanggil dari app.py::main().
Sumber data: st.session_state.artifacts (diisi artifacts.ambil_artefak()).
"""

from __future__ import annotations

import html

import streamlit as st


def _files() -> list[dict]:
    """Daftar file buatan Yuki, dibaca langsung dari session_state.
    (Tanpa import dari artifacts.py supaya modul ini mandiri.)"""
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []
    return st.session_state.artifacts

# ============================================================================
# >>> ATUR TAMPILAN DOK DI SINI <<<
# ============================================================================
DOK_LEBAR_PX = 336            # lebar kartu daftar file
DOK_MAKS_TINGGI = "62vh"      # tinggi maksimum sebelum daftar discroll
WARNA_KARTU = "#2C1F33"       # latar kartu (ungu gelap)
WARNA_TEKS = "#F6EEDF"        # teks utama (krem terang)
WARNA_REDUP = "#B8A9C0"       # teks sekunder
WARNA_AKSEN = "#E8B04B"       # emas: chip ekstensi & hover tombol
MAKS_FILE_TAMPIL = 12         # dok itu kecil; sisanya cukup disebut jumlahnya

TOMBOL_ATAS_PX = 56           # posisi ikon folder dari atas layar
TOMBOL_KANAN_PX = 16          # posisi ikon folder dari kanan layar
TEKS_GELEMBUNG = "File kamu ada di sini"


# ============================================================================
# CSS
# ============================================================================
def _css(terbuka: bool) -> str:
    panel_atas = TOMBOL_ATAS_PX + 56
    return (
        "<style>"
        # ---- ikon folder melayang -------------------------------------
        "body [class*='st-key-fd_toggle']{"
        f"position:fixed!important;top:{TOMBOL_ATAS_PX}px!important;"
        f"right:{TOMBOL_KANAN_PX}px!important;left:auto!important;"
        "width:46px!important;margin:0!important;z-index:999998!important;}"
        "body [class*='st-key-fd_toggle'] button{"
        "width:46px!important;height:46px!important;min-width:46px!important;"
        "padding:0!important;border-radius:50%!important;"
        f"background:{WARNA_KARTU}!important;color:{WARNA_TEKS}!important;"
        "border:1px solid rgba(255,255,255,.16)!important;"
        "box-shadow:0 6px 18px rgba(44,31,51,.30)!important;}"
        "body [class*='st-key-fd_toggle'] button:hover{"
        f"background:{WARNA_AKSEN}!important;color:{WARNA_KARTU}!important;}}"
        # ---- titik merah penghitung file baru -------------------------
        ".fd-dot{"
        f"position:fixed;top:{TOMBOL_ATAS_PX - 6}px;"
        f"right:{TOMBOL_KANAN_PX - 4}px;z-index:999999;"
        "min-width:20px;height:20px;padding:0 5px;border-radius:10px;"
        "background:#D9534F;color:#FFF;font-size:11px;font-weight:700;"
        "display:flex;align-items:center;justify-content:center;"
        "box-shadow:0 2px 8px rgba(0,0,0,.25);pointer-events:none;}"
        # ---- gelembung kecil di samping ikon ---------------------------
        ".fd-bubble{"
        f"position:fixed;top:{TOMBOL_ATAS_PX + 8}px;"
        f"right:{TOMBOL_KANAN_PX + 56}px;z-index:999999;"
        f"background:{WARNA_KARTU};color:{WARNA_TEKS};"
        "font-size:12.5px;font-weight:600;padding:8px 13px;"
        "border-radius:14px 14px 4px 14px;white-space:nowrap;"
        "box-shadow:0 8px 22px rgba(44,31,51,.30);pointer-events:none;"
        "animation:fd-float 2.2s ease-in-out infinite;}"
        ".fd-bubble::after{content:'';position:absolute;right:-6px;top:50%;"
        f"transform:translateY(-50%);border-left:7px solid {WARNA_KARTU};"
        "border-top:6px solid transparent;border-bottom:6px solid transparent;}"
        "@keyframes fd-float{0%,100%{transform:translateX(0)}"
        "50%{transform:translateX(-5px)}}"
        # ---- kartu dok ------------------------------------------------
        "body .st-key-fd_panel{"
        f"position:fixed!important;top:{panel_atas}px!important;"
        f"right:{TOMBOL_KANAN_PX}px!important;left:auto!important;"
        f"width:{DOK_LEBAR_PX}px!important;"
        f"max-height:{DOK_MAKS_TINGGI}!important;overflow-y:auto!important;"
        f"background:{WARNA_KARTU}!important;"
        "border:1px solid rgba(255,255,255,.10)!important;"
        "border-radius:18px!important;padding:18px 16px 14px!important;"
        "box-shadow:0 18px 48px rgba(20,12,26,.45)!important;"
        "z-index:999997!important;animation:fd-in .22s ease-out;}"
        "@keyframes fd-in{from{opacity:0;transform:translateY(-8px)}"
        "to{opacity:1;transform:translateY(0)}}"
        # ---- isi kartu -------------------------------------------------
        f".fd-title{{color:{WARNA_TEKS};font-size:16px;font-weight:700;margin:0;}}"
        f".fd-sub{{color:{WARNA_REDUP};font-size:12px;margin:2px 0 12px;}}"
        f".fd-name{{color:{WARNA_TEKS};font-size:13.5px;font-weight:650;"
        "word-break:break-all;line-height:1.35;}"
        f".fd-meta{{color:{WARNA_REDUP};font-size:11.5px;margin-top:2px;}}"
        ".fd-ext{display:inline-block;vertical-align:2px;"
        f"background:{WARNA_AKSEN};color:{WARNA_KARTU};font-size:10px;"
        "font-weight:800;border-radius:6px;padding:1px 6px;margin-right:7px;}"
        f".fd-more{{color:{WARNA_REDUP};font-size:12px;text-align:center;"
        "margin:2px 0 4px;}"
        f".fd-empty{{color:{WARNA_REDUP};font-size:13px;text-align:center;"
        "line-height:1.6;padding:14px 6px 10px;}"
        # ---- baris file -------------------------------------------------
        "body [class*='st-key-fd_row_']{"
        "background:rgba(255,255,255,.055)!important;"
        "border:1px solid rgba(255,255,255,.07)!important;"
        "border-radius:12px!important;padding:10px!important;"
        "margin:0 0 8px!important;}"
        "body [class*='st-key-fd_row_'] button{"
        "height:34px!important;min-height:34px!important;width:100%!important;"
        "padding:0!important;border-radius:10px!important;"
        f"background:rgba(255,255,255,.08)!important;color:{WARNA_TEKS}!important;"
        "border:1px solid rgba(255,255,255,.14)!important;"
        "box-shadow:none!important;}"
        "body [class*='st-key-fd_row_'] button:hover{"
        f"background:{WARNA_AKSEN}!important;color:{WARNA_KARTU}!important;"
        f"border-color:{WARNA_AKSEN}!important;}}"
        # ---- ponsel -----------------------------------------------------
        "@media(max-width:850px){"
        "body .st-key-fd_panel{width:calc(100vw - 24px)!important;"
        "right:12px!important;}"
        ".fd-bubble{font-size:12px;}}"
        "</style>"
    )


# ============================================================================
# PINTU MASUK
# ============================================================================
def render_file_dock() -> None:
    """Ikon folder melayang + gelembung penanda + kartu daftar file."""
    files = _files()
    terbuka = bool(st.session_state.get("file_dock_open"))
    dilihat = int(st.session_state.get("file_dock_seen", 0))
    baru = max(0, len(files) - dilihat)

    st.markdown(_css(terbuka), unsafe_allow_html=True)

    # Ikon folder: SELALU tampil. Membuka dok menandai semua file "dilihat".
    with st.container(key="fd_toggle"):
        if st.button(
            ":material/close:" if terbuka else ":material/folder_open:",
            key="fd_btn",
            help="Tutup daftar file" if terbuka else "File buatan Yuki",
        ):
            st.session_state["file_dock_open"] = not terbuka
            st.session_state["file_dock_seen"] = len(files)
            st.rerun()

    # Gelembung + titik merah: hanya saat ada file BARU dan dok tertutup.
    if baru and not terbuka:
        st.markdown(
            f'<div class="fd-dot">{baru}</div>'
            f'<div class="fd-bubble">{html.escape(TEKS_GELEMBUNG)}</div>',
            unsafe_allow_html=True,
        )

    if not terbuka:
        return

    with st.container(key="fd_panel"):
        st.markdown(
            '<div class="fd-title">File dari Yuki</div>'
            f'<div class="fd-sub">{len(files)} file di sesi ini</div>',
            unsafe_allow_html=True,
        )

        if not files:
            st.markdown(
                '<div class="fd-empty">Belum ada file.<br>'
                "Minta Yuki membuat kode atau dokumen,<br>"
                "nanti muncul di sini ya. 🐧</div>",
                unsafe_allow_html=True,
            )
            return

        for a in files[:MAKS_FILE_TAMPIL]:
            ext = (
                a["title"].rsplit(".", 1)[-1].upper()
                if "." in a["title"] else (a["lang"] or "TXT").upper()
            )
            with st.container(key=f"fd_row_{a['id']}"):
                info, aksi = st.columns([2.1, 1.4], gap="small")

                with info:
                    st.markdown(
                        f'<div class="fd-name"><span class="fd-ext">'
                        f'{html.escape(ext)}</span>'
                        f'{html.escape(a["title"])}</div>'
                        f'<div class="fd-meta">'
                        f'{len(a["content"].splitlines())} baris · '
                        f'{html.escape(a.get("time", ""))}</div>',
                        unsafe_allow_html=True,
                    )

                with aksi:
                    lihat, unduh = st.columns(2, gap="small")
                    with lihat:
                        with st.popover(
                            ":material/visibility:",
                            use_container_width=True,
                        ):
                            st.markdown(f"**{a['title']}**")
                            st.code(a["content"], language=a["lang"] or None)
                    with unduh:
                        st.download_button(
                            ":material/download:",
                            data=a["content"],
                            file_name=a["title"],
                            mime="text/plain",
                            key=f"fd_dl_{a['id']}",
                            use_container_width=True,
                        )

        if len(files) > MAKS_FILE_TAMPIL:
            st.markdown(
                f'<div class="fd-more">…dan {len(files) - MAKS_FILE_TAMPIL} '
                "file lain di sesi ini</div>",
                unsafe_allow_html=True,
            )
