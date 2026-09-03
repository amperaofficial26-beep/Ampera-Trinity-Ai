# -*- coding: utf-8 -*-
"""CSS — TEMA TRINITY (beige + ungu).

Seluruh gaya visual aplikasi tinggal di file ini; app.py cukup memanggil
inject_css(). Dipisah dari app.py supaya tidak terlalu panjang.
"""
import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ========= PALET WARNA TRINITY (beige + ungu) =========
   Latar halaman  : #E8DCC8 (warm beige)
   Permukaan      : #F2E8D6 (beige terang, untuk kartu)
   Gelembung user : #E0D2BB / #E5D8C3
   Teks utama     : #2C1F33 (Deep Violet)
   Teks sekunder  : #6B6172
   Aksen          : #2C1F33 (Deep Violet) / ikon & teks aksen #4A3559
   Border         : #DBCEB9
======================================================= */

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #E8DCC8 !important;
    color: #2C1F33;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ---------- SIDEBAR ala Claude ---------- */
section[data-testid="stSidebar"] {
    background: #EDE2D1 !important;
    border-right: 1px solid #DBCEB9 !important;
    width: 230px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.4rem 0.7rem 0.5rem;
}
/* konten sidebar DIPENTOK KE ATAS: buang ruang kosong bawaan di atasnya */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    padding: 0 !important;
    min-height: 0 !important;
    height: 0 !important;
}
/* tombol tutup sidebar — ikon Material, melayang di pojok */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > * {
    position: absolute;
    top: 25px; right: -38px;
    z-index: 10;
}
[data-testid="stSidebarCollapseButton"] button {
    color: #6B6172 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] svg {
    display: none !important;
}
[data-testid="stSidebarCollapseButton"] button::before {
    content: "left_panel_close";
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", sans-serif;
    font-size: 22px;
    line-height: 1;
    color: #6B6172;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}
/* tombol buka sidebar (saat tertutup) — ikon hamburger Material */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #2C1F33 !important;
    z-index: 999990 !important;
}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    color: #2C1F33 !important;
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"],
[data-testid="collapsedControl"] [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg {
    display: none !important;
}
[data-testid="stSidebarCollapsedControl"] button::before,
[data-testid="collapsedControl"] button::before,
[data-testid="stExpandSidebarButton"]::before {
    content: "menu";
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", sans-serif;
    font-size: 22px;
    line-height: 1;
    color: #2C1F33;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
}
[data-testid="stExpandSidebarButton"],
button[kind="headerNoPadding"] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #2C1F33 !important;
}
[data-testid="stHeader"] {
    visibility: visible !important;
    pointer-events: auto !important;
}

/* judul brand serif ala "Claude" — rapat ke atas, besar */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.5rem; font-weight: 700; color: #1B1220;
    letter-spacing: -0.02em;
    padding: 0 6px 8px;
    margin-top: 0;
    line-height: 1.1;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude)
   → teks & ikon DIPERBESAR, tinggi baris DIRAPATKAN */
section[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 3px 10px !important;
    min-height: 30px !important;
    line-height: 1.2 !important;
    color: #2C1F33 !important;
    font-size: 1.06rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #E2D6C1 !important;
    border: none !important;
    box-shadow: none !important;
    color: #2C1F33 !important;
}
/* paksa SEMUA lapisan dalam tombol rata kiri (markdown container ikut) */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 1.06rem !important;
    line-height: 1.25 !important;
    color: #2C1F33 !important;
    margin: 0 !important;
}
/* ikon Material di tombol sidebar: sengaja LEBIH BESAR dari teksnya.
   Streamlit memberi span ikon ini fontSize + width + height dari token
   iconSizes (default `base` = 1rem), jadi ketiganya harus dinaikkan
   bersama-sama agar glyph tidak meluber keluar kotaknya. */
section[data-testid="stSidebar"] div.stButton > button [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] div.stDownloadButton > button [data-testid="stIconMaterial"] {
    font-size: 1.35rem !important;
    width: 1.35rem !important;
    height: 1.35rem !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
}
/* tombol "+ Baru" menonjol sedikit (latar krem seperti Claude) */
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #E2D6C1 !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #DBCEB9 !important;
}

/* label grup riwayat: "Hari ini" abu kecil */
.sb-group {
    font-size: 0.85rem; font-weight: 500; color: #7D7484;
    padding: 11px 12px 3px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button {
    font-weight: 400 !important;
    color: #4E4553 !important;
    min-height: 30px !important;
    padding: 3px 10px !important;
    line-height: 1.2 !important;
    position: relative;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button::before {
    content: "";
    width: 9px; height: 9px;
    border: 1.5px solid #C1B49F;
    border-radius: 50%;
    margin-right: 11px;
    flex-shrink: 0;
    display: inline-block;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button p {
    font-size: 1.06rem !important;
    line-height: 1.25 !important;
    font-weight: 400 !important;
    color: #4E4553 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 168px;
}
/* item riwayat aktif */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #E2D6C1 !important;
}

/* tombol unduh di sidebar: sama polosnya dengan menu lain */
section[data-testid="stSidebar"] div.stDownloadButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 3px 10px !important;
    min-height: 30px !important;
    line-height: 1.2 !important;
    color: #2C1F33 !important;
    font-size: 1.06rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button > div,
section[data-testid="stSidebar"] div.stDownloadButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button:hover {
    background: #E2D6C1 !important;
    border: none !important;
    color: #2C1F33 !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button p {
    text-align: left !important;
    font-size: 1.06rem !important;
    line-height: 1.25 !important;
    color: #2C1F33 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #DBCEB9; margin: 4px 2px;
}

/* baris kartu nama user ala Claude — DIPAKU di dasar layar, selebar sidebar (230px) */
.sb-account {
    position: fixed;
    bottom: 0; left: 0;
    width: 230px !important;              /* = persis selebar sidebar */
    max-width: 230px !important;
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px 12px;
    padding-right: 42px;                  /* ruang untuk tombol menu ⋯ */
    border-top: 1px solid #DBCEB9 !important;
    background: #EDE2D1 !important;
    z-index: 999995;
    box-sizing: border-box;
    pointer-events: none;                 /* teksnya saja; tombol di sebelahnya */
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 70px !important;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E0D2BB; color: #4E4553;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #CDBFA8;
}
.sb-account .name {
    font-size: 0.95rem;
    font-weight: 600;
    color: #2C1F33;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 135px;
}
.sb-account .plan { font-size: 0.85rem; color: #7E7387; font-weight: 400; }
.sb-account .caret { color: #7E7387; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #6B6172; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar (0 = benar-benar rapat;
   ruang antar baris menu cukup datang dari padding tombolnya sendiri) */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

/* scrollbar halus ala Claude */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CDBFA8; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #B7A88F; }

::selection { background: rgba(44,31,51,0.25); }

/* ---------- header app (minimal, serif ala Claude) ---------- */
.trinity-head {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; padding: 4px 0 2px; margin-bottom: 6px;
}
.trinity-logo {
    width: 34px; height: 34px; border-radius: 10px;
    display: grid; place-items: center; font-size: 17px;
    background: #2C1F33; color: #FFFFFF;
    flex-shrink: 0;
}
.trinity-head h1 {
    margin: 0;
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
    font-size: 0.90rem; font-weight: 600;
    color: #2C1F33; letter-spacing: -0.01em;
}
.trinity-head p {
    margin: 0; color: #6B6172; font-size: 0.78rem; font-weight: 400;
}
.trinity-sub {
    text-align: center; color: #6B6172; font-size: 0.8rem;
    margin: 0 0 22px;
}

/* sapaan besar serif ala halaman awal Claude */
.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2.5rem; font-weight: 500; color: #2C1F33;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #2C1F33; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 12px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 4px 0 22px; }

/* ---------- jarak antar pesan: rapat & konsisten ala Claude ---------- */
/* Streamlit menambah spasi sendiri antar elemen (gap 1rem antar container
   + hack margin -1rem pada markdown) sehingga jarak antar bubble membengkak
   dan tidak menentu. Dimatikan total di area chat — jarak sepenuhnya
   dikendalikan margin .bubble-row di atas agar rapat seperti Claude. */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
[data-testid="stMainBlockContainer"] .element-container {
    margin: 0 !important;
}
[data-testid="stMarkdownContainer"] {
    margin: 0 !important;
}
/* elemen mode gambar tetap diberi jarak wajar */
[data-testid="stMainBlockContainer"] div.stDownloadButton {
    margin: 6px 0 18px !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stImage"] {
    margin: 0 !important;
}

.bubble {
    font-size: 0.965rem; line-height: 1.65;
    word-break: break-word; overflow-wrap: anywhere;
    white-space: pre-wrap;
}
.bubble.user {
    max-width: 78%;
    background: #E0D2BB;
    color: #2C1F33;
    border-radius: 18px;
    padding: 11px 16px;
    border: 1px solid rgba(44,31,51,0.05);
}
/* AI: teks polos di atas latar — persis gaya Claude */
.bubble.ai {
    max-width: 100%;
    background: transparent;
    color: #2C1F33;
    padding: 0 2px;
    border: none;
}
.bubble-meta {
    font-size: 0.7rem; color: #7E7387;
    margin: 0 4px 4px; font-weight: 500;
}
.bubble-wrap { display: flex; flex-direction: column; max-width: 78%; }
.bubble-row.ai .bubble-wrap { max-width: 100%; }
.bubble-row.user .bubble-wrap { align-items: flex-end; }
.bubble-wrap .bubble { max-width: 100%; }

/* lampiran gambar di bubble user (thumbnail rapi ala Claude) */
.bubble-imgs {
    display: flex; flex-wrap: wrap; gap: 6px;
    justify-content: flex-end; margin-top: 8px;
}
.bubble-img {
    max-width: 180px; max-height: 180px;
    border-radius: 12px; display: block;
    border: 1px solid rgba(44,31,51,0.08);
}

/* ---------- baris aksi kecil di bawah jawaban Yuki (ala Claude) ---------- */
.msg-action-btn {
    background: transparent; border: none; cursor: pointer;
    color: #7E7387; font-size: 0.95rem; line-height: 1;
    padding: 4px 6px; border-radius: 8px;
    transition: background .15s ease, color .15s ease;
}
.msg-action-btn:hover { background: #E2D6C1; color: #4E4553; }
[class*="st-key-msg_actions_"] { margin: -4px 0 4px !important; }
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] {
    gap: 0 !important; align-items: center !important;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2),
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
    margin-top: -18px !important;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 2px !important;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 28px !important;
    max-width: 40px !important;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
    flex: 1 1 auto !important;
    max-width: none !important;
    min-width: 0 !important;
}
[class*="st-key-msg_actions_"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 6px !important;
    min-height: 26px !important;
    height: 26px !important;
    font-size: 0.85rem !important;
    color: #7E7387 !important;
}
[class*="st-key-msg_actions_"] div.stButton > button:hover {
    background: #E2D6C1 !important;
    border: none !important;
    box-shadow: none !important;
}
/* LAPISAN TAMBAHAN: beberapa versi Streamlit menaruh latar putih di elemen
   dalam tombol (style emotion) atau memberi class key per tombol — paksa
   transparan semuanya supaya baris feedback benar-benar polos tanpa kotak. */
[class*="st-key-msg_actions_"] [data-testid^="stBaseButton"],
[class*="st-key-fb_up_"] button, [class*="st-key-fb_down_"] button,
[class*="st-key-msg_actions_"] div.stButton > button > div,
[class*="st-key-fb_up_"] button > div, [class*="st-key-fb_down_"] button > div,
[class*="st-key-msg_actions_"] div.stButton > button p,
[class*="st-key-msg_actions_"] [data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ---------- ikon SVG garis tipis ala Claude (stroke = warna teks) ---------- */
.icon-svg {
    width: 15px; height: 15px;
    display: inline-block; vertical-align: -2px; flex-shrink: 0;
}
.msg-action-btn .icon-svg { width: 15px; height: 15px; }
.bubble-meta .icon-svg { width: 12px; height: 12px; margin-right: 3px; }
.bubble > .icon-svg { width: 16px; height: 16px; margin-right: 6px; vertical-align: -3px; }
.sb-account .icon-svg { width: 14px; height: 14px; color: #7E7387; }
.sb-account .right-icons .icon-svg { width: 16px; height: 16px; color: #6B6172; }
.trinity-foot .logo-foot { width: 12px; height: 12px; vertical-align: -2px; margin-right: 4px; }

/* ikon material di baris aksi: ukuran rapi; state aktif (primary) terracotta */
[class*="st-key-msg_actions_"] [data-testid="stIconMaterial"] {
    font-size: 1.05rem !important;
}
[class*="st-key-msg_actions_"] div.stButton > button[kind="primary"],
[class*="st-key-msg_actions_"] [data-testid="stBaseButton-primary"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #4A3559 !important;
}
.msg-action-time {
    font-size: 0.7rem;
    color: #827788;
    padding: 0 4px;
    line-height: 26px;
    margin: 0;
}
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
    margin-top: -18px !important;
}

/* label "Yuki" dengan logo custom di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.92rem; font-weight: 600; color: #2C1F33;
    margin-bottom: 6px;
}
/* bintang ✳ fallback di label jawaban Yuki: tanpa warna latar belakang,
   ukuran disamakan dengan logo agar layout tidak lompat */
.ai-label .star {
    background: transparent !important;
    background-color: transparent !important;
    border: none; box-shadow: none;
    color: #2C1F33;
    font-size: 1.45rem; line-height: 1;
    width: 30px; height: 30px;
    display: inline-flex; align-items: center; justify-content: center;
}

/* ===== ukuran logo custom di berbagai tempat (statis, tanpa animasi) ===== */
.logo-label {
    width: 26px; height: 26px;
    display: inline-block; vertical-align: middle;
}
.logo-greeting {
    width: 48px; height: 48px;
    display: inline-block; vertical-align: -12px;
    margin-right: 2px;
}
.logo-progress {
    width: 20px; height: 20px;
    display: inline-block; vertical-align: middle;
}
/* logo SVG selalu memakai warna aksen, ikut tema, tanpa file PNG */
.logo-greeting, .logo-label, .logo-progress, .logo-foot,
.claude-think .logo-shimmer { color: #2C1F33; }

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
/* ====== URUTAN AREA INPUT ala Claude — HANYA 2 lapisan terluar yang
   dibongkar (pakai ">"), supaya struktur DI DALAM pending_strip dan
   chat_controls (posisi tombol ×, baris + & model) tidak ikut rusak ====== */
[data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"] {
    display: contents !important;
}
[data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
[data-testid="stBottomBlockContainer"] > [data-testid="stVerticalBlock"] > .element-container {
    display: contents !important;
}
[data-testid="stBottomBlockContainer"] [class*="st-key-pending_strip"] { order: 1 !important; }
[data-testid="stBottomBlockContainer"] [data-testid="stChatInput"]      { order: 2 !important; }
[data-testid="stBottomBlockContainer"] .st-key-chat_controls            { order: 3 !important; }

[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #E8DCC8 !important; border: none !important; box-shadow: none !important;
}
/* KARTU GABUNGAN ala Claude: kotak teks + baris kontrol (+, model)
   dibungkus jadi SATU kartu membulat. */
[data-testid="stBottomBlockContainer"] {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 22px !important;
    box-shadow: 0 4px 14px rgba(44,31,51,0.07) !important;
    padding: 6px 6px 4px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stBottomBlockContainer"]:focus-within {
    border-color: #2C1F33 !important;
    box-shadow: 0 4px 18px rgba(44,31,51,0.16) !important;
}
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 6px !important;
}
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: transparent !important; border: none !important; box-shadow: none !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #2C1F33 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #7E7387 !important;
}
[data-testid="stChatInput"] button {
    background: #2C1F33 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    transition: background .18s ease !important;
}
[data-testid="stChatInput"] button:hover {
    background: #4A3559 !important;
}
[data-testid="stChatInput"] button svg { fill: #FFFFFF !important; color: #FFFFFF !important; }
[data-testid="stChatInput"] button:disabled {
    background: #DBCEB9 !important;
}
[data-testid="stChatInput"] button:disabled svg { fill: #7E7387 !important; color: #7E7387 !important; }

.st-key-chat_controls {
    position: relative;
    margin-top: 0 !important;
    padding: 2px 4px 2px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
}
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #7E7387;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls [data-testid="stPopover"] > div > button,
.st-key-chat_controls button[data-testid="stBaseButton-secondary"],
.st-key-chat_controls button[data-testid="stPopoverButton"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    min-height: 30px !important;
    height: 30px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #6B6172 !important;
    box-shadow: none !important;
    white-space: nowrap;
    justify-content: flex-start !important;
    width: auto !important;
}
.st-key-chat_controls [data-testid="stPopover"] button:hover,
.st-key-chat_controls button[data-testid="stPopoverButton"]:hover {
    background: rgba(44,31,51,0.06) !important;
    color: #2C1F33 !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

[data-testid="stChatInput"] [data-testid="stChatInputFileUploadButton"] {
    display: none !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"],
[data-testid="stChatInput"] [data-testid="stChatInputCancelButton"],
[data-testid="stChatInput"] [data-testid="stChatInputApproveButton"] {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 10px !important;
    color: #4E4553 !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"] svg,
[data-testid="stChatInput"] [data-testid="stChatInputCancelButton"] svg,
[data-testid="stChatInput"] [data-testid="stChatInputApproveButton"] svg {
    fill: #4E4553 !important; color: #4E4553 !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"]:hover {
    border-color: #2C1F33 !important;
}

/* Urutan dok (versi lama, sebelum 3 ubahan) */
[data-testid="stBottomBlockContainer"] {
    display: flex !important;
    flex-direction: column !important;
}/* ====================================================================
   POSISI KOLOM CHAT (dok input di bawah layar)
   --------------------------------------------------------------------
   Kenapa pakai margin, bukan transform:
   Elemen [data-testid="stBottom"] di Streamlit adalah position: sticky
   dengan bottom: 0. Menggesernya pakai transform sering tidak terlihat
   karena posisi lengketnya dihitung ulang oleh browser. Yang PASTI
   bekerja adalah menambah margin pada kartu input di dalamnya: tinggi
   batang dok ikut bertambah, sehingga kartunya benar-benar terangkat.

   --chat-lift  : tinggi angkat kolom chat dari dasar layar saat chat
                  SUDAH berjalan. 0px = menempel bawah.
   --chat-shift : geser mendatar. Minus = ke kiri, plus = ke kanan.
   --chat-width : lebar maksimum kartu input.
   --chat-lift-fresh : posisi saat halaman awal (belum ada chat).
==================================================================== */
:root {
    --chat-lift: 32px;
    --chat-shift: 0px;
    --chat-width: 46rem;
    --chat-lift-fresh: 26vh;
}

/* Angkat & geser kartu input (berlaku saat chat sudah berjalan) */
[data-testid="stBottomBlockContainer"] {
    margin-bottom: var(--chat-lift) !important;
    transform: translateX(var(--chat-shift)) !important;
    max-width: var(--chat-width) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Batang dok dibuat transparan di area tambahan hasil pengangkatan,
   supaya yang terlihat naik hanya kartunya, bukan blok warna. */
[data-testid="stBottom"] > div {
    background: transparent !important;
}

/* Di layar sempit (HP): tanpa geseran, lebar penuh. */
@media (max-width: 640px) {
    :root {
        --chat-shift: 0px;
        --chat-width: 100%;
    }
}
.pending-card {
    position: relative;
    width: 72px;
    text-align: center;
}
[class*="st-key-pending_card_"] {
    position: relative !important;
    width: 72px !important;
    overflow: visible !important;
}
[class*="st-key-pending_rm_"] {
    position: absolute !important;
    top: 0 !important;
    right: 0 !important;
    width: 22px !important;
    height: 22px !important;
    z-index: 8 !important;
    margin: 0 !important;
}
[class*="st-key-pending_rm_"] button,
[class*="st-key-pending_rm_"] [data-testid="stBaseButton-secondary"] {
    min-width: 22px !important;
    width: 22px !important;
    height: 22px !important;
    min-height: 22px !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 1 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #2C1F33 !important;
    font-size: 16px !important;
    line-height: 1 !important;
}
.st-key-chat_controls [class*="st-key-plus_menu"] [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important;
    border-radius: 999px !important;
    min-width: 32px !important;
    width: 32px !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    color: #2C1F33 !important;
    box-shadow: none !important;
    justify-content: center !important;
}
.st-key-chat_controls [class*="st-key-plus_menu"] [data-testid="stPopover"] button:hover {
    background: #EDE2D1 !important;
    border-color: #2C1F33 !important;
    color: #4A3559 !important;
}
/* Streamlit menambahkan ikon panah kecil di ujung tombol popover secara
   otomatis (indikator dropdown) — disembunyikan supaya tombol ➕ tetap
   polos, hanya ikon plus saja tanpa panah di sebelahnya. */
.st-key-chat_controls [class*="st-key-plus_menu"] [data-testid="stPopover"] button svg:last-child,
.st-key-chat_controls [class*="st-key-plus_menu"] [data-testid="stPopover"] button [data-testid="stIconMaterial"]:last-child {
    display: none !important;
}
/* isi popover ➕ minimalist: cukup tombol unggah, tanpa label/hint besar */
.plus-menu-hint {
    font-size: 0.72rem; color: #7E7387;
    padding: 2px 4px 4px;
}
.plus-menu-divider {
    height: 1px; background: #DBCEB9; margin: 6px 4px;
}
/* baris menu tambahan di popover + (screenshot, pencarian web) —
   sama gayanya dengan item lain: teks polos, hover krem */
[data-testid="stPopoverBody"] [class*="st-key-plus_menu"] div.stButton > button,
[class*="st-key-plus_menu"] [data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #2C1F33 !important;
}
/* ---- reskin st.file_uploader jadi baris menu polos: ikon + teks saja,
   TANPA tombol "Upload"/"Browse files" terpisah yang terlihat.
   Triknya: dropzone (berisi tombol upload bawaan) dibuat transparan penuh
   dan direntangkan menutupi seluruh baris (overlay), sedangkan LABEL
   uploader (teks ikon+nama yang kita isi dari Python) tetap terlihat
   sebagai satu-satunya representasi visual — klik di mana saja pada
   baris tetap membuka dialog pilih file karena overlay ada di atasnya. */
[class*="st-key-plus_upload_file"], [class*="st-key-plus_upload_image"] {
    position: relative !important;
    border-radius: 10px !important;
    transition: background .15s ease;
}
[class*="st-key-plus_upload_file"]:hover, [class*="st-key-plus_upload_image"]:hover {
    background: #E8DCC8 !important;
}
[class*="st-key-plus_upload_file"] [data-testid="stFileUploaderDropzoneInstructions"],
[class*="st-key-plus_upload_image"] [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
[class*="st-key-plus_upload_file"] [data-testid="stFileUploaderDropzone"],
[class*="st-key-plus_upload_image"] [data-testid="stFileUploaderDropzone"] {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
}
[class*="st-key-plus_upload_file"] [data-testid="stFileUploader"],
[class*="st-key-plus_upload_image"] [data-testid="stFileUploader"] {
    margin: 0 !important;
}
[class*="st-key-plus_upload_file"] [data-testid="stWidgetLabel"],
[class*="st-key-plus_upload_image"] [data-testid="stWidgetLabel"] {
    position: relative !important;
    z-index: 0 !important;
    display: flex !important;
    align-items: center !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    pointer-events: none !important;  /* klik tembus ke overlay dropzone */
}
[class*="st-key-plus_upload_file"] [data-testid="stWidgetLabel"] p,
[class*="st-key-plus_upload_image"] [data-testid="stWidgetLabel"] p {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #2C1F33 !important;
    margin: 0 !important;
}
/* strip lampiran yang menunggu dikirim (hasil menu ➕) */
[class*="st-key-pending_strip"] { padding: 2px 2px 0; }
.pending-row {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 10px;
    padding: 10px 8px 6px;
}
.pending-card { width: 72px; text-align: center; }
.pending-square {
    width: 72px;
    height: 72px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #DBCEB9;
    background: #E8DCC8;
}
.pending-square img {
    width: 72px;
    height: 72px;
    object-fit: cover;
    object-position: center;
    display: block;
}
.pending-loading {
    background: linear-gradient(90deg, #E8DCC8 0%, #F2E8D6 45%, #E8DCC8 100%);
    background-size: 200% 100%;
    animation: pendingShimmer 1.1s ease-in-out infinite;
    position: relative;
}
.pending-loading::after {
    content: "";
    position: absolute;
    inset: 26px;
    border: 2px solid #C1B49F;
    border-top-color: #2C1F33;
    border-radius: 50%;
    animation: pendingSpin 0.8s linear infinite;
}
@keyframes pendingShimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
@keyframes pendingSpin {
    to { transform: rotate(360deg); }
}
.pending-name {
    font-size: 0.65rem;
    color: #6B6172;
    margin-top: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 72px;
}
[class*="st-key-pending_strip"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: flex-start !important;
}
[class*="st-key-pending_strip"] [data-testid="stImage"] { margin: 0 !important; }
[class*="st-key-pending_strip"] button {
    min-height: 24px !important;
    height: 24px !important;
    font-size: 0.72rem !important;
    padding: 0 10px !important;
    border-radius: 8px !important;
}
/* chip file bawaan st.chat_input supaya kelihatan di dalam kotak */
[data-testid="stChatInput"] [data-testid="stChatInputUploadedFiles"],
[data-testid="stChatInput"] [class*="uploadedFile"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    padding: 8px 8px 0 !important;
    visibility: visible !important;
    height: auto !important;
    overflow: visible !important;
}
/* ---------- tombol & popover: pill lembut ala Claude ---------- */
div.stButton > button, [data-testid="stPopover"] > button,
div.stDownloadButton > button {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    color: #2C1F33 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(44,31,51,0.05) !important;
    transition: all .18s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover,
div.stDownloadButton > button:hover {
    background: #EDE2D1 !important;
    border-color: #2C1F33 !important;
    color: #4A3559 !important;
    box-shadow: 0 2px 8px rgba(44,31,51,0.14) !important;
}
/* ---------- pop-up model ala Claude: SATU panel, item = teks polos ---------- */
[data-testid="stPopoverBody"] {
    background: #FBF6EC !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 48px rgba(44,31,51,0.18) !important;
    min-width: 300px !important;
    padding: 8px 6px !important;
}
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] div {
    color: #2C1F33;
}
/* item model: TANPA kotak sendiri-sendiri — hanya teks, hover baru menyala */
[data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    display: flex !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #E8DCC8 !important;
    border: none !important;
    box-shadow: none !important;
    color: inherit !important;
}
/* isi tombol (markdown) dipaksa RATA KIRI penuh */
[data-testid="stPopoverBody"] div.stButton > button > div,
[data-testid="stPopoverBody"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
/* deskripsi model: lebih kecil dari nama modelnya */
[data-testid="stPopoverBody"] div.stButton > button .stMarkdownColoredText {
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    line-height: 1.35 !important;
    display: block;
}
/* nama model (baris pertama) tebal gelap, deskripsi kecil abu */
[data-testid="stPopoverBody"] div.stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #2C1F33 !important;
    line-height: 1.45 !important;
}
/* label PREMIUM kecil di sebelah nama model (tier Hard & Extreme) */
.model-premium-badge {
    display: inline-block;
    font-size: 0.62rem; font-weight: 700;
    color: #4A3559;
    background: rgba(44,31,51,0.12);
    border: 1px solid rgba(44,31,51,0.35);
    border-radius: 999px;
    padding: 1px 7px;
    margin-left: 6px;
    letter-spacing: 0.03em;
    vertical-align: middle;
}
/* label PREMIUM: dipojokkan kecil di sudut kanan-atas tiap baris model
   (bukan menempel di sebelah nama) — ukuran & huruf dibuat mini */
[data-testid="stPopoverBody"] [class*="_premium"] {
    position: relative;
}
[data-testid="stPopoverBody"] [class*="_premium"]::after {
    content: "Premium";
    position: absolute;
    top: 4px; right: 6px;
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #5C4470;
    background: rgba(44,31,51,0.10);
    border: 1px solid rgba(44,31,51,0.25);
    border-radius: 999px;
    padding: 1px 6px;
    pointer-events: none;
}
/* rapatkan jarak antar item */
[data-testid="stPopoverBody"] .element-container { margin: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 2px !important; }

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #2C1F33 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
/* warna track toggle saat aktif → terracotta */
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #2C1F33 !important;
}

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.img {
    background: rgba(44,31,51,0.10);
    border: 1px solid rgba(44,31,51,0.35); color: #4A3559;
}

/* ---------- spinner ala Claude ---------- */
[data-testid="stSpinner"] > div {
    border-top-color: #2C1F33 !important;
}
[data-testid="stSpinner"] p { color: #6B6172 !important; }

/* ---------- thinking indicator ala Claude ---------- */
.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
/* bintang ✳ fallback: pastikan tidak pernah ada warna latar belakang/kotak */
.star {
    background: transparent !important;
    background-color: transparent !important;
    border: none; box-shadow: none;
}
/* bintang ✳ terracotta berdenyut & berputar pelan (fallback) */
.claude-think .star {
    font-size: 1.05rem; color: #2C1F33; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}

/* ===== LOGO THINKING: shimmer glow BERJALAN yang halus + denyut ===== */
/* Pita cahaya lembut (gradasi transparan→putih→transparan + blur +
   blend screen) menyapu melintasi logo dari kiri ke kanan terus-menerus.
   Tepinya gradasi & di-blur → mulus tanpa garis patah. */
.claude-think .logo-shimmer {
    position: relative;
    display: inline-block;
    width: 34px; height: 34px;
    flex-shrink: 0;
    overflow: hidden;
    border-radius: 6px;
    animation: logoPulse 3s ease-in-out infinite;
}
.claude-think .logo-shimmer img,
.logo-label img, .logo-greeting img, .logo-progress img, .logo-foot img {
    width: 100%; height: 100%;
    display: block;
}
/* pita cahaya berjalan */
.claude-think .logo-shimmer::after {
    content: "";
    position: absolute;
    top: -30%; bottom: -30%;
    left: 0; width: 60%;
    background: linear-gradient(
        100deg,
        rgba(255,255,255,0) 0%,
        rgba(236,228,244,0.85) 50%,
        rgba(255,255,255,0) 100%
    );
    filter: blur(3px);
    mix-blend-mode: screen;
    transform: translateX(-130%) skewX(-16deg);
    animation: shineSweep 2.6s ease-in-out infinite;
    pointer-events: none;
}
@keyframes shineSweep {
    0%   { transform: translateX(-130%) skewX(-16deg); }
    60%  { transform: translateX(260%) skewX(-16deg); }
    100% { transform: translateX(260%) skewX(-16deg); }
}
@keyframes logoPulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.14); }
}
/* teks dengan shimmer lembut menyapu perlahan (gaya Claude) */
.claude-think .phrase {
    font-size: 0.92rem; font-weight: 500;
    background: linear-gradient(
        90deg,
        #7E7387 0%, #7E7387 35%,
        #2C1F33 50%,
        #7E7387 65%, #7E7387 100%
    );
    background-size: 220% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerSweep 4s linear infinite, phraseIn 3s ease both;
}
@keyframes shimmerSweep {
    0%   { background-position: 110% 0; }
    100% { background-position: -110% 0; }
}
/* teks muncul perlahan-lahan (fade masuk lambat) */
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
/* frasa berganti-ganti pelan (rotasi via CSS, jalan terus di browser
   walau server sedang sibuk memanggil API) */
.claude-think .phrases { position: relative; height: 1.5em; min-width: 260px; }
.claude-think .phrases .phrase {
    position: absolute; left: 0; top: 0; white-space: nowrap;
    opacity: 0;
    animation: shimmerSweep 4s linear infinite,
               phraseCycle 16s ease-in-out infinite;
}
.claude-think .phrases .phrase:nth-child(1) { animation-delay: 0s, 0s; }
.claude-think .phrases .phrase:nth-child(2) { animation-delay: 0s, 4s; }
.claude-think .phrases .phrase:nth-child(3) { animation-delay: 0s, 8s; }
.claude-think .phrases .phrase:nth-child(4) { animation-delay: 0s, 12s; }
@keyframes phraseCycle {
    0%      { opacity: 0; filter: blur(4px); }
    3%      { opacity: 1; filter: blur(0); }
    21%     { opacity: 1; filter: blur(0); }
    25%     { opacity: 0; filter: blur(4px); }
    100%    { opacity: 0; }
}

/* caret berkedip saat jawaban muncul bertahap */
.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #2C1F33; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* ====================================================================
   KOTAK LOADING PEMBUATAN GAMBAR ALA CHATGPT (Perimeter Shimmer Box)
   --------------------------------------------------------------------
   - Kotak kanvas persegi (aspect-ratio 1:1) ala ChatGPT / DALL-E.
   - Efek berkas cahaya / shimmer berputar 360° mengitari tepi samping kotak.
   - Gelombang shimmer halus menyapu di atas permukaan kanvas kotak.
   - Ikon kanvas berdenyut di tengah + status bertahap & mini progress bar.
==================================================================== */

.img-gen-box-wrapper,
.img-progress {
    position: relative !important;
    width: 100% !important;
    max-width: 340px !important;
    aspect-ratio: 1 / 1 !important;
    border-radius: 22px !important;
    padding: 2px !important;            /* tebal pita cahaya di tepi */
    overflow: hidden !important;
    isolation: isolate;                 /* pita cahaya tak bocor ke luar */
    margin: 8px 0 16px !important;
    box-shadow: 0 10px 34px rgba(44, 31, 51, 0.13) !important;
    display: block !important;
    background: #FFFFFF !important;     /* kotak putih ala ChatGPT */
    animation: thinkFadeIn 0.45s ease both !important;
    box-sizing: border-box !important;
}

/* Berkas shimmer cahaya yang berputar 360° mengitari tepi kotak.
   Memakai kotak pembungkus 1:1 yang diputar (bukan @property --angle),
   supaya jalan di semua browser termasuk Safari & Firefox. */
.img-gen-box-wrapper::before,
.img-progress::before {
    content: "";
    position: absolute;
    z-index: 0;
    top: 50%;
    left: 50%;
    width: 150%;
    aspect-ratio: 1 / 1;
    height: auto;
    background: conic-gradient(
        from 0deg,
        rgba(255, 255, 255, 0) 0deg,
        rgba(255, 255, 255, 0) 40deg,
        rgba(110, 84, 130, 0.25) 95deg,
        rgba(74, 53, 89, 0.95) 135deg,
        rgba(200, 178, 220, 0.95) 160deg,
        rgba(110, 84, 130, 0.25) 200deg,
        rgba(255, 255, 255, 0) 260deg,
        rgba(255, 255, 255, 0) 360deg
    );
    transform-origin: center center;
    animation: borderShimmerSpin 2.6s linear infinite;
    will-change: transform;
}

@keyframes borderShimmerSpin {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to   { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Saat selesai: pita cahaya berhenti & memudar */
.img-gen-box-wrapper.is-done::before { animation: none; opacity: 0; }
.img-gen-box-wrapper.is-done .img-gen-canvas-shimmer { animation: none; opacity: 0; }

/* Lapisan dalam kotak kanvas (putih) */
.img-gen-box-inner {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
    background: #FFFFFF;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* Gelombang shimmer menyapu diagonal di permukaan kanvas putih */
.img-gen-canvas-shimmer {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        115deg,
        rgba(240, 234, 246, 0) 30%,
        rgba(226, 216, 238, 0.75) 48%,
        rgba(240, 234, 246, 0) 66%
    );
    background-size: 260% 260%;
    animation: canvasShimmerWave 2.4s ease-in-out infinite;
    pointer-events: none;
    z-index: 2;
}

@keyframes canvasShimmerWave {
    0%   { background-position: 170% 170%; }
    100% { background-position: -70% -70%; }
}

/* Ikon tengah dengan breathing pulse */
.img-gen-center-icon {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: #2C1F33;
    color: #FFFFFF;
    display: grid;
    place-items: center;
    box-shadow: 0 6px 20px rgba(44, 31, 51, 0.20);
    animation: iconPulseBreath 2.2s ease-in-out infinite;
    margin-bottom: 14px;
    position: relative;
    z-index: 3;
}

@keyframes iconPulseBreath {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 6px 20px rgba(44, 31, 51, 0.20);
    }
    50% {
        transform: scale(1.06);
        box-shadow: 0 10px 28px rgba(74, 53, 89, 0.34);
    }
}

.img-gen-icon-svg {
    width: 27px;
    height: 27px;
    stroke: #FFFFFF;
}

/* Pembungkus status teks & progress */
.img-gen-status-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    z-index: 3;
    text-align: center;
    padding: 0 24px;
}

/* Teks status berganti sendiri lewat CSS (tanpa rerun server) */
.img-gen-phrases {
    position: relative;
    height: 1.4em;
    min-width: 210px;
}
.img-gen-phrase {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    white-space: nowrap;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    background: linear-gradient(
        90deg,
        #8C82A0 0%, #8C82A0 30%,
        #2C1F33 50%,
        #8C82A0 70%, #8C82A0 100%
    );
    background-size: 220% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 0;
    animation: shimmerSweep 2.6s linear infinite,
               imgPhraseCycle 20s ease-in-out infinite;
}
.img-gen-phrase:nth-child(1) { animation-delay: 0s, 0s; }
.img-gen-phrase:nth-child(2) { animation-delay: 0s, 5s; }
.img-gen-phrase:nth-child(3) { animation-delay: 0s, 10s; }
.img-gen-phrase:nth-child(4) { animation-delay: 0s, 15s; }
/* kalau cuma satu frasa (mis. "Selesai"), tampilkan terus */
.img-gen-phrase:only-child {
    opacity: 1;
    animation: shimmerSweep 2.6s linear infinite;
}
@keyframes imgPhraseCycle {
    0%   { opacity: 0; filter: blur(4px); }
    3%   { opacity: 1; filter: blur(0); }
    22%  { opacity: 1; filter: blur(0); }
    25%  { opacity: 0; filter: blur(4px); }
    100% { opacity: 0; }
}

.img-gen-mini-bar {
    position: relative;
    width: 140px;
    height: 4px;
    border-radius: 99px;
    background: rgba(44, 31, 51, 0.10);
    overflow: hidden;
}

/* Bar indeterminate: meluncur terus selama gambar dibuat */
.img-gen-mini-fill {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 42%;
    background: linear-gradient(90deg, rgba(44,31,51,0), #2C1F33, #6E5482, rgba(110,84,130,0));
    border-radius: 99px;
    animation: imgBarSlide 1.5s ease-in-out infinite;
}
@keyframes imgBarSlide {
    0%   { transform: translateX(-110%); }
    100% { transform: translateX(340%); }
}
.img-gen-box-wrapper.is-done .img-gen-mini-fill {
    animation: none;
    width: 100%;
    transform: none;
    background: #2C1F33;
}
/* ====================================================================
   KARTU KAYA (rich cards): perbandingan, langkah, link
   Meniru gaya kartu Claude: putih, sudut lembut, garis pemisah tipis,
   bayangan sangat halus, tipografi bertingkat.
==================================================================== */
.rc-card {
    background: #FFFFFF;
    border: 1px solid #E4D9C6;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(44, 31, 51, 0.05);
    margin: 10px 0 14px;
    max-width: 640px;
    overflow: hidden;
    animation: rcIn 0.3s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes rcIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- 1. KARTU PERBANDINGAN ---------- */
.rc-cmp-row {
    display: grid;
    grid-template-columns: repeat(var(--rc-cols, 2), 1fr);
    border-top: 1px solid #EFE6D6;
}
.rc-cmp-row.rc-cmp-toprow { border-top: none; }
.rc-cmp-head {
    padding: 16px 18px 6px;
    font-size: 1.02rem;
    font-weight: 650;
    color: #2C1F33;
    letter-spacing: -0.01em;
}
.rc-cmp-cell { padding: 12px 18px 14px; }
.rc-cmp-label {
    font-size: 0.76rem;
    color: #8E8398;
    margin-bottom: 3px;
    letter-spacing: 0.01em;
}
.rc-cmp-value {
    font-size: 0.92rem;
    color: #2C1F33;
    font-weight: 500;
    line-height: 1.4;
}
/* garis pemisah vertikal antar kolom */
.rc-cmp-row > *:not(:first-child) { border-left: 1px solid #F3ECE0; }

/* ---------- 2. KARTU LANGKAH ---------- */
.rc-step { padding: 18px 20px 16px; }
.rc-step-title {
    font-size: 1.18rem;
    font-weight: 600;
    color: #2C1F33;
    letter-spacing: -0.015em;
    margin-bottom: 6px;
}
.rc-step-desc {
    font-size: 0.9rem;
    color: #6B6172;
    line-height: 1.55;
    margin-bottom: 14px;
}
.rc-step-dots { display: flex; align-items: center; gap: 7px; }
.rc-dot {
    width: 26px; height: 26px;
    display: inline-flex; align-items: center; justify-content: center;
    border-radius: 50%;
    background: #F1EADD;
    color: #8E8398;
    font-size: 0.76rem;
    font-weight: 600;
    transition: background .2s ease, color .2s ease, transform .2s ease;
}
.rc-dot.on {
    background: #2C1F33;
    color: #FBF6EC;
    transform: scale(1.06);
}
.rc-step-count {
    margin-left: 6px;
    font-size: 0.78rem;
    color: #8E8398;
}
/* tombol navigasi langkah */
[class*="st-key-rc_nav_"] { max-width: 640px; margin: -6px 0 16px !important; }
[class*="st-key-rc_nav_"] div.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #DBCEB9 !important;
    background: #FFFFFF !important;
    color: #2C1F33 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    min-height: 40px !important;
    transition: background .15s ease, transform .1s ease !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:hover:not(:disabled) {
    background: #FAF3E8 !important;
    border-color: #2C1F33 !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:active:not(:disabled) {
    transform: scale(0.985) !important;
}
[class*="st-key-rc_nav_"] div.stButton > button[kind="primary"] {
    background: #2C1F33 !important;
    border-color: #2C1F33 !important;
    color: #FBF6EC !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:disabled {
    opacity: 0.45 !important;
    cursor: not-allowed !important;
}

/* ---------- 3. KARTU LINK ---------- */
.rc-link { padding: 14px 18px 13px; }
.rc-link-title {
    display: inline-block;
    font-size: 0.98rem;
    font-weight: 600;
    color: #2C1F33 !important;
    text-decoration: underline;
    text-underline-offset: 3px;
    text-decoration-thickness: 1px;
    margin-bottom: 5px;
}
.rc-link-title:hover { color: #4A3559 !important; }
.rc-link-desc {
    font-size: 0.87rem;
    color: #6B6172;
    line-height: 1.5;
    margin-bottom: 7px;
}
.rc-link-src {
    font-size: 0.78rem;
    color: #A095AC;
    letter-spacing: 0.01em;
}
/* ---------- 4. KARTU PETA ---------- */
[class*="st-key-rc_map_"] { max-width: 660px; margin-bottom: 14px; }
[class*="st-key-rc_map_"] iframe {
    border: 1px solid #E4D9C6 !important;
    border-radius: 12px !important;
    width: 100% !important;
    background: #F6F1E7;
}
[class*="st-key-rc_map_"] [data-testid="stHorizontalBlock"] { gap: 10px !important; }
.rc-map-side { padding: 14px 16px; height: 100%; }
.rc-map-title {
    font-size: 0.96rem; font-weight: 600; color: #2C1F33;
    line-height: 1.35; margin-bottom: 5px;
}
.rc-map-desc {
    font-size: 0.83rem; color: #6B6172; line-height: 1.5; margin-bottom: 9px;
}
.rc-map-link {
    font-size: 0.82rem; font-weight: 600; color: #2C1F33 !important;
    text-decoration: underline; text-underline-offset: 3px;
}
.rc-map-fallback { padding: 18px; text-align: center; }

/* ---------- 5. KARTU ITINERARY ---------- */
[class*="st-key-rc_itin_"] { max-width: 640px; margin-bottom: 14px; }
[class*="st-key-rc_itin_"] [data-testid="stHorizontalBlock"] {
    gap: 6px !important; margin-bottom: 4px !important;
}
[class*="st-key-rc_itin_"] div.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #E4D9C6 !important;
    background: #F6F1E7 !important;
    color: #8E8398 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    min-height: 36px !important;
    transition: background .15s ease, color .15s ease !important;
}
[class*="st-key-rc_itin_"] div.stButton > button[kind="primary"] {
    background: #FFFFFF !important;
    border-color: #DBCEB9 !important;
    color: #2C1F33 !important;
    box-shadow: 0 1px 3px rgba(44,31,51,0.08) !important;
}
.rc-itin { padding: 16px 18px 8px; }
.rc-itin-day {
    font-size: 0.78rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 12px;
}
.rc-itin-row { display: grid; grid-template-columns: 58px 18px 1fr; }
.rc-itin-time {
    font-size: 0.82rem; color: #8E8398; text-align: right;
    padding-top: 2px; padding-right: 4px;
}
.rc-itin-mark { position: relative; display: flex; justify-content: center; }
.rc-itin-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #C9BCA6; margin-top: 7px; z-index: 1;
}
/* garis penghubung antar titik linimasa */
.rc-itin-row:not(:last-child) .rc-itin-mark::after {
    content: ""; position: absolute; top: 15px; bottom: -6px;
    width: 1px; background: #EAE0D0;
}
.rc-itin-body { padding: 0 0 16px 6px; }
.rc-itin-act {
    font-size: 0.98rem; font-weight: 600; color: #2C1F33;
    letter-spacing: -0.01em; line-height: 1.35;
}
.rc-itin-note {
    font-size: 0.85rem; color: #6B6172; line-height: 1.5; margin-top: 2px;
}

/* ---------- 6. KARTU TERJEMAHAN ---------- */
.rc-tr { display: grid; grid-template-columns: 1fr 1fr; }
.rc-tr-pane { padding: 13px 16px 15px; }
.rc-tr-pane:last-child { border-left: 1px solid #F3ECE0; }
.rc-tr-head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
}
.rc-tr-lang { font-size: 0.78rem; color: #8E8398; letter-spacing: 0.01em; }
.rc-tr-text {
    font-size: 0.96rem; color: #2C1F33; line-height: 1.5; font-weight: 500;
}
.rc-icon-btn {
    background: transparent; border: none; cursor: pointer;
    font-size: 0.86rem; line-height: 1; padding: 2px 4px;
    border-radius: 6px; color: #8E8398;
    transition: background .15s ease, transform .1s ease;
}
.rc-icon-btn:hover { background: rgba(44,31,51,0.06); }
.rc-icon-btn:active { transform: scale(0.9); 
}
/* ---------- 7. KARTU PALET WARNA ---------- */
.rc-pal { padding: 14px 16px 12px; }
.rc-pal-title {
    font-size: 0.9rem; font-weight: 600; color: #2C1F33; margin-bottom: 10px;
}
.rc-pal-row { display: flex; gap: 8px; flex-wrap: wrap; }
.rc-pal-item { flex: 1 1 84px; min-width: 84px; }
.rc-pal-chip {
    height: 62px;
    border-radius: 10px;
    border: 1px solid rgba(44, 31, 51, 0.10);
    display: flex; align-items: flex-end; justify-content: center;
    padding-bottom: 6px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.02em;
    transition: transform .15s ease, box-shadow .15s ease;
}
.rc-pal-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 14px rgba(44, 31, 51, 0.14);
}
.rc-pal-label {
    font-size: 0.74rem; color: #8E8398; margin-top: 5px;
    text-align: center; line-height: 1.3;
}
.rc-pal-foot {
    margin-top: 11px; padding-top: 9px;
    border-top: 1px solid #F3ECE0;
    font-size: 0.74rem; color: #A095AC;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
}

/* ---------- 8. HALAMAN AI DESAIN & AI PENJADWAL ---------- */
/* label bagian, dipakai di kedua halaman */
.sec-label {
    font-size: 0.74rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.07em; text-transform: uppercase;
    margin: 4px 0 8px;
}
.sec-divider {
    height: 1px; background: #E0D2BB;
    margin: 22px 0 18px; border: none;
}
/* ruang kosong agar isi terakhir tidak tertutup kotak input */
.dock-spacer { height: 96px; }

/* panel daftar tugas */
[class*="st-key-jd_panel"] {
    background: #F7F1E6;
    border: 1px solid #E4D9C6;
    border-radius: 14px;
    padding: 6px 14px 10px !important;
    margin-bottom: 10px;
}
[class*="st-key-jd_panel"] [data-testid="stVerticalBlock"] { gap: 0 !important; }

.jd-progress-wrap { margin: 2px 0 12px; }
.jd-progress-text { font-size: 0.8rem; color: #6B6172; margin-bottom: 6px; }
.jd-progress-bar {
    height: 6px; background: #E4D9C6; border-radius: 99px; overflow: hidden;
}
.jd-progress-fill {
    height: 100%; background: #2C1F33; border-radius: 99px;
    transition: width .4s cubic-bezier(.32,.72,0,1);
}
.jd-group {
    font-size: 0.72rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.05em; text-transform: uppercase;
    margin: 12px 0 2px; padding-top: 2px;
}
.jd-item {
    display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
    padding: 2px 0;
}
.jd-dot {
    width: 7px; height: 7px; border-radius: 50%;
    display: inline-block; flex: 0 0 auto; transform: translateY(-1px);
}
.jd-title { font-size: 0.93rem; color: #2C1F33; font-weight: 500; }
.jd-meta { font-size: 0.75rem; color: #A095AC; }
.jd-item.jd-done .jd-title { text-decoration: line-through; color: #B0A6BC; }
.jd-item.jd-done .jd-dot { opacity: 0.4; }

/* baris tugas: rapatkan jarak antar baris & rapikan tombolnya */
[class*="st-key-jd_row_"] { margin: 0 !important; }
[class*="st-key-jd_row_"] [data-testid="stHorizontalBlock"] {
    gap: 8px !important; align-items: center !important;
    min-height: 34px;
}
[class*="st-key-jd_row_"] div.stButton { margin: 0 !important; }
[class*="st-key-jd_row_"] div.stButton > button {
    background: transparent !important;
    border: 1px solid #DBCEB9 !important;
    color: #6B6172 !important;
    width: 24px !important; min-width: 24px !important; height: 24px !important;
    padding: 0 !important; border-radius: 7px !important;
    font-size: 0.75rem !important; line-height: 1 !important;
}
[class*="st-key-jd_row_"] div.stButton > button:hover {
    background: #E0D2BB !important; color: #2C1F33 !important;
}
[class*="st-key-jd_clear_wrap"] div.stButton > button {
    background: transparent !important;
    border: 1px dashed #CDBFA8 !important;
    color: #8E8398 !important;
    font-size: 0.8rem !important;
    min-height: 34px !important;
    margin-top: 8px !important;
}

/* tombol mulai cepat di kedua halaman AI khusus */
[class*="st-key-desain_quick"] div.stButton > button,
[class*="st-key-jadwal_quick"] div.stButton > button {
    background: #F2E8D6 !important;
    border: 1px solid #E0D2BB !important;
    border-radius: 11px !important;
    color: #2C1F33 !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    min-height: 46px !important;
    white-space: normal !important;
    line-height: 1.3 !important;
    transition: background .15s ease, border-color .15s ease,
                transform .1s ease !important;
}
[class*="st-key-desain_quick"] div.stButton > button:hover,
[class*="st-key-jadwal_quick"] div.stButton > button:hover {
    background: #FFFFFF !important;
    border-color: #2C1F33 !important;
    transform: translateY(-1px) !important;
}
[class*="st-key-desain_quick"] [data-testid="stHorizontalBlock"],
[class*="st-key-jadwal_quick"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}
[class*="st-key-desain_quick"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}

/* form "Tambah tugas sendiri" */
[data-testid="stMainBlockContainer"] [data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #E4D9C6 !important;
    margin-bottom: 8px !important;
}
/* ---------- 9. PANEL FILE / ARTEFAK (sidebar kanan) ---------- */
/* -- kartu ringkas di dalam chat -- */
.af-chip {
    display: flex; align-items: center; gap: 9px; flex-wrap: wrap;
    background: #F7F1E6; border: 1px solid #E0D2BB; border-radius: 11px;
    padding: 10px 13px; margin: 6px 0 4px; max-width: 460px;
    animation: iosPopIn .34s cubic-bezier(.32,.72,0,1) both;
}
.af-chip-ic {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; font-weight: 700; color: #FBF6EC;
    background: #2C1F33; border-radius: 7px; padding: 3px 7px; line-height: 1.2;
}
.af-chip-name {
    font-size: 0.92rem; font-weight: 600; color: #2C1F33;
    font-family: 'JetBrains Mono', monospace;
}
.af-chip-meta { font-size: 0.76rem; color: #A095AC; }
[class*="st-key-af_open_"] div.stButton > button {
    background: transparent !important; border: 1px solid #DBCEB9 !important;
    border-radius: 9px !important; color: #4A3559 !important;
    font-size: 0.8rem !important; font-weight: 600 !important;
    min-height: 30px !important; margin-top: 4px !important;
}
[class*="st-key-af_open_"] div.stButton > button:hover {
    background: #E0D2BB !important; border-color: #2C1F33 !important;
}

/* ================= TAMPILAN DAFTAR ================= */
.af-sec {
    font-size: 1.28rem; font-weight: 650; color: #2C1F33;
    letter-spacing: -0.02em; margin: 2px 0 12px;
    font-family: 'Source Serif 4', serif;
}
.af-sec-2 { margin-top: 22px; }

/* tombol "Unduh semua" */
[class*="st-key-af_dlall"] div.stDownloadButton > button {
    background: transparent !important; border: none !important;
    color: #2C1F33 !important; font-size: 0.9rem !important;
    font-weight: 600 !important; justify-content: flex-end !important;
    min-height: 30px !important; margin: -46px 0 10px !important;
}
[class*="st-key-af_dlall"] div.stDownloadButton > button:hover {
    color: #4A3559 !important; text-decoration: underline !important;
}

/* kartu file */
[class*="st-key-af_card_"] {
    background: #FFFFFF !important; border: 1px solid #EAE0D0 !important;
    border-radius: 14px !important; padding: 12px 14px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 1px 3px rgba(44,31,51,0.04) !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
[class*="st-key-af_card_"]:hover {
    border-color: #DBCEB9 !important;
    box-shadow: 0 4px 14px rgba(44,31,51,0.08) !important;
}
[class*="st-key-af_card_"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important; align-items: center !important;
}
.af-file-ic {
    width: 46px; height: 54px; border-radius: 8px;
    background: linear-gradient(150deg, #F6E7CE 0%, #EFD9B4 100%);
    border: 1px solid #E3C89B;
    display: grid; place-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem; font-weight: 700; color: #B5762F;
}
.af-file-name {
    font-size: 1.05rem; font-weight: 600; color: #2C1F33; line-height: 1.25;
    word-break: break-all;
}
.af-file-ext {
    font-size: 0.82rem; color: #A095AC; margin-top: 1px;
    text-transform: uppercase; letter-spacing: 0.03em;
}
[class*="st-key-af_card_"] div.stDownloadButton > button {
    background: transparent !important; border: none !important;
    color: #6B6172 !important; min-height: 32px !important;
    padding: 0 !important;
}
[class*="st-key-af_card_"] div.stDownloadButton > button:hover {
    color: #2C1F33 !important;
}

/* petak Konten (gambar) */
[class*="st-key-af_konten"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important; margin-bottom: 10px !important;
}
[class*="st-key-af_konten"] [data-testid="stImage"] img {
    border-radius: 12px !important; border: 1px solid #EAE0D0 !important;
    background: #FFFFFF;
}

/* panel kosong */
.af-empty {
    background: #FFFFFF; border: 1px dashed #DBCEB9; border-radius: 12px;
    padding: 16px; font-size: 0.86rem; color: #6B6172; line-height: 1.6;
}
.af-empty b { color: #2C1F33; }

/* ================= TAMPILAN ISI FILE ================= */
.af-title-row { display: flex; align-items: baseline; gap: 2px; padding-top: 4px; }
.af-title {
    font-size: 1.18rem; font-weight: 650; color: #2C1F33;
    letter-spacing: -0.02em; font-family: 'Source Serif 4', serif;
}
.af-title-ext { font-size: 0.95rem; color: #A095AC; }

/* Baris aksi: Salin | perlebar | tutup.
   Ketiganya dipaksa TINGGI SAMA (36px) dan sejajar tengah. Tanpa ini,
   tombol Salin (HTML biasa) dan tombol Streamlit punya margin bawaan
   berbeda sehingga terlihat tidak rata. */
[class*="st-key-af_actbar"] [data-testid="stHorizontalBlock"] {
    gap: 6px !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
}
[class*="st-key-af_actbar"] [data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
    min-width: 0 !important;
}
/* nol-kan margin bawaan pembungkus Streamlit */
[class*="st-key-af_actbar"] .element-container,
[class*="st-key-af_actbar"] [data-testid="stMarkdownContainer"],
[class*="st-key-af_actbar"] [data-testid="stMarkdown"],
[class*="st-key-af_actbar"] div.stButton {
    margin: 0 !important; padding: 0 !important; line-height: 0 !important;
    width: 100% !important;
}
.af-copy {
    background: #FFFFFF; border: 1px solid #DBCEB9; border-radius: 9px;
    cursor: pointer; font-size: 0.82rem; font-weight: 600; color: #2C1F33;
    height: 36px; width: 100%; padding: 0 14px; margin: 0;
    display: inline-flex; align-items: center; justify-content: center;
    line-height: 1;
    transition: background .15s ease, transform .1s ease;
}
.af-copy:hover { background: #F2E8D6; }
.af-copy:active { transform: scale(0.96); }
[class*="st-key-af_actbar"] div.stButton > button {
    background: #FFFFFF !important; border: 1px solid #DBCEB9 !important;
    color: #4A3559 !important; border-radius: 9px !important;
    width: 36px !important; min-width: 36px !important;
    height: 36px !important; min-height: 36px !important;
    padding: 0 !important; margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important; justify-content: center !important;
    line-height: 1 !important;
}
[class*="st-key-af_actbar"] div.stButton > button:hover {
    background: #F2E8D6 !important; border-color: #2C1F33 !important;
}
[class*="st-key-af_actbar"] [data-testid="stIconMaterial"] {
    font-size: 1.05rem !important;
    width: 1.05rem !important; height: 1.05rem !important;
    line-height: 1 !important;
}
[class*="st-key-af_actbar"] div.stButton > button:hover {
    background: #F2E8D6 !important; border-color: #2C1F33 !important;
}
[class*="st-key-af_back"] div.stButton > button {
    background: transparent !important; border: none !important;
    color: #8E8398 !important; font-size: 0.8rem !important;
    min-height: 26px !important; padding: 0 !important;
    margin: -2px 0 8px !important;
}
[class*="st-key-af_back"] div.stButton > button:hover { color: #2C1F33 !important; }

/* kotak kode: nomor baris + pewarnaan */
.af-codebox {
    background: #FFFFFF; border: 1px solid #EAE0D0; border-radius: 12px;
    padding: 12px 4px 12px 0; overflow: auto; max-height: 64vh;
    font-family: 'JetBrains Mono', monospace; font-size: 0.79rem;
    line-height: 1.75;
}
.af-ln { display: flex; white-space: pre; }
.af-ln:hover { background: #FBF7F0; }
.af-num {
    flex: 0 0 46px; text-align: right; padding-right: 14px;
    color: #C4BACF; user-select: none;
}
.af-code { white-space: pre; color: #2C1F33; padding-right: 14px; }
.af-code .k-key { color: #7A3E9D; font-weight: 600; }   /* kata kunci */
.af-code .k-str { color: #1F7A4D; }                      /* teks */
.af-code .k-com { color: #A095AC; font-style: italic; }  /* komentar */
.af-code .k-num { color: #B5762F; }                      /* angka */

[class*="st-key-af_actions"] div.stDownloadButton > button {
    background: #2C1F33 !important; border: none !important;
    color: #FBF6EC !important; border-radius: 10px !important;
    font-size: 0.84rem !important; font-weight: 600 !important;
    min-height: 40px !important; margin-top: 10px !important;
}
/* ---------- layar sempit ---------- */
@media (max-width: 640px) {
    .rc-card { max-width: 100%; }
    .rc-cmp-row { grid-template-columns: 1fr; }
    .rc-cmp-row > *:not(:first-child) {
        border-left: none;
        border-top: 1px solid #F3ECE0;
    }
    [class*="st-key-rc_nav_"] { max-width: 100%; }
    [class*="st-key-rc_map_"], [class*="st-key-rc_itin_"] { max-width: 100%; }
    .rc-tr { grid-template-columns: 1fr; }
    .rc-tr-pane:last-child {
        border-left: none;
        border-top: 1px solid #F3ECE0;
    }
    .rc-itin-row { grid-template-columns: 48px 16px 1fr; 
    }
/* ====================================================================
   KARTU PILIHAN INTERAKTIF (quick reply)
   Muncul di bawah jawaban Yuki saat dia perlu memastikan sesuatu.
   Tata letak: grid 2 kolom bila label pendek, vertikal di layar sempit.
==================================================================== */
[class*="st-key-qr_card_"] {
    background: #FBF6EC !important;              /* sedikit lebih terang dari kanvas */
    border: 1px solid #E0D2BB !important;
    border-radius: 14px !important;
    padding: 14px 14px 12px !important;
    margin: 8px 0 20px !important;
    max-width: 560px;
    box-shadow: 0 2px 10px rgba(44, 31, 51, 0.05) !important;
    animation: qrCardIn 0.32s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes qrCardIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* --- pertanyaan --- */
.qr-question {
    font-size: 0.9rem;
    font-weight: 600;                 /* semibold: terbaca sekilas */
    color: #2C1F33;
    letter-spacing: -0.01em;
    margin: 0 0 12px;
    line-height: 1.45;
}

/* --- tombol pilihan --- */
[class*="st-key-qr_card_"] div.stButton > button {
    background: #FFFFFF !important;   /* "mengambang" di atas kartu */
    border: 1px solid #DBCEB9 !important;
    border-radius: 10px !important;
    color: #2C1F33 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;      /* medium */
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    min-height: 44px !important;      /* nyaman di-tap pada layar sentuh */
    box-shadow: 0 1px 2px rgba(44, 31, 51, 0.05) !important;
    white-space: normal !important;
    line-height: 1.35 !important;
    transition: background .16s ease, border-color .16s ease,
                transform .1s ease, box-shadow .16s ease !important;
}
[class*="st-key-qr_card_"] div.stButton > button:hover {
    background: #FFFDF9 !important;
    border-color: #2C1F33 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(44, 31, 51, 0.11) !important;
}
[class*="st-key-qr_card_"] div.stButton > button:active {
    transform: scale(0.985) translateY(0) !important;  /* umpan balik instan */
    background: #F4EADA !important;
    box-shadow: 0 1px 2px rgba(44, 31, 51, 0.08) !important;
}
[class*="st-key-qr_card_"] div.stButton > button:focus-visible {
    outline: 2px solid #2C1F33 !important;
    outline-offset: 2px !important;
}

/* --- keadaan TERPILIH (multi-pilih, tombol primary) --- */
[class*="st-key-qr_card_"] div.stButton > button[kind="primary"],
[class*="st-key-qr_card_"] [data-testid="stBaseButton-primary"] {
    background: #2C1F33 !important;
    border-color: #2C1F33 !important;
    color: #FBF6EC !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(44, 31, 51, 0.20) !important;
}
[class*="st-key-qr_card_"] div.stButton > button[kind="primary"]:hover {
    background: #40304A !important;
    border-color: #40304A !important;
}

/* --- tombol "Kirim pilihan" pada kartu multi-pilih --- */
[class*="st-key-qr_send_"] div.stButton > button {
    margin-top: 4px !important;
    background: #EFE4D2 !important;
    border-style: dashed !important;
    text-align: center !important;
    justify-content: center !important;
    font-weight: 600 !important;
}
[class*="st-key-qr_send_"] div.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* --- jarak antar tombol --- */
[class*="st-key-qr_card_"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    margin-bottom: 10px !important;
}
[class*="st-key-qr_card_"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
[class*="st-key-qr_card_"] div.stButton { margin: 0 !important; }

/* --- layar sempit: paksa satu tombol per baris --- */
@media (max-width: 640px) {
    [class*="st-key-qr_card_"] [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    [class*="st-key-qr_card_"] [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [class*="st-key-qr_card_"] { max-width: 100%; }
}

/* --- kartu lama (sudah dijawab): jejak abu, tidak bisa diklik --- */
.qr-row-done { display: flex; flex-wrap: wrap; gap: 6px; }
.qr-chip-done {
    font-size: 0.78rem;
    color: #948AA0;
    background: rgba(44, 31, 51, 0.05);
    border: 1px solid #E2D6C2;
    border-radius: 8px;
    padding: 4px 10px;
}
/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 12px !important;
    color: #2C1F33 !important;
}

/* PENTING soal ukuran font footer:
   Streamlit punya aturan bawaan [data-testid="stMarkdownContainer"] p {...}
   yang spesifisitasnya (0,1,1) LEBIH TINGGI daripada .trinity-foot (0,1,0),
   jadi kalau ditulis pakai kelas saja, font-size-nya selalu kalah dan
   terlihat "tidak mau mengecil". Karena itu selektornya dinaikkan
   (elemen p + wadah markdown) dan diberi !important.
   >>> UBAH ANGKA DI SINI untuk mengatur ukuran footer <<< */
/* >>> ATUR POSISI FOOTER DI SINI <<<
   --foot-x : geser mendatar. Minus = ke kiri, plus = ke kanan.
   --foot-y : geser tegak.    Minus = ke atas, plus = ke bawah. */
:root {
    --foot-x: 100px;
    --foot-y: 0px;
}

.trinity-foot,
p.trinity-foot,
[data-testid="stMarkdownContainer"] p.trinity-foot,
[data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] p.trinity-foot {
    /* display:block + lebar penuh -> text-align:center benar-benar bekerja.
       Tanpa ini footer bisa terlihat menempel ke kiri. */
    display: block !important;
    width: 100% !important;
    transform: translate(var(--foot-x), var(--foot-y));
    text-align: center !important;
    color: #7E7387 !important;
    font-size: 12px !important;      /* halaman awal (sebelum mulai chat) */
    line-height: 1.5 !important;
    margin-top: -7px !important;
    margin-bottom: 0 !important;
    font-family: 'Inter', sans-serif !important;
    -webkit-text-size-adjust: 100%;  /* cegah browser HP membesarkan teks kecil */
    text-size-adjust: 100%;
}

/* versi saat chat berjalan: lebih kecil lagi dari versi halaman awal */
.trinity-foot.in-chat,
p.trinity-foot.in-chat,
[data-testid="stMarkdownContainer"] p.trinity-foot.in-chat,
[data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] p.trinity-foot.in-chat {
    font-size: 11px !important;       /* saat chat sudah berjalan */
    color: #827788 !important;
    margin-top: 22px !important;
}

/* logo kecil di dalam footer ikut menyesuaikan */
.trinity-foot .logo-foot {
    width: 1.2em !important;
    height: 1.2em !important;
}

/* ============ HALAMAN BARU (Artefak · Pengaturan · Bahasa ·
   Bantuan · Trinity Pro · Aplikasi · Trinity Kursus · Pelajari) ============ */
/* --- baris akun + menu titik tiga --- */
.sb-account {
    width: 230px !important;
    max-width: 230px !important;
    padding-right: 42px;            /* ruang untuk tombol menu ⋯ */
    pointer-events: none;           /* teksnya saja; tombol di sebelahnya */
}
.st-key-sb_account [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-sb_account [data-testid="stColumn"]:first-child { padding-right: 0 !important; }
/* >>> ATUR POSISI TOMBOL TITIK TIGA (menu akun) DI SINI <<<
   --acct-x : jarak dari tepi KIRI layar.
   --acct-y : jarak dari DASAR layar. Perbesar = naik.
   Catatan: dipakai position: fixed !important supaya tidak ikut hanyut
   mengikuti daftar menu sidebar (itu penyebab tombolnya tadi nyangkut
   di bawah "Unduh Chat"). */
:root {
    --acct-x: 190px;
    --acct-y: -60px;
}

.st-key-acct_menu {
    position: fixed !important;
    left: var(--acct-x) !important;
    bottom: var(--acct-y) !important;
    top: auto !important;
    right: auto !important;
    width: 32px !important;
    margin: 0 !important;
    z-index: 999996 !important;
}
/* Sembunyikan baris kartu nama user saat sidebar tertutup */
section[data-testid="stSidebar"][aria-expanded="false"] .sb-account,
section[data-testid="stSidebar"][aria-expanded="false"] .st-key-acct_menu,
section[data-testid="stSidebar"][aria-expanded="false"] .st-key-sb_account {
    display: none !important;
    visibility: hidden !important;
}
.st-key-acct_menu [data-testid="stPopover"] > div { width: auto !important; }
.st-key-acct_menu button[data-testid="stPopoverButton"],
.st-key-acct_menu [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    color: #6B6172 !important;
    width: 32px !important; min-width: 32px !important; height: 32px !important;
    border-radius: 8px !important; padding: 0 !important;
    display: grid !important; place-items: center !important;
}
.st-key-acct_menu button:hover {
    background: #E0D2BB !important; color: #2C1F33 !important;
}
.st-key-acct_menu button svg { width: 20px !important; height: 20px !important; }

/* --- judul halaman --- */
.page-head {
    display: flex; align-items: flex-start; gap: 14px;
    margin: 4px 0 18px;
}
.page-head-icon {
    width: 40px; height: 40px; flex-shrink: 0;
    border-radius: 12px;
    background: #E0D2BB; border: 1px solid #CDBFA8;
    display: grid; place-items: center;
    color: #4A3559;
}
.page-head-icon [data-testid="stIconMaterial"],
.page-head-icon span[data-testid="stIconMaterial"] { font-size: 21px !important; }
/* Ikon Material yang kita buat sendiri lewat mi() (dipakai di dalam HTML,
   karena sintaks ikon material tidak diterjemahkan Streamlit di dalam HTML).
   Ukurannya disamakan dengan ikon bawaan Streamlit di posisi yang sama. */
.page-head-icon .mi { font-size: 21px; }
.cap-row .cap-icon .mi { font-size: 18px; }
.cap-row .cap-state .mi { font-size: 15px; vertical-align: -3px; }
.help-step .step-icon .mi { font-size: 18px; }
.mini-card .mini-icon .mi { font-size: 22px; }
.feat-row .chip-on .mi, .feat-row .chip-off .mi { font-size: 15px; vertical-align: -3px; }
.page-head h2.page-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 600; color: #1B1220;
    margin: 0 0 2px; line-height: 1.15; letter-spacing: -0.01em;
}
.page-head p.page-sub {
    margin: 0; font-size: 0.9rem; color: #6B6172; line-height: 1.45;
}

/* --- kartu kategori berbentuk PERSEGI (halaman Artefak & Trinity kursus) ---
   Susunan: IKON BESAR di atas, lalu judul, lalu deskripsi kecil — semua
   di tengah. Ikon sengaja jauh lebih besar daripada teksnya. */
button[kind="secondary"] > div > p > strong,
div.stButton > button p strong { color: #2C1F33; }
.st-key-cat_app button, .st-key-cat_doc button, .st-key-cat_game button,
.st-key-cat_prod button, .st-key-cat_kre button, .st-key-cat_quiz button,
.st-key-cat_new button,
[class*="st-key-kurs_"] button {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 18px !important;
    padding: 18px 14px !important;
    /* PERSEGI: tinggi mengikuti lebar, dibatasi agar tidak raksasa */
    aspect-ratio: 1 / 1 !important;
    width: 100% !important;
    max-width: 220px !important;
    min-height: 0 !important;
    height: auto !important;
    margin: 0 auto !important;
    /* isi ditumpuk vertikal & dipusatkan */
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    gap: 0 !important;
    transition: border-color .16s ease, background .16s ease, transform .16s ease;
}
.st-key-cat_app button:hover, .st-key-cat_doc button:hover,
.st-key-cat_game button:hover, .st-key-cat_prod button:hover,
.st-key-cat_kre button:hover, .st-key-cat_quiz button:hover,
.st-key-cat_new button:hover,
[class*="st-key-kurs_"] button:hover {
    border-color: #8B7499 !important;
    background: #F7ECD9 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(44,31,51,0.09) !important;
}
[class*="st-key-cat_"] button [data-testid="stMarkdownContainer"],
[class*="st-key-kurs_"] button [data-testid="stMarkdownContainer"] {
    width: 100%;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
[class*="st-key-cat_"] button p, [class*="st-key-kurs_"] button p {
    white-space: normal !important;
    line-height: 1.3 !important;
    text-align: center !important;
    margin: 0 !important;
}
/* IKON: paling besar, jadi baris tersendiri di paling atas */
[class*="st-key-cat_"] button span[role="img"],
[class*="st-key-kurs_"] button span[role="img"] {
    display: block !important;
    font-size: 2.7rem !important;
    line-height: 1 !important;
    color: #4A3559 !important;
    margin: 0 0 12px !important;
    vertical-align: baseline !important;
}
/* judul: sedang, tebal */
[class*="st-key-cat_"] button p strong, [class*="st-key-kurs_"] button p strong {
    font-size: 0.98rem;
    font-weight: 600;
    display: block;
    margin-bottom: 6px;
}
/* deskripsi: paling kecil & abu (sintaks "small" tidak ada di Streamlit) */
[class*="st-key-cat_"] button .stMarkdownColoredText,
[class*="st-key-kurs_"] button .stMarkdownColoredText {
    display: block;
    font-size: 0.78rem;
    line-height: 1.35;
}

/* --- kartu kosong --- */
.empty-card {
    background: #F2E8D6; border: 1px dashed #CDBFA8;
    border-radius: 14px; padding: 18px;
    color: #6B6172; font-size: 0.9rem; line-height: 1.55;
    margin: 2px 0 16px;
}

/* --- hero halaman --- */
.trinity-hero {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 18px;
    padding: 22px; display: flex; gap: 18px; align-items: center;
    margin-bottom: 16px;
}
.trinity-hero > div:first-child { flex-shrink: 0; }
.trinity-hero .logo-greeting { width: 42px; height: 42px; }
.trinity-hero .hero-text h1 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.8rem; font-weight: 600; color: #1B1220;
    margin: 0 0 6px; letter-spacing: -0.01em;
}
.trinity-hero .hero-text p {
    margin: 0; color: #6B6172; font-size: 0.92rem; line-height: 1.55;
}

/* --- judul bagian di dalam halaman --- */
.set-section {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.06rem; font-weight: 600; color: #2C1F33;
    margin: 22px 0 10px;
}

/* --- kartu kemampuan --- */
.cap-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 6px 14px; margin: 4px 0 8px;
}
.cap-row {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 0; border-bottom: 1px solid #E7D9C1;
    font-size: 0.9rem;
}
.cap-row:last-child { border-bottom: none; }
.cap-row .cap-icon { color: #4A3559; display: grid; place-items: center; width: 22px; }
.cap-row .cap-name { flex: 1; color: #2C1F33; }
.cap-row .cap-state {
    display: inline-flex; align-items: center; gap: 6px;
    color: #7E7387; font-size: 0.82rem;
}

/* --- baris fitur / status kecil --- */
.feat-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 9px 2px; font-size: 0.88rem; color: #2C1F33;
    border-bottom: 1px solid #E7D9C1;
}
.feat-row:last-child { border-bottom: none; }
.chip-on, .chip-off {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.76rem; font-weight: 600;
    padding: 2px 8px; border-radius: 99px; white-space: nowrap;
}
.chip-on { background: #E4EAD8; color: #3F6B33; }
.chip-off { background: #E7DBC6; color: #7D7484; }

/* --- kartu paket (Trinity Pro) --- */
.plan-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 16px;
    padding: 20px; height: 100%; box-sizing: border-box;
}
.plan-card.is-pro {
    border-color: #2C1F33; background: #F7EBD6;
    box-shadow: 0 6px 22px rgba(44,31,51,0.14);
}
.plan-name {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.2rem; font-weight: 600; color: #1B1220;
}
.plan-price {
    font-size: 1.75rem; font-weight: 700; color: #4A3559;
    margin: 6px 0 2px; letter-spacing: -0.02em;
}
.plan-note { font-size: 0.8rem; color: #7E7387; margin-bottom: 12px; }
.feat-list { margin-top: 4px; }

/* --- memori --- */
.mem-item {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #2C1F33; margin-bottom: 6px;
}

/* --- daftar bahasa --- */
.lang-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 4px 14px;
}
.lang-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid #E7D9C1; font-size: 0.9rem;
}
.lang-row:last-child { border-bottom: none; }
.lang-row .flag { font-size: 1.15rem; line-height: 1; }
.lang-row .lang-name {
    flex: 1; color: #2C1F33; font-weight: 500;
    display: flex; flex-direction: column;
}
.lang-row .lang-native { font-size: 0.76rem; color: #7E7387; font-weight: 400; }
.lang-row .lang-level { display: inline-flex; align-items: center; gap: 6px; }

/* --- langkah bantuan & tips --- */
.help-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; font-size: 0.9rem; color: #2C1F33; line-height: 1.5;
}
.help-step .step-no {
    width: 24px; height: 24px; flex-shrink: 0;
    border-radius: 50%; background: #E0D2BB; color: #4E4553;
    display: grid; place-items: center;
    font-size: 0.74rem; font-weight: 700;
}
.help-step .step-icon { color: #4A3559; padding-top: 2px; }
.tip-row {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 0; font-size: 0.89rem; color: #2C1F33; line-height: 1.5;
}
.tip-row .tip-no {
    width: 22px; height: 22px; flex-shrink: 0; border-radius: 50%;
    background: #DDD2E4; color: #4A3559;
    display: grid; place-items: center; font-size: 0.72rem; font-weight: 700;
}

/* --- mini card (tentang aplikasi) --- */
.mini-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 16px; height: 100%; box-sizing: border-box;
}
.mini-card .mini-icon { color: #4A3559; margin-bottom: 8px; }
.mini-card .mini-title { font-weight: 600; color: #2C1F33; margin-bottom: 4px; }
.mini-card .mini-desc { font-size: 0.84rem; color: #6B6172; line-height: 1.5; }

/* --- kartu ponsel (halaman Dapatkan aplikasi) --- */
.phone-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 22px;
    padding: 30px 20px; text-align: center;
}
.phone-card .logo-greeting { width: 54px; height: 54px; margin: 0 auto 12px; }
.phone-card .phone-name { font-weight: 600; color: #2C1F33; }
.phone-card .phone-tag { font-size: 0.78rem; color: #7E7387; margin-top: 2px; }

/* --- baris modul kursus --- */
.mod-row {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #2C1F33; margin-bottom: 6px;
}

/* --- tab Pengaturan: rapikan --- */
[data-baseweb="tab-list"] { gap: 4px !important; border-bottom: 1px solid #DBCEB9 !important; }
[data-baseweb="tab"] {
    font-size: 0.86rem !important; padding: 8px 10px !important;
    color: #6B6172 !important; background: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] { color: #2C1F33 !important; font-weight: 600 !important; }
[data-baseweb="tab-highlight"] { background-color: #2C1F33 !important; }
/* ====================================================================
   ANIMASI TRINITY
   --------------------------------------------------------------------
   - Setiap tombol muncul dengan animasi mengembang (pop) yang halus.
   - Hover tombol: terangkat + menyala sedikit.
   - Klik tombol: menekan (scale mengecil sesaat).
   - Tombol "Top up / Trinity Pro" punya animasi mengembang lebih besar
     + kilau cahaya menyapu setelah muncul.
   - Saat pindah halaman: judul, kartu, baris fitur, dan teks masuk
     dengan fade + naik perlahan (fade-slide).
==================================================================== */

/* Semua tombol: masuk dengan pop halus. Pakai fill-mode `backwards`
   supaya setelah animasi selesai transisi hover normal tetap jalan. */
div.stButton > button,
div.stDownloadButton > button,
[data-testid="stPopover"] > button,
[data-testid="stChatInput"] button {
    animation: trinityBtnIn 0.34s cubic-bezier(0.22, 0.9, 0.32, 1.12) backwards !important;
    transform-origin: center center !important;
}
@keyframes trinityBtnIn {
    0%   { opacity: 0; transform: scale(0.9) translateY(6px); }
    55%  { opacity: 1; transform: scale(1.025) translateY(-1px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* Hover & tekan semua tombol: angkat sedikit lalu menekan saat diklik. */
div.stButton > button,
div.stDownloadButton > button,
[data-testid="stPopover"] > button,
[data-testid="stChatInput"] button {
    transition:
        background 0.16s ease,
        border-color 0.16s ease,
        color 0.16s ease,
        box-shadow 0.18s ease,
        transform 0.16s cubic-bezier(0.22, 0.9, 0.32, 1.12) !important;
}
div.stButton > button:not(:disabled):hover,
div.stDownloadButton > button:not(:disabled):hover,
[data-testid="stPopover"] > button:not(:disabled):hover,
[data-testid="stChatInput"] button:not(:disabled):hover {
    transform: translateY(-1px) scale(1.012);
}
div.stButton > button:not(:disabled):active,
div.stDownloadButton > button:not(:disabled):active,
[data-testid="stPopover"] > button:not(:disabled):active,
[data-testid="stChatInput"] button:not(:disabled):active {
    transform: translateY(0) scale(0.975);
    box-shadow: 0 1px 3px rgba(44, 31, 51, 0.12) !important;
}

/* ===== TOMBOL TOP UP / TRINITY PRO =====
   Muncul lebih dramatis: mengembang dari kecil (0.70) sambil naik,
   lalu diikuti kilau cahaya yang menyapu dari kiri ke kanan. */
[class*="st-key-akun_pro"] button,
[class*="st-key-plan_pro"] button,
[class*="st-key-acct_pro"] button,
[class*="st-key-pel_pro"] button,
button[class*="st-key-akun_pro"],
button[class*="st-key-plan_pro"],
button[class*="st-key-acct_pro"],
button[class*="st-key-pel_pro"] {
    animation: trinityProIn 0.58s cubic-bezier(0.16, 1.1, 0.3, 1) 0.05s backwards !important;
    position: relative !important;
    overflow: hidden !important;
}
@keyframes trinityProIn {
    0% {
        opacity: 0;
        transform: scale(0.68) translateY(14px);
        box-shadow: 0 0 0 rgba(74, 53, 89, 0);
    }
    60% {
        opacity: 1;
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 8px 26px rgba(74, 53, 89, 0.28);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
        box-shadow: 0 2px 10px rgba(44, 31, 51, 0.14);
    }
}
[class*="st-key-akun_pro"] button::after,
[class*="st-key-plan_pro"] button::after,
[class*="st-key-acct_pro"] button::after,
[class*="st-key-pel_pro"] button::after,
button[class*="st-key-akun_pro"]::after,
button[class*="st-key-plan_pro"]::after,
button[class*="st-key-acct_pro"]::after,
button[class*="st-key-pel_pro"]::after {
    content: "";
    position: absolute;
    top: -55%; bottom: -55%;
    left: 0; width: 55%;
    background: linear-gradient(
        100deg,
        rgba(255,255,255,0) 0%,
        rgba(255,255,255,0.62) 50%,
        rgba(255,255,255,0) 100%
    );
    filter: blur(1px);
    transform: translateX(-140%) skewX(-18deg);
    animation: trinitySweep 1.35s ease 0.5s backwards;
    pointer-events: none;
}
@keyframes trinitySweep {
    0%   { transform: translateX(-140%) skewX(-18deg); }
    55%, 100% { transform: translateX(340%) skewX(-18deg); }
}

/* ===== FADE TEXT SAAT PINDAH HALAMAN =====
   Heading, kartu, baris fitur, dan teks lain masuk dengan fade + naik
   perlahan. Karena setiap pindah halaman Streamlit merender ulang, CSS
   ini otomatis "memutar ulang" animasi pada halaman yang baru dibuka. */
.page-head,
.trinity-hero,
.trinity-greeting,
.trinity-sub,
.page-title,
.page-sub,
.set-section,
.plan-card,
.mini-card,
.phone-card,
.lang-card,
.cap-card,
.mem-item,
.mod-row,
.empty-card,
.icon-bar,
.help-step,
.tip-row,
.feat-row,
.cap-row,
.lang-row {
    animation: trinityPageIn 0.42s ease 0.03s backwards !important;
}
@keyframes trinityPageIn {
    from {
        opacity: 0;
        transform: translateY(9px);
        filter: blur(2px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }
}

/* Kartu kategori (Artefak / Kursus) & kartu lain ikut fade masuk agar
   seluruh isi halaman terasa "berbuka" sekali per pindah halaman. */
[class*="st-key-cat_"] button,
[class*="st-key-kurs_"] button {
    animation: trinityCardIn 0.45s ease backwards !important;
}
@keyframes trinityCardIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(12px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* Aksesibilitas: matikan animasi bagi pengguna yang memintanya */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.001ms !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
