"""Logo & sapaan Trinity (dipisah dari app.py agar tidak terlalu panjang).

Berisi logo brand (PNG Deep Violet tertanam base64), pembungkus HTML logo,
sapaan halaman utama yang acak per sesi, dan indikator "berpikir".
Tidak mengubah perilaku apa pun — hanya pemisahan modul.
"""
from __future__ import annotations

import html
import random
from datetime import datetime

import streamlit as st

# Logo brand (PNG transparan, Deep Violet) ditanam sebagai base64 agar
# tampil SAMA di semua tempat (tab, sapaan, label, thinking, footer)
# tanpa bergantung pada file di assets/.
LOGO_B64 = (
    "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"
    "STsh+//ANMEG5juvhwAAAABJRU5ErkJggg=="
)


def logo_img_html(css_class: str = "logo-inline") -> str:
    """Logo brand (PNG base64) — identik dengan logo tab/thinking."""
    return (f'<span class="{css_class}" role="img" aria-label="logo Trinity">'
            f'<img src="data:image/png;base64,{LOGO_B64}" alt=""/></span>')


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
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    # Logo brand dengan pita cahaya berjalan (shimmer).
    icon = ('<span class="logo-shimmer">'
            f'<img src="data:image/png;base64,{LOGO_B64}" alt=""/></span>')
    return (
        '<div class="claude-think">'
        f"{icon}"
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )
