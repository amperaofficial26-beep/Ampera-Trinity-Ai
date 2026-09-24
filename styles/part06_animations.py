# -*- coding: utf-8 -*-
"""Animasi Trinity & efek fade text saat pindah halaman

Dipecah dari styles.py asli (baris 3550-3718), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ====================================================================
   ANIMASI TRINITY
   --------------------------------------------------------------------
   - Setiap tombol muncul dengan animasi mengembang (pop) yang halus.
   - Hover tombol: terangkat + menyala sedikit.
   - Klik tombol: menekan (scale mengecil sesaat).
   - Tombol "Top up / Trinity Pro" punya animasi mengembang lebih besar
     + kilau cahaya menyapu setelah muncul.
   - Saat pindah halaman: judul, kartu, baris fitur, dan teks masuk
     dengan fade + naik perlahan (fade-slide).
==================================================================== */

/* Semua tombol: masuk dengan pop halus. Pakai fill-mode `backwards`
   supaya setelah animasi selesai transisi hover normal tetap jalan. */
div.stButton > button,
div.stDownloadButton > button,
[data-testid="stPopover"] > button,
[data-testid="stChatInput"] button {
    animation: trinityBtnIn 0.34s cubic-bezier(0.22, 0.9, 0.32, 1.12) backwards !important;
    transform-origin: center center !important;
}
@keyframes trinityBtnIn {
    0%   { opacity: 0; transform: scale(0.9) translateY(6px); }
    55%  { opacity: 1; transform: scale(1.025) translateY(-1px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* Hover & tekan semua tombol: angkat sedikit lalu menekan saat diklik. */
div.stButton > button,
div.stDownloadButton > button,
[data-testid="stPopover"] > button,
[data-testid="stChatInput"] button {
    transition:
        background 0.16s ease,
        border-color 0.16s ease,
        color 0.16s ease,
        box-shadow 0.18s ease,
        transform 0.16s cubic-bezier(0.22, 0.9, 0.32, 1.12) !important;
}
div.stButton > button:not(:disabled):hover,
div.stDownloadButton > button:not(:disabled):hover,
[data-testid="stPopover"] > button:not(:disabled):hover,
[data-testid="stChatInput"] button:not(:disabled):hover {
    transform: translateY(-1px) scale(1.012);
}
div.stButton > button:not(:disabled):active,
div.stDownloadButton > button:not(:disabled):active,
[data-testid="stPopover"] > button:not(:disabled):active,
[data-testid="stChatInput"] button:not(:disabled):active {
    transform: translateY(0) scale(0.975);
    box-shadow: 0 1px 3px rgba(44, 31, 51, 0.12) !important;
}

/* ===== TOMBOL TOP UP / TRINITY PRO =====
   Muncul lebih dramatis: mengembang dari kecil (0.70) sambil naik,
   lalu diikuti kilau cahaya yang menyapu dari kiri ke kanan. */
[class*="st-key-akun_pro"] button,
[class*="st-key-plan_pro"] button,
[class*="st-key-acct_pro"] button,
[class*="st-key-pel_pro"] button,
button[class*="st-key-akun_pro"],
button[class*="st-key-plan_pro"],
button[class*="st-key-acct_pro"],
button[class*="st-key-pel_pro"] {
    animation: trinityProIn 0.58s cubic-bezier(0.16, 1.1, 0.3, 1) 0.05s backwards !important;
    position: relative !important;
    overflow: hidden !important;
}
@keyframes trinityProIn {
    0% {
        opacity: 0;
        transform: scale(0.68) translateY(14px);
        box-shadow: 0 0 0 rgba(74, 53, 89, 0);
    }
    60% {
        opacity: 1;
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 8px 26px rgba(74, 53, 89, 0.28);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
        box-shadow: 0 2px 10px rgba(44, 31, 51, 0.14);
    }
}
[class*="st-key-akun_pro"] button::after,
[class*="st-key-plan_pro"] button::after,
[class*="st-key-acct_pro"] button::after,
[class*="st-key-pel_pro"] button::after,
button[class*="st-key-akun_pro"]::after,
button[class*="st-key-plan_pro"]::after,
button[class*="st-key-acct_pro"]::after,
button[class*="st-key-pel_pro"]::after {
    content: "";
    position: absolute;
    top: -55%; bottom: -55%;
    left: 0; width: 55%;
    background: linear-gradient(
        100deg,
        rgba(255,255,255,0) 0%,
        rgba(255,255,255,0.62) 50%,
        rgba(255,255,255,0) 100%
    );
    filter: blur(1px);
    transform: translateX(-140%) skewX(-18deg);
    animation: trinitySweep 1.35s ease 0.5s backwards;
    pointer-events: none;
}
@keyframes trinitySweep {
    0%   { transform: translateX(-140%) skewX(-18deg); }
    55%, 100% { transform: translateX(340%) skewX(-18deg); }
}

/* ===== FADE TEXT SAAT PINDAH HALAMAN =====
   Heading, kartu, baris fitur, dan teks lain masuk dengan fade + naik
   perlahan. Karena setiap pindah halaman Streamlit merender ulang, CSS
   ini otomatis "memutar ulang" animasi pada halaman yang baru dibuka. */
.page-head,
.trinity-hero,
.trinity-greeting,
.trinity-sub,
.page-title,
.page-sub,
.set-section,
.plan-card,
.mini-card,
.phone-card,
.lang-card,
.cap-card,
.mem-item,
.mod-row,
.empty-card,
.icon-bar,
.help-step,
.tip-row,
.feat-row,
.cap-row,
.lang-row {
    animation: trinityPageIn 0.42s ease 0.03s backwards !important;
}
@keyframes trinityPageIn {
    from {
        opacity: 0;
        transform: translateY(9px);
        filter: blur(2px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
        filter: blur(0);
    }
}

/* Kartu kategori (Artefak / Kursus) & kartu lain ikut fade masuk agar
   seluruh isi halaman terasa "berbuka" sekali per pindah halaman. */
[class*="st-key-cat_"] button,
[class*="st-key-kurs_"] button {
    animation: trinityCardIn 0.45s ease backwards !important;
}
@keyframes trinityCardIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(12px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
"""
