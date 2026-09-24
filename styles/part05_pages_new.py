# -*- coding: utf-8 -*-
"""Halaman baru: Artefak, Pengaturan, Bahasa, Bantuan, Trinity Pro, Aplikasi, Kursus, Pelajari, baris akun, tombol top up

Dipecah dari styles.py asli (baris 3224-3549), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ============ HALAMAN BARU (Artefak · Pengaturan · Bahasa ·
   Bantuan · Trinity Pro · Aplikasi · Trinity Kursus · Pelajari) ============ */
/* --- baris akun + menu titik tiga --- */
.sb-account {
    width: 230px !important;
    max-width: 230px !important;
    padding-right: 42px;            /* ruang untuk tombol menu ⋯ */
    pointer-events: none;           /* teksnya saja; tombol di sebelahnya */
}
.st-key-sb_account [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-sb_account [data-testid="stColumn"]:first-child { padding-right: 0 !important; }
/* >>> PENTING: POSISI TOMBOL TITIK TIGA (menu akun) TIDAK diatur di sini.
   Posisinya diatur di sidebar.py (ACCT_MENU_X_PX / ACCT_MENU_Y_PX), yang
   disuntik sebagai <style> tepat di dekat tombolnya. Kalau posisinya juga
   ditulis di sini, dua aturan saling bertabrakan dan yang menang tidak
   terduga — pernah membuat tombolnya terlempar 60px ke bawah layar dan
   seolah "hilang". Aturan di bawah hanya gaya visualnya saja. */
/* Sembunyikan baris kartu nama user saat sidebar tertutup */
section[data-testid="stSidebar"][aria-expanded="false"] .sb-account,
section[data-testid="stSidebar"][aria-expanded="false"] .st-key-acct_menu,
section[data-testid="stSidebar"][aria-expanded="false"] .st-key-sb_account {
    display: none !important;
    visibility: hidden !important;
}
.st-key-acct_menu [data-testid="stPopover"] > div { width: auto !important; }
.st-key-acct_menu button[data-testid="stPopoverButton"],
.st-key-acct_menu [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    color: #6B6172 !important;
    width: 32px !important; min-width: 32px !important; height: 32px !important;
    border-radius: 8px !important; padding: 0 !important;
    display: grid !important; place-items: center !important;
}
.st-key-acct_menu button:hover {
    background: #E0D2BB !important; color: #2C1F33 !important;
}
.st-key-acct_menu button svg { width: 20px !important; height: 20px !important; }

/* --- judul halaman --- */
.page-head {
    display: flex; align-items: flex-start; gap: 14px;
    margin: 4px 0 18px;
}
.page-head-icon {
    width: 40px; height: 40px; flex-shrink: 0;
    border-radius: 12px;
    background: #E0D2BB; border: 1px solid #CDBFA8;
    display: grid; place-items: center;
    color: #4A3559;
}
.page-head-icon [data-testid="stIconMaterial"],
.page-head-icon span[data-testid="stIconMaterial"] { font-size: 21px !important; }
/* Ikon Material yang kita buat sendiri lewat mi() (dipakai di dalam HTML,
   karena sintaks ikon material tidak diterjemahkan Streamlit di dalam HTML).
   Ukurannya disamakan dengan ikon bawaan Streamlit di posisi yang sama. */
.page-head-icon .mi { font-size: 21px; }
.cap-row .cap-icon .mi { font-size: 18px; }
.cap-row .cap-state .mi { font-size: 15px; vertical-align: -3px; }
.help-step .step-icon .mi { font-size: 18px; }
.mini-card .mini-icon .mi { font-size: 22px; }
.feat-row .chip-on .mi, .feat-row .chip-off .mi { font-size: 15px; vertical-align: -3px; }
.page-head h2.page-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 600; color: #1B1220;
    margin: 0 0 2px; line-height: 1.15; letter-spacing: -0.01em;
}
.page-head p.page-sub {
    margin: 0; font-size: 0.9rem; color: #6B6172; line-height: 1.45;
}

/* --- kartu kategori berbentuk PERSEGI (halaman Artefak & Trinity kursus) ---
   Susunan: IKON BESAR di atas, lalu judul, lalu deskripsi kecil — semua
   di tengah. Ikon sengaja jauh lebih besar daripada teksnya. */
button[kind="secondary"] > div > p > strong,
div.stButton > button p strong { color: #2C1F33; }
.st-key-cat_app button, .st-key-cat_doc button, .st-key-cat_game button,
.st-key-cat_prod button, .st-key-cat_kre button, .st-key-cat_quiz button,
.st-key-cat_new button,
[class*="st-key-kurs_"] button {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 18px !important;
    padding: 18px 14px !important;
    /* PERSEGI: tinggi mengikuti lebar, dibatasi agar tidak raksasa */
    aspect-ratio: 1 / 1 !important;
    width: 100% !important;
    max-width: 220px !important;
    min-height: 0 !important;
    height: auto !important;
    margin: 0 auto !important;
    /* isi ditumpuk vertikal & dipusatkan */
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    gap: 0 !important;
    transition: border-color .16s ease, background .16s ease, transform .16s ease;
}
.st-key-cat_app button:hover, .st-key-cat_doc button:hover,
.st-key-cat_game button:hover, .st-key-cat_prod button:hover,
.st-key-cat_kre button:hover, .st-key-cat_quiz button:hover,
.st-key-cat_new button:hover,
[class*="st-key-kurs_"] button:hover {
    border-color: #8B7499 !important;
    background: #F7ECD9 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(44,31,51,0.09) !important;
}
[class*="st-key-cat_"] button [data-testid="stMarkdownContainer"],
[class*="st-key-kurs_"] button [data-testid="stMarkdownContainer"] {
    width: 100%;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}
[class*="st-key-cat_"] button p, [class*="st-key-kurs_"] button p {
    white-space: normal !important;
    line-height: 1.3 !important;
    text-align: center !important;
    margin: 0 !important;
}
/* IKON: paling besar, jadi baris tersendiri di paling atas */
[class*="st-key-cat_"] button span[role="img"],
[class*="st-key-kurs_"] button span[role="img"] {
    display: block !important;
    font-size: 2.7rem !important;
    line-height: 1 !important;
    color: #4A3559 !important;
    margin: 0 0 12px !important;
    vertical-align: baseline !important;
}
/* judul: sedang, tebal */
[class*="st-key-cat_"] button p strong, [class*="st-key-kurs_"] button p strong {
    font-size: 0.98rem;
    font-weight: 600;
    display: block;
    margin-bottom: 6px;
}
/* deskripsi: paling kecil & abu (sintaks "small" tidak ada di Streamlit) */
[class*="st-key-cat_"] button .stMarkdownColoredText,
[class*="st-key-kurs_"] button .stMarkdownColoredText {
    display: block;
    font-size: 0.78rem;
    line-height: 1.35;
}

/* --- kartu kosong --- */
.empty-card {
    background: #F2E8D6; border: 1px dashed #CDBFA8;
    border-radius: 14px; padding: 18px;
    color: #6B6172; font-size: 0.9rem; line-height: 1.55;
    margin: 2px 0 16px;
}

/* --- hero halaman --- */
.trinity-hero {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 18px;
    padding: 22px; display: flex; gap: 18px; align-items: center;
    margin-bottom: 16px;
}
.trinity-hero > div:first-child { flex-shrink: 0; }
.trinity-hero .logo-greeting { width: 42px; height: 42px; }
.trinity-hero .hero-text h1 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.8rem; font-weight: 600; color: #1B1220;
    margin: 0 0 6px; letter-spacing: -0.01em;
}
.trinity-hero .hero-text p {
    margin: 0; color: #6B6172; font-size: 0.92rem; line-height: 1.55;
}

/* --- judul bagian di dalam halaman --- */
.set-section {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.06rem; font-weight: 600; color: #2C1F33;
    margin: 22px 0 10px;
}
/* judul bagian PERTAMA di sebuah tab/halaman tidak perlu jarak atas besar,
   supaya ritme jarak antar bagian terasa konsisten */
[data-testid="stVerticalBlock"] > .element-container:first-child .set-section,
[data-testid="stVerticalBlock"] > [data-testid="stMarkdownContainer"]:first-child .set-section {
    margin-top: 2px;
}

/* --- bagian berbahaya (hapus data) di tab Privasi --- */
.set-section.danger { color: #A63D3D; }
.danger-box {
    background: #F7ECEC; border: 1px solid #E0C5C5; border-radius: 12px;
    padding: 10px 14px; font-size: 0.85rem; color: #6B4A4A;
    line-height: 1.5; margin-bottom: 10px;
}

/* --- kartu kemampuan --- */
.cap-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 6px 14px; margin: 4px 0 8px;
}
.cap-row {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 0; border-bottom: 1px solid #E7D9C1;
    font-size: 0.9rem;
}
.cap-row:last-child { border-bottom: none; }
.cap-row .cap-icon { color: #4A3559; display: grid; place-items: center; width: 22px; }
.cap-row .cap-name { flex: 1; color: #2C1F33; }
.cap-row .cap-state {
    display: inline-flex; align-items: center; gap: 6px;
    color: #7E7387; font-size: 0.82rem;
}

/* --- baris fitur / status kecil --- */
.feat-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 9px 2px; font-size: 0.88rem; color: #2C1F33;
    border-bottom: 1px solid #E7D9C1;
}
.feat-row:last-child { border-bottom: none; }
.chip-on, .chip-off {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.76rem; font-weight: 600;
    padding: 2px 8px; border-radius: 99px; white-space: nowrap;
}
.chip-on { background: #E4EAD8; color: #3F6B33; }
.chip-off { background: #E7DBC6; color: #7D7484; }

/* --- kartu paket (Trinity Pro) --- */
.plan-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 16px;
    padding: 20px; height: 100%; box-sizing: border-box;
}
.plan-card.is-pro {
    border-color: #2C1F33; background: #F7EBD6;
    box-shadow: 0 6px 22px rgba(44,31,51,0.14);
}
.plan-name {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.2rem; font-weight: 600; color: #1B1220;
}
.plan-price {
    font-size: 1.75rem; font-weight: 700; color: #4A3559;
    margin: 6px 0 2px; letter-spacing: -0.02em;
}
.plan-note { font-size: 0.8rem; color: #7E7387; margin-bottom: 12px; }
.feat-list { margin-top: 4px; }

/* --- memori --- */
.mem-item {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #2C1F33; margin-bottom: 6px;
}

/* --- daftar bahasa --- */
.lang-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 4px 14px;
}
.lang-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid #E7D9C1; font-size: 0.9rem;
}
.lang-row:last-child { border-bottom: none; }
.lang-row .flag { font-size: 1.15rem; line-height: 1; }
.lang-row .lang-name {
    flex: 1; color: #2C1F33; font-weight: 500;
    display: flex; flex-direction: column;
}
.lang-row .lang-native { font-size: 0.76rem; color: #7E7387; font-weight: 400; }
.lang-row .lang-level { display: inline-flex; align-items: center; gap: 6px; }

/* --- langkah bantuan & tips --- */
.help-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; font-size: 0.9rem; color: #2C1F33; line-height: 1.5;
}
.help-step .step-no {
    width: 24px; height: 24px; flex-shrink: 0;
    border-radius: 50%; background: #E0D2BB; color: #4E4553;
    display: grid; place-items: center;
    font-size: 0.74rem; font-weight: 700;
}
.help-step .step-icon { color: #4A3559; padding-top: 2px; }
.tip-row {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 0; font-size: 0.89rem; color: #2C1F33; line-height: 1.5;
}
.tip-row .tip-no {
    width: 22px; height: 22px; flex-shrink: 0; border-radius: 50%;
    background: #DDD2E4; color: #4A3559;
    display: grid; place-items: center; font-size: 0.72rem; font-weight: 700;
}

/* --- mini card (tentang aplikasi) --- */
.mini-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 14px;
    padding: 16px; height: 100%; box-sizing: border-box;
}
.mini-card .mini-icon { color: #4A3559; margin-bottom: 8px; }
.mini-card .mini-title { font-weight: 600; color: #2C1F33; margin-bottom: 4px; }
.mini-card .mini-desc { font-size: 0.84rem; color: #6B6172; line-height: 1.5; }

/* --- kartu ponsel (halaman Dapatkan aplikasi) --- */
.phone-card {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 22px;
    padding: 30px 20px; text-align: center;
}
.phone-card .logo-greeting { width: 54px; height: 54px; margin: 0 auto 12px; }
.phone-card .phone-name { font-weight: 600; color: #2C1F33; }
.phone-card .phone-tag { font-size: 0.78rem; color: #7E7387; margin-top: 2px; }

/* --- baris modul kursus --- */
.mod-row {
    background: #F2E8D6; border: 1px solid #DBCEB9; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #2C1F33; margin-bottom: 6px;
}

/* --- tab Pengaturan: rapikan --- */
[data-baseweb="tab-list"] { gap: 4px !important; border-bottom: 1px solid #DBCEB9 !important; }
[data-baseweb="tab"] {
    font-size: 0.86rem !important; padding: 8px 10px !important;
    color: #6B6172 !important; background: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] { color: #2C1F33 !important; font-weight: 600 !important; }
[data-baseweb="tab-highlight"] { background-color: #2C1F33 !important; }
"""
