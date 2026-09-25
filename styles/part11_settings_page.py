# -*- coding: utf-8 -*-
"""Halaman Pengaturan (Settings): background, header, floating icon navigation, kolom input

Dipecah dari styles.py asli (baris 8541-8791), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ============================================================
   TRINITY AI — SETTINGS
   MENGIKUTI PALET UTAMA APP
   ============================================================ */

.stApp:has(.set-section)
[data-testid="stMain"] {
    background: transparent !important;
}

/* ============================================================
   PENGATURAN — BACKGROUND
   ============================================================ */

.stApp:has(.set-section) {
    background: #F3E8D7 !important;
}

.stApp:has(.set-section)
[data-testid="stAppViewContainer"],
.stApp:has(.set-section)
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

.stApp:has(.set-section)
p,
.stApp:has(.set-section)
label {
    color: #6B6172;
}
/* ============================================================
   DIVIDER
   ============================================================ */

.stApp:has(.set-section)
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
.stApp:has(.set-section) input,
.stApp:has(.set-section) textarea {
    background: #FFF9F0 !important;
    color: #2C1F33 !important;
    border-color: #E4D7C4 !important;
}

/* Selectbox / dropdown */
.stApp:has(.set-section)
[data-baseweb="select"] > div {
    background: #FFF9F0 !important;
    color: #2C1F33 !important;
    border-color: #E4D7C4 !important;
}

/* Kolom angka / number input */
.stApp:has(.set-section)
[data-testid="stNumberInput"] input {
    background: #FFF9F0 !important;
}

/* Slider */
.stApp:has(.set-section)
[data-testid="stSlider"] {
    background: transparent !important;
}

/* Checkbox */
.stApp:has(.set-section)
[data-testid="stCheckbox"] {
    background: #FFF9F0 !important;
    border: 1px solid #E4D7C4 !important;
    border-radius: 12px !important;
    padding: 8px 12px !important;
}

/* Radio / pilihan */
.stApp:has(.set-section)
[data-testid="stRadio"] {
    background: #FFF9F0 !important;
    border: 1px solid #E4D7C4 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
}

/* Tombol pilihan / action */
.stApp:has(.set-section)
button {
    border-color: #E4D7C4 !important;
}
/* ============================================================
   PENGATURAN — RAPAT, SEIMBANG, DAN RESPONSIF
   ============================================================ */

/* Zona utama dipisahkan dari latar: 50px dari sisi konten,
   20px dari atas, dan 32px ruang aman di bagian bawah. */
.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 100px) !important;
    max-width: none !important;
    margin: 20px 50px 32px !important;
    padding: 32px 40px 84px !important;
    box-sizing: border-box !important;
    background: #FFF9F0 !important;
    border: 1px solid #D8C7AF !important;
    border-radius: 24px !important;
    box-shadow:
        0 18px 42px rgba(60, 45, 35, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
    min-height: calc(100vh - -300px) !important;
    overflow: visible !important;
}

.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
}

/* Header tidak lagi memotong subtitle ketika ukuran layar menyempit. */
.stApp:has(.set-section) .page-head {
    width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    padding: 22px 26px !important;
    margin: 0 0 26px !important;
    align-items: flex-start !important;
}

.stApp:has(.set-section) .page-head > div:last-child {
    min-width: 0 !important;
    flex: 1 1 auto !important;
}

.stApp:has(.set-section) .page-title {
    font-size: clamp(1.65rem, 3vw, 2.15rem) !important;
    line-height: 1.12 !important;
    margin: 0 0 7px !important;
}

.stApp:has(.set-section) .page-sub {
    max-width: 100% !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.5 !important;
}

/* Semua pasangan kolom memakai jarak dan garis awal yang sama. */
.stApp:has(.set-section)
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    column-gap: 24px !important;
    row-gap: 18px !important;
}

.stApp:has(.set-section)
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Jarak teks label ke widget dibuat konsisten di semua tab. */
.stApp:has(.set-section)
[data-testid="stWidgetLabel"] {
    margin-bottom: 6px !important;
}

.stApp:has(.set-section)
[data-testid="stWidgetLabel"] p,
.stApp:has(.set-section) label p {
    margin: 0 !important;
    color: #4B3D55 !important;
    font-size: 0.94rem !important;
    line-height: 1.35 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/* Kolom pilihan dan input mempunyai tinggi, radius, dan padding yang seragam. */
.stApp:has(.set-section)
[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 12px !important;
    padding: 0 12px !important;
    box-sizing: border-box !important;
}

.stApp:has(.set-section)
[data-testid="stTextInput"] input,
.stApp:has(.set-section)
[data-testid="stTextArea"] textarea,
.stApp:has(.set-section)
[data-testid="stNumberInput"] input {
    min-height: 44px !important;
    border-radius: 12px !important;
    padding: 9px 12px !important;
    box-sizing: border-box !important;
}

.stApp:has(.set-section)
[data-testid="stTextArea"] textarea {
    line-height: 1.45 !important;
}

.stApp:has(.set-section)
[data-testid="stCheckbox"],
.stApp:has(.set-section)
[data-testid="stRadio"],
.stApp:has(.set-section)
[data-testid="stToggle"] {
    margin: 6px 0 !important;
}

/* Judul subbagian dibuat sebagai ritme visual yang sama di semua tab. */
.stApp:has(.set-section) .set-section {
    margin: 28px 0 12px !important;
    line-height: 1.25 !important;
}

.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] .set-section:first-child {
    margin-top: 0 !important;
}

/* Tombol aksi memiliki ukuran dan teks yang seragam, termasuk tombol panjang. */
.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] div.stButton > button,
.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] div.stDownloadButton > button {
    min-height: 42px !important;
    height: auto !important;
    padding: 9px 16px !important;
    border-radius: 12px !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] div.stButton > button p,
.stApp:has(.set-section)
[data-testid="stMainBlockContainer"] div.stDownloadButton > button p {
    margin: 0 !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/* Jangan biarkan tombol navigasi ikon ikut menjadi tombol tinggi. */
.stApp:has(.set-section)
[class*="st-key-settings_float_"] button {
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    border-radius: 50% !important;
}

/* Dialog "Sesuaikan" mengikuti ukuran dan ritme widget halaman Settings. */
div[role="dialog"] {
    background: #FFF9F0 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 20px !important;
    box-shadow: 0 18px 48px rgba(44, 31, 51, 0.18) !important;
}

div[role="dialog"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}

div[role="dialog"] [data-testid="stWidgetLabel"] {
    margin-bottom: 5px !important;
}

div[role="dialog"] [data-testid="stWidgetLabel"] p,
div[role="dialog"] label p {
    margin: 0 !important;
    color: #4B3D55 !important;
    font-size: 0.94rem !important;
    line-height: 1.35 !important;
    white-space: normal !important;
}

div[role="dialog"] input,
div[role="dialog"] textarea {
    background: #FFFFFF !important;
    color: #2C1F33 !important;
    border: 1px solid #E4D7C4 !important;
    border-radius: 12px !important;
    box-sizing: border-box !important;
}

div[role="dialog"] input {
    min-height: 44px !important;
    padding: 9px 12px !important;
}

div[role="dialog"] textarea {
    line-height: 1.45 !important;
    padding: 10px 12px !important;
}

div[role="dialog"] div.stButton > button {
    min-height: 42px !important;
    border-radius: 12px !important;
    padding: 9px 16px !important;
    line-height: 1.3 !important;
}

div[role="dialog"] div.stButton > button p {
    margin: 0 !important;
    white-space: normal !important;
}

@media (max-width: 760px) {
    .stApp:has(.set-section)
    [data-testid="stMainBlockContainer"] {
        width: calc(100vw - 16px) !important;
        padding: 22px 18px 76px !important;
        border-radius: 18px !important;
    }

    .stApp:has(.set-section) .page-head {
        padding: 18px !important;
        margin-bottom: 20px !important;
    }

    .stApp:has(.set-section)
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }

    .stApp:has(.set-section)
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
}
"""
