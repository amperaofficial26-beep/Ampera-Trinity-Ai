"""Logo & sapaan Trinity (dipisah dari app.py agar tidak terlalu panjang).

Logo dibaca dari ``assets/logo_thinking_small.png`` (sekarang Coffee Brown —
sebelumnya Deep Violet) lalu ditanam sebagai base64 supaya tampil SAMA di
tab, sapaan, label "Yuki", indikator berpikir, dan footer. Bila file tidak
ada, jatuh ke bintang ✳. Tidak mengubah perilaku apa pun selain warna &
ukuran — hanya pemisahan modul.
"""
from __future__ import annotations

import base64
import html
import os
import random
from datetime import datetime

import streamlit as st

_LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "logo_thinking_small.png"
)


def _logo_b64() -> str:
    """Base64 file logo; kosong bila file tidak ada."""
    try:
        with open(_LOGO_PATH, "rb") as fh:
            return base64.b64encode(fh.read()).decode("ascii")
    except Exception:
        return ""


# Dibaca sekali saat import.
LOGO_B64 = _logo_b64()

# ----------------------------------------------------------------------
# UKURAN LOGO PER TEMPAT PAKAI (FIX: logo di halaman sapaan kegedean)
#   Ditulis sebagai inline style supaya PASTI menang walau ada aturan
#   lain di stylesheet yang mengira logo harus tampil besar.
# ----------------------------------------------------------------------
_LOGO_SIZES = {
    "logo-greeting": "48px",   # logo di sebelah "Selamat pagi" — SEBELUMNYA kegedean
    "logo-label":    "16px",   # logo kecil di label "Yuki" pada bubble jawaban
    "logo-progress": "18px",   # logo di progress bar generate gambar
    "logo-foot":     "14px",   # logo di footer halaman
    "logo-inline":   "18px",   # default umum
    "logo-shimmer":  "22px",   # logo di indikator "berpikir"
}


def logo_img_html(css_class: str = "logo-inline") -> str:
    """Logo brand (PNG base64); jatuh ke bintang ✳ bila file hilang.

    Ukurannya dipatok inline per css_class (lihat _LOGO_SIZES) supaya
    selalu tampil proporsional.
    """
    size = _LOGO_SIZES.get(css_class, "18px")
    if LOGO_B64:
        return (
            f'<span class="{css_class}" role="img" aria-label="logo Trinity" '
            f'style="display:inline-block;width:{size};height:{size};'
            f'vertical-align:middle;line-height:0;">'
            f'<img src="data:image/png;base64,{LOGO_B64}" alt="" '
            f'style="width:100%;height:100%;object-fit:contain;display:block;"/>'
            f'</span>'
        )
    return (
        f'<span class="{css_class} star" '
        f'style="display:inline-block;width:{size};height:{size};'
        f'font-size:{size};line-height:1;vertical-align:middle;">✳</span>'
    )


# Kumpulan sapaan per waktu; dipilih acak tiap sesi agar halaman utama
# tidak monoton saat aplikasi dibuka berulang kali.
SAPAAN = {
    "pagi":  ["Selamat pagi", "Pagi! Siap berkarya?", "Halo, selamat pagi"],
    "siang": ["Selamat siang", "Halo! Ada yang bisa kubantu?", "Selamat datang kembali"],
    "sore":  ["Selamat sore", "Sore! Lanjut berkarya?", "Halo, selamat sore"],
    "malam": ["Selamat malam", "Malam! Masih semangat?", "Halo, selamat malam"],
}


def get_greeting() -> str:
    """Sapaan halaman utama; acak per sesi, sesuai waktu, tidak monoton."""
    if "sapaan" not in st.session_state:
        h = datetime.now().hour
        periode = ("pagi" if 4 <= h < 11 else "siang" if 11 <= h < 15
                   else "sore" if 15 <= h < 19 else "malam")
        st.session_state["sapaan"] = random.choice(SAPAAN[periode])
    return st.session_state["sapaan"]


def thinking_html(phrases: list[str]) -> str:
    """Indikator 'berpikir': logo + frasa dengan shimmer."""
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    icon = logo_img_html("logo-shimmer")
    return (
        '<div class="claude-think">'
        f"{icon}"
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )
