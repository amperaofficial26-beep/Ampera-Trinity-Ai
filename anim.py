# -*- coding: utf-8 -*-
"""
Animasi ala iOS untuk Ampera Trinity AI.

Kenapa terpisah dari styles.py:
  1. Disuntik BELAKANGAN (setelah CSS utama), jadi pasti menang.
  2. Gampang dimatikan/disetel tanpa menyentuh stylesheet besar.

Catatan teknis penting:
  Popover Streamlit (stPopoverBody) diposisikan oleh BaseWeb memakai
  INLINE style `transform: translate3d(...)`. Kalau kita ikut menganimasikan
  `transform` pada elemen itu, posisinya jadi kacau / animasinya tidak
  kelihatan. Karena itu yang dianimasikan adalah ISI di dalamnya, bukan
  kotak popover-nya sendiri.

>>> ATUR KEKUATAN ANIMASI DI BAGIAN "PENGATURAN" DI BAWAH <<<
"""

from __future__ import annotations

import streamlit as st

# ============================================================================
# PENGATURAN
# ============================================================================
ANIM_ON = True                 # False = matikan semua animasi
DURASI_MS = 450                # durasi animasi (ms)
SKALA_AWAL = 0.85              # makin kecil makin dramatis (0.85 = dramatis)
PANTULAN = 1.03                # 1.0 = tanpa pantulan; 1.03 = memantul jelas
KURVA = "cubic-bezier(.32,.72,0,1)"   # kurva khas iOS
# ============================================================================


def inject_anim_css() -> None:
    """Suntik CSS animasi. Panggil sekali di main(), setelah inject_css()."""
    if not ANIM_ON:
        return

    d = str(DURASI_MS) + "ms"
    s = str(SKALA_AWAL)
    b = str(PANTULAN)

    css = (
        "<style>"
        # ---------- keyframes ----------
        "@keyframes iosPopIn{"
        "0%{opacity:0;transform:scale(" + s + ") translateY(10px);}"
        "60%{opacity:1;transform:scale(" + b + ") translateY(0);}"
        "100%{opacity:1;transform:scale(1) translateY(0);}"
        "}"
        "@keyframes iosGrowIn{"
        "0%{opacity:0;transform:scale(" + s + ");}"
        "60%{opacity:1;transform:scale(" + b + ");}"
        "100%{opacity:1;transform:scale(1);}"
        "}"
        "@keyframes iosPageIn{"
        "0%{opacity:0;transform:scale(0.94) translateY(12px);}"
        "100%{opacity:1;transform:scale(1) translateY(0);}"
        "}"
        "@keyframes iosFadeIn{0%{opacity:0;}100%{opacity:1;}}"

        # ---------- 1. POPOVER ----------
        # Kotak popover-nya HANYA di-fade (transform-nya milik BaseWeb,
        # jangan diganggu). Isinya yang tumbuh dari sudut.
        "[data-testid='stPopoverBody']{"
        "animation:iosFadeIn " + str(int(DURASI_MS * 0.45)) + "ms " + KURVA + " both;"
        "}"
        "[data-testid='stPopoverBody'] > div,"
        "[data-testid='stPopoverBody'] [data-testid='stVerticalBlock']:first-child{"
        "animation:iosPopIn " + d + " " + KURVA + " both;"
        "transform-origin:top center;"
        "will-change:transform,opacity;"
        "}"

        # ---------- 2. TOMBOL DITEKAN ----------
        "button[data-testid='stPopoverButton']:active,"
        "[data-testid='stPopover'] button:active{"
        "transform:scale(0.94) !important;"
        "transition:transform 90ms " + KURVA + " !important;"
        "}"

        # ---------- 3. KARTU GAMBAR ----------
        "[class*='st-key-img_pop_'] img{"
        "animation:iosGrowIn " + d + " " + KURVA + " both;"
        "transform-origin:center center;"
        "border-radius:12px;"
        "}"
        "[class*='st-key-img_pop_'] div.stDownloadButton{"
        "animation:iosPopIn " + d + " " + KURVA + " both;"
        "animation-delay:120ms;"
        "}"

        # ---------- hormati preferensi 'kurangi gerak' ----------
        "@media (prefers-reduced-motion: reduce){"
        "[data-testid='stPopoverBody'],"
        "[data-testid='stPopoverBody'] > div,"
        "[class*='st-key-img_pop_'] img,"
        "[class*='st-key-img_pop_'] div.stDownloadButton{animation:none !important;}"
        "}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def inject_page_anim() -> None:
    """Animasi perpindahan halaman. Dipanggil HANYA saat halaman berganti,
    supaya tidak terputar ulang tiap kali kirim chat atau klik tombol."""
    if not ANIM_ON:
        return
    st.markdown(
        "<style>[data-testid='stMainBlockContainer']{"
        "animation:iosPageIn " + str(DURASI_MS) + "ms " + KURVA + " both;"
        "transform-origin:left center;}</style>",
        unsafe_allow_html=True,
    )
