# -*- coding: utf-8 -*-
"""Posisi nyata chat input, ikon kontrol chat (mic, file, model), font global, fix first-load

Dipecah dari styles.py asli (baris 4791-5950), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ============================================================
   CHAT INPUT — POSISI NYATA
   Menggeser elemen input yang benar-benar terlihat.
   Berlaku:
   1. saat loading / tombol Hentikan
   2. saat chat sudah berjalan
   ============================================================ */

.stApp:has(.tr-chat-layout)
[data-testid="stBottomBlockContainer"] {
    position: relative !important;

    left: var(--chat-shift, 0px) !important;

    margin-left: auto !important;
    margin-right: auto !important;

    box-sizing: border-box !important;

    transition:
        left 0.45s ease-in-out !important;
}

/* Kolom chat normal */
.stApp:has(.tr-chat-layout)
[data-testid="stBottomBlockContainer"]
[data-testid="stChatInput"] {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

/* Saat Yuki sedang berpikir / loading */
.stApp:has(.tr-chat-layout)
.st-key-yuki_thinking_input {
    position: relative !important;

    left: var(--chat-shift, 0px) !important;

    transition:
        left 0.45s ease-in-out !important;
}
/* ============================================================
   KONTROL POSISI JUDUL & PERCAKAPAN
   ------------------------------------------------------------
   KHUSUS untuk judul sapaan dan area percakapan.
   TIDAK mengubah posisi kolom input.
   ============================================================ */

.stApp:has(.tr-chat-layout) {

    /* =========================
       JUDUL SAPAAN
       ========================= */

    /* Geser kiri/kanan judul */
    --greeting-x: -200px;

    /* Geser atas/bawah judul */
    --greeting-y: 0px;


    /* =========================
       AREA PERCAKAPAN
       ========================= */

    /* Geser seluruh bubble percakapan kiri/kanan */
    --conversation-x: -190px;

    /* Geser seluruh bubble percakapan atas/bawah */
    --conversation-y: 20px;
}


/* ============================================================
   JUDUL SAPAAN
   ============================================================ */

.stApp:has(.tr-chat-layout) .trinity-greeting {
    position: relative !important;

    left: var(--greeting-x) !important;
    top: var(--greeting-y) !important;

    text-align: center !important;
}


/* ============================================================
   BUBBLE PERCAKAPAN
   ============================================================ */

.stApp:has(.tr-chat-layout) .bubble-row {
    position: relative !important;

    left: var(--conversation-x) !important;
    top: var(--conversation-y) !important;
}


/* ============================================================
   TOMBOL AKSI DI BAWAH JAWABAN AI
   Ikut bergerak bersama percakapan
   ============================================================ */

.stApp:has(.tr-chat-layout) [class*="st-key-msg_actions_"] {
    position: relative !important;

    left: var(--conversation-x) !important;
    top: var(--conversation-y) !important;
}
/* ================================================================
   CHAT INPUT — CONTROL BAR COMPACT
   Semua kontrol tetap satu baris dan tidak membuat kartu membesar.
   ================================================================ */

.st-key-chat_controls {
    width: auto !important;

    margin: 0 !important;

    padding:
        0
        2px !important;

    background: transparent !important;
}
/* ================================================================
   MIC BUTTON — FULLY TRANSPARENT
   ================================================================ */

[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"],
[data-testid="stChatInputMicButton"]:hover,
[data-testid="stChatInputMicButton"]:focus,
[data-testid="stChatInputMicButton"]:focus-visible,
[data-testid="stChatInputMicButton"]:active {

    background: transparent !important;
    background-color: transparent !important;

    border-color: transparent !important;
    box-shadow: none !important;

    outline: none !important;
}


/* Hilangkan background dari wrapper tombol */
[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"]::after {

    background: transparent !important;
    box-shadow: none !important;
}


/* Pastikan ikon tetap terlihat */
[data-testid="stChatInput"]
[data-testid="stChatInputMicButton"]::before {

    background: transparent !important;
    box-shadow: none !important;
}
/* ================================================================
   MIC BUTTON — FORCE TRANSPARENT
   Target langsung berdasarkan struktur DOM Streamlit
   ================================================================ */

button[data-testid="stChatInputMicButton"] {
    width: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;

    padding: 0 !important;
    margin: 0 !important;

    /* MATIKAN BACKGROUND STREAMLIT */
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    border-width: 0 !important;
    border-color: transparent !important;

    box-shadow: none !important;
    outline: none !important;

    border-radius: 50% !important;

    appearance: none !important;
    -webkit-appearance: none !important;

    color: #4E4553 !important;
}

/* ================================================================
   SEMUA STATE TOMBOL
   ================================================================ */

button[data-testid="stChatInputMicButton"]:hover,
button[data-testid="stChatInputMicButton"]:focus,
button[data-testid="stChatInputMicButton"]:focus-visible,
button[data-testid="stChatInputMicButton"]:active {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;
    outline: none !important;
}

/* ================================================================
   HILANGKAN STYLE DARI CLASS EMOTION STREAMLIT
   ================================================================ */

button[data-testid="stChatInputMicButton"].st-emotion-cache-nmzvcc {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
}

button[data-testid="stChatInputMicButton"].e1p9v2yr9 {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
}

/* ================================================================
   SVG ASLI MIC DISEMBUNYIKAN
   ================================================================ */

button[data-testid="stChatInputMicButton"] svg {
    display: none !important;
}

/* ================================================================
   GANTI DENGAN ICON SOUND WAVE
   ================================================================ */

button[data-testid="stChatInputMicButton"]::before {
    content: "graphic_eq" !important;

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

    padding: 0 !important;
    margin: 0 !important;

    background: transparent !important;
    background-color: transparent !important;

    color: #4E4553 !important;

    border: none !important;
    box-shadow: none !important;
}

/* Jangan biarkan pseudo-element lain membuat background */
button[data-testid="stChatInputMicButton"]::after {
    display: none !important;
    content: none !important;
}
/* ================================================================
   MODEL POPOVER — REMOVE CHEVRON
   ================================================================ */

.st-key-chat_controls
[data-testid="stPopover"] button
[data-testid="stIconMaterial"].e1vmumty0 {
    display: none !important;
}
/* ================================================================
   SEMUA ICON CONTROL — UKURAN SAMA
   ================================================================ */

/* FILE + MODEL */
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
}

/* ICON MATERIAL DI DALAMNYA */
.st-key-chat_controls
[data-testid="stPopover"] > button
[data-testid="stIconMaterial"],

.st-key-chat_controls
button[data-testid="stPopoverButton"]
[data-testid="stIconMaterial"] {
    width: 20px !important;
    min-width: 20px !important;
    max-width: 20px !important;

    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;

    font-size: 20px !important;
    line-height: 20px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    margin: 0 !important;
    padding: 0 !important;
}
/* ================================================================
   CHAT CONTROL ICONS — FINAL
   FILE / MODEL / MIC / SEND
   ================================================================ */

/* ================================================================
   FILE + MODEL — MENYATU DENGAN CHAT INPUT
   Tidak ada lingkaran / background / border
   ================================================================ */

.st-key-chat_controls
[data-testid="stPopover"] > button,

.st-key-chat_controls
button[data-testid="stPopoverButton"] {

    /* ukuran area tombol */
    width: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;

    height: 34px !important;
    min-height: 34px !important;
    max-height: 34px !important;

    padding: 0 !important;
    margin: 0 !important;

    /* posisi icon */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    /* HILANGKAN LINGKARAN */
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;
    outline: none !important;

    border-radius: 0 !important;

    /* jangan ada transform bawaan */
    transform: none !important;

    font-size: 0 !important;
}


/* ------------------------------------------------
   Semua state juga transparan
   ------------------------------------------------ */

.st-key-chat_controls
[data-testid="stPopover"] > button:hover,

.st-key-chat_controls
[data-testid="stPopover"] > button:focus,

.st-key-chat_controls
[data-testid="stPopover"] > button:focus-visible,

.st-key-chat_controls
[data-testid="stPopover"] > button:active,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:hover,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:focus,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:focus-visible,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:active {

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;
    outline: none !important;

    transform: none !important;
}


/* ================================================================
   ICON FILE + MODEL
   ================================================================ */

.st-key-chat_controls
[data-testid="stPopover"] > button
[data-testid="stIconMaterial"],

.st-key-chat_controls
button[data-testid="stPopoverButton"]
[data-testid="stIconMaterial"] {

    width: 20px !important;
    min-width: 20px !important;
    max-width: 20px !important;

    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;

    padding: 0 !important;
    margin: 0 !important;

    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-size: 20px !important;
    line-height: 20px !important;

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;
    box-shadow: none !important;

    transform: none !important;
}


/* ================================================================
   HILANGKAN expand_more
   ================================================================ */

.st-key-chat_controls
[data-testid="stPopover"] > button
[data-testid="stIconMaterial"].e1vmumty0 {

    display: none !important;
}

/* ------------------------------------------------
   4. MIC
   34 x 34 — sama dengan file/model
   ------------------------------------------------ */

.st-key-chat_controls
[data-testid="stChatInputMicButton"] {

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

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    box-shadow: none !important;
    outline: none !important;

    border-radius: 50% !important;

    position: relative !important;
}


/* Hilangkan SVG mic asli */
.st-key-chat_controls
[data-testid="stChatInputMicButton"] svg {
    display: none !important;
}


/* Sound wave */
.st-key-chat_controls
[data-testid="stChatInputMicButton"]::before {

    content: "graphic_eq" !important;

    font-family:
        "Material Symbols Rounded",
        "Material Symbols",
        "Material Icons",
        sans-serif !important;

    font-size: 20px !important;
    line-height: 20px !important;

    width: 20px !important;
    height: 20px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    color: #4E4553 !important;

    background: transparent !important;

    border: none !important;
    box-shadow: none !important;

    margin: 0 !important;
    padding: 0 !important;
}


/* Semua state mic tetap transparan */
.st-key-chat_controls
[data-testid="stChatInputMicButton"]:hover,

.st-key-chat_controls
[data-testid="stChatInputMicButton"]:focus,

.st-key-chat_controls
[data-testid="stChatInputMicButton"]:active {

    background: transparent !important;
    background-color: transparent !important;

    border: none !important;
    box-shadow: none !important;
}


/* ------------------------------------------------
   5. SEND
   34 x 34
   ------------------------------------------------ */

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

    border-radius: 50% !important;

    position: relative !important;
}


/* Hilangkan panah bawaan */
[data-testid="stChatInput"]
button[type="submit"] svg {
    display: none !important;
}


/* ------------------------------------------------
   6. PAPER PLANE
   ------------------------------------------------ */

[data-testid="stChatInput"]
button[type="submit"]::before {

    content: "send" !important;

    font-family:
        "Material Symbols Rounded",
        "Material Symbols",
        "Material Icons",
        sans-serif !important;

    font-size: 20px !important;
    line-height: 20px !important;

    width: 20px !important;
    height: 20px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    margin: 0 !important;
    padding: 0 !important;

    color: #4E4553 !important;

    background: transparent !important;

    font-variation-settings:
        "FILL" 1,
        "wght" 400,
        "GRAD" 0,
        "opsz" 20 !important;
}


/* ------------------------------------------------
   7. SEMUA ICON CONTROL — TIDAK BOLEH MEMBESAR
   ------------------------------------------------ */

.st-key-chat_controls
[data-testid="stPopover"] > button,
.st-key-chat_controls
button[data-testid="stPopoverButton"],
.st-key-chat_controls
[data-testid="stChatInputMicButton"],
[data-testid="stChatInput"] button[type="submit"] {

    transform-origin: center center !important;
}


/* Hilangkan efek hover yang mengubah ukuran */
.st-key-chat_controls
[data-testid="stPopover"] > button:hover,

.st-key-chat_controls
button[data-testid="stPopoverButton"]:hover,

.st-key-chat_controls
[data-testid="stChatInputMicButton"]:hover,

[data-testid="stChatInput"]
button[type="submit"]:hover {

    transform: none !important;
}
/* ================================================================
   FILE BUTTON — HILANGKAN LINGKARAN
   ================================================================ */

/* File = popover pertama */
.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
[data-testid="stPopover"] > button {

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

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    border-color: transparent !important;

    box-shadow: none !important;
    outline: none !important;

    border-radius: 0 !important;

    transform: none !important;
}


/* Semua state */
.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
[data-testid="stPopover"] > button:hover,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
[data-testid="stPopover"] > button:focus,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
[data-testid="stPopover"] > button:active {

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}


/* Icon attach_file */
.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
[data-testid="stPopover"] > button
[data-testid="stIconMaterial"] {

    width: 20px !important;
    height: 20px !important;

    min-width: 20px !important;
    min-height: 20px !important;

    padding: 0 !important;
    margin: 0 !important;

    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-size: 20px !important;
    line-height: 20px !important;

    background: transparent !important;
    box-shadow: none !important;
}
/* =========================================================
   FILE + MODEL — SQUARE / CENTER
   ========================================================= */

/* FILE */
.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"],

/* MODEL */
.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"] {
    position: relative !important;

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

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border: 1px solid rgba(78, 69, 83, 0.12) !important;
    border-radius: 9px !important;

    box-shadow: none !important;
    outline: none !important;

    transform: none !important;
}


/* =========================================================
   SEMUA STATE — TETAP TRANSPARAN
   ========================================================= */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"]:hover,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"]:focus,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"]:focus-visible,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"]:active,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]:hover,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]:focus,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]:focus-visible,

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]:active {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    border-color: rgba(78, 69, 83, 0.18) !important;

    box-shadow: none !important;
    outline: none !important;
}


/* =========================================================
   FILE ICON — BENAR-BENAR DI TENGAH
   ========================================================= */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(1)
button[data-testid="stPopoverButton"]
span[role="img"][aria-label="attach_file icon"] {
    position: absolute !important;

    left: 50% !important;
    top: 50% !important;

    transform: translate(-50%, -50%) !important;

    width: 20px !important;
    height: 20px !important;

    margin: 0 !important;
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-family: "Material Symbols Rounded" !important;
    font-size: 20px !important;
    line-height: 20px !important;

    color: #4E4553 !important;
}


/* =========================================================
   MODEL ICON — BENAR-BENAR DI TENGAH
   ========================================================= */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]
span[role="img"] {
    position: absolute !important;

    left: 50% !important;
    top: 50% !important;

    transform: translate(-50%, -50%) !important;

    width: 24px !important;
    height: 24px !important;

    margin: 0 !important;
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    font-family: "Material Symbols Rounded" !important;
    font-size: 21px !important;
    line-height: 21px !important;

    color: #4E4553 !important;
}


/* =========================================================
   HILANGKAN CHEVRON MODEL
   ========================================================= */

.st-key-chat_controls
[data-testid="stHorizontalBlock"]
> [data-testid="stColumn"]:nth-child(3)
button[data-testid="stPopoverButton"]
[aria-hidden="true"] {
    display: none !important;
}
/* =========================================================
   GLOBAL FONT — SPACE GROTESK
   ========================================================= */

html,
body,
.stApp,
.stApp * {
    font-family:
        "Space Grotesk",
        sans-serif !important;

    font-style: normal !important;
}


/* Material Icons tetap menggunakan font ikonnya.
   .mi wajib ikut dikecualikan: helper mi() di icons.py menghasilkan span.mi.
   Tanpa selector ini, aturan `.stApp *` di atas (yang memakai !important)
   menimpa font ligature ikon dan teks seperti "support_agent" tampil mentah. */
[data-testid="stIconMaterial"],
span[role="img"],
.mi,
[class*="material-symbols"],
[class*="material-icons"] {
    font-family:
        "Material Symbols Rounded",
        "Material Symbols",
        "Material Icons",
        sans-serif !important;

    font-style: normal !important;
    font-weight: normal !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    white-space: nowrap !important;
}
/* ================================================================
   CHAT FIRST-LOAD FIX
   KHUSUS dashboard chat — TIDAK menyentuh welcome/login
================================================================ */

.stApp:has(.tr-chat-layout) .st-key-chat_topbar {
    position: fixed !important;

    top: 12px !important;

    left: var(--dash-center-left) !important;

    right: var(--dash-center-right) !important;

    width: auto !important;

    max-width: none !important;

    min-width: 0 !important;

    margin: 0 !important;

    transform: none !important;
}


.stApp:has(.tr-chat-layout) .st-key-chat_right_rail {
    position: fixed !important;

    top: 12px !important;

    right: 18px !important;

    bottom: 16px !important;

    width: 250px !important;

    max-width: 250px !important;

    min-width: 250px !important;

    margin: 0 !important;

    transform: none !important;
}


/* Area utama tetap dihitung dari sidebar + panel kanan. */

.stApp:has(.tr-chat-layout) [data-testid="stMainBlockContainer"] {
    width: 100% !important;

    max-width: none !important;

    padding-left:
        calc(210px + 18px) !important;

    padding-right:
        calc(250px + 36px) !important;
}


/* Lebar isi tengah. */

.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"]
> [data-testid="stVerticalBlock"] {

    width:
        min(
            720px,
            calc(
                100vw
                - 210px
                - 250px
                - 54px
            )
        ) !important;

    max-width:
        min(
            720px,
            calc(
                100vw
                - 210px
                - 250px
                - 54px
            )
        ) !important;

    margin-left: auto !important;

    margin-right: auto !important;
}


/* Fresh maupun chat berjalan memakai geometri horizontal
   yang sama. Hanya posisi vertikal bottom dock yang berbeda. */

.stApp:has(.tr-chat-layout.tr-fresh-home)
.st-key-chat_topbar,
.stApp:has(.tr-chat-layout)
.st-key-chat_topbar {

    left:
        var(--dash-center-left) !important;

    right:
        var(--dash-center-right) !important;
}


@media (max-width: 1180px) {

    .stApp:has(.tr-chat-layout)
    .st-key-chat_right_rail {

        display: none !important;
    }

    .stApp:has(.tr-chat-layout)
    .st-key-chat_topbar {

        left: 230px !important;

        right: 18px !important;
    }

    .stApp:has(.tr-chat-layout)
    [data-testid="stMainBlockContainer"] {

        padding-left: 230px !important;

        padding-right: 18px !important;
    }

    .stApp:has(.tr-chat-layout)
    [data-testid="stMainBlockContainer"]
    > [data-testid="stVerticalBlock"] {

        width:
            min(
                760px,
                calc(100vw - 248px)
            ) !important;

        max-width:
            min(
                760px,
                calc(100vw - 248px)
            ) !important;
    }
}
"""
