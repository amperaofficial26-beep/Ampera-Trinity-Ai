# -*- coding: utf-8 -*-
"""Kartu chat gabungan & seluruh kontrol chat input (tombol +, pilihan model, ukuran teks, mic, tombol kirim, responsive HP)

Dipecah dari styles.py asli (baris 703-2226), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ================================================================
   KARTU CHAT GABUNGAN
   Kolom teks, tombol +, dan nama model menjadi satu kartu.
   ================================================================ */
[data-testid="stBottomBlockContainer"] {
    position: relative !important;

    display: flex !important;
    flex-direction: column !important;

    width: min(760px, calc(100vw - 24px)) !important;

    margin-left: auto !important;
    margin-right: auto !important;

    padding:
        8px
        8px
        6px !important;

    background:
        linear-gradient(
            145deg,
            rgba(248, 239, 222, 0.98),
            rgba(239, 225, 202, 0.98)
        ) !important;

    border:
        1px solid
        rgba(159, 126, 72, 0.38) !important;

    border-radius: 22px !important;

    box-shadow:
        0 8px 24px rgba(65, 46, 27, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.78) !important;

    overflow: visible !important;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease !important;
}


/* Glow saat pengguna mengetik. */
[data-testid="stBottomBlockContainer"]:focus-within {
    border-color:
        rgba(177, 131, 47, 0.72) !important;

    box-shadow:
        0 10px 28px rgba(65, 46, 27, 0.16),
        0 0 0 1px rgba(199, 151, 57, 0.18),
        0 0 22px rgba(211, 163, 65, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
}


/* ================================================================
   URUTAN ELEMEN DI DALAM KARTU
   1. Lampiran
   2. Kolom teks
   3. Tombol + dan nama model
   ================================================================ */
[data-testid="stBottomBlockContainer"]
> [data-testid="stVerticalBlock"] {
    display: contents !important;
}

[data-testid="stBottomBlockContainer"]
> [data-testid="stVerticalBlock"]
> [data-testid="stElementContainer"],
[data-testid="stBottomBlockContainer"]
> [data-testid="stVerticalBlock"]
> .element-container {
    display: contents !important;
}

[data-testid="stBottomBlockContainer"]
[class*="st-key-pending_strip"] {
    order: 1 !important;
}

[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {
    order: 2 !important;
}

[data-testid="stBottomBlockContainer"]
.st-key-chat_controls {
    order: 3 !important;
}
/* ================================================================
   BARIS KONTROL CHAT — COMPACT
   Struktur asli:
   1. +
   2. spacer
   3. model
   ================================================================ */

.st-key-chat_controls {
    position: absolute !important;

    left: 0 !important;
    right: 0 !important;
    bottom: 8px !important;

    width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    z-index: 30 !important;

    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    pointer-events: none !important;
}


/* Baris kontrol memenuhi kartu */
.st-key-chat_controls
[data-testid="stHorizontalBlock"] {
    position: relative !important;

    width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    display: flex !important;

    align-items: center !important;

    gap: 0 !important;

    flex-wrap: nowrap !important;

    pointer-events: none !important;
}


/* ================================================================
   KOLOM 1 — TOMBOL +
   ================================================================ */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1) {
    position: absolute !important;

    left: 8px !important;
    bottom: -3px !important;

    width: 36px !important;
    min-width: 36px !important;
    max-width: 36px !important;

    margin: 0 !important;
    padding: 0 !important;

    pointer-events: auto !important;
}


/* ================================================================
   KOLOM 2 — SPACER
   Jangan tampilkan sebagai kontrol.
   ================================================================ */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(2) {
    width: 100% !important;

    min-width: 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    pointer-events: none !important;
}


/* ================================================================
   KOLOM 3 — PILIHAN MODEL
   Berada sebelum mic + tombol kirim.
   ================================================================ */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3) {
    position: absolute !important;

    right: 112px !important;
    bottom: -3px !important;

    width: auto !important;
    min-width: 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    pointer-events: auto !important;
}
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {
    width: 100% !important;

    padding:
        4px
        6px
        2px !important;

    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}

/* Bersihkan seluruh pembungkus bawaan input. */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] div,

[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
[data-baseweb="base-input"],

[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
[data-baseweb="textarea"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}


/* Tulisan di dalam kolom chat — COMPACT */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] textarea {

    /* =========================================================
       UKURAN TEKS
       ========================================================= */

    font-size: 12px !important;
    font-weight: 500 !important;

    line-height: 1.35 !important;


    /* =========================================================
       POSISI TEKS
       =========================================================
       
       Atur angka ini untuk memindahkan tulisan.
       
       kiri/kanan  -> padding-left
       atas/bawah  -> padding-top
       
       Contoh:
       padding-left: 10px  = makin ke kanan
       padding-left: 4px   = makin ke kiri

       padding-top: 13px    = makin ke bawah
       padding-top: 5px    = makin ke atas
       ========================================================= */

    padding:
        10px
        8px
        13px
        10px !important;


    /* =========================================================
       UKURAN DAN DIMENSI INPUT — TETAP
       ========================================================= */

    min-height: 42px !important;
    height: 42px !important;


    /* =========================================================
       WARNA TEKS
       ========================================================= */

    color: #34271e !important;


    /* =========================================================
       FONT
       ========================================================= */

    font-family:
        "Manrope",
        "Inter",
        sans-serif !important;


    /* =========================================================
       BACKGROUND
       ========================================================= */

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;

    resize: none !important;
}


/* =========================================================
   PLACEHOLDER — "Tulis pesan..."
   ========================================================= */

[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
textarea::placeholder {

    font-size: 14px !important;

    font-weight: 500 !important;

    line-height: 1.35 !important;

    color: #8a7969 !important;

    opacity: 1 !important;
}
/* Warna placeholder. */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
textarea::placeholder {
    color: #8a7969 !important;
    opacity: 1 !important;
}


/* ================================================================
   KONTROL CHAT — POSISI TERPISAH
   + di kiri, model di kanan sebelum mic + kirim.
   ================================================================ */

.st-key-chat_controls {
    position: absolute !important;

    left: 0 !important;
    right: 0 !important;

    bottom: 25px !important;

    width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    z-index: 20 !important;

    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    pointer-events: none !important;
}


/* Baris kontrol memenuhi lebar kartu */
.st-key-chat_controls
[data-testid="stHorizontalBlock"] {
    position: relative !important;

    width: 100% !important;

    display: flex !important;

    align-items: center !important;

    gap: 0 !important;

    flex-wrap: nowrap !important;

    pointer-events: none !important;
}


/* ================================================================
   TOMBOL + DAN MODEL
   ================================================================ */
.st-key-chat_controls
button[data-testid="stPopoverButton"],

.st-key-chat_controls
button[data-testid="stPopoverButton"],

/* ================================================================
   IKON KONTROL CHAT — UKURAN SERAGAM
   File + Model
   ================================================================ */

.st-key-chat_controls
[data-testid="stPopover"] > button,
.st-key-chat_controls
button[data-testid="stPopoverButton"] {

    width: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;

    padding: 0 !important;

    margin: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    border-radius: 50% !important;

    font-size: 0 !important;
}


/* Ikon Material di dalam tombol */
.st-key-chat_controls
[data-testid="stPopover"] > button
[data-testid="stIconMaterial"],

.st-key-chat_controls
button[data-testid="stPopoverButton"]
[data-testid="stIconMaterial"] {

    font-size: 20px !important;
    font-weight: 700 !important;
    
    line-height: 1 !important;

    width: 20px !important;
    height: 20px !important;

    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

    color: #5a493a !important;

    background:
        rgba(255, 250, 240, 0.46) !important;

    border:
        1px solid
        rgba(150, 116, 62, 0.16) !important;

    border-radius: 10px !important;

    box-shadow: none !important;

    font-family:
        "Manrope",
        "Inter",
        sans-serif !important;

    font-weight: 700 !important;

    white-space: nowrap !important;

    transition:
        color 0.18s ease,
        background 0.18s ease,
        border-color 0.18s ease,
        transform 0.18s ease !important;
}


/* Efek hover tombol + dan nama model. */
.st-key-chat_controls
[data-testid="stPopover"] button:hover,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:hover {
    color: #3a2a1e !important;

    background:
        rgba(213, 169, 80, 0.18) !important;

    border-color:
        rgba(173, 128, 42, 0.32) !important;

    transform:
        translateY(-1px) !important;
}


/* ================================================================
   KETERANGAN AI DI TENGAH
   ================================================================ */
.input-disclaimer {
    position: absolute !important;

    left: 50% !important;

    /*
     * Keluar dari kartu chat.
     * Nilai negatif = turun ke bawah kartu.
     */
    bottom: -24px !important;

    transform: translateX(-50%) !important;

    width: min(
        760px,
        calc(100vw - 40px)
    ) !important;

    padding:
        0
        8px !important;

    margin: 0 !important;

    color: #8a7969 !important;

    text-align: center !important;

    font-family:
        "Inter",
        sans-serif !important;

    font-size: 11px !important;

    font-weight: 400 !important;

    line-height: 1.3 !important;

    white-space: nowrap !important;

    overflow: hidden !important;

    text-overflow: ellipsis !important;

    pointer-events: none !important;

    z-index: 5 !important;
}
 /* ================================================================
    YUKI THINKING — KARTU HENTIKAN
    Saat Yuki berpikir, hanya tombol Hentikan yang ditampilkan.
    ================================================================ */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input) {

    /*
     * Tetap memakai ukuran kartu yang sama,
     * tetapi isi dirapikan menjadi satu tombol di tengah.
     */
    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    min-height: 56px !important;

    padding:
        8px
        8px
        8px !important;
}


/* Hilangkan baris kontrol normal saat thinking. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-chat_controls {

    display: none !important;
}


/* Hilangkan disclaimer saat thinking. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.input-disclaimer {

    display: none !important;
}


/* Hilangkan preview/lampiran yang mungkin masih ada. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-pending_preview {

    display: none !important;
}


/* ================================================================
   WRAPPER TOMBOL HENTIKAN
   ================================================================ */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-yuki_thinking_input {

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;
}


/* Baris columns tempat tombol berada. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-yuki_thinking_input
[data-testid="stHorizontalBlock"] {

    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    display: flex !important;

    align-items: center !important;

    justify-content: center !important;

    gap: 0 !important;
}


/* Sembunyikan dua column kosong kiri/kanan. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-yuki_thinking_input
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"] {

    display: none !important;
}


/* Hanya column tengah yang ditampilkan. */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-yuki_thinking_input
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:has(.st-key-yuki_stop_dok) {

    display: flex !important;

    flex: 0 0 auto !important;

    width: auto !important;

    min-width: 0 !important;

    padding: 0 !important;

    margin: 0 !important;

    align-items: center !important;

    justify-content: center !important;
}


/* ================================================================
   TOMBOL
   ================================================================ */

[data-testid="stBottomBlockContainer"]:has(.st-key-yuki_thinking_input)
.st-key-yuki_stop_dok button {

    min-height: 30px !important;

    height: 30px !important;

    width: auto !important;

    min-width: 126px !important;

    padding:
        0.05rem
        0.95rem !important;

    margin: 0 !important;

    border-radius: 999px !important;

    display: inline-flex !important;

    align-items: center !important;

    justify-content: center !important;
}
/* ================================================================
   TOMBOL KIRIM
   ================================================================ */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
button {
    color: #fff8e8 !important;

    background:
        linear-gradient(
            145deg,
            #7a5930,
            #4c3520
        ) !important;

    border:
        1px solid
        rgba(225, 187, 111, 0.36) !important;

    border-radius: 10px !important;

    box-shadow:
        0 4px 12px
        rgba(68, 43, 22, 0.18) !important;
}


/* Ikon tombol kirim. */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
button svg {
    color: #fff8e8 !important;
    fill: #fff8e8 !important;
}


/* Tombol kirim saat tidak aktif. */
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"]
button:disabled {
    color: #9b8a79 !important;

    background:
        rgba(183, 160, 126, 0.26) !important;

    box-shadow: none !important;
}


/* ================================================================
   RESPONSIVE HP
   ================================================================ */
@media (max-width: 600px) {
    [data-testid="stBottomBlockContainer"] {
        width:
            calc(100vw - 16px) !important;

        padding:
            6px
            6px
            5px !important;

        border-radius: 18px !important;
    }

    [data-testid="stBottomBlockContainer"]
    [data-testid="stChatInput"]
    textarea {
        min-height: 48px !important;

        font-size: 14px !important;
    }

    .st-key-chat_controls
    [data-testid="stPopover"] button,

    .st-key-chat_controls
    button[data-testid="stPopoverButton"] {
        min-height: 30px !important;
        height: 30px !important;

        padding:
            2px
            8px !important;

        font-size: 11.5px !important;
    }

    .input-disclaimer {
        font-size: 9.5px !important;
        padding-left: 4px !important;
        padding-right: 4px !important;
    }
}

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
/* ================================================================
   CHAT INPUT — IKON MIC / AUDIO
   ================================================================ */

[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"] {

    width: 34px !important;
    min-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;

    padding: 0 !important;

    border-radius: 50% !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: relative !important;
}


/* Sembunyikan ikon mic bawaan */
[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"] svg {
    display: none !important;
}


/* Ganti dengan ikon gelombang suara */
[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"]::before{

    content: "graphic_eq";

    font-family: "Material Symbols Rounded",
                 "Material Symbols",
                 "Material Icons",
                 sans-serif !important;

    font-size: 20px !important;

    line-height: 1 !important;

    width: 20px !important;
    height: 20px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-weight: normal !important;

    color: #4E4553 !important;
}
/* ================================================================
   MIC — TANPA WARNA TOMBOL
   ================================================================ */

[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"] {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;
    box-shadow: none !important;
}
/* ================================================================
   CHAT INPUT — IKON KIRIM
   ================================================================ */

[data-testid="stChatInput"]
button[type="submit"] {

    width: 34px !important;
    min-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;

    padding: 0 !important;

    border-radius: 50% !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: relative !important;
}


/* Sembunyikan ikon bawaan */
[data-testid="stChatInput"]
button[type="submit"] svg {
    display: none !important;
}


/* ================================================================
   SEND BUTTON — PAPER PLANE
   ================================================================ */

[data-testid="stChatInput"]
button[type="submit"] {
    width: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;

    padding: 0 !important;
    margin: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: relative !important;
}

/* Sembunyikan icon bawaan Streamlit */
[data-testid="stChatInput"]
button[type="submit"] svg {
    display: none !important;
}

/* PAPER PLANE */
[data-testid="stChatInput"]
button[type="submit"]::before {
    content: "send" !important;

    font-family:
        "Material Symbols Rounded",
        "Material Symbols",
        "Material Icons",
        sans-serif !important;

    font-size: 20px !important;
    line-height: 1 !important;

    width: 20px !important;
    height: 20px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    margin: 0 !important;
    padding: 0 !important;

    color: #4E4553 !important;

    font-variation-settings:
        "FILL" 0,
        "wght" 400,
        "GRAD" 0,
        "opsz" 20 !important;
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
    --chat-lift: -145px;
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

"""
