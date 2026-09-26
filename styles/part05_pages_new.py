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

/* ============================================================
   ARTEFAK — LANDING PAGE BERBASIS KARTU
   ============================================================ */
.stApp:has(.artifact-page-shell) {
    background: #F5EBDD !important;
}

.stApp:has(.artifact-page-shell)
[data-testid="stMain"],
.stApp:has(.artifact-page-shell)
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

.stApp:has(.artifact-page-shell)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 136px) !important;
    max-width: none !important;
    margin: 0 auto !important;
    padding: 32px 0 90px !important;
    box-sizing: border-box !important;
}

.stApp:has(.artifact-page-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    gap: 0 !important;
}

.artifact-page-shell {
    display: none !important;
}

.artifact-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    margin: 0 0 28px;
}

.artifact-heading {
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 0;
}

.artifact-heading-icon,
.artifact-category-icon {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 52px;
    height: 52px;
    border-radius: 16px;
    color: #443262;
    background: linear-gradient(145deg, #FFFFFF, #EEE8F7);
    border: 1px solid #E1D8ED;
    box-shadow: 0 8px 20px rgba(83, 64, 112, 0.10);
}

.artifact-heading-icon .mi,
.artifact-category-icon .mi {
    font-size: 27px;
}

.artifact-heading h1 {
    margin: 0;
    color: #2B203A;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    line-height: 1.05;
    letter-spacing: -0.04em;
}

.artifact-heading p {
    margin: 7px 0 0;
    color: #7D7186;
    font-size: 0.92rem;
    line-height: 1.35;
}

.artifact-brand {
    display: flex;
    align-items: center;
    gap: 13px;
    flex: 0 0 auto;
    color: #695B74;
    font-size: 0.84rem;
}

.artifact-brand > span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 13px;
    border: 1px solid #E8DFD4;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.54);
    color: #51435F;
    font-weight: 600;
}

.artifact-brand > span .mi { font-size: 16px; }
.artifact-brand i {
    width: 1px;
    height: 20px;
    background: #DED4C8;
}
.artifact-brand small { color: #8A7F8A; }

.artifact-hero {
    position: relative;
    min-height: 238px;
    display: flex;
    align-items: center;
    overflow: hidden;
    margin: 0 0 38px;
    padding: 34px 40px;
    border: 1px solid #E9DFD2;
    border-radius: 18px;
    background:
        radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.92), transparent 31%),
        linear-gradient(110deg, #F7F0E6 0%, #FCF7EE 54%, #F4ECDD 100%);
    box-shadow: 0 12px 28px rgba(111, 85, 53, 0.055);
}

.artifact-hero-copy {
    position: relative;
    z-index: 2;
    width: min(50%, 560px);
}

.artifact-welcome {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 13px;
    border: 1px solid #E9DDCA;
    border-radius: 999px;
    background: rgba(255, 250, 239, 0.78);
    color: #4F405B;
    font-size: 0.8rem;
    font-weight: 600;
}
.artifact-welcome .mi { font-size: 16px; color: #625080; }

.artifact-hero h2 {
    margin: 18px 0 12px;
    color: #302244;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.45rem);
    line-height: 1.1;
    letter-spacing: -0.045em;
}
.artifact-hero p {
    max-width: 560px;
    margin: 0;
    color: #756A7A;
    font-size: 0.98rem;
    line-height: 1.65;
}

.artifact-hero-art {
    position: absolute;
    inset: 0 3% 0 48%;
    overflow: hidden;
}
.artifact-orbit {
    position: absolute;
    width: 85%;
    height: 160px;
    border: 1px solid rgba(206, 187, 218, 0.52);
    border-radius: 50%;
    transform: rotate(-15deg);
}
.artifact-orbit-a { top: 45px; left: 7%; }
.artifact-orbit-b { top: 58px; left: 5%; transform: rotate(18deg); opacity: 0.58; }

.artifact-hero-window {
    position: absolute;
    top: 40px;
    left: 35%;
    width: 220px;
    height: 150px;
    padding: 17px 18px;
    border: 1px solid rgba(222, 213, 224, 0.9);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.72);
    box-shadow: 0 18px 32px rgba(107, 80, 128, 0.13);
    transform: rotate(-7deg);
}
.artifact-window-bar { display: flex; gap: 5px; margin-bottom: 18px; }
.artifact-window-bar b {
    width: 7px; height: 7px; border-radius: 50%; background: #D9C7E5;
}
.artifact-window-line {
    width: 70%; height: 8px; margin: 9px 0;
    border-radius: 99px; background: #E6DCEB;
}
.artifact-window-line.wide { width: 88%; background: #CFC0E1; }
.artifact-window-line.short { width: 48%; }
.artifact-window-spark {
    position: absolute;
    right: 24px;
    bottom: 20px;
    display: grid;
    place-items: center;
    width: 43px;
    height: 43px;
    border-radius: 12px;
    color: #FFF;
    background: linear-gradient(145deg, #8A6BC0, #4E397C);
    box-shadow: 0 8px 18px rgba(86, 56, 130, 0.27);
}
.artifact-window-spark .mi { font-size: 24px; }

.artifact-float {
    position: absolute;
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border: 1px solid rgba(229, 220, 232, 0.92);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.76);
    color: #7560A0;
    box-shadow: 0 8px 18px rgba(105, 81, 123, 0.10);
}
.artifact-float .mi { font-size: 23px; }
.artifact-float-image { top: 30px; left: 22%; transform: rotate(-7deg); }
.artifact-float-code { bottom: 36px; left: 18%; transform: rotate(8deg); }
.artifact-float-type { top: 26px; right: 20%; color: #76549A; font: 700 1.8rem Georgia, serif; transform: rotate(5deg); }
.artifact-float-play { bottom: 47px; right: 16%; transform: rotate(-8deg); }

.artifact-category-heading {
    display: flex;
    align-items: center;
    gap: 14px;
    min-height: 54px;
}
.artifact-category-icon { width: 46px; height: 46px; border-radius: 14px; }
.artifact-category-icon .mi { font-size: 23px; }
.artifact-category-heading h2 {
    margin: 0 0 4px;
    color: #332642;
    font-size: 1.18rem;
    line-height: 1.2;
    letter-spacing: -0.025em;
}
.artifact-category-heading p {
    margin: 0;
    color: #867A88;
    font-size: 0.82rem;
    line-height: 1.4;
}

.stApp:has(.artifact-page-shell) [class*="st-key-artifact_search_box"] {
    padding: 0 !important;
}
.stApp:has(.artifact-page-shell) [class*="st-key-artifact_search_box"] [data-testid="stTextInput"] {
    margin: 0 !important;
}
.stApp:has(.artifact-page-shell) [class*="st-key-artifact_search_box"] input {
    min-height: 44px !important;
    padding: 0 18px 0 42px !important;
    border: 1px solid #E4D9CD !important;
    border-radius: 999px !important;
    background: rgba(255, 255, 255, 0.66) !important;
    color: #3B2D4A !important;
    box-shadow: 0 6px 14px rgba(88, 65, 95, 0.045) !important;
}
.stApp:has(.artifact-page-shell) [class*="st-key-artifact_search_box"] [data-testid="stTextInput"]::before {
    content: "search";
    position: absolute;
    z-index: 2;
    margin: 12px 0 0 15px;
    color: #776C83;
    font-family: 'Material Symbols Rounded';
    font-size: 21px;
}

.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] {
    min-width: 0 !important;
    min-height: 224px !important;
    margin: 26px 0 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    border: 1px solid #E7DDD0 !important;
    border-radius: 16px !important;
    background: rgba(255, 255, 255, 0.58) !important;
    box-shadow: 0 8px 22px rgba(101, 76, 50, 0.045) !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    min-height: 224px !important;
}

.artifact-card-visual {
    position: relative;
    height: 142px;
    overflow: hidden;
    margin: 0;
    background: linear-gradient(145deg, #F5F1FF, #EEF4FF);
}
.artifact-card-visual::after {
    content: "";
    position: absolute;
    right: -32px;
    bottom: -48px;
    width: 170px;
    height: 120px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.50);
    transform: rotate(-14deg);
}
.artifact-visual-glow {
    position: absolute;
    left: 18%;
    top: 25%;
    width: 100px;
    height: 70px;
    border-radius: 50%;
    background: rgba(168, 188, 255, 0.35);
    filter: blur(22px);
}
.artifact-visual-icon {
    position: absolute;
    left: 14%;
    top: 28px;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 43px;
    height: 43px;
    border-radius: 50%;
    color: #4A60A4;
    background: #E4ECFF;
    box-shadow: 0 8px 16px rgba(74, 96, 164, 0.13);
}
.artifact-visual-icon .mi { font-size: 23px; }
.artifact-visual-sheet {
    position: absolute;
    z-index: 1;
    right: 15%;
    top: 28px;
    width: 98px;
    height: 76px;
    padding: 14px 12px;
    box-sizing: border-box;
    border: 1px solid rgba(214, 222, 244, 0.88);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.76);
    box-shadow: 6px 9px 15px rgba(84, 103, 158, 0.12);
    transform: rotate(7deg);
}
.artifact-visual-sheet span {
    display: block;
    width: 75%;
    height: 6px;
    margin: 0 0 9px;
    border-radius: 99px;
    background: #C9D8F4;
}
.artifact-visual-sheet span:nth-child(2) { width: 92%; background: #DFE6F6; }
.artifact-visual-sheet span:nth-child(3) { width: 60%; background: #E8E8F2; }
.artifact-visual-badge {
    position: absolute;
    right: 11%;
    bottom: 18px;
    z-index: 3;
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 9px;
    color: #FFF;
    background: #7990CD;
    box-shadow: 0 5px 12px rgba(64, 88, 151, 0.25);
}
.artifact-visual-badge .mi { font-size: 18px; }

.artifact-visual-doc { background: linear-gradient(145deg, #F3F8FF, #EAF2FD); }
.artifact-visual-doc .artifact-visual-icon { color: #3D6BB3; background: #E0EDFF; }
.artifact-visual-doc .artifact-visual-badge { background: #76A5DC; }
.artifact-visual-game { background: linear-gradient(145deg, #FFF7E9, #FFF0D8); }
.artifact-visual-game .artifact-visual-icon { color: #D7831B; background: #FFE9C4; }
.artifact-visual-game .artifact-visual-badge { background: #E7A64B; }
.artifact-visual-prod { background: linear-gradient(145deg, #F1FFF5, #E6F8ED); }
.artifact-visual-prod .artifact-visual-icon { color: #329568; background: #DDF4E6; }
.artifact-visual-prod .artifact-visual-badge { background: #53AE82; }
.artifact-visual-kre { background: linear-gradient(145deg, #FCF2FF, #F4EAFF); }
.artifact-visual-kre .artifact-visual-icon { color: #8051B2; background: #EEDFFF; }
.artifact-visual-kre .artifact-visual-badge { background: #A27AC9; }
.artifact-visual-quiz { background: linear-gradient(145deg, #FFF2F4, #FFE7EC); }
.artifact-visual-quiz .artifact-visual-icon { color: #B85C79; background: #FFDDE5; }
.artifact-visual-quiz .artifact-visual-badge { background: #D77B98; }
.artifact-visual-new { background: linear-gradient(145deg, #FFF4F8, #FFF0F5); }
.artifact-visual-new .artifact-visual-icon { color: #D05088; background: #FFDDEB; }
.artifact-visual-new .artifact-visual-sheet { border-color: #F4D4E2; background: rgba(255, 255, 255, 0.73); }
.artifact-visual-new .artifact-visual-sheet span { display: none; }
.artifact-visual-new .artifact-visual-sheet::after {
    content: "+";
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    color: #B85AA0;
    font-size: 3.2rem;
    font-weight: 300;
}

.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] {
    min-height: 82px !important;
    padding: 12px 20px 18px !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button {
    width: 100% !important;
    max-width: none !important;
    min-height: 82px !important;
    height: auto !important;
    aspect-ratio: auto !important;
    margin: 0 !important;
    padding: 10px 0 16px !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #302244 !important;
    text-align: left !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button:hover {
    background: transparent !important;
    transform: none !important;
    box-shadow: none !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button p {
    margin: 0 !important;
    text-align: left !important;
    line-height: 1.35 !important;
    white-space: normal !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button p strong {
    display: block;
    margin-bottom: 6px;
    color: #302244 !important;
    font-size: 0.98rem !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button .stMarkdownColoredText {
    display: block;
    max-width: 220px;
    color: #887D8B !important;
    font-size: 0.78rem !important;
}
.stApp:has(.artifact-page-shell)
[class*="st-key-artifact_card_"] [class*="st-key-cat_"] button p:last-child {
    color: #47345B !important;
    font-size: 1.35rem !important;
    line-height: 1 !important;
}

.artifact-no-results {
    margin: 28px 0;
    padding: 26px;
    border: 1px dashed #D7C9B8;
    border-radius: 15px;
    color: #766B7B;
    background: rgba(255, 255, 255, 0.45);
}
.artifact-saved-heading {
    margin: 32px 0 10px;
    color: #332642;
    font-size: 1.05rem;
    font-weight: 650;
}

/* ============================================================
   ARTEFAK — WORKSPACE / CHAT HASIL KARTU
   ============================================================ */
.stApp:has(.artifact-workspace-shell) {
    background: #F5EBDD !important;
}

.stApp:has(.artifact-workspace-shell)
[data-testid="stMain"],
.stApp:has(.artifact-workspace-shell)
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

.stApp:has(.artifact-workspace-shell)
[data-testid="stMainBlockContainer"] {
    width: min(100% - 136px, 980px) !important;
    max-width: none !important;
    margin: 0 auto !important;
    padding: 28px 0 150px !important;
    box-sizing: border-box !important;
}

.stApp:has(.artifact-workspace-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    gap: 0 !important;
}

.artifact-workspace-shell {
    display: none !important;
}

/* Naikkan dok input khusus workspace Artefak. Nilai negatif masih
   mempertahankan jarak dari bawah, tetapi lebih tinggi daripada posisi
   bawaan halaman artefak lama. */
.stApp:has(.artifact-workspace-shell) {
    --chat-lift: 90px !important;
    --chat-shift: 0px !important;
}

.stApp:has(.artifact-workspace-shell)
[data-testid="stBottomBlockContainer"] {
    margin-bottom: var(--chat-lift) !important;
    transform: translateX(var(--chat-shift)) !important;
}

.stApp:has(.artifact-workspace-shell)
[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    column-gap: 18px !important;
}

.stApp:has(.artifact-workspace-shell)
[class*="st-key-artifact_workspace_back"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
}
.stApp:has(.artifact-workspace-shell)
[class*="st-key-artifact_workspace_back"] button {
    width: 42px !important;
    min-width: 42px !important;
    height: 42px !important;
    min-height: 42px !important;
    padding: 0 !important;
    border: 1px solid #D9C9B5 !important;
    border-radius: 13px !important;
    background: #E7D8C3 !important;
    color: #4A3559 !important;
    box-shadow: 0 5px 14px rgba(86, 64, 42, 0.08) !important;
}
.stApp:has(.artifact-workspace-shell)
[class*="st-key-artifact_workspace_back"] button:hover {
    background: #DCCAB1 !important;
    transform: translateY(-1px) !important;
}

.artifact-workspace-heading {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}
.artifact-workspace-icon,
.artifact-workspace-banner-icon {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 52px;
    height: 52px;
    border-radius: 16px;
    color: #4A3559;
    background: #F0ECF5;
    border: 1px solid #DFD4E8;
}
.artifact-workspace-icon .mi { font-size: 26px; }
.artifact-workspace-heading h1 {
    margin: 0;
    color: #302244;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: clamp(1.55rem, 3vw, 2.1rem);
    line-height: 1.1;
    letter-spacing: -0.04em;
    overflow-wrap: anywhere;
}
.artifact-workspace-heading p {
    margin: 6px 0 0;
    color: #766A7B;
    font-size: 0.9rem;
    line-height: 1.4;
}
.artifact-workspace-status {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 9px 12px;
    border: 1px solid #DCCEBE;
    border-radius: 999px;
    background: rgba(255, 251, 244, 0.68);
    color: #5C765D;
    font-size: 0.78rem;
    white-space: nowrap;
}
.artifact-workspace-status .mi { font-size: 16px; }

.artifact-workspace-banner {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 28px 0 26px;
    padding: 18px 22px;
    border: 1px solid #E1D4C3;
    border-radius: 17px;
    background: rgba(255, 250, 241, 0.62);
    box-shadow: 0 9px 22px rgba(89, 65, 43, 0.045);
}
.artifact-workspace-banner-icon {
    width: 42px;
    height: 42px;
    border-radius: 13px;
}
.artifact-workspace-banner-icon .mi { font-size: 22px; }
.artifact-workspace-banner strong {
    display: block;
    margin-bottom: 4px;
    color: #3B2B4A;
    font-size: 0.96rem;
}
.artifact-workspace-banner p {
    margin: 0;
    color: #786D7D;
    font-size: 0.84rem;
    line-height: 1.5;
}

/* Pesan pengguna menjadi kartu brief yang lebih lapang. */
.stApp:has(.artifact-workspace-shell) .bubble-row {
    width: 100% !important;
    margin: 14px 0 22px !important;
}
.stApp:has(.artifact-workspace-shell) .bubble-row.user {
    justify-content: flex-end !important;
}
.stApp:has(.artifact-workspace-shell) .bubble-row.user .bubble-wrap {
    width: min(82%, 780px) !important;
    max-width: 780px !important;
}
.stApp:has(.artifact-workspace-shell) .bubble.user {
    max-width: none !important;
    padding: 20px 24px !important;
    border: 1px solid #D7C5AD !important;
    border-radius: 18px !important;
    background: #E6D7C1 !important;
    color: #3A2B48 !important;
    font-size: 1.02rem !important;
    line-height: 1.75 !important;
    box-shadow: 0 7px 18px rgba(89, 65, 43, 0.06) !important;
}

/* Jawaban Yuki tampil di permukaan putih terpisah, bukan menempel di latar. */
.stApp:has(.artifact-workspace-shell) .bubble-row.ai {
    margin: 18px 0 28px !important;
}
.stApp:has(.artifact-workspace-shell) .bubble-row.ai .bubble-wrap {
    width: 100% !important;
    max-width: 100% !important;
}
.stApp:has(.artifact-workspace-shell) .bubble.ai {
    padding: 22px 24px !important;
    border: 1px solid #E5DCD0 !important;
    border-radius: 18px !important;
    background: rgba(255, 253, 249, 0.72) !important;
    color: #3B2D4A !important;
    box-shadow: 0 7px 20px rgba(89, 65, 43, 0.045) !important;
}

/* Loader / status generasi tetap memiliki ruang dan gaya workspace. */
.stApp:has(.artifact-workspace-shell)
[data-testid="stStatusWidget"],
.stApp:has(.artifact-workspace-shell)
[class*="st-key-loader"],
.stApp:has(.artifact-workspace-shell)
[class*="st-key-loading"] {
    color: #756A7A !important;
}
.stApp:has(.artifact-workspace-shell) .msg-action-time {
    color: #8E8290 !important;
}

@media (max-width: 900px) {
    .stApp:has(.artifact-workspace-shell)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 32px) !important;
        padding-top: 22px !important;
    }
    .artifact-workspace-status { display: none; }
    .artifact-workspace-heading h1 { font-size: 1.45rem; }
    .stApp:has(.artifact-workspace-shell) .bubble-row.user .bubble-wrap {
        width: 100% !important;
    }
}

@media (max-width: 640px) {
    .artifact-workspace-banner { align-items: flex-start; padding: 16px; }
    .artifact-workspace-banner p { font-size: 0.8rem; }
    .stApp:has(.artifact-workspace-shell) .bubble.user,
    .stApp:has(.artifact-workspace-shell) .bubble.ai {
        padding: 17px !important;
        font-size: 0.94rem !important;
    }
}

@media (max-width: 900px) {
    .stApp:has(.artifact-page-shell)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 32px) !important;
        padding-top: 22px !important;
    }
    .artifact-topbar { align-items: flex-start; }
    .artifact-brand { display: none; }
    .artifact-hero { padding: 26px; }
    .artifact-hero-copy { width: 100%; }
    .artifact-hero-art { opacity: 0.28; left: 35%; }
}

@media (max-width: 640px) {
    .artifact-topbar { margin-bottom: 20px; }
    .artifact-heading-icon { width: 44px; height: 44px; }
    .artifact-heading p { font-size: 0.8rem; }
    .artifact-hero { min-height: 270px; }
    .artifact-hero h2 { font-size: 1.7rem; }
    .artifact-hero-art { left: 15%; top: 105px; opacity: 0.23; }
}

/* ============================================================
   AI DESAIN — LANDING PAGE
   ============================================================ */
.stApp:has(.design-page-shell) {
    background: #F5EBDD !important;
}
.stApp:has(.design-page-shell)
[data-testid="stMain"],
.stApp:has(.design-page-shell)
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}
.stApp:has(.design-page-shell)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 220px) !important;
    max-width: none !important;
    margin: 0 auto !important;
    padding: 38px 0 150px !important;
    box-sizing: border-box !important;
}
.stApp:has(.design-page-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    gap: 0 !important;
}
.design-page-shell { display: none !important; }

.design-topbar {
    display: flex;
    align-items: center;
    min-height: 82px;
    padding-bottom: 18px;
    border-bottom: 1px solid #E6DED2;
}
.design-heading {
    display: flex;
    align-items: center;
    gap: 18px;
}
.design-heading-icon {
    display: grid;
    place-items: center;
    width: 58px;
    height: 58px;
    flex: 0 0 58px;
    border: 1px solid #E1D8E8;
    border-radius: 15px;
    background: linear-gradient(145deg, #F5EEF8, #EDE6F3);
    color: #4D3A69;
    box-shadow: 0 6px 16px rgba(83, 64, 112, 0.08);
}
.design-heading-icon .mi { font-size: 29px; }
.design-heading h1 {
    margin: 0;
    color: #302243;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: clamp(1.65rem, 3vw, 2.2rem);
    line-height: 1.05;
    letter-spacing: -0.045em;
}
.design-heading p {
    max-width: 590px;
    margin: 6px 0 0;
    color: #7A7080;
    font-size: 0.86rem;
    line-height: 1.4;
}

.design-section-title {
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
.design-section-title i {
    height: 1px;
    flex: 1 1 auto;
    background: #E3DBD1;
}
.design-section-icon { color: #4D3A69; font-size: 19px; }
.design-section-icon .mi { font-size: 20px; }

.stApp:has(.design-page-shell)
[class*="st-key-desain_quick"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] {
    min-width: 0 !important;
    min-height: 108px !important;
    overflow: hidden !important;
    border: 1px solid #E6DDD2 !important;
    border-radius: 13px !important;
    background: rgba(255, 253, 249, 0.68) !important;
    box-shadow: 0 5px 14px rgba(88, 67, 47, 0.04) !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    min-height: 108px !important;
}
.design-quick-visual {
    position: relative;
    height: 78px;
    overflow: hidden;
    background: linear-gradient(135deg, #FBF5ED, #F4EAF0);
}
.design-quick-visual::after {
    content: "";
    position: absolute;
    right: 30px;
    bottom: -56px;
    width: 190px;
    height: 115px;
    border-radius: 50%;
    background: rgba(255,255,255,.57);
    transform: rotate(-10deg);
}
.design-quick-icon {
    position: absolute;
    left: 17px;
    top: 16px;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    color: #4E3B6C;
    background: #F0E8F4;
    font-size: 1.25rem;
    font-weight: 500;
}
.design-quick-icon .mi { font-size: 21px; }
.design-quick-art {
    position: absolute;
    right: 38px;
    top: 18px;
    width: 76px;
    height: 48px;
    border: 1px solid rgba(221, 212, 230, .9);
    border-radius: 12px;
    background: rgba(255,255,255,.68);
    box-shadow: 7px 8px 15px rgba(98, 75, 119, .10);
    transform: rotate(-5deg);
}
.design-quick-art::before,
.design-quick-art::after {
    content: "";
    position: absolute;
    left: 14px;
    right: 14px;
    height: 6px;
    border-radius: 99px;
    background: #D8CBE5;
}
.design-quick-art::before { top: 17px; }
.design-quick-art::after { top: 33px; width: 52%; }
.design-visual-palette .design-quick-art {
    background: linear-gradient(90deg, #E9D9BF 0 25%, #9783C6 25% 50%, #C7A9E3 50% 75%, #F0BFD1 75%);
    border: none;
    height: 25px;
    top: 46px;
    transform: rotate(-3deg);
}
.design-visual-palette .design-quick-art::before,
.design-visual-palette .design-quick-art::after { display: none; }
.design-visual-font .design-quick-icon {
    font-family: Georgia, serif;
    font-size: 1.8rem;
}
.design-visual-font .design-quick-art {
    border: none;
    background: transparent;
    box-shadow: none;
    font: 3rem Georgia, serif;
    color: #5A466E;
}
.design-visual-font .design-quick-art::before {
    content: "Aa";
    top: 0;
    left: 0;
    right: auto;
    height: auto;
    background: none;
}
.design-visual-font .design-quick-art::after {
    content: "Aa";
    top: 25px;
    left: 52px;
    width: auto;
    height: auto;
    background: none;
    color: #C7B8CC;
    font-size: 1.65rem;
}
.design-visual-critique { background: linear-gradient(135deg, #F9F1EF, #F1EAF5); }
.design-visual-critique .design-quick-icon { color: #77518C; }
.design-visual-critique .design-quick-art {
    width: 28px; height: 28px; right: 80px; top: 38px;
    border-radius: 50%; border: 0; background: #BCA0D7;
    box-shadow: 42px 25px 0 -7px #E7D0EC, 76px -11px 0 -11px #A98AC5;
}
.design-visual-critique .design-quick-art::before,
.design-visual-critique .design-quick-art::after { display: none; }
.design-visual-moodboard { background: linear-gradient(135deg, #F4F2F7, #EAF0F7); }
.design-visual-moodboard .design-quick-icon { color: #5B7092; background: #E5ECF6; }
.design-visual-moodboard .design-quick-art {
    width: 48px; height: 48px; right: 80px; top: 25px;
    background: #FFF; transform: rotate(7deg);
}
.design-visual-moodboard .design-quick-art::before {
    content: ""; left: 52px; top: 13px; width: 42px; height: 42px;
    background: #D5E2F1; transform: rotate(-13deg);
}
.design-visual-moodboard .design-quick-art::after {
    content: ""; left: 72px; top: 25px; width: 30px; height: 30px;
    background: #C5B5D8; transform: rotate(5deg);
}

.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] {
    min-height: 70px !important;
    padding: 0 16px !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button {
    width: 100% !important;
    min-height: 70px !important;
    height: auto !important;
    aspect-ratio: auto !important;
    margin: 0 !important;
    padding: 9px 0 12px !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    color: #332543 !important;
    text-align: left !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button:hover {
    background: transparent !important;
    transform: none !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button p {
    margin: 0 !important;
    text-align: left !important;
    white-space: normal !important;
    line-height: 1.35 !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button p strong {
    display: block;
    margin-bottom: 4px;
    color: #332543 !important;
    font-size: 0.88rem !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button .stMarkdownColoredText {
    display: block;
    max-width: 250px;
    color: #837887 !important;
    font-size: 0.7rem !important;
}
.stApp:has(.design-page-shell)
[class*="st-key-desain_quick_card_"] [class*="st-key-desain_q_"] button p:last-child {
    color: #47345B !important;
    font-size: 1.25rem !important;
    line-height: 1 !important;
}

.design-prompt-card {
    position: relative;
    display: flex;
    align-items: center;
    min-height: 218px;
    overflow: hidden;
    margin: 28px 0 0;
    border: 1px solid #E5DBD0;
    border-radius: 16px;
    background: rgba(255, 253, 248, 0.7);
    box-shadow: 0 9px 22px rgba(88, 67, 47, 0.045);
}
.design-prompt-art {
    position: relative;
    width: 28%;
    min-width: 220px;
    align-self: stretch;
    overflow: hidden;
    background: linear-gradient(145deg, #F3EDF6, #F8F0EA);
}
.design-prompt-art::before {
    content: "";
    position: absolute;
    left: 28px;
    bottom: -34px;
    width: 190px;
    height: 210px;
    border: 1px solid #E8D9E9;
    background: rgba(255,255,255,.3);
    transform: rotate(-14deg);
}
.design-prompt-paper {
    position: absolute;
    z-index: 2;
    left: 86px;
    top: 38px;
    width: 88px;
    height: 116px;
    padding: 16px 12px;
    box-sizing: border-box;
    border: 1px solid #E6D9ED;
    border-radius: 10px;
    background: rgba(255,255,255,.7);
    color: #6B4E86;
    font: 2.1rem Georgia, serif;
    transform: rotate(-8deg);
    box-shadow: 7px 8px 15px rgba(94, 68, 113, .10);
}
.design-prompt-paper div,
.design-prompt-paper span {
    display: block;
    width: 62px;
    height: 5px;
    margin-top: 13px;
    border-radius: 99px;
    background: #CFC1D9;
}
.design-prompt-paper span { width: 42px; margin-top: 7px; background: #E3D8E8; }
.design-prompt-swatch {
    position: absolute;
    z-index: 3;
    right: 22px;
    width: 17px;
    height: 17px;
    border-radius: 5px;
}
.swatch-a { top: 62px; background: #A287C1; }
.swatch-b { top: 86px; background: #C9B6DB; }
.swatch-c { top: 110px; background: #E1D1E4; }
.design-prompt-spark {
    position: absolute;
    z-index: 4;
    right: 30px;
    bottom: 52px;
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    color: #FFF;
    background: linear-gradient(145deg, #8563B4, #4F3978);
    box-shadow: 0 8px 16px rgba(86, 56, 130, .22);
}
.design-prompt-spark .mi { font-size: 23px; }
.design-prompt-copy {
    flex: 1 1 auto;
    padding: 28px 42px;
}
.design-prompt-copy h2 {
    margin: 0 0 10px;
    color: #38294A;
    font-size: 1.22rem;
    letter-spacing: -0.025em;
}
.design-prompt-copy h2 .mi { margin-right: 10px; color: #65468A; font-size: 21px; }
.design-prompt-copy p {
    max-width: 720px;
    margin: 0;
    color: #807483;
    font-size: 0.88rem;
    line-height: 1.55;
}

.stApp:has(.design-page-shell)
[data-testid="stBottomBlockContainer"] {
    --chat-lift: 32px !important;
    margin-bottom: var(--chat-lift) !important;
    max-width: min(52rem, calc(100vw - 250px)) !important;
}
.stApp:has(.design-page-shell) .dock-spacer { height: 70px !important; }

@media (max-width: 900px) {
    .stApp:has(.design-page-shell)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 32px) !important;
        padding-top: 22px !important;
    }
    .design-heading { gap: 17px; }
    .design-heading-icon { width: 58px; height: 58px; flex-basis: 58px; }
    .design-heading-icon .mi { font-size: 30px; }
    .design-heading p { font-size: 0.86rem; }
    .design-prompt-art { min-width: 150px; }
    .design-prompt-paper { left: 42px; }
}

@media (max-width: 640px) {
    .design-topbar { min-height: 92px; padding-bottom: 20px; }
    .design-heading h1 { font-size: 1.85rem; }
    .design-heading p { font-size: 0.78rem; }
    .design-section-title { margin-top: 22px; }
    .design-prompt-card { display: block; }
    .design-prompt-art { width: 100%; height: 160px; min-width: 0; }
    .design-prompt-paper { left: 34%; top: 22px; }
    .design-prompt-copy { padding: 22px; }
}

/* ============================================================
   AI PENJADWAL — LANDING PAGE
   ============================================================ */
.stApp:has(.scheduler-page-shell) {
    background: #F5EBDD !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stMain"],
.stApp:has(.scheduler-page-shell)
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stMainBlockContainer"] {
    width: calc(100% - 164px) !important;
    max-width: none !important;
    margin: 0 auto !important;
    padding: 30px 0 150px !important;
    box-sizing: border-box !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    gap: 0 !important;
}
.scheduler-page-shell { display: none !important; }

.scheduler-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 82px;
    padding-bottom: 22px;
    border-bottom: 1px solid #E2D8CC;
}
.scheduler-heading {
    display: flex;
    align-items: center;
    gap: 20px;
}
.scheduler-heading-icon {
    display: grid;
    place-items: center;
    width: 64px;
    height: 64px;
    flex: 0 0 64px;
    border: 1px solid #E0D6E7;
    border-radius: 16px;
    background: #F4EDF7;
    color: #4D3A69;
    box-shadow: 0 7px 18px rgba(83, 64, 112, 0.07);
}
.scheduler-heading-icon .mi { font-size: 32px; }
.scheduler-heading h1 {
    margin: 0;
    color: #302243;
    font-size: clamp(1.9rem, 3.4vw, 2.6rem);
    line-height: 1.05;
    letter-spacing: -0.05em;
}
.scheduler-heading p {
    margin: 7px 0 0;
    color: #7A7080;
    font-size: 0.9rem;
}
.scheduler-brand {
    display: flex;
    align-items: center;
    gap: 13px;
    color: #8A7F8A;
    font-size: 0.78rem;
}
.scheduler-brand > span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 12px;
    border: 1px solid #E5DCD2;
    border-radius: 999px;
    background: rgba(255, 253, 248, .62);
    color: #5A4C66;
    font-weight: 650;
}
.scheduler-brand > span .mi { font-size: 15px; }
.scheduler-brand i { width: 1px; height: 18px; background: #DED4C9; }

.scheduler-hero {
    position: relative;
    min-height: 150px;
    display: flex;
    align-items: center;
    overflow: hidden;
    margin: 26px 0 22px;
    padding: 24px 36px;
    border: 1px solid #E6DCD1;
    border-radius: 17px;
    background:
        radial-gradient(circle at 82% 52%, rgba(255,255,255,.92), transparent 30%),
        linear-gradient(110deg, #F8F1E9, #F9F3EF 62%, #F2EAF3);
    box-shadow: 0 9px 22px rgba(88, 67, 47, .04);
}
.scheduler-hero-copy {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 20px;
    max-width: 610px;
}
.scheduler-hero-icon {
    display: grid;
    place-items: center;
    width: 50px;
    height: 50px;
    flex: 0 0 50px;
    border-radius: 50%;
    color: #4D3A69;
    background: #F1E8F4;
}
.scheduler-hero-icon .mi { font-size: 25px; }
.scheduler-hero h2 {
    margin: 0 0 7px;
    color: #35264A;
    font-size: 1.18rem;
}
.scheduler-hero p {
    max-width: 560px;
    margin: 0;
    color: #7B7080;
    font-size: .82rem;
    line-height: 1.55;
}
.scheduler-hero-art {
    position: absolute;
    inset: 0 4% 0 62%;
}
.scheduler-calendar {
    position: absolute;
    right: 16%;
    top: 24px;
    display: grid;
    grid-template-columns: repeat(3, 19px);
    gap: 7px;
    width: 118px;
    height: 90px;
    padding: 29px 12px 10px;
    border-radius: 12px;
    background: linear-gradient(145deg, #8B72C7, #614596);
    box-shadow: 8px 13px 20px rgba(79, 57, 126, .20);
    transform: rotate(4deg);
}
.scheduler-calendar::before {
    content: "";
    position: absolute;
    left: 0; right: 0; top: 18px;
    height: 1px;
    background: rgba(255,255,255,.48);
}
.scheduler-calendar::after {
    content: "";
    position: absolute;
    left: 17px; right: 17px; top: -9px;
    height: 16px;
    border-top: 5px solid #EDE5F4;
    border-radius: 50%;
}
.scheduler-calendar b {
    width: 18px; height: 14px;
    border-radius: 4px;
    background: rgba(255,255,255,.66);
}
.scheduler-calendar span { display: none; }
.scheduler-clock {
    position: absolute;
    right: 8%;
    bottom: 22px;
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    color: #5B467A;
    background: #F7F1F8;
    border: 5px solid #E3D5E8;
    box-shadow: 0 7px 14px rgba(84, 61, 118, .14);
}
.scheduler-clock .mi { font-size: 24px; }
.scheduler-check {
    position: absolute;
    right: 0;
    top: 66px;
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 9px;
    color: #FFF;
    background: #9B83CE;
}
.scheduler-check .mi { font-size: 19px; }

.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] {
    margin: 0 !important;
    padding: 24px 30px 22px !important;
    border: 1px solid #E5DCD1 !important;
    border-radius: 17px !important;
    background: rgba(255, 253, 249, .68) !important;
    box-shadow: 0 8px 20px rgba(88, 67, 47, .04) !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] > [data-testid="stVerticalBlock"] {
    gap: 0.45rem !important;
}
.scheduler-builder-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 13px;
}
.scheduler-builder-icon {
    display: grid;
    place-items: center;
    width: 37px;
    height: 37px;
    border-radius: 11px;
    color: #4D3A69;
    background: #F0E9F4;
}
.scheduler-builder-icon .mi { font-size: 21px; }
.scheduler-builder-heading h2 {
    margin: 0 0 3px;
    color: #35264A;
    font-size: 1.03rem;
}
.scheduler-builder-heading p {
    margin: 0;
    color: #837887;
    font-size: .75rem;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] [data-testid="stWidgetLabel"] p {
    color: #4E415B !important;
    font-size: .76rem !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] input,
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] textarea,
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] [data-baseweb="select"] > div {
    min-height: 39px !important;
    border: 1px solid #E2D8D0 !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,.56) !important;
    color: #3B2D4A !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] input,
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] textarea {
    padding: 8px 11px !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] textarea { min-height: 76px !important; }
.scheduler-style-label {
    margin: 13px 0 4px;
    color: #4E415B;
    font-size: .76rem;
    font-weight: 600;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] [data-testid="stRadio"] {
    margin: 0 !important;
    padding: 8px 10px !important;
    border: 1px solid #E5DCD2 !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,.38) !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] [data-testid="stRadio"] label p {
    color: #62546C !important;
    font-size: .76rem !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_builder"] [class*="st-key-jd_make_schedule"] button {
    min-height: 42px !important;
    border-radius: 10px !important;
    background: #4C3567 !important;
    color: #FFF !important;
    border-color: #4C3567 !important;
    font-size: .8rem !important;
}
.scheduler-quick-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 25px 0 10px;
    color: #665A6E;
    font-size: .76rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.scheduler-quick-label .mi { color: #4D3A69; font-size: 19px; }
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] {
    min-height: 96px !important;
    overflow: hidden !important;
    border: 1px solid #E5DCD2 !important;
    border-radius: 13px !important;
    background: rgba(255,253,249,.68) !important;
    box-shadow: 0 5px 14px rgba(88,67,47,.035) !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    min-height: 96px !important;
}
.scheduler-quick-visual {
    position: relative;
    height: 52px;
    overflow: hidden;
    background: #F2ECF6;
}
.scheduler-quick-icon {
    position: absolute;
    left: 14px;
    top: 10px;
    z-index: 1;
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    color: #4D3A69;
    background: #EEE5F3;
}
.scheduler-quick-icon .mi { font-size: 18px; }
.scheduler-quick-art {
    position: absolute;
    right: 20px;
    top: 17px;
    width: 54px;
    height: 22px;
    border: 1px solid #D9C9E4;
    border-radius: 6px;
    background: rgba(255,255,255,.65);
    transform: rotate(-4deg);
}
.scheduler-visual-meeting { background: #F1F4F8; }
.scheduler-visual-daily { background: #F2F7F1; }
.scheduler-visual-weekly { background: #F7F1E7; }
.scheduler-visual-meeting .scheduler-quick-icon { background: #E6EDF5; }
.scheduler-visual-daily .scheduler-quick-icon { background: #E2F0E5; }
.scheduler-visual-weekly .scheduler-quick-icon { background: #F3E8D4; }
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] [class*="st-key-jadwal_q_"] button {
    width: 100% !important;
    min-height: 58px !important;
    padding: 7px 14px 10px !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    text-align: left !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] [class*="st-key-jadwal_q_"] button p {
    margin: 0 !important;
    text-align: left !important;
    line-height: 1.25 !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] [class*="st-key-jadwal_q_"] button p strong {
    display: block;
    margin-bottom: 3px;
    color: #35264A !important;
    font-size: .78rem !important;
}
.stApp:has(.scheduler-page-shell)
[class*="st-key-jadwal_quick_card_"] [class*="st-key-jadwal_q_"] button .stMarkdownColoredText {
    color: #837887 !important;
    font-size: .67rem !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stBottomBlockContainer"] {
    --chat-lift: 32px !important;
    margin-bottom: var(--chat-lift) !important;
    max-width: min(52rem, calc(100vw - 250px)) !important;
}
.stApp:has(.scheduler-page-shell) .dock-spacer { height: 70px !important; }

@media (max-width: 900px) {
    .stApp:has(.scheduler-page-shell)
    [data-testid="stMainBlockContainer"] {
        width: calc(100% - 32px) !important;
        padding-top: 22px !important;
    }
    .scheduler-brand { display: none; }
    .scheduler-heading { gap: 14px; }
    .scheduler-heading-icon { width: 52px; height: 52px; flex-basis: 52px; }
    .scheduler-hero { padding: 20px; }
    .scheduler-hero-art { opacity: .23; left: 45%; }
    .scheduler-builder { padding: 18px !important; }
}

@media (max-width: 640px) {
    .scheduler-heading h1 { font-size: 1.75rem; }
    .scheduler-heading p { font-size: .78rem; }
    .scheduler-hero-copy { gap: 12px; }
    .scheduler-hero-icon { width: 39px; height: 39px; flex-basis: 39px; }
    .scheduler-hero h2 { font-size: 1rem; }
    .scheduler-hero p { font-size: .74rem; }
}

/* Form tugas manual pada AI Penjadwal */
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] {
    overflow: hidden !important;
    margin: 22px 0 10px !important;
    border: 1px solid #DED3C5 !important;
    border-radius: 16px !important;
    background: rgba(255, 253, 248, .72) !important;
    box-shadow: 0 8px 20px rgba(78, 58, 40, .045) !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] details > summary {
    min-height: 54px !important;
    padding: 0 20px !important;
    border-bottom: 1px solid transparent !important;
    background: linear-gradient(90deg, rgba(247, 240, 230, .95), rgba(255, 253, 248, .64)) !important;
    color: #3E2E4D !important;
    transition: background .16s ease, border-color .16s ease !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] details[open] > summary {
    border-bottom-color: #E5DCD1 !important;
    background: #F7F0E6 !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] details > summary:hover {
    background: #F4ECE1 !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] details > summary p {
    margin: 0 !important;
    color: #443251 !important;
    font-size: .93rem !important;
    font-weight: 600 !important;
    letter-spacing: -.01em !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpander"] details > summary svg {
    color: #665375 !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] {
    padding: 20px 24px 22px !important;
    background: rgba(255, 253, 248, .52) !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] > [data-testid="stVerticalBlock"] {
    gap: .55rem !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [data-testid="stWidgetLabel"] p {
    margin-bottom: 4px !important;
    color: #554360 !important;
    font-size: .74rem !important;
    font-weight: 650 !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] input,
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [data-baseweb="select"] > div {
    min-height: 40px !important;
    border: 1px solid #E1D6C8 !important;
    border-radius: 11px !important;
    background: #FFFDF9 !important;
    color: #3E2E4D !important;
    box-shadow: none !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] input {
    padding: 8px 12px !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] input:focus {
    border-color: #8E72A4 !important;
    box-shadow: 0 0 0 3px rgba(142, 114, 164, .12) !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"] {
    gap: 14px !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [class*="st-key-jd_add"] {
    display: flex !important;
    justify-content: flex-end !important;
    margin-top: 4px !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [class*="st-key-jd_add"] button {
    width: min(100%, 184px) !important;
    min-height: 40px !important;
    margin-left: auto !important;
    border: 1px solid #4C3567 !important;
    border-radius: 10px !important;
    background: #4C3567 !important;
    color: #FFF !important;
    font-size: .8rem !important;
    font-weight: 650 !important;
    box-shadow: 0 5px 12px rgba(76, 53, 103, .12) !important;
}
.stApp:has(.scheduler-page-shell)
[data-testid="stExpanderDetails"] [class*="st-key-jd_add"] button:hover {
    background: #5A4176 !important;
    border-color: #5A4176 !important;
    transform: translateY(-1px) !important;
}

@media (max-width: 640px) {
    .stApp:has(.scheduler-page-shell)
    [data-testid="stExpanderDetails"] {
        padding: 17px 15px 19px !important;
    }
    .stApp:has(.scheduler-page-shell)
    [data-testid="stExpanderDetails"] [class*="st-key-jd_add"] button {
        width: 100% !important;
    }
}
"""
