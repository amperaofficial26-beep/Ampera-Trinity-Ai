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
