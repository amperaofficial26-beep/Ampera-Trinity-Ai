# -*- coding: utf-8 -*-
"""Layout dashboard chat (sidebar kiri, panel kanan, topbar, area chat, responsive) sebelum posisi chat input final

Dipecah dari styles.py asli (baris 3719-4790), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ====================================================================
   LAYOUT DASHBOARD CHAT — mengikuti referensi, tetapi tetap memakai
   warna tema Trinity yang sedang aktif (var(--tr-*)). Tidak ada gambar
   baru; avatar aplikasi adalah huruf berbasis CSS.
==================================================================== */
.tr-chat-layout {
    display: none !important;
}

[data-testid="stMainBlockContainer"]:has(.tr-chat-layout) {
    max-width: none !important;
    width: 100% !important;
    padding-top: 96px !important;
    padding-left: 28px !important;
    padding-right: 340px !important;
    padding-bottom: 10rem !important;
}

[data-testid="stMainBlockContainer"]:has(.tr-chat-layout) > [data-testid="stVerticalBlock"] {
    max-width: min(880px, calc(100vw - 230px - 380px - 48px)) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stMainBlockContainer"]:has(.tr-chat-layout.tr-fresh-home) {
    padding-top: 84px !important;
}

/* Topbar utama */
.st-key-chat_topbar {
    position: fixed !important;
    top: 16px !important;
    left: 252px !important;
    right: 500px !important;
    z-index: 999990 !important;
    margin: 0 !important;
    padding: 10px !important;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 78%, var(--tr-accent, #4A3559) 22%) !important;
    border-radius: calc(var(--tr-radius, 12px) + 14px) !important;
    background: color-mix(in srgb, var(--tr-surface, #F2E8D6) 88%, transparent) !important;
    box-shadow: 0 16px 42px color-mix(in srgb, var(--tr-text, #2C1F33) 13%, transparent) !important;
    backdrop-filter: blur(18px) saturate(1.15) !important;
    -webkit-backdrop-filter: blur(18px) saturate(1.15) !important;
}

.stApp:has(section[data-testid="stSidebar"][aria-expanded="false"]) .st-key-chat_topbar {
    left: 76px !important;
}

.st-key-chat_topbar [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 10px !important;
}

.st-key-chat_topbar [data-testid="stColumn"] {
    min-width: 0 !important;
}

.tr-brand-profile,
.tr-assistant-pill,
.tr-user-pill {
    min-height: 48px;
    display: flex;
    align-items: center;
    border-radius: calc(var(--tr-radius, 12px) + 10px);
}

.tr-brand-profile {
    gap: 10px;
    padding: 5px 6px;
}

.tr-brand-avatar,
.tr-pill-icon,
.tr-user-avatar {
    flex: 0 0 auto;
    display: grid;
    place-items: center;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 70%, var(--tr-accent, #4A3559) 30%);
    background: color-mix(in srgb, var(--tr-accent, #4A3559) 14%, var(--tr-surface, #F2E8D6));
    color: var(--tr-accent, #4A3559);
    box-shadow: inset 0 1px 0 color-mix(in srgb, white 48%, transparent);
}

.tr-brand-avatar {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.35rem;
    font-weight: 800;
}

.tr-brand-name {
    color: var(--tr-text, #2C1F33);
    font-weight: 800;
    letter-spacing: -0.025em;
    font-size: 1.05rem;
}

.tr-brand-sub,
.tr-pill-sub,
.tr-user-copy small {
    color: var(--tr-text2, #6B6172);
    font-size: .76rem;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tr-assistant-pill {
    gap: 10px;
    padding: 6px 13px;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 72%, var(--tr-accent, #4A3559) 28%);
    background: color-mix(in srgb, var(--tr-bg, #E8DCC8) 30%, var(--tr-surface, #F2E8D6) 70%);
}

.tr-pill-icon {
    width: 36px;
    height: 36px;
    border-radius: 13px;
}

.tr-pill-title {
    color: var(--tr-text, #2C1F33);
    font-size: .93rem;
    font-weight: 800;
}

.tr-user-pill {
    gap: 8px;
    padding: 6px 9px;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 86%, transparent);
    background: color-mix(in srgb, var(--tr-surface, #F2E8D6) 68%, transparent);
}

.tr-user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-size: .82rem;
    font-weight: 800;
}
/* Panel fitur kanan */
.st-key-chat_right_rail {
    position: fixed !important;
    top: 92px !important;
    right: 18px !important;
    bottom: 22px !important;
    width: 286px !important;
    z-index: 999980 !important;
    margin: 0 !important;
    padding: 14px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 80%, var(--tr-accent, #4A3559) 20%) !important;
    border-radius: calc(var(--tr-radius, 12px) + 14px) !important;
    background: color-mix(in srgb, var(--tr-surface, #F2E8D6) 90%, transparent) !important;
    box-shadow: 0 16px 42px color-mix(in srgb, var(--tr-text, #2C1F33) 12%, transparent) !important;
    backdrop-filter: blur(18px) saturate(1.12) !important;
    -webkit-backdrop-filter: blur(18px) saturate(1.12) !important;
}

.st-key-chat_right_rail [data-testid="stVerticalBlock"] {
    gap: 8px !important;
}

.st-key-chat_right_rail [data-testid="stHorizontalBlock"] {
    gap: 8px !important;
}

.tr-rail-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 2px 1px 8px;
    color: var(--tr-text, #2C1F33);
    font-size: .94rem;
    font-weight: 800;
}

.tr-rail-title-row.with-link {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 78%, transparent);
}

.tr-rail-title-row small {
    color: var(--tr-accent, #4A3559);
    font-size: .72rem;
    font-weight: 700;
}

.tr-rail-empty {
    padding: 12px;
    border: 1px dashed var(--tr-border, #DBCEB9);
    border-radius: var(--tr-radius, 12px);
    color: var(--tr-text2, #6B6172);
    font-size: .84rem;
    text-align: center;
}

/* ================================================================
   PANEL KANAN — SEMUA KARTU LEBIH TERANG DARI LATAR
================================================================ */


/* ================================================================
   BASE SEMUA KARTU
================================================================ */

.st-key-chat_right_rail div.stButton > button {
    width: 100% !important;

    justify-content: flex-start !important;

    text-align: left !important;

    white-space: normal !important;

    border-radius:
        calc(var(--tr-radius, 12px) + 4px)
        !important;

    color:
        var(--tr-text, #2C1F33)
        !important;

    border:
        1px solid
        rgba(107, 97, 114, 0.10)
        !important;

    box-shadow:
        0 2px 8px
        rgba(44, 31, 51, 0.035)
        !important;

    transition:
        transform .18s ease,
        border-color .18s ease,
        background .18s ease,
        box-shadow .18s ease
        !important;
}


/* ================================================================
   FITUR CEPAT
================================================================ */


/* Chat AI — soft violet */
.st-key-rail_quick_chat div.stButton > button {
    background: #F1EAF5 !important;
    border-color: #E3D7EA !important;
}


/* Multi AI — soft blue */
.st-key-rail_quick_multi div.stButton > button {
    background: #EAF0F5 !important;
    border-color: #DCE6ED !important;
}


/* Generate Gambar — soft peach */
.st-key-rail_quick_image div.stButton > button {
    background: #F5ECE4 !important;
    border-color: #E9DDD3 !important;
}


/* Upload File — soft green */
.st-key-rail_quick_upload div.stButton > button {
    background: #EBF2E8 !important;
    border-color: #DDE8D8 !important;
}


/* ================================================================
   MODEL AI POPULER
   ------------------------------------------------
   Setiap kartu model dibuat terang, tetapi sedikit berbeda
   supaya panel tidak terlihat monoton.
================================================================ */


/* Model 1 — warm cream */
[class*="st-key-rail_model_"]:nth-of-type(1)
div.stButton > button {
    background: #F3ECDD !important;
    border-color: #E7DDCB !important;
}


/* Model 2 — soft violet */
[class*="st-key-rail_model_"]:nth-of-type(2)
div.stButton > button {
    background: #F0EAF4 !important;
    border-color: #E2D8E8 !important;
}


/* Model 3 — soft blue */
[class*="st-key-rail_model_"]:nth-of-type(3)
div.stButton > button {
    background: #EAF0F4 !important;
    border-color: #DCE4EA !important;
}


/* Model 4 — soft green */
[class*="st-key-rail_model_"]:nth-of-type(4)
div.stButton > button {
    background: #ECF1E9 !important;
    border-color: #DDE5D9 !important;
}


/* ================================================================
   CHAT TERBARU
================================================================ */


/* Recent 1 */
[class*="st-key-rail_recent_"]:nth-of-type(1)
div.stButton > button {
    background: #F1EBDD !important;
    border-color: #E5DCCB !important;
}


/* Recent 2 */
[class*="st-key-rail_recent_"]:nth-of-type(2)
div.stButton > button {
    background: #EEEAF2 !important;
    border-color: #E0D8E6 !important;
}


/* Recent 3 */
[class*="st-key-rail_recent_"]:nth-of-type(3)
div.stButton > button {
    background: #EAEFF3 !important;
    border-color: #DCE4EA !important;
}


/* ================================================================
   HOVER
================================================================ */

.st-key-chat_right_rail div.stButton > button:hover {
    transform: translateY(-1px) !important;

    box-shadow:
        0 5px 14px
        rgba(44, 31, 51, 0.07)
        !important;
}


/* Quick feature hover */

.st-key-rail_quick_chat div.stButton > button:hover {
    background: #E9DEF0 !important;
    border-color: #D6C5E0 !important;
}

.st-key-rail_quick_multi div.stButton > button:hover {
    background: #DEE9F1 !important;
    border-color: #CADCE8 !important;
}

.st-key-rail_quick_image div.stButton > button:hover {
    background: #F0DFD2 !important;
    border-color: #DEC7B8 !important;
}

.st-key-rail_quick_upload div.stButton > button:hover {
    background: #DFEADB !important;
    border-color: #CDDCC7 !important;
}


/* ================================================================
   MODEL + CHAT TERBARU — HOVER
================================================================ */

[class*="st-key-rail_model_"] div.stButton > button:hover,
[class*="st-key-rail_recent_"] div.stButton > button:hover {
    background: #E8DFD2 !important;

    border-color:
        rgba(74, 53, 89, 0.16)
        !important;
}
.st-key-chat_right_rail div.stButton > button:hover {
    transform: translateY(-1px) !important;
    border-color: var(--tr-accent, #4A3559) !important;
    background: var(--tr-bubble, #E0D2BB) !important;
}

[class*="st-key-rail_quick_"] div.stButton > button {
    min-height: 92px !important;
    align-items: flex-start !important;
    padding: 12px !important;
}

[class*="st-key-rail_model_"] div.stButton > button,
[class*="st-key-rail_recent_"] div.stButton > button {
    min-height: 50px !important;
    padding: 9px 11px !important;
}
/* Sidebar lebih mendekati dashboard: brand terlihat sebagai profil app,
   tanpa gambar/mascot tambahan. */
.sb-brand {
    padding: 12px 10px 14px !important;
    margin: 0 0 8px !important;
    border: 1px solid color-mix(in srgb, var(--tr-border, #DBCEB9) 82%, transparent);
    border-radius: calc(var(--tr-radius, 12px) + 6px);
    background: color-mix(in srgb, var(--tr-surface, #F2E8D6) 70%, transparent);
}

section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: var(--tr-accent, #4A3559) !important;
    border: 1px solid var(--tr-accent, #4A3559) !important;
    color: var(--tr-on-accent, #FFFFFF) !important;
}

section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p,
section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {
    color: var(--tr-on-accent, #FFFFFF) !important;
}

@media (max-width: 1180px) {
    .st-key-chat_right_rail {
        display: none !important;
    }

    .st-key-chat_topbar {
        right: 18px !important;
    }

    [data-testid="stMainBlockContainer"]:has(.tr-chat-layout) {
        padding-right: 28px !important;
    }

    [data-testid="stMainBlockContainer"]:has(.tr-chat-layout) > [data-testid="stVerticalBlock"] {
        max-width: min(880px, calc(100vw - 230px - 56px)) !important;
    }
}

@media (max-width: 820px) {
    .st-key-chat_topbar {
        display: none !important;
    }

    [data-testid="stMainBlockContainer"]:has(.tr-chat-layout),
    [data-testid="stMainBlockContainer"]:has(.tr-chat-layout.tr-fresh-home) {
        padding-top: 1.2rem !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }

    [data-testid="stMainBlockContainer"]:has(.tr-chat-layout) > [data-testid="stVerticalBlock"] {
        max-width: 100% !important;
    }
}
/* Penyesuaian setelah uji tampilan:
   - Topbar dibuat lebih kecil/ringan.
   - Dock input chat mengikuti ruang kosong antara sidebar kiri dan panel kanan.
   - Saat sidebar ditutup, dock otomatis bergeser lebih ke kiri supaya tidak
     tertutup panel kanan. */
.stApp:has(.tr-chat-layout) {
    --chat-width: min(42rem, calc(100vw - 230px - 356px - 72px));
    --chat-shift: 100px;
}

.stApp:has(.tr-chat-layout):has(section[data-testid="stSidebar"][aria-expanded="false"]) {
    --chat-width: min(42rem, calc(100vw - 76px - 356px - 72px));
    --chat-shift: -140px;
}

.stApp:has(.tr-chat-layout) [data-testid="stBottomBlockContainer"] {
    width: var(--chat-width) !important;
    max-width: var(--chat-width) !important;
}

/* Saat belum ada chat, [data-testid="stBottom"] juga memakai --chat-shift.
   Hindari geser ganda dengan menetralkan transform di kartu dalamnya. */
.stApp:has(.tr-chat-layout.tr-fresh-home) [data-testid="stBottomBlockContainer"] {
    transform: translateX(0) !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar {
    top: 12px !important;
    padding: 6px 8px !important;
    border-radius: calc(var(--tr-radius, 12px) + 10px) !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-profile,
.stApp:has(.tr-chat-layout) .tr-assistant-pill,
.stApp:has(.tr-chat-layout) .tr-user-pill {
    min-height: 38px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-avatar {
    width: 32px !important;
    height: 32px !important;
    border-radius: 11px !important;
    font-size: 1.05rem !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon {
    width: 30px !important;
    height: 30px !important;
    border-radius: 10px !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon .mi {
    font-size: 18px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-name,
.stApp:has(.tr-chat-layout) .tr-pill-title {
    font-size: .86rem !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-sub,
.stApp:has(.tr-chat-layout) .tr-pill-sub,
.stApp:has(.tr-chat-layout) .tr-user-copy small {
    font-size: .68rem !important;
}

.stApp:has(.tr-chat-layout) .tr-user-avatar {
    width: 28px !important;
    height: 28px !important;
    font-size: .74rem !important;
}

.stApp:has(.tr-chat-layout) .tr-user-copy b {
    font-size: .78rem !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar div.stButton > button {
    min-height: 38px !important;
    height: 38px !important;
    padding: 4px 10px !important;
    border-radius: calc(var(--tr-radius, 12px) + 5px) !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
    top: 76px !important;
}

[data-testid="stMainBlockContainer"]:has(.tr-chat-layout) {
    padding-top: 78px !important;
}

[data-testid="stMainBlockContainer"]:has(.tr-chat-layout.tr-fresh-home) {
    padding-top: 70px !important;
}

@media (max-width: 1180px) {
    .stApp:has(.tr-chat-layout) {
        --chat-width: min(42rem, calc(100vw - 230px - 72px));
        --chat-shift: 0px;
    }

    .stApp:has(.tr-chat-layout):has(section[data-testid="stSidebar"][aria-expanded="false"]) {
        --chat-width: min(42rem, calc(100vw - 76px - 72px));
        --chat-shift: 0px;
    }
}
/* ================================================================
   OVERRIDE KOLOM ATAS / DASHBOARD CHAT FINAL
   ----------------------------------------------------------------
   Alamat: /home/user/Ampera-Trinity-Ai/styles.py

   Semua ukuran dashboard chat dipatok dari variabel di bawah:
   - sidebar kiri tetap terbuka, lebih sempit, dan tidak scroll
   - kolom atas/topbar tepat di tengah ruang antara sidebar dan panel kanan
   - panel kanan mentok ke atas dan sedikit lebih sempit
   - judul sapaan, area chat, dan input chat ikut pusat ruang tengah
================================================================ */
.stApp:has(.tr-chat-layout) {
    /* ===== ANGKA PATOKAN UTAMA ===== */
    --dash-sidebar: 210px;       /* lebar sidebar kiri */
    --dash-rail: 250px;          /* lebar panel kanan */
    --dash-gap: 18px;            /* jarak sidebar/topbar/panel */
    --dash-top: 10px;            /* jarak atas topbar & panel kanan */
    --dash-bottom: 16px;         /* jarak bawah panel kanan */

    /*
       Rumus ruang tengah:
       sidebar | gap | AREA TENGAH | gap | panel kanan | gap layar

       Kiri area tengah  = lebar sidebar + gap.
       Kanan area tengah = lebar panel kanan + gap antara area tengah dan panel
                           + gap panel ke tepi layar.
    */
    --dash-center-left: calc(var(--dash-sidebar) + var(--dash-gap));
    --dash-center-right: calc(var(--dash-rail) + (var(--dash-gap) * 2));
    --dash-center-width: calc(
        100vw - var(--dash-center-left) - var(--dash-center-right)
    );

    --dash-content-width: min(-100px, var(--dash-center-width));
    --chat-width: min(42rem, var(--dash-center-width));

    /* Bottom dock bawaan Streamlit selalu menghitung dari tengah viewport.
       Shift ini memindahkan input ke tengah AREA TENGAH, bukan tengah layar. */
    --chat-shift: calc(
        (var(--dash-center-left) - var(--dash-center-right)) / 2
    );
}

/* ================================================================
   SIDEBAR KIRI
================================================================ */
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"],
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;

    width: var(--dash-sidebar) !important;
    min-width: var(--dash-sidebar) !important;
    max-width: var(--dash-sidebar) !important;

    transform: none !important;
    margin-left: 0 !important;
    overflow: hidden !important;
}

.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] > div,
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    overflow: hidden !important;
    max-height: 100vh !important;
}

.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] > div {
    padding-left: 0.55rem !important;
    padding-right: 0.55rem !important;
}

/* Sidebar harus tetap terbuka: tombol tutup/buka disembunyikan. */
.stApp:has(.tr-chat-layout) [data-testid="stSidebarCollapseButton"],
.stApp:has(.tr-chat-layout) [data-testid="stSidebarCollapsedControl"],
.stApp:has(.tr-chat-layout) [data-testid="collapsedControl"],
.stApp:has(.tr-chat-layout) [data-testid="stExpandSidebarButton"],
.stApp:has(.tr-chat-layout) button[kind="headerNoPadding"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

.stApp:has(.tr-chat-layout) .sb-account {
    width: var(--dash-sidebar) !important;
    max-width: var(--dash-sidebar) !important;
}

.stApp:has(.tr-chat-layout) .sb-account .name {
    max-width: 116px !important;
}

/* ================================================================
   PANEL KANAN
================================================================ */
.stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
    position: fixed !important;
    top: var(--dash-top) !important;
    right: var(--dash-gap) !important;
    bottom: var(--dash-bottom) !important;

    width: var(--dash-rail) !important;
    padding: 12px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* ================================================================
   KOLOM ATAS / TOPBAR
================================================================ */
.stApp:has(.tr-chat-layout) .st-key-chat_topbar,
.stApp:has(.tr-chat-layout):has(section[data-testid="stSidebar"][aria-expanded="false"])
.st-key-chat_topbar {
    position: fixed !important;
    top: var(--dash-top) !important;

    /* Jarak kiri = sidebar + gap, jarak kanan = panel + 2 gap. */
    left: var(--dash-center-left) !important;
    right: var(--dash-center-right) !important;

    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;

    margin: 0 !important;
    padding: 5px 7px !important;
    border-radius: calc(var(--tr-radius, 12px) + 8px) !important;
    z-index: 999990 !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 7px !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar [data-testid="stColumn"] {
    min-width: 0 !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar .element-container,
.stApp:has(.tr-chat-layout) .st-key-chat_topbar [data-testid="stMarkdownContainer"] {
    margin: 0 !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-profile,
.stApp:has(.tr-chat-layout) .tr-assistant-pill,
.stApp:has(.tr-chat-layout) .tr-user-pill {
    min-height: 34px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-avatar {
    width: 28px !important;
    height: 28px !important;
    border-radius: 9px !important;
    font-size: .92rem !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon {
    width: 27px !important;
    height: 27px !important;
    border-radius: 9px !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon .mi {
    font-size: 16px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-name,
.stApp:has(.tr-chat-layout) .tr-pill-title {
    font-size: .8rem !important;
    line-height: 1.1 !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-sub,
.stApp:has(.tr-chat-layout) .tr-pill-sub {
    font-size: .62rem !important;
    line-height: 1.1 !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-copy,
.stApp:has(.tr-chat-layout) .tr-pill-copy,
.stApp:has(.tr-chat-layout) .tr-user-copy {
    min-width: 0 !important;
    overflow: hidden !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-name,
.stApp:has(.tr-chat-layout) .tr-brand-sub,
.stApp:has(.tr-chat-layout) .tr-pill-title,
.stApp:has(.tr-chat-layout) .tr-pill-sub {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* ================================================================
   AREA CHAT, JUDUL SAPAAN, DAN INPUT
================================================================ */
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"],
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout),
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout.tr-fresh-home) {
    max-width: none !important;
    width: 100% !important;

    padding-top: 74px !important;
    padding-left: var(--dash-center-left) !important;
    padding-right: var(--dash-center-right) !important;
    padding-bottom: 10rem !important;
}

.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout) > [data-testid="stVerticalBlock"] {
    width: var(--dash-content-width) !important;
    max-width: var(--dash-content-width) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

.stApp:has(.tr-chat-layout) .trinity-greeting {
    text-align: center !important;
}

.stApp:has(.tr-chat-layout) [data-testid="stBottomBlockContainer"] {
    width: var(--chat-width) !important;
    max-width: var(--chat-width) !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Saat belum ada chat, posisi vertikal sudah diatur di [data-testid="stBottom"].
   Kartu input bagian dalam tidak perlu geser ganda. */
.stApp:has(.tr-chat-layout.tr-fresh-home) [data-testid="stBottomBlockContainer"] {
    transform: translateX(0) !important;
}

/* ================================================================
   RESPONSIVE: SAAT PANEL KANAN DISEMBUNYIKAN
================================================================ */
@media (max-width: 1180px) {
    .stApp:has(.tr-chat-layout) {
        --dash-rail: 0px;
        --dash-center-right: var(--dash-gap);
        --dash-center-width: calc(
            100vw - var(--dash-center-left) - var(--dash-center-right)
        );
        --dash-content-width: min(720px, var(--dash-center-width));
        --chat-width: min(42rem, var(--dash-center-width));
        --chat-shift: calc(
            (var(--dash-center-left) - var(--dash-center-right)) / 2
        );
    }

    .stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
        display: none !important;
    }
}

/* ====================================================================
   PATOKAN FINAL DASHBOARD CHAT
   --------------------------------------------------------------------
   Satu sumber ukuran untuk halaman chat:
   - sidebar tetap terbuka, lebih sempit, dan tidak scroll
   - panel kanan mentok ke atas dan sedikit lebih sempit
   - topbar, sapaan, area chat, dan input berada di tengah ruang antara
     sidebar kiri dan panel kanan
==================================================================== */
.stApp:has(.tr-chat-layout) {
    --dash-sidebar: 210px;
    --dash-rail: 260px;
    --dash-gap: 18px;
    --dash-top: 12px;
    --dash-bottom: 16px;

    /*
       Ruang tengah dihitung dengan jarak yang sama:
       sidebar | gap | area tengah | gap | panel kanan | gap layar.
       Karena panel kanan sendiri sudah punya right: --dash-gap, sisi kanan
       area tengah perlu menyisakan: lebar panel + 2x gap.
    */
    --dash-center-left: calc(var(--dash-sidebar) + var(--dash-gap));
    --dash-center-right: calc(var(--dash-rail) + var(--dash-gap) + var(--dash-gap));
    --dash-center-width: calc(100vw - var(--dash-center-left) - var(--dash-center-right));

    --dash-content-width: min(720px, var(--dash-center-width));
    --chat-width: min(42rem, var(--dash-center-width));
    --chat-shift: calc((var(--dash-center-left) - var(--dash-center-right)) / 2);
}

/* Sidebar: fixed terbuka, lebih kecil, dan tidak bisa scroll. */
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"],
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"][aria-expanded="false"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;

    width: var(--dash-sidebar) !important;
    min-width: var(--dash-sidebar) !important;
    max-width: var(--dash-sidebar) !important;

    transform: none !important;
    margin-left: 0 !important;
    overflow: hidden !important;
}

.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] > div,
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    overflow: hidden !important;
    max-height: 100vh !important;
}

.stApp:has(.tr-chat-layout) section[data-testid="stSidebar"] > div {
    padding-left: 0.55rem !important;
    padding-right: 0.55rem !important;
}

/* Tombol collapse/expand disembunyikan supaya sidebar tetap terbuka. */
.stApp:has(.tr-chat-layout) [data-testid="stSidebarCollapseButton"],
.stApp:has(.tr-chat-layout) [data-testid="stSidebarCollapsedControl"],
.stApp:has(.tr-chat-layout) [data-testid="collapsedControl"],
.stApp:has(.tr-chat-layout) [data-testid="stExpandSidebarButton"],
.stApp:has(.tr-chat-layout) button[kind="headerNoPadding"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

.stApp:has(.tr-chat-layout) .sb-account {
    width: var(--dash-sidebar) !important;
    max-width: var(--dash-sidebar) !important;
}

.stApp:has(.tr-chat-layout) .sb-account .name {
    max-width: 116px !important;
}

/* Panel kanan: mentok ke atas, sedikit lebih sempit. */
.stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
    top: 68px !important;
    right: var(--dash-gap) !important;
    bottom: var(--dash-bottom) !important;

    width: var(--dash-rail) !important;
    padding: 12px !important;
}

/* Topbar: dipatok tepat di ruang tengah antara sidebar dan panel kanan. */
.stApp:has(.tr-chat-layout) .st-key-chat_topbar,
.stApp:has(.tr-chat-layout):has(section[data-testid="stSidebar"][aria-expanded="false"]) .st-key-chat_topbar {
    position: fixed !important;

    top: var(--dash-top) !important;
    left: var(--dash-center-left) !important;
    right: var(--dash-center-right) !important;

    width: auto !important;
    max-width: none !important;
    min-width: 0 !important;

    margin: 0 !important;
    padding: 5px 7px !important;

    border-radius: calc(var(--tr-radius, 12px) + 8px) !important;
}

.stApp:has(.tr-chat-layout) .st-key-chat_topbar [data-testid="stHorizontalBlock"] {
    gap: 7px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-profile,
.stApp:has(.tr-chat-layout) .tr-assistant-pill,
.stApp:has(.tr-chat-layout) .tr-user-pill {
    min-height: 34px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-avatar {
    width: 28px !important;
    height: 28px !important;
    border-radius: 9px !important;
    font-size: .92rem !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon {
    width: 27px !important;
    height: 27px !important;
    border-radius: 9px !important;
}

.stApp:has(.tr-chat-layout) .tr-pill-icon .mi {
    font-size: 16px !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-name,
.stApp:has(.tr-chat-layout) .tr-pill-title {
    font-size: .8rem !important;
    line-height: 1.1 !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-sub,
.stApp:has(.tr-chat-layout) .tr-pill-sub {
    font-size: .62rem !important;
    line-height: 1.1 !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-copy,
.stApp:has(.tr-chat-layout) .tr-pill-copy {
    min-width: 0 !important;
    overflow: hidden !important;
}

.stApp:has(.tr-chat-layout) .tr-brand-name,
.stApp:has(.tr-chat-layout) .tr-brand-sub,
.stApp:has(.tr-chat-layout) .tr-pill-title,
.stApp:has(.tr-chat-layout) .tr-pill-sub {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Area chat + judul sapaan: benar-benar berada di tengah ruang antar panel. */
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"],
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout),
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout.tr-fresh-home) {
    max-width: none !important;
    width: 100% !important;

    padding-top: 74px !important;
    padding-left: var(--dash-center-left) !important;
    padding-right: var(--dash-center-right) !important;
    padding-bottom: 10rem !important;
}

.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"]:has(.tr-chat-layout) > [data-testid="stVerticalBlock"] {
    width: var(--dash-content-width) !important;
    max-width: var(--dash-content-width) !important;

    margin-left: auto !important;
    margin-right: auto !important;
}

.stApp:has(.tr-chat-layout) .trinity-greeting {
    text-align: center !important;
}

/* Input chat mengikuti pusat ruang antara sidebar dan panel kanan. */
.stApp:has(.tr-chat-layout) [data-testid="stBottomBlockContainer"] {
    width: var(--chat-width) !important;
    max-width: var(--chat-width) !important;

    margin-left: auto !important;
    margin-right: auto !important;
}

/* Saat halaman awal, transform posisi vertikal ada di [data-testid="stBottom"].
   Kartu input bagian dalam tidak perlu geser dua kali. */
.stApp:has(.tr-chat-layout.tr-fresh-home) [data-testid="stBottomBlockContainer"] {
    transform: translateX(0) !important;
}

/* Layar yang panel kanannya disembunyikan: pusat dihitung dari sidebar saja. */
@media (max-width: 1180px) {
    .stApp:has(.tr-chat-layout) {
        --dash-rail: 0px;
        --dash-center-right: var(--dash-gap);

        --dash-content-width: min(
            760px,
            calc(100vw - var(--dash-center-left) - var(--dash-center-right))
        );

        --chat-width: min(
            44rem,
            calc(100vw - var(--dash-center-left) - var(--dash-center-right))
        );

        --chat-shift: calc(var(--dash-sidebar) / 2);
    }

    .stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
        display: none !important;
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
"""
