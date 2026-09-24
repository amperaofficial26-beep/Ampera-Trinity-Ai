# -*- coding: utf-8 -*-
"""Halaman Pengaturan (Settings): background, header, floating icon navigation, kolom input

Dipecah dari styles.py asli (baris 8541-8791), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ============================================================
   TRINITY AI — SETTINGS
   MENGIKUTI PALET UTAMA APP
   ============================================================ */

.stApp:has([class*="st-key-settings_float_"])
[data-testid="stMain"] {
    background: transparent !important;
}

/* ============================================================
   PENGATURAN — BACKGROUND
   ============================================================ */

.stApp:has([class*="st-key-settings_float_"]) {
    background: #F3E8D7 !important;
}

.stApp:has([class*="st-key-settings_float_"])
[data-testid="stAppViewContainer"],
.stApp:has([class*="st-key-settings_float_"])
[data-testid="stMain"] {
    background: transparent !important;
}
/* ============================================================
   HEADER SETTINGS
   ============================================================ */

.stApp .page-head {
    background: #F2E8D6 !important;

    border: 1px solid #DBCEB9 !important;

    box-shadow:
        0 8px 24px rgba(48, 40, 58, 0.055),
        inset 0 1px 0 rgba(255,255,255,0.65) !important;
}

.stApp .page-title {
    color: #2C1F33 !important;
}

.stApp .page-sub {
    color: #6B6172 !important;
}


/* ============================================================
   TEXT SETTINGS
   ============================================================ */

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #2C1F33 !important;
}

.stApp:has([class*="st-key-settings_float_"])
p,
.stApp:has([class*="st-key-settings_float_"])
label {
    color: #6B6172;
}
/* ============================================================
   DIVIDER
   ============================================================ */

.stApp:has([class*="st-key-settings_float_"])
hr {
    border-color: #DBCEB9 !important;
}
/* ============================================================
   SETTINGS — FLOATING ICON NAVIGATION
   ============================================================ */

/* Semua tombol settings */
.stApp [class*="st-key-settings_float_"] {
    position: fixed !important;

    right: 8px !important;

    width: 46px !important;
    height: 46px !important;

    z-index: 999999 !important;

    margin: 0 !important;
    padding: 0 !important;
}

/* Posisi icon — dibuat lebih rapat */
.stApp .st-key-settings_float_umum {
    top: calc(50% - 176px) !important;
}

.stApp .st-key-settings_float_tampilan {
    top: calc(50% - 132px) !important;
}

.stApp .st-key-settings_float_akun {
    top: calc(50% - 88px) !important;
}

.stApp .st-key-settings_float_privasi {
    top: calc(50% - 44px) !important;
}

.stApp .st-key-settings_float_penagihan {
    top: 50% !important;
}

.stApp .st-key-settings_float_kemampuan {
    top: calc(50% + 44px) !important;
}

.stApp .st-key-settings_float_memori {
    top: calc(50% + 88px) !important;
}

.stApp .st-key-settings_float_refleksi {
    top: calc(50% + 132px) !important;
}

.stApp .st-key-settings_float_waktu {
    top: calc(50% + 176px) !important;
}

/* Tombol */

.stApp [class*="st-key-settings_float_"] button {
    width: 36px !important;
    height: 36px !important;

    min-width: 36px !important;
    min-height: 36px !important;

    padding: 0 !important;
    margin: 0 !important;

    border-radius: 50% !important;

    border: 1px solid rgba(100, 90, 110, 0.18) !important;

    background: rgba(255, 255, 255, 0.90) !important;

    box-shadow:
        0 6px 18px rgba(30, 25, 40, 0.12) !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease !important;
}


/* Icon */

.stApp [class*="st-key-settings_float_"] button span {
    font-size: 20px !important;
}


/* Hover */

.stApp [class*="st-key-settings_float_"] button:hover {
    transform: scale(1.10) !important;

    box-shadow:
        0 8px 24px rgba(30, 25, 40, 0.18) !important;
}


/* Klik */

.stApp [class*="st-key-settings_float_"] button:active {
    transform: scale(0.92) !important;
}
/* ============================================================
   PENGATURAN — KOLOM PILIHAN LEBIH TERANG
   ============================================================ */

/* Input teks */
.stApp:has([class*="st-key-settings_float_"]) input,
.stApp:has([class*="st-key-settings_float_"]) textarea {
    background: #FFF9F0 !important;
    color: #2C1F33 !important;
    border-color: #E4D7C4 !important;
}

/* Selectbox / dropdown */
.stApp:has([class*="st-key-settings_float_"])
[data-baseweb="select"] > div {
    background: #FFF9F0 !important;
    color: #2C1F33 !important;
    border-color: #E4D7C4 !important;
}

/* Kolom angka / number input */
.stApp:has([class*="st-key-settings_float_"])
[data-testid="stNumberInput"] input {
    background: #FFF9F0 !important;
}

/* Slider */
.stApp:has([class*="st-key-settings_float_"])
[data-testid="stSlider"] {
    background: transparent !important;
}

/* Checkbox */
.stApp:has([class*="st-key-settings_float_"])
[data-testid="stCheckbox"] {
    background: #FFF9F0 !important;
    border: 1px solid #E4D7C4 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
}

/* Radio / pilihan */
.stApp:has([class*="st-key-settings_float_"])
[data-testid="stRadio"] {
    background: #FFF9F0 !important;
    border: 1px solid #E4D7C4 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}

/* Tombol pilihan / action */
.stApp:has([class*="st-key-settings_float_"])
button {
    border-color: #E4D7C4 !important;
}
/* ============================================================
   PENGATURAN — ZONA KONTEN TENGAH
   ============================================================ */

.stApp:has([class*="st-key-settings_float_"])
[data-testid="stMainBlockContainer"] {
    background: rgba(255, 249, 240, 0.72) !important;
    border: 1px solid rgba(228, 215, 196, 0.75) !important;
    border-radius: 24px !important;
    box-shadow:
        0 10px 30px rgba(60, 45, 35, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.65) !important;
    padding: 28px 32px !important;
}
"""
