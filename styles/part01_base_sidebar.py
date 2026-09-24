# -*- coding: utf-8 -*-
"""Palet warna dasar, background app, sidebar (brand, menu, riwayat, tombol unduh)

Dipecah dari styles.py asli (baris 14-702), isi CSS TIDAK diubah.
"""

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&display=swap');

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

    min-height: 27 !important;
    height: 27px !important;

    padding: 0 10px !important;
    line-height: 1 !important;

    position: relative;
    margin: 0 !important;
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
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0px !important; }
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
    font-size: 0.965rem; line-height: 1.6;
    word-break: break-word; overflow-wrap: anywhere;
    white-space: pre-wrap;
}
/* jarak antar paragraf di dalam bubble: spacer kecil terkontrol
   (menggantikan baris kosong penuh yang dulu setinggi 1 baris) */
.bubble .para-gap { height: 0.6em; }
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
/* Hierarki tipografi jawaban Yuki: judul, subjudul, bagian, dan isi. */
.yuki-answer-body {
    display: block;
    width: 100%;
}

.yuki-title {
    margin: 0 0 12px;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.48rem;
    line-height: 1.25;
    font-weight: 650;
    letter-spacing: -0.018em;
}

.yuki-subtitle {
    margin: 18px 0 7px;
    font-size: 1.14rem;
    line-height: 1.35;
    font-weight: 700;
}

.yuki-section {
    margin: 14px 0 5px;
    font-size: 0.98rem;
    line-height: 1.4;
    font-weight: 700;
}

.yuki-paragraph {
    margin: 0 0 10px;
    line-height: 1.72;
}

.yuki-paragraph:last-child {
    margin-bottom: 0;
}

.yuki-list {
    margin: 5px 0 12px;
    padding-left: 1.35rem;
}

.yuki-list li {
    margin: 3px 0;
    padding-left: 2px;
    line-height: 1.62;
}

.yuki-code {
    margin: 10px 0 14px;
    padding: 13px 15px;
    overflow-x: auto;
    border: 1px solid rgba(44,31,51,0.11);
    border-radius: 12px;
    background: rgba(44,31,51,0.045);
    white-space: pre;
    line-height: 1.55;
}

.yuki-inline-code {
    padding: 1px 5px;
    border-radius: 5px;
    background: rgba(44,31,51,0.07);
    font-size: 0.91em;
}

.yuki-answer-body a {
    color: inherit;
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
}
/* Setiap baris jawaban muncul bergiliran dengan interval 0,9 detik. */
.yuki-fade-blur .yuki-reveal-line {
    animation:
        yukiLineFadeBlur
        720ms
        cubic-bezier(.22,.8,.24,1)
        both;

    animation-delay:
        calc(
            var(--yuki-line-index, 0)
            * 0.3s
        );

    transform-origin: left center;
}

.yuki-fade-blur span.yuki-reveal-line {
    display: inline-block;
}

@keyframes yukiLineFadeBlur {
    0% {
        opacity: 0;
        filter: blur(9px);
        transform: translateY(6px);
    }

    55% {
        opacity: .76;
        filter: blur(2px);
    }

    100% {
        opacity: 1;
        filter: blur(0);
        transform: translateY(0);
    }
}

@media (prefers-reduced-motion: reduce) {
    .yuki-fade-blur .yuki-reveal-line {
        animation: none !important;
    }
}

@media (max-width: 640px) {
    .yuki-title {
        font-size: 1.3rem;
    }

    .yuki-subtitle {
        font-size: 1.08rem;
    }
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

"""
