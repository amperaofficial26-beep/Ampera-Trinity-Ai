# -*- coding: utf-8 -*-
"""Kartu kaya (perbandingan, langkah, link) serta tampilan daftar & isi file

Dipecah dari styles.py asli (baris 2448-3223), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ====================================================================
   KARTU KAYA (rich cards): perbandingan, langkah, link
   Meniru gaya kartu Claude: putih, sudut lembut, garis pemisah tipis,
   bayangan sangat halus, tipografi bertingkat.
==================================================================== */
.rc-card {
    background: #FFFFFF;
    border: 1px solid #E4D9C6;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(44, 31, 51, 0.05);
    margin: 10px 0 14px;
    max-width: 640px;
    overflow: hidden;
    animation: rcIn 0.3s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes rcIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- 1. KARTU PERBANDINGAN ---------- */
.rc-cmp-row {
    display: grid;
    grid-template-columns: repeat(var(--rc-cols, 2), 1fr);
    border-top: 1px solid #EFE6D6;
}
.rc-cmp-row.rc-cmp-toprow { border-top: none; }
.rc-cmp-head {
    padding: 16px 18px 6px;
    font-size: 1.02rem;
    font-weight: 650;
    color: #2C1F33;
    letter-spacing: -0.01em;
}
.rc-cmp-cell { padding: 12px 18px 14px; }
.rc-cmp-label {
    font-size: 0.76rem;
    color: #8E8398;
    margin-bottom: 3px;
    letter-spacing: 0.01em;
}
.rc-cmp-value {
    font-size: 0.92rem;
    color: #2C1F33;
    font-weight: 500;
    line-height: 1.4;
}
/* garis pemisah vertikal antar kolom */
.rc-cmp-row > *:not(:first-child) { border-left: 1px solid #F3ECE0; }

/* ---------- 2. KARTU LANGKAH ---------- */
.rc-step { padding: 18px 20px 16px; }
.rc-step-title {
    font-size: 1.18rem;
    font-weight: 600;
    color: #2C1F33;
    letter-spacing: -0.015em;
    margin-bottom: 6px;
}
.rc-step-desc {
    font-size: 0.9rem;
    color: #6B6172;
    line-height: 1.55;
    margin-bottom: 14px;
}
.rc-step-dots { display: flex; align-items: center; gap: 7px; }
.rc-dot {
    width: 26px; height: 26px;
    display: inline-flex; align-items: center; justify-content: center;
    border-radius: 50%;
    background: #F1EADD;
    color: #8E8398;
    font-size: 0.76rem;
    font-weight: 600;
    transition: background .2s ease, color .2s ease, transform .2s ease;
}
.rc-dot.on {
    background: #2C1F33;
    color: #FBF6EC;
    transform: scale(1.06);
}
.rc-step-count {
    margin-left: 6px;
    font-size: 0.78rem;
    color: #8E8398;
}
/* tombol navigasi langkah */
[class*="st-key-rc_nav_"] { max-width: 640px; margin: -6px 0 16px !important; }
[class*="st-key-rc_nav_"] div.stButton > button {
    border-radius: 10px !important;
    border: 1px solid #DBCEB9 !important;
    background: #FFFFFF !important;
    color: #2C1F33 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    min-height: 40px !important;
    transition: background .15s ease, transform .1s ease !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:hover:not(:disabled) {
    background: #FAF3E8 !important;
    border-color: #2C1F33 !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:active:not(:disabled) {
    transform: scale(0.985) !important;
}
[class*="st-key-rc_nav_"] div.stButton > button[kind="primary"] {
    background: #2C1F33 !important;
    border-color: #2C1F33 !important;
    color: #FBF6EC !important;
}
[class*="st-key-rc_nav_"] div.stButton > button:disabled {
    opacity: 0.45 !important;
    cursor: not-allowed !important;
}

/* ---------- 3. KARTU LINK ---------- */
.rc-link { padding: 14px 18px 13px; }
.rc-link-title {
    display: inline-block;
    font-size: 0.98rem;
    font-weight: 600;
    color: #2C1F33 !important;
    text-decoration: underline;
    text-underline-offset: 3px;
    text-decoration-thickness: 1px;
    margin-bottom: 5px;
}
.rc-link-title:hover { color: #4A3559 !important; }
.rc-link-desc {
    font-size: 0.87rem;
    color: #6B6172;
    line-height: 1.5;
    margin-bottom: 7px;
}
.rc-link-src {
    font-size: 0.78rem;
    color: #A095AC;
    letter-spacing: 0.01em;
}
/* ---------- 4. KARTU PETA ---------- */
[class*="st-key-rc_map_"] { max-width: 660px; margin-bottom: 14px; }
[class*="st-key-rc_map_"] iframe {
    border: 1px solid #E4D9C6 !important;
    border-radius: 12px !important;
    width: 100% !important;
    background: #F6F1E7;
}
[class*="st-key-rc_map_"] [data-testid="stHorizontalBlock"] { gap: 10px !important; }
.rc-map-side { padding: 14px 16px; height: 100%; }
.rc-map-title {
    font-size: 0.96rem; font-weight: 600; color: #2C1F33;
    line-height: 1.35; margin-bottom: 5px;
}
.rc-map-desc {
    font-size: 0.83rem; color: #6B6172; line-height: 1.5; margin-bottom: 9px;
}
.rc-map-link {
    font-size: 0.82rem; font-weight: 600; color: #2C1F33 !important;
    text-decoration: underline; text-underline-offset: 3px;
}
.rc-map-fallback { padding: 18px; text-align: center; }

/* ---------- 5. KARTU ITINERARY ---------- */
[class*="st-key-rc_itin_"] { max-width: 640px; margin-bottom: 14px; }
[class*="st-key-rc_itin_"] [data-testid="stHorizontalBlock"] {
    gap: 6px !important; margin-bottom: 4px !important;
}
[class*="st-key-rc_itin_"] div.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #E4D9C6 !important;
    background: #F6F1E7 !important;
    color: #8E8398 !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    min-height: 36px !important;
    transition: background .15s ease, color .15s ease !important;
}
[class*="st-key-rc_itin_"] div.stButton > button[kind="primary"] {
    background: #FFFFFF !important;
    border-color: #DBCEB9 !important;
    color: #2C1F33 !important;
    box-shadow: 0 1px 3px rgba(44,31,51,0.08) !important;
}
.rc-itin { padding: 16px 18px 8px; }
.rc-itin-day {
    font-size: 0.78rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 12px;
}
.rc-itin-row { display: grid; grid-template-columns: 58px 18px 1fr; }
.rc-itin-time {
    font-size: 0.82rem; color: #8E8398; text-align: right;
    padding-top: 2px; padding-right: 4px;
}
.rc-itin-mark { position: relative; display: flex; justify-content: center; }
.rc-itin-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #C9BCA6; margin-top: 7px; z-index: 1;
}
/* garis penghubung antar titik linimasa */
.rc-itin-row:not(:last-child) .rc-itin-mark::after {
    content: ""; position: absolute; top: 15px; bottom: -6px;
    width: 1px; background: #EAE0D0;
}
.rc-itin-body { padding: 0 0 16px 6px; }
.rc-itin-act {
    font-size: 0.98rem; font-weight: 600; color: #2C1F33;
    letter-spacing: -0.01em; line-height: 1.35;
}
.rc-itin-note {
    font-size: 0.85rem; color: #6B6172; line-height: 1.5; margin-top: 2px;
}

/* ---------- 6. KARTU TERJEMAHAN ---------- */
.rc-tr { display: grid; grid-template-columns: 1fr 1fr; }
.rc-tr-pane { padding: 13px 16px 15px; }
.rc-tr-pane:last-child { border-left: 1px solid #F3ECE0; }
.rc-tr-head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
}
.rc-tr-lang { font-size: 0.78rem; color: #8E8398; letter-spacing: 0.01em; }
.rc-tr-text {
    font-size: 0.96rem; color: #2C1F33; line-height: 1.5; font-weight: 500;
}
.rc-icon-btn {
    background: transparent; border: none; cursor: pointer;
    font-size: 0.86rem; line-height: 1; padding: 2px 4px;
    border-radius: 6px; color: #8E8398;
    transition: background .15s ease, transform .1s ease;
}
.rc-icon-btn:hover { background: rgba(44,31,51,0.06); }
.rc-icon-btn:active { transform: scale(0.9); 
}
/* ---------- 7. KARTU PALET WARNA ---------- */
.rc-pal { padding: 14px 16px 12px; }
.rc-pal-title {
    font-size: 0.9rem; font-weight: 600; color: #2C1F33; margin-bottom: 10px;
}
.rc-pal-row { display: flex; gap: 8px; flex-wrap: wrap; }
.rc-pal-item { flex: 1 1 84px; min-width: 84px; }
.rc-pal-chip {
    height: 62px;
    border-radius: 10px;
    border: 1px solid rgba(44, 31, 51, 0.10);
    display: flex; align-items: flex-end; justify-content: center;
    padding-bottom: 6px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.02em;
    transition: transform .15s ease, box-shadow .15s ease;
}
.rc-pal-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 14px rgba(44, 31, 51, 0.14);
}
.rc-pal-label {
    font-size: 0.74rem; color: #8E8398; margin-top: 5px;
    text-align: center; line-height: 1.3;
}
.rc-pal-foot {
    margin-top: 11px; padding-top: 9px;
    border-top: 1px solid #F3ECE0;
    font-size: 0.74rem; color: #A095AC;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
}

/* ---------- 8. HALAMAN AI DESAIN & AI PENJADWAL ---------- */
/* label bagian, dipakai di kedua halaman */
.sec-label {
    font-size: 0.74rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.07em; text-transform: uppercase;
    margin: 4px 0 8px;
}
.sec-divider {
    height: 1px; background: #E0D2BB;
    margin: 22px 0 18px; border: none;
}
/* ruang kosong agar isi terakhir tidak tertutup kotak input */
.dock-spacer { height: 96px; }

/* panel daftar tugas */
[class*="st-key-jd_panel"] {
    background: #F7F1E6;
    border: 1px solid #E4D9C6;
    border-radius: 14px;
    padding: 6px 14px 10px !important;
    margin-bottom: 10px;
}
[class*="st-key-jd_panel"] [data-testid="stVerticalBlock"] { gap: 0 !important; }

.jd-progress-wrap { margin: 2px 0 12px; }
.jd-progress-text { font-size: 0.8rem; color: #6B6172; margin-bottom: 6px; }
.jd-progress-bar {
    height: 6px; background: #E4D9C6; border-radius: 99px; overflow: hidden;
}
.jd-progress-fill {
    height: 100%; background: #2C1F33; border-radius: 99px;
    transition: width .4s cubic-bezier(.32,.72,0,1);
}
.jd-group {
    font-size: 0.72rem; font-weight: 700; color: #A095AC;
    letter-spacing: 0.05em; text-transform: uppercase;
    margin: 12px 0 2px; padding-top: 2px;
}
.jd-item {
    display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap;
    padding: 2px 0;
}
.jd-dot {
    width: 7px; height: 7px; border-radius: 50%;
    display: inline-block; flex: 0 0 auto; transform: translateY(-1px);
}
.jd-title { font-size: 0.93rem; color: #2C1F33; font-weight: 500; }
.jd-meta { font-size: 0.75rem; color: #A095AC; }
.jd-item.jd-done .jd-title { text-decoration: line-through; color: #B0A6BC; }
.jd-item.jd-done .jd-dot { opacity: 0.4; }

/* baris tugas: rapatkan jarak antar baris & rapikan tombolnya */
[class*="st-key-jd_row_"] { margin: 0 !important; }
[class*="st-key-jd_row_"] [data-testid="stHorizontalBlock"] {
    gap: 8px !important; align-items: center !important;
    min-height: 34px;
}
[class*="st-key-jd_row_"] div.stButton { margin: 0 !important; }
[class*="st-key-jd_row_"] div.stButton > button {
    background: transparent !important;
    border: 1px solid #DBCEB9 !important;
    color: #6B6172 !important;
    width: 24px !important; min-width: 24px !important; height: 24px !important;
    padding: 0 !important; border-radius: 7px !important;
    font-size: 0.75rem !important; line-height: 1 !important;
}
[class*="st-key-jd_row_"] div.stButton > button:hover {
    background: #E0D2BB !important; color: #2C1F33 !important;
}
[class*="st-key-jd_clear_wrap"] div.stButton > button {
    background: transparent !important;
    border: 1px dashed #CDBFA8 !important;
    color: #8E8398 !important;
    font-size: 0.8rem !important;
    min-height: 34px !important;
    margin-top: 8px !important;
}

/* tombol mulai cepat di kedua halaman AI khusus */
[class*="st-key-desain_quick"] div.stButton > button,
[class*="st-key-jadwal_quick"] div.stButton > button {
    background: #F2E8D6 !important;
    border: 1px solid #E0D2BB !important;
    border-radius: 11px !important;
    color: #2C1F33 !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    min-height: 46px !important;
    white-space: normal !important;
    line-height: 1.3 !important;
    transition: background .15s ease, border-color .15s ease,
                transform .1s ease !important;
}
[class*="st-key-desain_quick"] div.stButton > button:hover,
[class*="st-key-jadwal_quick"] div.stButton > button:hover {
    background: #FFFFFF !important;
    border-color: #2C1F33 !important;
    transform: translateY(-1px) !important;
}
[class*="st-key-desain_quick"] [data-testid="stHorizontalBlock"],
[class*="st-key-jadwal_quick"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}
[class*="st-key-desain_quick"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}

/* form "Tambah tugas sendiri" */
[data-testid="stMainBlockContainer"] [data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #E4D9C6 !important;
    margin-bottom: 8px !important;
}
/* ---------- 9. PANEL FILE / ARTEFAK (sidebar kanan) ---------- */
/* -- kartu ringkas di dalam chat -- */
.af-chip {
    display: flex; align-items: center; gap: 9px; flex-wrap: wrap;
    background: #F7F1E6; border: 1px solid #E0D2BB; border-radius: 11px;
    padding: 10px 13px; margin: 6px 0 4px; max-width: 460px;
    animation: iosPopIn .34s cubic-bezier(.32,.72,0,1) both;
}
.af-chip-ic {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; font-weight: 700; color: #FBF6EC;
    background: #2C1F33; border-radius: 7px; padding: 3px 7px; line-height: 1.2;
}
.af-chip-name {
    font-size: 0.92rem; font-weight: 600; color: #2C1F33;
    font-family: 'JetBrains Mono', monospace;
}
.af-chip-meta { font-size: 0.76rem; color: #A095AC; }
[class*="st-key-af_open_"] div.stButton > button {
    background: transparent !important; border: 1px solid #DBCEB9 !important;
    border-radius: 9px !important; color: #4A3559 !important;
    font-size: 0.8rem !important; font-weight: 600 !important;
    min-height: 30px !important; margin-top: 4px !important;
}
[class*="st-key-af_open_"] div.stButton > button:hover {
    background: #E0D2BB !important; border-color: #2C1F33 !important;
}

/* ================= TAMPILAN DAFTAR ================= */
.af-sec {
    font-size: 1.28rem; font-weight: 650; color: #2C1F33;
    letter-spacing: -0.02em; margin: 2px 0 12px;
    font-family: 'Source Serif 4', serif;
}
.af-sec-2 { margin-top: 22px; }

/* tombol "Unduh semua" */
[class*="st-key-af_dlall"] div.stDownloadButton > button {
    background: transparent !important; border: none !important;
    color: #2C1F33 !important; font-size: 0.9rem !important;
    font-weight: 600 !important; justify-content: flex-end !important;
    min-height: 30px !important; margin: -46px 0 10px !important;
}
[class*="st-key-af_dlall"] div.stDownloadButton > button:hover {
    color: #4A3559 !important; text-decoration: underline !important;
}

/* kartu file */
[class*="st-key-af_card_"] {
    background: #FFFFFF !important; border: 1px solid #EAE0D0 !important;
    border-radius: 14px !important; padding: 12px 14px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 1px 3px rgba(44,31,51,0.04) !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
[class*="st-key-af_card_"]:hover {
    border-color: #DBCEB9 !important;
    box-shadow: 0 4px 14px rgba(44,31,51,0.08) !important;
}
[class*="st-key-af_card_"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important; align-items: center !important;
}
.af-file-ic {
    width: 46px; height: 54px; border-radius: 8px;
    background: linear-gradient(150deg, #F6E7CE 0%, #EFD9B4 100%);
    border: 1px solid #E3C89B;
    display: grid; place-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem; font-weight: 700; color: #B5762F;
}
.af-file-name {
    font-size: 1.05rem; font-weight: 600; color: #2C1F33; line-height: 1.25;
    word-break: break-all;
}
.af-file-ext {
    font-size: 0.82rem; color: #A095AC; margin-top: 1px;
    text-transform: uppercase; letter-spacing: 0.03em;
}
[class*="st-key-af_card_"] div.stDownloadButton > button {
    background: transparent !important; border: none !important;
    color: #6B6172 !important; min-height: 32px !important;
    padding: 0 !important;
}
[class*="st-key-af_card_"] div.stDownloadButton > button:hover {
    color: #2C1F33 !important;
}

/* petak Konten (gambar) */
[class*="st-key-af_konten"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important; margin-bottom: 10px !important;
}
[class*="st-key-af_konten"] [data-testid="stImage"] img {
    border-radius: 12px !important; border: 1px solid #EAE0D0 !important;
    background: #FFFFFF;
}

/* panel kosong */
.af-empty {
    background: #FFFFFF; border: 1px dashed #DBCEB9; border-radius: 12px;
    padding: 16px; font-size: 0.86rem; color: #6B6172; line-height: 1.6;
}
.af-empty b { color: #2C1F33; }

/* ================= TAMPILAN ISI FILE ================= */
.af-title-row { display: flex; align-items: baseline; gap: 2px; padding-top: 4px; }
.af-title {
    font-size: 1.18rem; font-weight: 650; color: #2C1F33;
    letter-spacing: -0.02em; font-family: 'Source Serif 4', serif;
}
.af-title-ext { font-size: 0.95rem; color: #A095AC; }

/* Baris aksi: Salin | perlebar | tutup.
   Ketiganya dipaksa TINGGI SAMA (36px) dan sejajar tengah. Tanpa ini,
   tombol Salin (HTML biasa) dan tombol Streamlit punya margin bawaan
   berbeda sehingga terlihat tidak rata. */
[class*="st-key-af_actbar"] [data-testid="stHorizontalBlock"] {
    gap: 6px !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
}
[class*="st-key-af_actbar"] [data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
    min-width: 0 !important;
}
/* nol-kan margin bawaan pembungkus Streamlit */
[class*="st-key-af_actbar"] .element-container,
[class*="st-key-af_actbar"] [data-testid="stMarkdownContainer"],
[class*="st-key-af_actbar"] [data-testid="stMarkdown"],
[class*="st-key-af_actbar"] div.stButton {
    margin: 0 !important; padding: 0 !important; line-height: 0 !important;
    width: 100% !important;
}
.af-copy {
    background: #FFFFFF; border: 1px solid #DBCEB9; border-radius: 9px;
    cursor: pointer; font-size: 0.82rem; font-weight: 600; color: #2C1F33;
    height: 36px; width: 100%; padding: 0 14px; margin: 0;
    display: inline-flex; align-items: center; justify-content: center;
    line-height: 1;
    transition: background .15s ease, transform .1s ease;
}
.af-copy:hover { background: #F2E8D6; }
.af-copy:active { transform: scale(0.96); }
[class*="st-key-af_actbar"] div.stButton > button {
    background: #FFFFFF !important; border: 1px solid #DBCEB9 !important;
    color: #4A3559 !important; border-radius: 9px !important;
    width: 36px !important; min-width: 36px !important;
    height: 36px !important; min-height: 36px !important;
    padding: 0 !important; margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important; justify-content: center !important;
    line-height: 1 !important;
}
[class*="st-key-af_actbar"] [data-testid="stIconMaterial"] {
    font-size: 1.05rem !important;
    width: 1.05rem !important; height: 1.05rem !important;
    line-height: 1 !important;
}
[class*="st-key-af_actbar"] div.stButton > button:hover {
    background: #F2E8D6 !important; border-color: #2C1F33 !important;
}
[class*="st-key-af_back"] div.stButton > button {
    background: transparent !important; border: none !important;
    color: #8E8398 !important; font-size: 0.8rem !important;
    min-height: 26px !important; padding: 0 !important;
    margin: -2px 0 8px !important;
}
[class*="st-key-af_back"] div.stButton > button:hover { color: #2C1F33 !important; }

/* kotak kode: nomor baris + pewarnaan */
.af-codebox {
    background: #FFFFFF; border: 1px solid #EAE0D0; border-radius: 12px;
    padding: 12px 4px 12px 0; overflow: auto; max-height: 64vh;
    font-family: 'JetBrains Mono', monospace; font-size: 0.79rem;
    line-height: 1.75;
}
.af-ln { display: flex; white-space: pre; }
.af-ln:hover { background: #FBF7F0; }
.af-num {
    flex: 0 0 46px; text-align: right; padding-right: 14px;
    color: #C4BACF; user-select: none;
}
.af-code { white-space: pre; color: #2C1F33; padding-right: 14px; }
.af-code .k-key { color: #7A3E9D; font-weight: 600; }   /* kata kunci */
.af-code .k-str { color: #1F7A4D; }                      /* teks */
.af-code .k-com { color: #A095AC; font-style: italic; }  /* komentar */
.af-code .k-num { color: #B5762F; }                      /* angka */

[class*="st-key-af_actions"] div.stDownloadButton > button {
    background: #2C1F33 !important; border: none !important;
    color: #FBF6EC !important; border-radius: 10px !important;
    font-size: 0.84rem !important; font-weight: 600 !important;
    min-height: 40px !important; margin-top: 10px !important;
}
/* ---------- layar sempit ---------- */
@media (max-width: 640px) {
    .rc-card { max-width: 100%; }
    .rc-cmp-row { grid-template-columns: 1fr; }
    .rc-cmp-row > *:not(:first-child) {
        border-left: none;
        border-top: 1px solid #F3ECE0;
    }
    [class*="st-key-rc_nav_"] { max-width: 100%; }
    [class*="st-key-rc_map_"], [class*="st-key-rc_itin_"] { max-width: 100%; }
    .rc-tr { grid-template-columns: 1fr; }
    .rc-tr-pane:last-child {
        border-left: none;
        border-top: 1px solid #F3ECE0;
    }
    .rc-itin-row { grid-template-columns: 48px 16px 1fr; 
    }
}
/* ====================================================================
   KARTU PILIHAN INTERAKTIF (quick reply)
   Muncul di bawah jawaban Yuki saat dia perlu memastikan sesuatu.
   Tata letak: grid 2 kolom bila label pendek, vertikal di layar sempit.
==================================================================== */
[class*="st-key-qr_card_"] {
    background: #FBF6EC !important;              /* sedikit lebih terang dari kanvas */
    border: 1px solid #E0D2BB !important;
    border-radius: 14px !important;
    padding: 14px 14px 12px !important;
    margin: 8px 0 20px !important;
    max-width: 560px;
    box-shadow: 0 2px 10px rgba(44, 31, 51, 0.05) !important;
    animation: qrCardIn 0.32s cubic-bezier(.2,.8,.2,1) both;
}
@keyframes qrCardIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* --- pertanyaan --- */
.qr-question {
    font-size: 0.9rem;
    font-weight: 600;                 /* semibold: terbaca sekilas */
    color: #2C1F33;
    letter-spacing: -0.01em;
    margin: 0 0 12px;
    line-height: 1.45;
}

/* --- tombol pilihan --- */
[class*="st-key-qr_card_"] div.stButton > button {
    background: #FFFFFF !important;   /* "mengambang" di atas kartu */
    border: 1px solid #DBCEB9 !important;
    border-radius: 10px !important;
    color: #2C1F33 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;      /* medium */
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    min-height: 44px !important;      /* nyaman di-tap pada layar sentuh */
    box-shadow: 0 1px 2px rgba(44, 31, 51, 0.05) !important;
    white-space: normal !important;
    line-height: 1.35 !important;
    transition: background .16s ease, border-color .16s ease,
                transform .1s ease, box-shadow .16s ease !important;
}
[class*="st-key-qr_card_"] div.stButton > button:hover {
    background: #FFFDF9 !important;
    border-color: #2C1F33 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 14px rgba(44, 31, 51, 0.11) !important;
}
[class*="st-key-qr_card_"] div.stButton > button:active {
    transform: scale(0.985) translateY(0) !important;  /* umpan balik instan */
    background: #F4EADA !important;
    box-shadow: 0 1px 2px rgba(44, 31, 51, 0.08) !important;
}
[class*="st-key-qr_card_"] div.stButton > button:focus-visible {
    outline: 2px solid #2C1F33 !important;
    outline-offset: 2px !important;
}

/* --- keadaan TERPILIH (multi-pilih, tombol primary) --- */
[class*="st-key-qr_card_"] div.stButton > button[kind="primary"],
[class*="st-key-qr_card_"] [data-testid="stBaseButton-primary"] {
    background: #2C1F33 !important;
    border-color: #2C1F33 !important;
    color: #FBF6EC !important;
    font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(44, 31, 51, 0.20) !important;
}
[class*="st-key-qr_card_"] div.stButton > button[kind="primary"]:hover {
    background: #40304A !important;
    border-color: #40304A !important;
}

/* --- tombol "Kirim pilihan" pada kartu multi-pilih --- */
[class*="st-key-qr_send_"] div.stButton > button {
    margin-top: 4px !important;
    background: #EFE4D2 !important;
    border-style: dashed !important;
    text-align: center !important;
    justify-content: center !important;
    font-weight: 600 !important;
}
[class*="st-key-qr_send_"] div.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* --- jarak antar tombol --- */
[class*="st-key-qr_card_"] [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    margin-bottom: 10px !important;
}
[class*="st-key-qr_card_"] [data-testid="stVerticalBlock"] {
    gap: 10px !important;
}
[class*="st-key-qr_card_"] div.stButton { margin: 0 !important; }

/* --- layar sempit: paksa satu tombol per baris --- */
@media (max-width: 640px) {
    [class*="st-key-qr_card_"] [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    [class*="st-key-qr_card_"] [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    [class*="st-key-qr_card_"] { max-width: 100%; }
}

/* --- kartu lama (sudah dijawab): jejak abu, tidak bisa diklik --- */
.qr-row-done { display: flex; flex-wrap: wrap; gap: 6px; }
.qr-chip-done {
    font-size: 0.78rem;
    color: #948AA0;
    background: rgba(44, 31, 51, 0.05);
    border: 1px solid #E2D6C2;
    border-radius: 8px;
    padding: 4px 10px;
}
/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #F2E8D6 !important;
    border: 1px solid #DBCEB9 !important;
    border-radius: 12px !important;
    color: #2C1F33 !important;
}

/* PENTING soal ukuran font footer:
   Streamlit punya aturan bawaan [data-testid="stMarkdownContainer"] p {...}
   yang spesifisitasnya (0,1,1) LEBIH TINGGI daripada .trinity-foot (0,1,0),
   jadi kalau ditulis pakai kelas saja, font-size-nya selalu kalah dan
   terlihat "tidak mau mengecil". Karena itu selektornya dinaikkan
   (elemen p + wadah markdown) dan diberi !important.
   >>> UBAH ANGKA DI SINI untuk mengatur ukuran footer <<< */
/* >>> ATUR POSISI FOOTER DI SINI <<<
   --foot-x : geser mendatar. Minus = ke kiri, plus = ke kanan (0 = tengah).
   --foot-y : geser tegak.    Minus = ke atas, plus = ke bawah. */
:root {
    --foot-x: -155px;
    --foot-y: -100px;
}

.trinity-foot,
p.trinity-foot,
[data-testid="stMarkdownContainer"] p.trinity-foot,
[data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] p.trinity-foot {
    /* display:block + lebar penuh -> text-align:center benar-benar bekerja.
       Tanpa ini footer bisa terlihat menempel ke kiri. */
    display: block !important;
    width: 100% !important;
    transform: translate(var(--foot-x), var(--foot-y));
    text-align: center !important;
    color: #7E7387 !important;
    font-size: 12px !important;      /* halaman awal (sebelum mulai chat) */
    line-height: 1.5 !important;
    /* margin besar (vh) = footer turun mendekati bawah layar, DI ATAS
       kotak input — tidak lagi menempel ke sapaan. */
    margin-top: -2vh !important;
    margin-bottom: 0 !important;
    font-family: 'Inter', sans-serif !important;
    -webkit-text-size-adjust: 100%;  /* cegah browser HP membesarkan teks kecil */
    text-size-adjust: 100%;
}

/* versi saat chat berjalan: lebih kecil lagi dari versi halaman awal */
.trinity-foot.in-chat,
p.trinity-foot.in-chat,
[data-testid="stMarkdownContainer"] p.trinity-foot.in-chat,
[data-testid="stMainBlockContainer"] [data-testid="stMarkdownContainer"] p.trinity-foot.in-chat {
    font-size: 11px !important;       /* saat chat sudah berjalan */
    color: #827788 !important;
    margin-top: 22px !important;
}

/* logo kecil di dalam footer ikut menyesuaikan */
.trinity-foot .logo-foot {
    width: 1.2em !important;
    height: 1.2em !important;
}

"""
