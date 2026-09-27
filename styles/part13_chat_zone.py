# -*- coding: utf-8 -*-
"""ZONA TENGAH CHAT — kartu latar di belakang percakapan halaman utama.

Sebelumnya isi percakapan langsung menempel di wallpaper/latar aplikasi
sehingga terasa "menyatu" dan sulit dilihat batas kolomnya. Di sini kolom
tengah halaman chat (dan halaman Multi AI yang memakai penanda kelas yang
sama) diberi kartu sendiri: latar lembut, garis tepi tipis, sudut membulat,
dan bayangan halus — persis ruang baca di tengah layar.

Semua warna memakai variabel tema (var(--tr-*)) supaya ikut berubah saat
User mengganti wallpaper/palet di halaman Tampilan.

>>> ATUR ZONA TENGAH DI SINI <<<
    --zona-pad-y / --zona-pad-x : jarak isi ke tepi kartu
    --zona-radius               : kelengkungan sudut kartu
    --zona-alpha                : 0-100, makin besar makin pekat (kontras)
    --zona-min-tinggi           : tinggi minimum kartu
"""

CSS = r"""
/* ====================================================================
   ZONA TENGAH CHAT
==================================================================== */
:root {
    --zona-pad-y: 26px;
    --zona-pad-x: 30px;
    --zona-radius: 26px;
    --zona-alpha: 88%;
    --zona-min-tinggi: calc(100vh - 260px);
}

.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"],
.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"]:has(.tr-chat-layout)
> [data-testid="stVerticalBlock"] {
    padding: var(--zona-pad-y) var(--zona-pad-x)
             calc(var(--zona-pad-y) + 6px) !important;
    border: 1px solid color-mix(in srgb,
        var(--tr-border, #DBCEB9) 72%, transparent) !important;
    border-radius: var(--zona-radius) !important;
    background: color-mix(in srgb,
        var(--tr-surface, #FBF3E6) var(--zona-alpha), #FFFFFF) !important;
    box-shadow: 0 22px 52px color-mix(in srgb,
        var(--tr-text, #2C1F33) 9%, transparent) !important;
    min-height: var(--zona-min-tinggi) !important;
    backdrop-filter: blur(6px) saturate(1.05);
    -webkit-backdrop-filter: blur(6px) saturate(1.05);
}

/* Isi percakapan rata tengah kartu, dengan lebar baca yang nyaman. */
.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
> [data-testid="stElementContainer"],
.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]
> [data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Halaman awal (belum ada chat): sapaan & kartu saran didorong ke tengah
   kartu secara vertikal supaya tidak menempel di sisi atas. */
.stApp:has(.tr-chat-layout.tr-fresh-home)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    justify-content: center !important;
}

/* Gelembung pesan sedikit dipertegas supaya tetap terbaca di atas kartu. */
.stApp:has(.tr-chat-layout) [data-testid="stChatMessage"] {
    background: transparent !important;
}

/* Layar sempit: kartu dibuat lebih rapat & sudutnya mengecil. */
@media (max-width: 900px) {
    :root {
        --zona-pad-y: 16px;
        --zona-pad-x: 14px;
        --zona-radius: 18px;
        --zona-min-tinggi: calc(100vh - 220px);
    }
}
"""
