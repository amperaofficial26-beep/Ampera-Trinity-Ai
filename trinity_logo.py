"""Logo & sapaan Trinity (dipisah dari app.py agar tidak terlalu panjang).

Logo dibaca dari ``assets/logo_thinking_small.png`` (sudah Deep Violet) lalu
ditanam sebagai base64 supaya tampil SAMA di tab, sapaan, label "Yuki",
indikator berpikir, dan footer. Bila file tidak ada, jatuh ke bintang ✳.
Tidak mengubah perilaku apa pun — hanya pemisahan modul.
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


def logo_img_html(css_class: str = "logo-inline") -> str:
    """Logo brand (PNG base64); jatuh ke bintang ✳ bila file hilang."""
    if LOGO_B64:
        return (f'<span class="{css_class}" role="img" aria-label="logo Trinity">'
                f'<img src="data:image/png;base64,{LOGO_B64}" alt=""/></span>')
    return f'<span class="{css_class} star">✳</span>'


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
    if LOGO_B64:
        icon = ('<span class="logo-shimmer">'
                f'<img src="data:image/png;base64,{LOGO_B64}" alt=""/></span>')
    else:
        icon = '<span class="star">✳</span>'
    return (
        '<div class="claude-think">'
        f"{icon}"
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )
