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

/* ============================================================
   PENGATURAN — RAPAT, SEIMBANG, DAN RESPONSIF
   ============================================================ */

/* Zona utama dipisahkan dari latar: 50px dari sisi konten,
   20px dari atas, dan 32px ruang aman di bagian bawah. */
.stApp:has(.settings-card)
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
    height: max-content !important;
    min-height: calc(100vh - 52px) !important;
    overflow: visible !important;
}

/* Streamlit memakai AppViewContainer sebagai viewport utama. Jadikan
   elemen ini scroll container agar seluruh kartu di bawah tetap dapat
   dicapai tanpa mengunci tinggi zona konten. */
.stApp:has(.settings-card)
[data-testid="stAppViewContainer"] {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

.stApp:has(.settings-card)
[data-testid="stMain"] {
    min-height: max-content !important;
    overflow: visible !important;
}

.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
}

/* Kartu tengah untuk setiap kelompok Pengaturan. */
.stApp:has(.settings-card)
[class*="st-key-settings_card_"] {
    background: rgba(255, 255, 255, 0.58) !important;
    border: 1px solid #E2D8C9 !important;
    border-radius: 16px !important;
    box-sizing: border-box !important;
    margin: 0 0 16px !important;
    padding: 18px 18px 20px !important;
    box-shadow: 0 4px 14px rgba(60, 45, 35, 0.045) !important;
}

.stApp:has(.settings-card)
[class*="st-key-settings_card_"] > [data-testid="stVerticalBlock"] {
    gap: 0.65rem !important;
    min-width: 0 !important;
}

.stApp:has(.settings-card)
[class*="st-key-settings_card_"] [data-testid="stHorizontalBlock"] {
    column-gap: 18px !important;
    row-gap: 14px !important;
}

.settings-card-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 16px;
    min-width: 0;
}

.settings-card-icon {
    width: 40px;
    height: 40px;
    flex: 0 0 40px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: #F0ECF5;
    border: 1px solid #E3DCEA;
    color: #4A3559;
}

.settings-card-icon .mi {
    font-size: 21px;
    vertical-align: middle;
}

.settings-card-copy {
    min-width: 0;
    flex: 1 1 auto;
}

.settings-card-title {
    color: #2C1F33;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.08rem;
    font-weight: 650;
    line-height: 1.2;
    overflow-wrap: anywhere;
}

.settings-card-subtitle {
    color: #6B6172;
    font-size: 0.82rem;
    line-height: 1.35;
    margin-top: 3px;
    overflow-wrap: anywhere;
}

/* Header tidak lagi memotong subtitle ketika ukuran layar menyempit. */
.stApp:has(.settings-card) .page-head {
    width: 100% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    padding: 4px 0 24px !important;
    margin: 0 0 2px !important;
    align-items: flex-start !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stApp:has(.settings-card) .page-head-icon {
    background: #F0ECF5 !important;
    border-color: #E3DCEA !important;
    color: #263A70 !important;
    transform: translateY(16px) !important;
}


.stApp:has(.settings-card) .page-head > div:last-child {
    min-width: 0 !important;
    flex: 1 1 auto !important;
}

.stApp:has(.settings-card) .page-title {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    font-size: clamp(1.65rem, 3vw, 2.15rem) !important;
    font-weight: 700 !important;
    color: #182653 !important;
    line-height: 1.12 !important;
    margin: 0 0 7px !important;
}

.stApp:has(.settings-card) .page-sub {
    color: #7180A3 !important;
}

.stApp:has(.settings-card) .page-sub {
    max-width: 100% !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.5 !important;
}

/* Semua pasangan kolom memakai jarak dan garis awal yang sama. */
.stApp:has(.settings-card)
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    column-gap: 24px !important;
    row-gap: 18px !important;
}

.stApp:has(.settings-card)
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 0 !important;
}

/* Jarak teks label ke widget dibuat konsisten di semua tab. */
.stApp:has(.settings-card)
[data-testid="stWidgetLabel"] {
    margin-bottom: 6px !important;
}

.stApp:has(.settings-card)
[data-testid="stWidgetLabel"] p,
.stApp:has(.settings-card) label p {
    margin: 0 !important;
    color: #4B3D55 !important;
    font-size: 0.94rem !important;
    line-height: 1.35 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/* Kolom pilihan dan input mempunyai tinggi, radius, dan padding yang seragam. */
.stApp:has(.settings-card)
[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 12px !important;
    padding: 0 12px !important;
    box-sizing: border-box !important;
}

.stApp:has(.settings-card)
[data-testid="stTextInput"] input,
.stApp:has(.settings-card)
[data-testid="stTextArea"] textarea,
.stApp:has(.settings-card)
[data-testid="stNumberInput"] input {
    min-height: 44px !important;
    border-radius: 12px !important;
    padding: 9px 12px !important;
    box-sizing: border-box !important;
}

.stApp:has(.settings-card)
[data-testid="stTextArea"] textarea {
    line-height: 1.45 !important;
}

.stApp:has(.settings-card)
[data-testid="stCheckbox"],
.stApp:has(.settings-card)
[data-testid="stRadio"],
.stApp:has(.settings-card)
[data-testid="stToggle"] {
    margin: 6px 0 !important;
}

/* Judul subbagian dibuat sebagai ritme visual yang sama di semua tab. */
.stApp:has(.settings-card) .set-section {
    margin: 28px 0 12px !important;
    line-height: 1.25 !important;
}

.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] .set-section:first-child {
    margin-top: 0 !important;
}

/* Tombol aksi memiliki ukuran dan teks yang seragam, termasuk tombol panjang. */
.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] div.stButton > button,
.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] div.stDownloadButton > button {
    min-height: 42px !important;
    height: auto !important;
    padding: 9px 16px !important;
    border-radius: 12px !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] div.stButton > button p,
.stApp:has(.settings-card)
[data-testid="stMainBlockContainer"] div.stDownloadButton > button p {
    margin: 0 !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/* Jangan biarkan tombol navigasi ikon ikut menjadi tombol tinggi. */
.stApp:has(.settings-card)
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
    .stApp:has(.settings-card)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 16px) !important;
        margin: 12px 8px 24px !important;
        padding: 22px 18px 76px !important;
        border-radius: 18px !important;
        min-height: calc(100vh - 36px) !important;
    }

    .stApp:has(.settings-card) .page-head {
        padding: 18px !important;
        margin-bottom: 20px !important;
    }

    .stApp:has(.settings-card)
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }

    .stApp:has(.settings-card)
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
}
"""
