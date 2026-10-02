# -*- coding: utf-8 -*-
"""
PENYESUAIAN TAMPILAN UNTUK LAYAR MOBILE

Di layar kecil, sidebar kiri dan panel kanan (rel fitur di chat, panel
"Pengaturan gambar" di halaman AI Gambar) saling menumpuk dan menutupi isi
halaman. Berkas ini mengumpulkan SEMUA penyesuaian mobile di satu tempat:

  * isi halaman memakai lebar penuh (tidak lagi disisakan ruang untuk panel);
  * sidebar kiri jadi lapisan mengambang yang bisa dibuka/tutup lewat tombol
    bawaan Streamlit;
  * panel kanan disembunyikan di luar layar dan baru meluncur masuk saat
    tombol bulat di pojok kanan bawah ditekan;
  * saat panel terbuka, ada kain gelap di belakangnya supaya jelas mana yang
    sedang aktif.

>>> SEMUA ANGKA YANG BOLEH DIUBAH ADA DI BAGIAN KONSTANTA DI BAWAH <<<
"""
from __future__ import annotations

import streamlit as st

# ============================================================================
# >>> ATUR DI SINI <<<
#   MOBILE_BP       : lebar layar (px) di mana mode mobile mulai berlaku.
#   PANEL_LEBAR_VW  : lebar panel kanan saat terbuka (persen lebar layar).
#   PANEL_LEBAR_MAX : batas maksimal lebar panel kanan (px).
#   FAB_KANAN/BAWAH : posisi tombol bulat pembuka panel (px).
#   HALAMAN_BERPANEL: halaman yang punya panel kanan (tombol hanya muncul
#                     di halaman-halaman ini).
# ============================================================================
MOBILE_BP = 820
PANEL_LEBAR_VW = 86
PANEL_LEBAR_MAX = 320
FAB_KANAN = 14
FAB_BAWAH = 108
HALAMAN_BERPANEL = ("chat", "image")

# Kunci session_state untuk keadaan buka/tutup panel kanan.
_STATE = "mobile_panel_open"

# Semua panel kanan yang dikenal di aplikasi ini.
_PANEL = (
    '.st-key-chat_right_rail',
    '.st-key-aiimg_panel',
)


# Layout yang di desktop menyembunyikan tombol sidebar — harus dilawan
# satu per satu supaya spesifisitas CSS-nya menang.
_LAYOUT = (
    ".tr-chat-layout",
    ".tr-multi-ai-layout",
    ".aiimg-page-shell",
)

# Semua nama tombol buka/tutup sidebar di berbagai versi Streamlit.
_TOMBOL_SB = (
    '[data-testid="stSidebarCollapsedControl"]',
    '[data-testid="collapsedControl"]',
    '[data-testid="stExpandSidebarButton"]',
    '[data-testid="stSidebarCollapseButton"]',
    'button[kind="headerNoPadding"]',
)


def _tombol_sidebar_css() -> str:
    """CSS yang memaksa tombol buka/tutup sidebar muncul di mobile."""
    sel = []
    for t in _TOMBOL_SB:
        sel.append("body .stApp " + t)
        for lay in _LAYOUT:
            sel.append("body .stApp:has(" + lay + ") " + t)
    tampil = (
        ",".join(sel) + "{"
        "display:flex!important;visibility:visible!important;"
        "opacity:1!important;pointer-events:auto!important;"
        "z-index:1000002!important;}"
    )
    # Tombol "buka" (saat sidebar tertutup) dipaku di pojok kiri atas.
    buka = []
    for t in _TOMBOL_SB[:3]:
        buka.append("body .stApp " + t)
        for lay in _LAYOUT:
            buka.append("body .stApp:has(" + lay + ") " + t)
    paku = (
        ",".join(buka) + "{"
        "position:fixed!important;top:10px!important;left:10px!important;"
        "right:auto!important;"
        "align-items:center!important;justify-content:center!important;"
        "width:42px!important;height:42px!important;"
        "border-radius:12px!important;"
        "background:#F2E8D6!important;"
        "box-shadow:0 6px 18px rgba(76,58,43,.18)!important;}"
    )
    return tampil + paku


def _sel(akhiran: str = "") -> str:
    """Gabungkan daftar panel jadi satu selektor CSS."""
    return ",".join(p + akhiran for p in _PANEL)


def inject_mobile_css() -> None:
    """Pasang seluruh penyesuaian mobile. Panggil sesudah inject_css()."""
    buka = bool(st.session_state.get(_STATE))
    lebar = f"min({PANEL_LEBAR_VW}vw, {PANEL_LEBAR_MAX}px)"

    css = (
        "<style>"
        f"@media (max-width: {MOBILE_BP}px){{"

        # ---------- 0. SETEL ULANG VARIABEL UKURAN DASHBOARD ----------
        # part07/part09 menghitung posisi topbar, isi, dan input chat dari
        # variabel ini. Di mobile semuanya dinolkan supaya tidak ada lagi
        # ruang yang disisakan untuk sidebar & panel kanan.
        ".stApp,"
        ".stApp:has(.tr-chat-layout),"
        ".stApp:has(.tr-multi-ai-layout),"
        ".stApp:has(.aiimg-page-shell){"
        "--dash-sidebar:0px;"
        "--dash-rail:0px;"
        "--dash-gap:10px;"
        "--dash-top:8px;"
        "--dash-bottom:8px;"
        "--dash-center-left:10px;"
        "--dash-center-right:10px;"
        "--dash-center-width:calc(100vw - 20px);"
        "--dash-content-width:calc(100vw - 20px);"
        "--chat-width:calc(100vw - 20px);"
        "--chat-shift:0px;"
        "--tr-sidebar-width:0px;"
        "--tr-right-width:0px;"
        "--tr-gap:10px;"
        "--aiimg-panel-w:0px;}"

        # Input chat: lebar penuh, tanpa geseran sisa hitungan desktop.
        'body .stApp [data-testid="stBottom"],'
        'body .stApp [data-testid="stBottomBlockContainer"]{'
        "transform:none!important;"
        "width:100%!important;max-width:100%!important;"
        "margin-left:0!important;margin-right:0!important;}"

        # Sapaan besar di beranda dikecilkan agar tidak terpotong.
        "body .stApp .trinity-greeting{"
        "margin-top:10vh!important;text-align:center!important;}"
        "body .stApp .trinity-greeting h1,"
        "body .stApp .trinity-greeting h2,"
        "body .stApp .trinity-greeting .greet-title{"
        "font-size:clamp(1.5rem,7vw,2.1rem)!important;"
        "line-height:1.2!important;word-break:normal!important;}"

        # ---------- 1. ISI HALAMAN MEMAKAI LEBAR PENUH ----------
        'body .stApp [data-testid="stMainBlockContainer"],'
        'body .stApp .stMainBlockContainer{'
        "width:100%!important;max-width:none!important;"
        "margin:0!important;"
        "padding:76px 12px 132px!important;}"

        'body .stApp [data-testid="stBottomBlockContainer"]{'
        "width:100%!important;max-width:none!important;"
        "margin-left:0!important;margin-right:0!important;"
        "padding-left:8px!important;padding-right:8px!important;}"

        # Topbar chat ikut melebar, tidak lagi menyisakan ruang panel.
        "body .stApp .st-key-chat_topbar,"
        "body .stApp:has(.tr-chat-layout) .st-key-chat_topbar{"
        "left:62px!important;right:10px!important;top:8px!important;"
        "width:auto!important;max-width:none!important;"
        "padding:6px!important;}"

        # ---------- 2. SIDEBAR JADI LAPISAN MENGAMBANG ----------
        'body .stApp section[data-testid="stSidebar"],'
        'body .stApp:has(.tr-chat-layout) section[data-testid="stSidebar"],'
        'body .stApp:has(.tr-multi-ai-layout) section[data-testid="stSidebar"],'
        'body .stApp:has(.aiimg-page-shell) section[data-testid="stSidebar"]{'
        "position:fixed!important;top:0!important;bottom:0!important;"
        "left:0!important;z-index:1000000!important;"
        "width:min(84vw,300px)!important;"
        "min-width:min(84vw,300px)!important;"
        "max-width:min(84vw,300px)!important;"
        "transition:transform .26s cubic-bezier(.22,1,.36,1)!important;"
        "box-shadow:0 0 44px rgba(46,32,64,.28)!important;}"
        # Isi sidebar ikut melebar supaya tulisannya tidak menumpuk vertikal.
        'body .stApp section[data-testid="stSidebar"] > div,'
        'body .stApp section[data-testid="stSidebar"] [data-testid="stSidebarContent"],'
        'body .stApp section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{'
        "width:100%!important;min-width:0!important;max-width:100%!important;}"
        # Saat ditutup, sidebar benar-benar keluar layar.
        'body .stApp section[data-testid="stSidebar"][aria-expanded="false"]{'
        "transform:translateX(-102%)!important;"
        "box-shadow:none!important;}"
        # Konten utama tidak pernah digeser oleh sidebar.
        'body .stApp [data-testid="stMain"],'
        'body .stApp [data-testid="stAppViewContainer"] > section:last-child{'
        "margin-left:0!important;width:100%!important;max-width:100%!important;}"
        # Tombol buka/tutup sidebar bawaan Streamlit WAJIB terlihat.
        # Di desktop, part07_dashboard_layout.py sengaja menyembunyikannya
        # (sidebar selalu terbuka), jadi di sini selektornya dibuat lebih
        # kuat: body + .stApp:has(<layout>) supaya menang di cascade.
        + _tombol_sidebar_css() +

        # Halaman yang memang tanpa sidebar (Tingkatkan paket, Dapatkan
        # aplikasi, Tentang kami): tombolnya tidak perlu muncul.
        '.stApp:has(.upgrade-page-shell) [data-testid="stSidebarCollapsedControl"],'
        '.stApp:has(.appdl-page-shell) [data-testid="stSidebarCollapsedControl"],'
        '.stApp:has(.about-page-shell) [data-testid="stSidebarCollapsedControl"],'
        '.stApp:has(.upgrade-page-shell) [data-testid="collapsedControl"],'
        '.stApp:has(.appdl-page-shell) [data-testid="collapsedControl"],'
        '.stApp:has(.about-page-shell) [data-testid="collapsedControl"]{'
        "display:none!important;}"

        # ---------- 3. PANEL KANAN JADI LACI GESER ----------
        + _sel() + "{"
        "position:fixed!important;top:0!important;bottom:0!important;"
        "right:0!important;left:auto!important;"
        f"width:{lebar}!important;max-width:{lebar}!important;"
        "min-height:0!important;height:auto!important;"
        "max-height:none!important;"
        "margin:0!important;border-radius:18px 0 0 18px!important;"
        "overflow-y:auto!important;"
        "z-index:999999!important;"
        "transform:translateX(104%);"
        "transition:transform .28s cubic-bezier(.22,1,.36,1);"
        "box-shadow:-10px 0 40px rgba(46,32,64,.26)!important;}"

        # Keadaan TERBUKA (ditandai penanda .tr-panel-open di halaman).
        ".stApp:has(.tr-panel-open) " + _sel() + "{"
        "transform:translateX(0);}"

        # Kain gelap di belakang panel.
        ".stApp:has(.tr-panel-open) .tr-panel-open{"
        "position:fixed!important;inset:0!important;"
        "display:block!important;"
        "background:rgba(32,22,46,.45)!important;"
        "backdrop-filter:blur(2px);"
        "z-index:999998!important;}"

        # ---------- 4. TOMBOL BULAT PEMBUKA PANEL ----------
        'body .stApp [class*="st-key-mobile_panel_fab"]{'
        "position:fixed!important;"
        f"right:{FAB_KANAN}px!important;bottom:{FAB_BAWAH}px!important;"
        "left:auto!important;top:auto!important;"
        "width:auto!important;margin:0!important;"
        "z-index:1000001!important;}"
        'body .stApp [class*="st-key-mobile_panel_fab"] button{'
        "min-height:46px!important;padding:0 16px!important;"
        "border-radius:999px!important;"
        "background:#4A3559!important;color:#FFF6E9!important;"
        "border:1px solid #3A2A4C!important;font-weight:700!important;"
        "box-shadow:0 10px 26px rgba(46,32,64,.34)!important;}"

        # ---------- 5. RAPIKAN SISA ELEMEN ----------
        # Kartu & grid yang dipaksa lebar di desktop dikembalikan normal.
        'body .stApp [data-testid="stHorizontalBlock"]{'
        "flex-wrap:wrap!important;gap:10px!important;}"
        'body .stApp [data-testid="stColumn"]{'
        "min-width:0!important;flex:1 1 100%!important;}"

        "}"        # tutup @media

        # Penanda panel: di layar besar tidak pernah tampil.
        ".tr-panel-open{display:none;}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)

    if buka:
        st.markdown('<div class="tr-panel-open"></div>',
                    unsafe_allow_html=True)


def _toggle() -> None:
    st.session_state[_STATE] = not st.session_state.get(_STATE)


def render_panel_toggle(page: str | None = None) -> None:
    """Tombol bulat pembuka/penutup panel kanan (hanya tampak di mobile).

    CSS-lah yang menyembunyikannya di layar besar, jadi tidak perlu tahu
    ukuran layar dari sisi Python.
    """
    page = page if page is not None else st.session_state.get("page", "chat")
    if page not in HALAMAN_BERPANEL:
        # Panel tertutup lagi saat pindah ke halaman tanpa panel.
        st.session_state[_STATE] = False
        return

    buka = bool(st.session_state.get(_STATE))
    label = (":material/close:  Tutup panel" if buka
             else ":material/tune:  Panel")
    with st.container(key="mobile_panel_fab"):
        st.button(label, key="mobile_panel_fab_btn", on_click=_toggle)

    # Di layar besar tombolnya tidak perlu ada sama sekali.
    st.markdown(
        "<style>"
        f"@media (min-width: {MOBILE_BP + 1}px){{"
        'body .stApp [class*="st-key-mobile_panel_fab"]{display:none!important;}'
        "}</style>",
        unsafe_allow_html=True,
    )
