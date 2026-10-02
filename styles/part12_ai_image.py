# -*- coding: utf-8 -*-
"""Halaman AI Image (page_image.py) — hero ala Canva Magic Media, kartu contoh
prompt, chip gaya & format di kotak bawah, plus penyesuaian responsif."""

CSS = r"""
/* ================================================================
   HALAMAN AI IMAGE — kerangka halaman
   ================================================================ */
.stApp:has(.aiimg-page-shell) {
    background: #F5EBDD !important;
}
.stApp:has(.aiimg-page-shell)
[data-testid="stMain"],
.stApp:has(.aiimg-page-shell)
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}
.stApp:has(.aiimg-page-shell)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 220px) !important;
    max-width: none !important;
    margin: 0 auto !important;
    padding: 38px 0 150px !important;
    box-sizing: border-box !important;
}
.stApp:has(.aiimg-page-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    gap: 0 !important;
}
.aiimg-page-shell { display: none !important; }

/* Ikon judul halaman: ubah dari beige ke ungu Trinity. */
.page-head-icon.aiimg-head-icon {
    background: linear-gradient(145deg, #F5EEF8, #EDE6F3) !important;
    border-color: #E1D8E8 !important;
    color: #4D3A69 !important;
}

/* Peringatan engine belum dikonfigurasi */
.aiimg-warning {
    margin: 0 0 16px;
    padding: 10px 14px;
    border: 1px solid #E8D5B5;
    border-left: 4px solid #C4703F;
    border-radius: 10px;
    background: #FBF3E4;
    color: #7A5A32;
    font-size: 0.86rem;
    line-height: 1.45;
}

/* ================================================================
   HERO — kartu besar ala Canva Magic Media
   ================================================================ */
.aiimg-hero {
    position: relative;
    overflow: hidden;
    margin: 6px 0 22px;
    padding: 44px 28px 36px;
    border: 1px solid #E5DCE9;
    border-radius: 22px;
    background:
        linear-gradient(140deg, #FBF4E8 0%, #F5ECDE 46%, #EFE7F5 100%);
    box-shadow:
        0 10px 28px rgba(83, 64, 112, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    text-align: center;
}
.aiimg-hero-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(46px);
    opacity: 0.55;
    pointer-events: none;
}
.aiimg-hero .blob-a {
    right: -70px; top: -90px;
    width: 250px; height: 250px;
    background: #E5D5F1;
}
.aiimg-hero .blob-b {
    left: -80px; bottom: -100px;
    width: 220px; height: 220px;
    background: #F3E1C4;
}
/* bingkai kecil melayang ala "kartu gambar" */
.aiimg-hero-frame {
    position: absolute;
    display: grid;
    place-items: center;
    width: 46px; height: 46px;
    border: 1px solid #E6DCEA;
    border-radius: 13px;
    background: rgba(255, 255, 255, 0.72);
    color: #6B5488;
    box-shadow: 0 7px 16px rgba(98, 75, 119, 0.10);
    pointer-events: none;
}
.aiimg-hero-frame .mi { font-size: 21px; }
.aiimg-hero .frame-a { left: 11%; top: 20%; transform: rotate(-8deg); }
.aiimg-hero .frame-b { right: 12%; top: 30%; transform: rotate(7deg); }
.aiimg-hero .frame-c {
    left: 19%; bottom: 16%;
    transform: rotate(6deg);
    width: 40px; height: 40px; border-radius: 11px;
}
.aiimg-hero .frame-c .mi { font-size: 18px; }

.aiimg-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 15px;
    padding: 5px 15px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7C5C99, #4D3A69);
    color: #FFF6E9;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    box-shadow: 0 6px 16px rgba(77, 58, 105, 0.28);
}
.aiimg-hero-badge .mi { font-size: 15px; }
.aiimg-hero h2 {
    margin: 0 0 10px;
    color: #302243;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: clamp(1.7rem, 3.4vw, 2.35rem);
    line-height: 1.08;
    letter-spacing: -0.02em;
}
.aiimg-hero p {
    max-width: 580px;
    margin: 0 auto;
    color: #7A7080;
    font-size: 0.95rem;
    line-height: 1.55;
}
.aiimg-hero-tags {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 19px;
}
.aiimg-hero-tags span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 13px;
    border: 1px solid #E4DACE;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.66);
    color: #5C5266;
    font-size: 0.78rem;
    font-weight: 600;
}
.aiimg-hero-tags .mi { font-size: 15px; color: #7C5C99; }

/* ================================================================
   JUDUL SEKSI + KARTU CONTOH PROMPT
   ================================================================ */
.aiimg-section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 20px 0 11px;
    color: #594B62;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.aiimg-section-title i {
    height: 1px;
    flex: 1 1 auto;
    background: #E3DBD1;
}
.aiimg-section-icon { color: #4D3A69; }
.aiimg-section-icon .mi { font-size: 20px; }

.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] {
    min-width: 0 !important;
    overflow: hidden !important;
    border: 1px solid #E6DDD2 !important;
    border-radius: 14px !important;
    background: rgba(255, 253, 249, 0.72) !important;
    box-shadow: 0 5px 14px rgba(88, 67, 47, 0.05) !important;
}
.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.aiimg-sug-visual {
    position: relative;
    height: 86px;
    overflow: hidden;
    background: linear-gradient(135deg, #FBF5ED, #F2EAF2);
}
.aiimg-sug-visual::after {
    content: "";
    position: absolute;
    right: 28px;
    bottom: -58px;
    width: 190px;
    height: 115px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.57);
    transform: rotate(-10deg);
}
.aiimg-sug-icon {
    position: absolute;
    left: 16px;
    top: 20px;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    color: #4E3B6C;
    background: #F0E8F4;
    box-shadow: 0 5px 12px rgba(98, 75, 119, 0.14);
}
.aiimg-sug-icon .mi { font-size: 22px; }
.aiimg-sug-art {
    position: absolute;
    right: 30px;
    top: 18px;
    width: 78px;
    height: 50px;
    border: 1px solid rgba(221, 212, 230, 0.9);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.68);
    box-shadow: 7px 8px 15px rgba(98, 75, 119, 0.10);
    transform: rotate(-5deg);
}
.aiimg-sug-art::before {
    content: "";
    position: absolute;
    inset: 9px;
    border-radius: 8px;
    background: linear-gradient(135deg, #EFE3F5, #F7E9D6);
}
.aiimg-sug-art::after {
    content: "";
    position: absolute;
    left: 12px;
    bottom: -12px;
    width: 54px;
    height: 34px;
    border: 1px solid rgba(221, 212, 230, 0.7);
    border-radius: 9px;
    background: rgba(255, 255, 255, 0.5);
    transform: rotate(6deg);
}

/* Tombol pada kartu contoh: menyatu dengan kartu. */
.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] [class*="st-key-aiimg_sug_btn_"] button {
    border: none !important;
    border-top: 1px solid #EFE7DB !important;
    border-radius: 0 0 13px 13px !important;
    background: rgba(255, 255, 255, 0.25) !important;
    box-shadow: none !important;
    padding: 10px 12px 11px !important;
}
.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] [class*="st-key-aiimg_sug_btn_"] button:hover {
    background: #F6EEF9 !important;
}
.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] [class*="st-key-aiimg_sug_btn_"] button p {
    line-height: 1.3 !important;
}
.stApp:has(.aiimg-page-shell)
[class*="st-key-aiimg_sug_"] [class*="st-key-aiimg_sug_btn_"] button p:first-child {
    color: #302243 !important;
    font-weight: 700 !important;
    font-size: 0.98rem !important;
}

/* Strip tips di bawah kartu contoh */
.aiimg-tips {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 14px 0 4px;
    padding: 10px 14px;
    border: 1px dashed #D8CBB8;
    border-radius: 12px;
    background: rgba(255, 253, 248, 0.6);
    color: #6B6172;
    font-size: 0.84rem;
    line-height: 1.5;
}
.aiimg-tips-icon {
    display: grid;
    place-items: center;
    flex: 0 0 30px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #F5EDD9;
    color: #A07E3C;
}
.aiimg-tips-icon .mi { font-size: 17px; }

/* ================================================================
   PANEL KANAN — pengaturan gaya & format
   ----------------------------------------------------------------
   Chip GAYA & FORMAT dulu menempel di kotak input bawah sehingga
   doknya tinggi dan gampang menumpuk. Sekarang keduanya tinggal di
   kartu melayang di sisi kanan layar (st.container(key="aiimg_panel")),
   dan kotak input ikut terangkat.

   --aiimg-panel-w   : lebar kartu panel
   --aiimg-panel-top : jarak kartu dari sisi atas layar
   ================================================================ */
:root {
    --aiimg-panel-w: 268px;
    --aiimg-panel-top: 30px;
    /* jarak dasar panel dari bawah layar — disamakan dengan tinggi
       angkat kotak input supaya kaki panel & kotak input sejajar */
    --aiimg-panel-bottom: 70px;
}

.stApp:has(.aiimg-page-shell) .st-key-aiimg_panel {
    position: fixed !important;
    top: var(--aiimg-panel-top) !important;
    right: 22px !important;
    left: auto !important;
    width: var(--aiimg-panel-w) !important;
    max-width: var(--aiimg-panel-w) !important;
    bottom: var(--aiimg-panel-bottom) !important;
    /* Ditulis SATU BARIS & pakai angka mentah (bukan var) supaya tidak ada
       satu pun browser/parser yang membuangnya — panel wajib memanjang. */
    height: auto !important;
    min-height: calc(100vh - 106px) !important;
    max-height: none !important;
    overflow-y: auto !important;
    padding: 15px 16px 14px !important;
    border: 1px solid #E6DAC6 !important;
    border-radius: 18px !important;
    background: linear-gradient(180deg, #FFFDF8 0%, #FBF3E6 100%) !important;
    box-shadow: 0 18px 42px rgba(76, 58, 105, 0.13) !important;
    gap: 7px !important;
    z-index: 40 !important;
    scrollbar-width: thin;
}
/* Judul kartu panel */
.aiimg-panel-head {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 0 0 4px;
    color: #4D3A69;
    font-size: 0.88rem;
    font-weight: 800;
    letter-spacing: 0.01em;
}
.aiimg-panel-head-icon {
    display: grid;
    place-items: center;
    flex: 0 0 28px;
    width: 28px;
    height: 28px;
    border-radius: 9px;
    background: linear-gradient(145deg, #F5EEF8, #EDE6F3);
    border: 1px solid #E1D8E8;
    color: #4D3A69;
}
.aiimg-panel-head-icon .mi { font-size: 16px; }
/* Keterangan format terpilih di dasar panel */
.aiimg-panel-hint {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px dashed #E3D6C2;
    color: #9B8FA6;
    font-size: 0.72rem;
    line-height: 1.45;
}
.aiimg-panel-hint .mi { font-size: 14px; color: #B39EC6; }

/* Pil di dalam panel boleh melipat ke baris berikutnya */
.stApp:has(.aiimg-page-shell) .stButtonGroup [role="group"],
.stApp:has(.aiimg-page-shell) .stButtonGroup > div {
    flex-wrap: wrap !important;
    gap: 6px !important;
}

/* Pil: keadaan biasa (beige) — dua penulisan agar cocok di versi
   Streamlit lama (stBaseButton-pills) maupun baru (data-variant). */
.stApp:has(.aiimg-page-shell) button[data-variant="pills"],
.stApp:has(.aiimg-page-shell) [data-testid="stBaseButton-pills"] {
    background: #F8F1E4 !important;
    border: 1px solid #E2D6C2 !important;
    border-radius: 999px !important;
    color: #5C5266 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.2rem 0.7rem !important;
    min-height: 31px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    transition: border-color 0.15s ease, background 0.15s ease,
                color 0.15s ease !important;
}
.stApp:has(.aiimg-page-shell) button[data-variant="pills"]:hover,
.stApp:has(.aiimg-page-shell) [data-testid="stBaseButton-pills"]:hover {
    border-color: #B39EC6 !important;
    background: #FBF6EC !important;
    color: #4A3559 !important;
}
/* Pil terpilih: ungu Trinity */
.stApp:has(.aiimg-page-shell) button[data-variant="pills"][data-selected],
.stApp:has(.aiimg-page-shell) button[data-variant="pills"][aria-selected="true"],
.stApp:has(.aiimg-page-shell) [data-testid="stBaseButton-pillsActive"] {
    background: linear-gradient(135deg, #7C5C99, #4D3A69) !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    color: #FFF6E9 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(77, 58, 105, 0.32) !important;
}
.stApp:has(.aiimg-page-shell) button[data-variant="pills"][data-selected] *,
.stApp:has(.aiimg-page-shell) button[data-variant="pills"][aria-selected="true"] *,
.stApp:has(.aiimg-page-shell) [data-testid="stBaseButton-pillsActive"] * {
    color: #FFF6E9 !important;
}
/* ikon material di dalam pil ikut mengecil */
.stApp:has(.aiimg-page-shell) button[data-variant="pills"]
[data-testid="stIconMaterial"],
.stApp:has(.aiimg-page-shell) [data-testid="stBaseButton-pills"]
[data-testid="stIconMaterial"] {
    font-size: 15px !important;
    width: 15px !important;
    height: 15px !important;
}

/* Tombol cadangan (Streamlit lama, tanpa st.pills) di dalam panel */
.st-key-aiimg_panel [class*="st-key-aiimg_gaya_"]:not([class*="st-key-aiimg_gaya_on"]) button,
.st-key-aiimg_panel [class*="st-key-aiimg_rasio_"]:not([class*="st-key-aiimg_rasio_on"]) button {
    background: #F8F1E4 !important;
    border: 1px solid #E2D6C2 !important;
    border-radius: 999px !important;
    color: #5C5266 !important;
    font-size: 0.78rem !important;
    min-height: 31px !important;
}
.st-key-aiimg_panel [class*="st-key-aiimg_gaya_on"] button,
.st-key-aiimg_panel [class*="st-key-aiimg_rasio_on"] button {
    background: linear-gradient(135deg, #7C5C99, #4D3A69) !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    color: #FFF6E9 !important;
    min-height: 31px !important;
}

/* Isi halaman diberi ruang supaya tidak tertimpa panel kanan */
.stApp:has(.aiimg-page-shell)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 220px - var(--aiimg-panel-w)) !important;
    margin-left: auto !important;
    margin-right: calc(var(--aiimg-panel-w) + 30px) !important;
    padding-bottom: 120px !important;
}

/* ================================================================
   KOLOM CHAT INPUT — dinaikkan (chip sudah tidak menempel lagi)
   ================================================================ */
/* --aiimg-chat-lift : tinggi angkat kolom input dari dasar layar.
   Perbesar angkanya kalau mau kolom chat lebih naik lagi. */
/* Kotaknya diberi KOTAK YANG SAMA dengan kolom isi halaman (kartu contoh
   & percakapan), lalu kartu input di dalamnya dipusatkan — jadi titik
   tengahnya persis segaris dengan kartu di atasnya, bukan tengah layar. */
.stApp:has(.aiimg-page-shell)
[data-testid="stBottomBlockContainer"] {
    --aiimg-chat-lift: 72px;
    margin-bottom: var(--aiimg-chat-lift) !important;
    width: calc(100% - 220px - var(--aiimg-panel-w)) !important;
    max-width: none !important;
    margin-left: auto !important;
    margin-right: calc(var(--aiimg-panel-w) + 30px) !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    align-items: center !important;
    transform: none !important;
}
.stApp:has(.aiimg-page-shell)
[data-testid="stBottomBlockContainer"] > * {
    width: 100% !important;
    max-width: 46rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.stApp:has(.aiimg-page-shell) .dock-spacer { height: 104px !important; }

/* Label "Gaya" / "Format" di atas deretan pil */
.aiimg-chip-label {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 2px 1px;
    color: #8E8398;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    white-space: nowrap;
}
.aiimg-chip-label .mi { font-size: 14px; color: #7C5C99; }
.aiimg-chip-label-2 { margin-top: 10px; }

/* Chip dasar (tidak aktif) */
[class*="st-key-aiimg_gaya_"]:not([class*="st-key-aiimg_gaya_on"]) button,
[class*="st-key-aiimg_rasio_"]:not([class*="st-key-aiimg_rasio_on"]) button {
    background: #F8F1E4 !important;
    border: 1px solid #E2D6C2 !important;
    border-radius: 999px !important;
    color: #5C5266 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.2rem 0.6rem !important;
    min-height: 31px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    transition: border-color 0.15s ease, background 0.15s ease,
                color 0.15s ease !important;
}
[class*="st-key-aiimg_gaya_"]:not([class*="st-key-aiimg_gaya_on"]) button:hover,
[class*="st-key-aiimg_rasio_"]:not([class*="st-key-aiimg_rasio_on"]) button:hover {
    border-color: #B39EC6 !important;
    background: #FBF6EC !important;
    color: #4A3559 !important;
}
/* Chip aktif: pil ungu Trinity */
[class*="st-key-aiimg_gaya_on"] button,
[class*="st-key-aiimg_rasio_on"] button {
    background: linear-gradient(135deg, #7C5C99, #4D3A69) !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    color: #FFF6E9 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    padding: 0.2rem 0.6rem !important;
    min-height: 31px !important;
    box-shadow: 0 4px 12px rgba(77, 58, 105, 0.32) !important;
    white-space: nowrap !important;
}
/* Keterangan format terpilih (mis. "Story · dipotong otomatis") */
.aiimg-rasio-hint {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 7px 2px 0 6px;
    color: #A79BAD;
    font-size: 0.72rem;
    white-space: nowrap;
}

/* ================================================================
   RESPONSIF — layar sempit
   ================================================================ */
/* Layar tidak cukup lebar untuk panel melayang: panel turun jadi kartu
   biasa di atas percakapan, isi halaman & kotak input kembali penuh. */
@media (max-width: 1200px) {
    .stApp:has(.aiimg-page-shell) .st-key-aiimg_panel {
        position: static !important;
        width: 100% !important;
        max-width: none !important;
        max-height: none !important;
        min-height: 0 !important;
        height: auto !important;
        bottom: auto !important;
        margin: 0 0 16px !important;
        overflow: visible !important;
    }
    .stApp:has(.aiimg-page-shell)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 64px) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .stApp:has(.aiimg-page-shell)
    [data-testid="stBottomBlockContainer"] {
        width: 100% !important;
        max-width: 46rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
}
@media (max-width: 860px) {
    .aiimg-hero { padding: 34px 18px 28px; }
    .aiimg-hero .frame-a,
    .aiimg-hero .frame-b,
    .aiimg-hero .frame-c { display: none; }
    .aiimg-hero p { font-size: 0.9rem; }
    .aiimg-rasio-hint { display: none; }
}
@media (max-width: 560px) {
    .aiimg-hero h2 { font-size: 1.55rem; }
    .aiimg-hero-tags span { font-size: 0.72rem; }
}

/* ================================================================
   HASIL GAMBAR & LOADER DI HALAMAN AI IMAGE
   Keduanya dipaku sejajar dengan teks percakapan, tidak boleh melar
   atau tertarik ke tepi kiri layar.

   --aiimg-hasil-x : geser halus kiri/kanan (px). 0 = sejajar teks.
   ================================================================ */
.stApp:has(.aiimg-page-shell) {
    --aiimg-hasil-x: 0px;
}
.stApp:has(.aiimg-page-shell) [class*="st-key-img_prev_"],
.stApp:has(.aiimg-page-shell) [class*="st-key-img_pop_"],
.stApp:has(.aiimg-page-shell) [class*="st-key-img_loader_slot"],
.stApp:has(.aiimg-page-shell) [class*="st-key-yuki_loader_slot"] {
    position: static !important;
    left: auto !important;
    right: auto !important;
    margin-left: var(--aiimg-hasil-x) !important;
    margin-right: auto !important;
    align-items: flex-start !important;
}
.stApp:has(.aiimg-page-shell) [class*="st-key-img_loader_slot"] iframe,
.stApp:has(.aiimg-page-shell) [class*="st-key-yuki_loader_slot"] iframe {
    position: static !important;
    left: auto !important;
    top: auto !important;
    margin-left: 0 !important;
}
.stApp:has(.aiimg-page-shell)
[data-testid="stMainBlockContainer"] div.stDownloadButton {
    margin-left: var(--aiimg-hasil-x) !important;
}
"""
