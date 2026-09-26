# -*- coding: utf-8 -*-
"""Layout Multi AI (hero, chat surface, topbar, input card)

Dipecah dari styles.py asli (baris 7917-8540), isi CSS TIDAK diubah.
"""

CSS = r"""
/* =========================================================
   MULTI AI — LAYOUT FINAL
   ========================================================= */

/*
 * Multi AI tetap memakai tr-chat-layout sebagai marker,
 * tetapi GEOMETRI Multi AI dibuat independen.
 */

.stApp:has(.tr-multi-ai-layout) {
    overflow-x: hidden !important;
}


/* =========================================================
   MAIN AREA
   Jangan diberi width 760px.
   Hero + chat akan mengatur width masing-masing.
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stMainBlockContainer"] {

    width: 100% !important;

    max-width: none !important;

    padding-top: 92px !important;

    padding-left:
        calc(210px + 18px) !important;

    padding-right:
        36px !important;

    padding-bottom:
        9rem !important;
}


/*
 * PENTING:
 * Parent utama dibuat full width.
 *
 * Sebelumnya parent ini dikunci 760px sehingga
 * hero, chat dan elemen lain ikut terikat pada
 * satu geometri.
 */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stMainBlockContainer"]
> [data-testid="stVerticalBlock"] {

    width: 100% !important;

    max-width: none !important;

    margin-left: 0 !important;

    margin-right: 0 !important;
}

.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {
    position: relative !important;

    transform:
        translate(
            var(--multi-input-x),
            var(--multi-input-y)
        ) !important;
}

/* =========================================================
   HERO — JUDUL + DESKRIPSI
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
.agent-hero {
    box-sizing: border-box !important;

    width:
        var(--multi-chat-width) !important;

    min-width:
        var(--multi-chat-width) !important;

    max-width:
        var(--multi-chat-width) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;

    margin-bottom:
        18px !important;

    padding:
        20px 24px !important;

    display:
        flex !important;

    align-items:
        center !important;

    gap:
        16px !important;

    background:
        var(--tr-surface-premium) !important;

    border:
        1px solid
        var(--tr-border-premium) !important;

    border-radius:
        22px !important;

    box-shadow:
        0 10px 30px
        rgba(48, 40, 58, 0.055) !important;

    transform:
        translate(
            var(--multi-hero-x),
            var(--multi-hero-y)
        ) !important;

    position: relative !important;
    top: var(--multi-hero-y) !important;
   
    overflow:
        hidden !important;

    box-sizing:
        border-box !important;

    transition:
        transform .28s ease,
        width .28s ease !important;
}


/* ============================================================
   ICON HERO
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
.agent-hero-icon {
    width:
        48px !important;

    height:
        48px !important;

    min-width:
        48px !important;

    flex:
        0 0 48px !important;

    display:
        flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    border-radius:
        15px !important;

    background:
        linear-gradient(
            145deg,
            #f3d47d,
            #bd8125
        ) !important;

    color:
        #2d2115 !important;

    box-shadow:
        0 7px 18px
        rgba(111, 74, 23, 0.18),
        0 0 18px
        rgba(218, 166, 55, 0.20) !important;

    overflow:
        hidden !important;
}


/* ============================================================
   MATERIAL ICON
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
.agent-hero-icon
.material-symbols-rounded {
    font-size:
        25px !important;

    line-height:
        1 !important;

    font-weight:
        500 !important;

    font-variation-settings:
        'FILL' 1,
        'wght' 500,
        'GRAD' 0,
        'opsz' 24 !important;
}


/* ============================================================
   KONTEN JUDUL + DESKRIPSI
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
.agent-hero-content {
    min-width:
        0 !important;

    flex:
        1 1 auto !important;

    overflow:
        hidden !important;
}


/* ============================================================
   JUDUL
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
.agent-hero h1 {
    margin:
        0 !important;

    padding:
        0 !important;

    color:
        var(--tr-text) !important;

    font-size:
        1.55rem !important;

    line-height:
        1.2 !important;

    font-weight:
        700 !important;

    letter-spacing:
        -0.025em !important;

    font-family:
        "Space Grotesk",
        sans-serif !important;
}


/* ============================================================
   DESKRIPSI
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
.agent-hero p {
    margin:
        7px 0 0 !important;

    padding:
        0 !important;

    color:
        var(--tr-text2) !important;

    font-size:
        0.92rem !important;

    line-height:
        1.5 !important;

    font-weight:
        400 !important;

    font-family:
        "Space Grotesk",
        sans-serif !important;

    max-width:
        100% !important;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .stApp:has(.tr-multi-ai-layout)
    .agent-hero {
        width:
            calc(100vw - 48px) !important;

        min-width:
            0 !important;

        max-width:
            calc(100vw - 48px) !important;

        padding:
            18px 20px !important;
    }

    .stApp:has(.tr-multi-ai-layout)
    .agent-hero h1 {
        font-size:
            1.35rem !important;
    }

    .stApp:has(.tr-multi-ai-layout)
    .agent-hero p {
        font-size:
            0.88rem !important;
    }
}


/* =========================================================
   PRO NOTE
   Tetap mengikuti posisi hero.
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
.agent-pro-note {

    width:
        min(
            760px,
            calc(100vw - 264px)
        ) !important;

    max-width:
        min(
            760px,
            calc(100vw - 264px)
        ) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;
}


/* =========================================================
   MULTI AI — CHAT SURFACE
   Background + pesan = SATU BOX
   ========================================================= */



    /* ukuran FIX */
.stApp:has(.tr-multi-ai-layout)
.st-key-multi_chat_area {

    /* ukuran mengikuti MULTI_CHAT_WIDTH */
    width: var(--multi-chat-width) !important;
    min-width: var(--multi-chat-width) !important;
    max-width: var(--multi-chat-width) !important;

    flex:
        0 0 var(--multi-chat-width) !important;

    box-sizing:
        border-box !important;

    /* posisi */
    margin-left:
        auto !important;

    margin-right:
        auto !important;

    transform:
        translate(
            var(--multi-chat-x),
            var(--multi-chat-y)
        ) !important;

    /* background */
    background:
        var(--tr-surface-premium) !important;

    border:
        1px solid
        var(--tr-border-premium) !important;

    border-radius:
        22px !important;

    box-shadow:
        0 10px 30px
        rgba(48, 40, 58, 0.055) !important;

    padding:
        18px !important;

    overflow:
        hidden !important;

    transition:
        transform .28s ease !important;
}


/* Paksa isi container mengikuti box,
   bukan melebar ke parent */

.stApp:has(.tr-multi-ai-layout)
.st-key-multi_chat_area
[data-testid="stVerticalBlock"] {

    width:
        100% !important;

    min-width:
        0 !important;

    max-width:
        100% !important;

    flex:
        0 0 100% !important;

    box-sizing:
        border-box !important;

    margin:
        0 !important;
}


/* Semua wrapper Streamlit di dalam chat
   tidak boleh menciptakan lebar tambahan */

.stApp:has(.tr-multi-ai-layout)
.st-key-multi_chat_area
.element-container {

    width:
        100% !important;

    max-width:
        100% !important;

    box-sizing:
        border-box !important;
}


/*
 * Input memiliki width + X/Y sendiri.
 */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {

    width:
        var(--multi-input-width) !important;

    max-width:
        calc(100vw - 264px) !important;

    margin-left:
        auto !important;

    margin-right:
        auto !important;

    transform:
        translate(
            var(--multi-input-x),
            var(--multi-input-y)
        ) !important;

    transition:
        transform .28s ease,
        width .28s ease !important;
}


/* =========================================================
   CHAT INPUT VISUAL
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stChatInput"] {

    border:
        1px solid
        var(--tr-border-premium) !important;

    border-radius:
        21px !important;

    background:
        var(--tr-surface-premium) !important;

    box-shadow:
        0 8px 24px
        rgba(48, 40, 58, 0.055) !important;
}


/* =========================================================
   TOPBAR
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
.st-key-chat_topbar {

    position:
        fixed !important;

    top:
        12px !important;

    left:
        calc(210px + 18px) !important;

    right:
        36px !important;

    width:
        auto !important;

    max-width:
        none !important;

    min-width:
        0 !important;

    margin:
        0 !important;

    transform:
        none !important;

    z-index:
        1000 !important;
}


/* =========================================================
   RIGHT PANEL MATI DI MULTI AI
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
.st-key-chat_right_rail {

    display:
        none !important;
}


/* =========================================================
   HORIZONTAL BLOCK
   ========================================================= */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stHorizontalBlock"] {

    overflow-x:
        hidden !important;
}
/* ============================================================
   MULTI AI — INPUT CARD + CHAT INPUT HARUS PRESISI
   ============================================================ */

.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"] {
    width: var(--multi-input-width) !important;
    max-width: var(--multi-input-width) !important;

    margin-left: auto !important;
    margin-right: auto !important;

    transform:
        translate(
            var(--multi-input-x),
            var(--multi-input-y)
        ) !important;

    box-sizing: border-box !important;
}


/* Kolom chat mengikuti ukuran kartu */
.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {
    width: 100% !important;
    max-width: none !important;

    margin-left: 0 !important;
    margin-right: 0 !important;

    transform: none !important;
}

/* ============================================================
   MULTI TRINITY AGENT — LANDING PAGE
   ============================================================ */
.stApp:has(.tr-multi-ai-layout)
[data-testid="stMainBlockContainer"] {
    width: 100% !important;
    max-width: none !important;
    padding: 18px 24px 126px !important;
    box-sizing: border-box !important;
}
.stApp:has(.tr-multi-ai-layout)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    gap: 0 !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-landing-hero {
    width: min(820px, calc(100vw - 48px)) !important;
    margin: 0 auto 18px !important;
    text-align: center !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-landing-logo {
    width: 92px !important;
    height: 92px !important;
    margin: 0 auto 6px !important;
    display: grid !important;
    place-items: center !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-landing-logo img {
    display: block !important;
    width: 92px !important;
    height: 92px !important;
    object-fit: contain !important;
    filter: drop-shadow(0 5px 9px rgba(73, 49, 92, .16)) !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-landing-hero h1 {
    margin: 0 !important;
    color: #30213F !important;
    font-family: "Space Grotesk", sans-serif !important;
    font-size: clamp(1.75rem, 3vw, 2.35rem) !important;
    font-weight: 700 !important;
    letter-spacing: -.045em !important;
    line-height: 1.12 !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-landing-hero p {
    margin: 8px auto 0 !important;
    color: #786D7D !important;
    font-family: "Space Grotesk", sans-serif !important;
    font-size: .82rem !important;
    line-height: 1.55 !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-grid {
    width: min(820px, calc(100vw - 48px)) !important;
    margin: 0 auto 40px !important;
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 12px !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card {
    min-height: 82px !important;
    padding: 11px 12px 10px !important;
    border: 1px solid #E2D6C8 !important;
    border-radius: 9px !important;
    background: rgba(255, 253, 248, .64) !important;
    box-shadow: 0 7px 15px rgba(78, 58, 40, .045) !important;
    text-align: left !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card > span {
    display: block !important;
    margin-bottom: 5px !important;
    color: #51406A !important;
    font-size: 18px !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card strong {
    display: block !important;
    color: #3B2D4A !important;
    font-size: .63rem !important;
    line-height: 1.2 !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card small {
    display: block !important;
    margin-top: 4px !important;
    color: #817686 !important;
    font-size: .54rem !important;
    line-height: 1.35 !important;
}
.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"] {
    width: min(760px, calc(100vw - 48px)) !important;
    max-width: min(760px, calc(100vw - 48px)) !important;
    margin: 0 auto !important;
    transform: none !important;
}
.stApp:has(.tr-multi-ai-layout)
[data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] {
    width: 100% !important;
    max-width: 100% !important;
    transform: none !important;
}
@media (max-width: 760px) {
    .stApp:has(.tr-multi-ai-layout) .multi-feature-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
}
@media (max-width: 520px) {
    .stApp:has(.tr-multi-ai-layout) [data-testid="stMainBlockContainer"] {
        padding-left: 16px !important;
        padding-right: 16px !important;
    }
    .stApp:has(.tr-multi-ai-layout) .multi-landing-hero,
    .stApp:has(.tr-multi-ai-layout) .multi-feature-grid {
        width: 100% !important;
    }
    .stApp:has(.tr-multi-ai-layout) .multi-landing-logo,
    .stApp:has(.tr-multi-ai-layout) .multi-landing-logo img {
        width: 72px !important;
        height: 72px !important;
    }
}

/* Kartu fitur diperbesar agar menjadi fokus landing page. */
.stApp:has(.tr-multi-ai-layout) .multi-feature-grid {
    width: min(1040px, calc(100vw - 48px)) !important;
    gap: 16px !important;
    margin-bottom: 48px !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card {
    min-height: 132px !important;
    padding: 16px 17px 14px !important;
    border-radius: 11px !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card > span {
    margin-bottom: 8px !important;
    font-size: 22px !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card strong {
    font-size: .76rem !important;
}
.stApp:has(.tr-multi-ai-layout) .multi-feature-card small {
    margin-top: 6px !important;
    font-size: .62rem !important;
    line-height: 1.45 !important;
}
"""
