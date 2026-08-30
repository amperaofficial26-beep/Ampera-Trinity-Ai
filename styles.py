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
    width: 260px !important;
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
    top: 8px; right: 20px;
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

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
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
    padding: 6px 10px !important;
    min-height: 34px !important;
    color: #2C1F33 !important;
    font-size: 0.9rem !important;
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
    font-size: 0.9rem !important;
    color: #2C1F33 !important;
    margin: 0 !important;
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
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button {
    font-weight: 400 !important;
    color: #4E4553 !important;
    min-height: 36px !important;
    padding: 6px 12px 6px 12px !important;
    position: relative;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button::before {
    content: "";
    width: 8px; height: 8px;
    border: 1.5px solid #C1B49F;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
    display: inline-block;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button p {
    font-size: 0.98rem !important;
    font-weight: 400 !important;
    color: #4E4553 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
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
    padding: 6px 10px !important;
    min-height: 34px !important;
    color: #2C1F33 !important;
    font-size: 0.9rem !important;
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
    font-size: 0.9rem !important;
    color: #2C1F33 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #DBCEB9; margin: 6px 2px;
}

/* baris akun ala Claude — DIPAKU di dasar layar, selebar sidebar */
.sb-account {
    position: fixed;
    bottom: 0; left: 0;
    width: 260px;              /* = lebar sidebar */
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #DBCEB9;
    background: #EDE2D1;
    z-index: 999995;
    box-sizing: border-box;
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
.sb-account .name { font-size: 1rem; font-weight: 600; color: #2C1F33; }
.sb-account .plan { font-size: 0.88rem; color: #7E7387; font-weight: 400; }
.sb-account .caret { color: #7E7387; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #6B6172; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
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
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #E8DCC8 !important; border: none !important; box-shadow: none !important;
}
/* KARTU GABUNGAN ala Claude: kotak teks + baris kontrol (+, toggle, model)
   dibungkus jadi SATU kartu membulat, supaya tombol + terlihat menyatu
   di dalam kotak chat input (bukan komponen terpisah di bawahnya). */
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
/* kotak input itu sendiri melebur transparan ke dalam kartu gabungan */
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
/* tombol kirim: bulat terracotta khas Claude */
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

/* ---------- baris kontrol DI DALAM kartu, tepat di bawah teks (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [+] [toggle Gambar] [toggle Suara] ......... [Nama Model] */
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
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(3) {
    flex: 1 1 auto !important;
}
/* disclaimer kecil di tengah (ala Claude) */
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #7E7387;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
/* toggle Gambar: teks kecil abu senada */
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #6B6172 !important;
}
/* tombol model = TULISAN BIASA tanpa kotak (ala Claude) */
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
/* hilangkan kotak pembungkus milik popover itu sendiri */
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
.st-key-chat_controls [data-testid="stCheckbox"] {
    margin: 0 !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.78rem !important;
    color: #6B6172 !important;
    white-space: nowrap;
}
/* rapikan tinggi elemen di baris kontrol */
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

/* ---------- MENU ➕ ALA CLAUDE (minimalist: upload saja) ---------- */
/* sembunyikan tombol lampiran bawaan Streamlit (diganti menu ➕);
   drag-drop & paste Ctrl+V tetap berfungsi (ditangani elemen lain) */
[data-testid="stChatInput"] [data-testid="stChatInputFileUploadButton"] {
    display: none !important;
}
/* tombol mic / rekam: bulat putih senada (bukan terracotta) */
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
/* Urutan dok: preview → kotak ketik → tombol + / model */
[data-testid="stBottomBlockContainer"] {
    display: flex !important;
    flex-direction: column !important;
}
.pending-card {
    position: relative;
    width: 72px;
}
.pending-x {
    position: absolute;
    top: 2px;
    right: 2px;
    z-index: 3;
    font-size: 16px;
    line-height: 1;
    color: #2C1F33;
    pointer-events: none;
    text-shadow: 0 0 3px #F2E8D6;
}
[class*="st-key-pending_card_"] {
    position: relative !important;
    width: 72px !important;
}
[class*="st-key-pending_card_"] [data-testid="stVerticalBlock"] {
    position: relative !important;
}
[class*="st-key-pending_card_"] div.stButton,
[class*="st-key-pending_card_"] [data-testid="stButton"] {
    position: absolute !important;
    top: 0 !important;
    right: 0 !important;
    width: 22px !important;
    height: 22px !important;
    z-index: 4 !important;
    margin: 0 !important;
}
[class*="st-key-pending_card_"] button,
[class*="st-key-pending_card_"] [data-testid="stBaseButton-secondary"] {
    min-width: 22px !important;
    width: 22px !important;
    height: 22px !important;
    min-height: 22px !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* tombol ➕ di baris kontrol: lingkaran putih bersih ala Claude, menyatu
   di dalam kartu (tanpa bayangan berlebih karena kartu sudah punya shadow) */
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
    background: #FFFFFF !important;
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

/* ---------- progress bar gambar: % + shimmer (ala Claude) ---------- */
.img-progress {
    padding: 14px 16px 16px;
    background: #F2E8D6;
    border: 1px solid #DBCEB9;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(44,31,51,0.06);
    animation: thinkFadeIn 1s ease both;
    margin: 6px 0 14px;
}
.img-progress-top {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 10px;
}
.img-progress-label {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.9rem; font-weight: 500;
    /* teks shimmer sama seperti thinking */
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
    animation: shimmerSweep 4s linear infinite;
}
.img-progress-label .star {
    -webkit-text-fill-color: #2C1F33;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block; font-size: 1rem;
}
.img-progress-pct {
    font-size: 0.92rem; font-weight: 600; color: #4A3559;
    font-variant-numeric: tabular-nums;
}
.img-progress-track {
    height: 8px; border-radius: 99px;
    background: #E0D2BB; overflow: hidden;
    position: relative;
}
.img-progress-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #2C1F33, #6E5482, #2C1F33);
    background-size: 200% 100%;
    animation: shimmerSweep 2.2s linear infinite;
    transition: width 0.5s ease;
    position: relative;
}
/* kilau putih menyapu di atas bar */
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 12px !important;
    color: #2C1F33 !important;
}

/* ---------- footer ---------- */
.trinity-foot {
    text-align: center; color: #7E7387; font-size: 0.30rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
/* versi saat chat berjalan: lebih kecil lagi dari versi halaman awal */
.trinity-foot.in-chat {
    font-size: 0.5rem;
    color: #827788;
    margin-top: 22px;
}

/* ============ HALAMAN BARU (Artefak · Pengaturan · Bahasa ·
   Bantuan · Trinity Pro · Aplikasi · Trinity Kursus · Pelajari) ============ */
/* --- baris akun + menu titik tiga --- */
.sb-account {
    padding-right: 48px;            /* ruang untuk tombol menu ⋯ */
    border-top: none;
    pointer-events: none;           /* teksnya saja; tombol di sebelahnya */
}
.st-key-sb_account [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-sb_account [data-testid="stColumn"]:first-child { padding-right: 0 !important; }
.st-key-acct_menu {
    position: fixed; bottom: 12px; left: 208px; z-index: 999996;
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
</style>
""",
        unsafe_allow_html=True,
    )
