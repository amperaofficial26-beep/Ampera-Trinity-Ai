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

/* Posisi landing dikontrol langsung dari page_multi_agent.py. */

/* ====================================================================
   MULTI AI — BATALKAN GESERAN PERCAKAPAN MILIK CHAT UTAMA
   --------------------------------------------------------------------
   part09_design_system.py memberi:
       .stApp:has(.tr-chat-layout) .bubble-row {
           position: relative; left: var(--conversation-x); }
   dengan --conversation-x: -190px (setelan halaman chat utama).

   Halaman Multi AI memakai penanda "tr-chat-layout tr-multi-ai-layout",
   jadi ikut tergeser -190px dan teksnya keluar dari kartu lalu terpotong.
   Di sini geseran itu DIBATALKAN khusus Multi AI. Ditulis di part10
   (dimuat setelah part09) dan diawali `body` agar bobotnya menang.
==================================================================== */
body .stApp:has(.tr-multi-ai-layout) .bubble-row,
body .stApp:has(.tr-multi-ai-layout) .bubble-wrap,
body .stApp:has(.tr-multi-ai-layout) [class*="st-key-msg_actions_"],
body .stApp:has(.tr-multi-ai-layout) .trinity-greeting {
    position: static !important;
    left: auto !important;
    right: auto !important;
    top: auto !important;
    transform: none !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
}
body .stApp:has(.tr-multi-ai-layout) .bubble-row.user {
    justify-content: flex-end !important;
}
body .stApp:has(.tr-multi-ai-layout) .bubble-row.ai {
    justify-content: flex-start !important;
}

/* ====================================================================
   MULTI AI — JAWABAN TANPA LATAR (flat, seperti chat utama)
   --------------------------------------------------------------------
   Sebelumnya jawaban Yuki duduk di atas kartu .st-key-multi_chat_area
   yang punya latar, garis tepi, bayangan, dan overflow:hidden — itu yang
   membuat teks terlihat terpotong di bagian bawah.

   Sekarang: gelembung AI dan kartunya dibuat transparan, dan kartunya
   tidak lagi memotong isi.

   >>> KALAU MAU KARTUNYA KEMBALI <<<
   hapus blok ini, atau ganti nilai background/border di bawah.
==================================================================== */
body .stApp:has(.tr-multi-ai-layout) .bubble.ai {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0 2px !important;
}

body .stApp:has(.tr-multi-ai-layout) .st-key-multi_chat_area {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0 !important;

    /* jangan memotong jawaban yang panjang */
    overflow: visible !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
}

/* Gelembung pengguna tetap punya latar supaya mudah dibedakan. */
body .stApp:has(.tr-multi-ai-layout) .bubble.user {
    background: var(--tr-bubble, #E0D2BB) !important;
    border-radius: 18px !important;
    padding: 11px 16px !important;
}

/* ====================================================================
   MULTI AI — TEKS JAWABAN SELALU TERLIHAT
   --------------------------------------------------------------------
   ui_helpers menandai jawaban terakhir dengan .yuki-fade-blur; tiap baris
   lalu dianimasikan dari opacity:0 + blur dengan jeda 0,3 detik per baris
   (animation-fill-mode: both). Pada jawaban panjang di Multi AI, baris
   terakhir baru muncul setelah ~7 detik, dan kalau animasinya tidak
   dijalankan ulang setelah rerun, teksnya tidak pernah terlihat.

   Di halaman Multi AI animasi itu dimatikan: jawaban langsung tampil utuh.
==================================================================== */
body .stApp:has(.tr-multi-ai-layout) .yuki-fade-blur .yuki-reveal-line,
body .stApp:has(.tr-multi-ai-layout) .yuki-reveal-line,
body .stApp:has(.tr-multi-ai-layout) .bubble.ai,
body .stApp:has(.tr-multi-ai-layout) .yuki-answer-body {
    animation: none !important;
    animation-delay: 0s !important;
    opacity: 1 !important;
    filter: none !important;
    transform: none !important;
    visibility: visible !important;
}

body .stApp:has(.tr-multi-ai-layout) .bubble.ai,
body .stApp:has(.tr-multi-ai-layout) .yuki-answer-body {
    display: block !important;
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ====================================================================
   MULTI AI — HALAMAN HARUS BISA DIGULIR SAMPAI HABIS
   --------------------------------------------------------------------
   Gejala: jawaban berhenti di tengah, seolah halaman "mentok".
   Tiga sebab yang ditutup di sini:

   1. Simulator interaktif dirender sebagai <iframe> setinggi 520px dengan
      scroll sendiri. Saat kursor berada di atasnya, roda mouse menggulir
      ISI IFRAME, bukan halaman — jadi terasa seperti tertahan. Tingginya
      dibatasi dan diberi tepi supaya jelas batasnya.
   2. Kartu input bawah melayang di atas isi; ruang bawah ditambah agar
      pesan terakhir tidak tertutup.
   3. Pastikan tidak ada pembatas tinggi/overflow pada wadah utama.

   >>> ATUR DI SINI <<<
   --multi-sim-tinggi : tinggi maksimum kartu simulasi
   --multi-ruang-bawah: ruang kosong di bawah pesan terakhir
==================================================================== */
body .stApp:has(.tr-multi-ai-layout) {
    --multi-sim-tinggi: 360px;
    --multi-ruang-bawah: 240px;
}

body .stApp:has(.tr-multi-ai-layout) [data-testid="stMain"],
body .stApp:has(.tr-multi-ai-layout) [data-testid="stAppViewContainer"] {
    max-height: none !important;
    overflow-y: auto !important;
}

body .stApp:has(.tr-multi-ai-layout)
[data-testid="stMainBlockContainer"] {
    padding-bottom: var(--multi-ruang-bawah) !important;
    overflow: visible !important;
}

/* Kartu simulasi interaktif: lebih pendek & tidak "menelan" guliran. */
body .stApp:has(.tr-multi-ai-layout) [class*="st-key-simulator_"] iframe,
body .stApp:has(.tr-multi-ai-layout) iframe[title="st.iframe"],
body .stApp:has(.tr-multi-ai-layout) [data-testid="stIFrame"] {
    height: var(--multi-sim-tinggi) !important;
    max-height: var(--multi-sim-tinggi) !important;
    width: 100% !important;
    border: 1px solid var(--tr-border, #DBCEB9) !important;
    border-radius: 14px !important;
    background: #FFFFFF !important;
}
body .stApp:has(.tr-multi-ai-layout) [class*="st-key-simulator_"] {
    margin: 8px 0 18px !important;
    overflow: visible !important;
}
"""
