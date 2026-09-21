# -*- coding: utf-8 -*-
"""
LAYOUT BARU: TOPBAR + 3 KOLOM + FOOTER BAR
==========================================

  ┌──────────────────────────────────────────────────────────────┐
  │  TOPBAR: [logo + "Trinity"] ................ [Tema|Profil|Keluar] │
  ├──────────────┬───────────────────────────────┬───────────────┤
  │  SIDEBAR     │       AREA CHAT UTAMA         │  PANEL KANAN  │
  │  KIRI (nav)  │  bubble AI/user + input pill  │  Fitur Cepat  │
  │              │                               │  Model AI     │
  │  Mascot      │                               │  Chat Terbaru │
  ├──────────────┴───────────────────────────────┴───────────────┤
  │  KETERANGAN / INFO TAMBAHAN                                  │
  └──────────────────────────────────────────────────────────────┘

PENTING — aturan pemetaan:
  * HANYA tata letak yang baru; warna tetap mengikuti palet aktif
    aplikasi (variabel --tr-* dari tampilan.py, dengan fallback
    warna bawaan).
  * Semua isi panel/topbar memakai fitur yang SUDAH ada:
    - Tombol Tema     = pengaturan "ui_palet" (tab Pengaturan > Tampilan)
    - Profil          = menu akun yang tadinya di dasar sidebar
    - Model AI        = katalog MODEL_CATALOG (config.py)
    - Chat Terbaru    = riwayat `conversations` (state.py)
    - Upload File     = lampiran pending_images (sama seperti menu ➕)
  * Tidak ada fitur baru yang ditambahkan (search bar / notifikasi
    sengaja tidak dibuat).
"""

from __future__ import annotations

import html
import time

import streamlit as st

from config import IMAGE_INPUT_TYPES, MODEL_CATALOG
from sidebar import go
from state import get_settings, open_conversation, reset_conversation
from ui_helpers import FOOTER_TEXT, logo_img_html

# Label provider untuk baris "Model AI" di panel kanan.
_PROV_LABEL = {
    "groq": "Groq",
    "plugsky": "Plugsky",
    "aion": "Aion Labs",
    "final_router": "Final Router",
    "openai": "OpenAI",
    "qwen": "Qwen",
    "deepseek": "DeepSeek",
    "meta": "Meta",
}


# ============================================================================
# CSS TATA LETAK BARU
#   Dipasang lewat render_topbar() supaya urutannya SETELAH styles.py,
#   sehingga aturan di sini menang bila bentrok.
# ============================================================================
_LAYOUT_CSS = """
<style>
/* ================= TOPBAR (bar atas, selebar layar) ================= */
.st-key-topbar {
    position: fixed !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    width: auto !important; max-width: none !important;
    height: 56px !important;
    margin: 0 !important;
    z-index: 1000001 !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 14px 0 18px !important;
    background: var(--tr-sidebar, #EDE2D1) !important;
    border-bottom: 1px solid var(--tr-border, #DBCEB9) !important;
    box-shadow: 0 1px 2px rgba(44, 31, 51, 0.04) !important;
}
.st-key-topbar > [data-testid="stVerticalBlock"] {
    display: contents !important;
}
.topbar-brand {
    flex: 1 1 auto; min-width: 0;
    display: flex; align-items: center; gap: 10px;
}
.topbar-title { display: flex; flex-direction: column; line-height: 1.12; }
.topbar-name {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.42rem; font-weight: 700;
    color: var(--tr-text, #2C1F33);
    letter-spacing: -0.02em;
}
.topbar-sub {
    font-size: 0.72rem; color: var(--tr-text2, #6B6172);
    letter-spacing: 0.05em;
}
.st-key-topbar [data-testid="stHorizontalBlock"] {
    flex: 0 0 auto; gap: 6px; align-items: center;
}
/* Tombol ikon di topbar: polos, hover lembut */
.st-key-topbar div.stButton > button,
.st-key-topbar button[data-testid="stPopoverButton"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    color: var(--tr-text2, #6B6172) !important;
    min-height: 36px !important;
}
.st-key-topbar div.stButton > button:hover,
.st-key-topbar button[data-testid="stPopoverButton"]:hover {
    background: var(--tr-surface, #F2E8D6) !important;
    color: var(--tr-text, #2C1F33) !important;
}
.st-key-topbar button p { font-size: 1.05rem !important; }

/* ============ OFFSET: sidebar & konten turun di bawah topbar ============ */
section[data-testid="stSidebar"] {
    top: 56px !important;
    height: calc(100% - 56px) !important;
}
/* tombol tutup sidebar: naik mendekati puncak sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > * {
    top: 13px !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: calc(56px + 1.2rem) !important;
    padding-bottom: calc(10rem + 30px) !important;
}

/* ================= FOOTER BAR (keterangan / info) ================= */
.trinity-footerbar {
    position: fixed; left: 0; right: 0; bottom: 0;
    height: 30px; z-index: 1000000;
    display: flex; align-items: center; justify-content: space-between;
    gap: 14px; padding: 0 16px;
    background: var(--tr-sidebar, #EDE2D1);
    border-top: 1px solid var(--tr-border, #DBCEB9);
    font-size: 0.72rem; color: var(--tr-text2, #6B6172);
    white-space: nowrap; overflow: hidden;
}
.trinity-footerbar .fb-kiri { overflow: hidden; text-overflow: ellipsis; }
.trinity-footerbar .fb-kanan { flex: 0 0 auto; }
/* dock input chat dinaikkan di atas footer bar */
[data-testid="stBottom"] { bottom: 30px !important; }
:root { --chat-lift: 42px !important; }

/* ================= PANEL KANAN (sidebar kanan) ================= */
/* Kontainer utama dilebarkan HANYA saat panel kanan ada (halaman chat),
   halaman lain tetap memakai lebar lama. */
html:has(.st-key-right_panel) [data-testid="stMainBlockContainer"] {
    max-width: 1150px !important;
}
/* kartu input digeser ke kiri supaya sejajar kolom chat */
html:has(.st-key-right_panel) { --chat-shift: -185px; }

.st-key-right_panel {
    position: sticky !important;
    top: 76px !important;
    align-self: flex-start !important;
    max-height: calc(100vh - 76px - 44px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 2px 2px 40px 2px !important;
}
.rp-card {
    background: var(--tr-surface, #F2E8D6);
    border: 1px solid var(--tr-border, #DBCEB9);
    border-radius: var(--tr-radius, 14px);
    padding: 12px 12px 10px;
    margin-bottom: 14px;
}
.rp-title {
    font-size: 0.74rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase;
    color: var(--tr-text2, #6B6172);
    margin: 0 0 8px 2px;
}
/* tombol di panel kanan: rata kiri, dua baris (pre-line) */
.st-key-right_panel div.stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    padding: 5px 10px !important;
    color: var(--tr-text, #2C1F33) !important;
}
.st-key-right_panel div.stButton > button:hover {
    background: var(--tr-bg, #E8DCC8) !important;
    border-color: var(--tr-border, #DBCEB9) !important;
}
.st-key-right_panel div.stButton > button p {
    white-space: pre-line !important;
    line-height: 1.28 !important;
    font-size: 0.87rem !important;
}
/* tombol model yang sedang dipakai */
.st-key-right_panel div.stButton > button.rp-aktif {
    background: var(--tr-surface, #F2E8D6) !important;
    border-color: var(--tr-border, #DBCEB9) !important;
    font-weight: 600;
}

/* ================= INPUT PILL + TOMBOL KIRIM BULAT ================= */
[data-testid="stBottomBlockContainer"] {
    border-radius: 26px !important;
}
[data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] button {
    border-radius: 999px !important;
    min-width: 38px !important;
    height: 38px !important;
    width: 38px !important;
}

/* ================= RESPONSIF ================= */
@media (max-width: 1080px) {
    .st-key-right_panel { display: none !important; }
    html:has(.st-key-right_panel) { --chat-shift: 0px; }
    html:has(.st-key-right_panel) [data-testid="stMainBlockContainer"] {
        max-width: 768px !important;
    }
}
@media (max-width: 640px) {
    .trinity-footerbar { display: none !important; }
    [data-testid="stBottom"] { bottom: 0 !important; }
    .topbar-sub { display: none; }
    .topbar-name { font-size: 1.2rem; }
}
</style>
"""


# ============================================================================
# TOPBAR
# ============================================================================
def render_topbar() -> None:
    """Bar paling atas: brand kiri + kontrol kanan (Tema, Profil, Keluar)."""
    st.markdown(_LAYOUT_CSS, unsafe_allow_html=True)

    with st.container(key="topbar"):
        # ---- KIRI: logo + tulisan besar "Trinity" + subjudul ----
        st.markdown(
            '<div class="topbar-brand">'
            + logo_img_html("topbar-logo")
            + '<div class="topbar-title">'
            + '<div class="topbar-name">Trinity</div>'
            + '<div class="topbar-sub">Room Chat AI</div>'
            + '</div></div>',
            unsafe_allow_html=True,
        )

        # ---- KANAN: Tema · Profil · Keluar ----
        c_tema, c_profil, c_keluar = st.columns([1, 1, 0.72])
        with c_tema:
            _popover_tema()
        with c_profil:
            _popover_profil()
        with c_keluar:
            if st.button(":material/logout:", key="topbar_keluar",
                         use_container_width=True, help="Keluar"):
                st.session_state.logged_out = True
                go("chat")


def _popover_tema() -> None:
    """Pemilih tema warna cepat (pengaturan ui_palet yang sudah ada)."""
    from tampilan import DEFAULT_PALET, PALET_NAMES

    with st.popover(":material/palette:", use_container_width=True,
                    help="Tema warna tampilan"):
        s = get_settings()
        aktif = s.get("ui_palet") or DEFAULT_PALET
        pilihan = st.radio(
            "Tema warna", PALET_NAMES,
            index=PALET_NAMES.index(aktif) if aktif in PALET_NAMES else 0,
            key="topbar_palet", label_visibility="collapsed",
        )
        if pilihan != aktif:
            merged = dict(st.session_state.get("settings") or {})
            merged["ui_palet"] = pilihan
            st.session_state.settings = merged
            st.rerun()
        st.caption("Pilihan lengkap (sudut, wallpaper) ada di "
                   "Pengaturan → Tampilan.")


def _popover_profil() -> None:
    """Profil akun + tautan halaman (menempatkan ulang menu akun lama)."""
    with st.popover(":material/account_circle:", use_container_width=True,
                    help="Akun"):
        s = get_settings()
        name = (s.get("display_name") or "User").strip() or "User"
        plan = s.get("plan") or "Free"
        initial = html.escape(name[0].upper())
        st.markdown(
            '<div class="sb-account" style="margin:2px 0 10px;">'
            f'<div class="ava">{initial}</div>'
            f'<div class="name">{html.escape(name)} '
            f'<span class="plan">&middot; {html.escape(plan)}</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button(":material/settings:  Pengaturan", key="tp_pengaturan",
                     use_container_width=True):
            go("pengaturan")
        if st.button(":material/translate:  Bahasa", key="tp_bahasa",
                     use_container_width=True):
            go("bahasa")
        if st.button(":material/help:  Dapatkan bantuan", key="tp_bantuan",
                     use_container_width=True):
            go("bantuan")
        if st.button(":material/workspace_premium:  Tingkatkan paket",
                     key="tp_pro", use_container_width=True):
            go("tingkatkan")
        if st.button(":material/phone_iphone:  Dapatkan aplikasi",
                     key="tp_app", use_container_width=True):
            go("aplikasi")
        if st.button(":material/school:  Trinity kursus", key="tp_kursus",
                     use_container_width=True):
            go("kursus")
        if st.button(":material/menu_book:  Pelajari lebih lanjut",
                     key="tp_pelajari", use_container_width=True):
            go("pelajari")


# ============================================================================
# FOOTER BAR
# ============================================================================
def render_footer_bar() -> None:
    """Bar keterangan di paling bawah (info tambahan, memakai teks lama)."""
    keterangan = (
        "Yuki adalah AI dan bisa membuat kesalahan. "
        "Harap periksa kembali respons."
    )
    st.markdown(
        '<div class="trinity-footerbar">'
        f'<span class="fb-kiri">ℹ️ {html.escape(keterangan)}</span>'
        f'<span class="fb-kanan">{html.escape(FOOTER_TEXT)}</span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ============================================================================
# PANEL KANAN
# ============================================================================
def render_right_sidebar() -> None:
    """Panel kanan pada halaman chat: Fitur Cepat · Model AI · Chat Terbaru."""
    with st.container(key="right_panel"):

        # ---------- FITUR CEPAT ----------
        with st.container(key="rp_card_cepat"):
            st.markdown('<div class="rp-card"><div class="rp-title">'
                        'Fitur Cepat</div>', unsafe_allow_html=True)

            r1a, r1b = st.columns(2)
            with r1a:
                if st.button(":material/add:  Chat Baru", key="rp_new",
                             use_container_width=True):
                    reset_conversation()
                    st.rerun()
            with r1b:
                if st.button(":material/chat_bubble:  Chat AI", key="rp_chat",
                             use_container_width=True):
                    st.session_state.image_mode = False
                    st.rerun()

            r2a, r2b = st.columns(2)
            with r2a:
                if st.button(":material/groups:  Multi AI", key="rp_multi",
                             use_container_width=True):
                    go("multi_agent")
            with r2b:
                if st.button(":material/image:  Generate Gambar",
                             key="rp_img", use_container_width=True):
                    st.session_state.image_mode = True
                    st.rerun()

            with st.popover(":material/attach_file:  Upload File",
                            key="rp_upload_pop", use_container_width=True):
                _upload_file_popover()

            st.markdown('</div>', unsafe_allow_html=True)

        # ---------- MODEL AI ----------
        with st.container(key="rp_card_model"):
            st.markdown('<div class="rp-card"><div class="rp-title">'
                        'Model AI</div>', unsafe_allow_html=True)
            _daftar_model()
            st.markdown('</div>', unsafe_allow_html=True)

        # ---------- CHAT TERBARU ----------
        with st.container(key="rp_card_riwayat"):
            st.markdown('<div class="rp-card"><div class="rp-title">'
                        'Chat Terbaru</div>', unsafe_allow_html=True)
            _chat_terbaru()
            st.markdown('</div>', unsafe_allow_html=True)


def _upload_file_popover() -> None:
    """Unggah lampiran dari panel kanan (masuk ke pending_images, seperti menu ➕)."""
    from chat_handlers import _make_square_preview

    picked = st.file_uploader(
        "Pilih gambar", type=IMAGE_INPUT_TYPES,
        accept_multiple_files=True, key="rp_uploader",
        label_visibility="collapsed",
    )
    if not picked:
        return
    ready = [
        im for im in st.session_state.get("pending_images", [])
        if im.get("status") != "loading"
    ]
    seen = {(im.get("name"), len(im.get("data") or b"")) for im in ready}
    tambah = 0
    for f in picked:
        try:
            raw = f.getvalue()
        except Exception:
            continue
        if not raw:
            continue
        kunci = (f.name, len(raw))
        if kunci in seen:
            continue
        thumb, tmime = _make_square_preview(raw)
        mime = (getattr(f, "type", "") or "image/png").lower()
        if not mime.startswith("image/"):
            mime = "image/png"
        ready.append({
            "name": f.name, "data": raw, "mime": mime,
            "preview": thumb, "preview_mime": tmime, "status": "ready",
        })
        seen.add(kunci)
        tambah += 1
    if tambah:
        st.session_state.pending_images = ready
        st.toast(f"{tambah} lampiran siap dikirim bersama pesanmu.",
                 icon=":material/attach_file:")
        st.rerun()


def _label_provider(m: dict) -> str:
    """Nama tampilan provider sebuah model dari katalog."""
    prov = m.get("provider")
    if not prov:
        prov = (m.get("id") or "").split("/")[0] or "groq"
    return _PROV_LABEL.get(prov, str(prov).capitalize())


def _daftar_model() -> None:
    """Daftar model dari MODEL_CATALOG — klik untuk memakainya."""
    from chat_handlers import _boleh_premium, _dialog_premium

    terpilih = st.session_state.get("selected_model_key")
    for m in MODEL_CATALOG:
        if m.get("chat_selectable") is False:
            continue
        nama = m["name"]
        baris2 = f"{_label_provider(m)} · {'Premium' if m.get('premium') else 'Free'}"
        tanda = "◉ " if m["key"] == terpilih else ""
        if st.button(
            f"{tanda}**{nama}**\n{baris2}",
            key=f"rp_model_{m['key']}",
            use_container_width=True,
        ):
            if m.get("premium") and not _boleh_premium():
                _dialog_premium()
            else:
                st.session_state.selected_model_key = m["key"]
                st.rerun()


def _waktu_relatif(ts) -> str:
    """'2 menit yang lalu' dari stempel waktu percakapan."""
    try:
        detik = time.time() - float(ts)
    except (TypeError, ValueError):
        return ""
    if detik < 0:
        return ""
    if detik < 60:
        return "baru saja"
    if detik < 3600:
        return f"{int(detik // 60)} menit yang lalu"
    if detik < 86400:
        return f"{int(detik // 3600)} jam yang lalu"
    return f"{int(detik // 86400)} hari yang lalu"


def _chat_terbaru() -> None:
    """Beberapa percakapan terakhir dari riwayat (conversations)."""
    convs = st.session_state.get("conversations") or []
    if not convs:
        st.caption("Belum ada percakapan.")
        return
    for c in convs[:4]:
        judul = " ".join(str(c.get("title") or "Percakapan").split())
        if len(judul) > 34:
            judul = judul[:34] + "…"
        waktu = _waktu_relatif(c.get("ts"))
        label = f"💬 {judul}\n{waktu}" if waktu else f"💬 {judul}"
        if st.button(label, key=f"rp_conv_{c['id']}",
                     use_container_width=True):
            open_conversation(c["id"])
            st.rerun()
