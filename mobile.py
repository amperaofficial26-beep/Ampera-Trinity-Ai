"""Halaman pengganti untuk perangkat mobile.

Versi mobile belum tersedia, jadi di HP hanya tampil logo, nama app,
dan pesan permintaan maaf. Di desktop app tampil seperti biasa.
"""

from __future__ import annotations

import streamlit as st

from trinity_logo import LOGO_B64

APP_NAME = "Ampera Trinity AI"
PESAN = "Maaf, Versi mobile app ini belum tersedia......"

# Warna gampang diganti di sini
BG = "#F5EBDD"
TEKS = "#4A3426"

_MOBILE_KEYWORDS = ("android", "iphone", "ipod", "mobile", "windows phone")


def is_mobile() -> bool:
    """Deteksi HP lewat User-Agent. Aman: bila tidak terbaca, dianggap desktop."""
    try:
        ua = (st.context.headers.get("User-Agent") or "").lower()
    except Exception:
        return False
    return any(k in ua for k in _MOBILE_KEYWORDS)


def render_mobile_notice() -> None:
    """Tampilkan logo + nama app + pesan, di tengah layar."""
    if LOGO_B64:
        logo = (
            f'<img src="data:image/png;base64,{LOGO_B64}" alt="logo Trinity" '
            f'style="width:72px;height:72px;object-fit:contain;"/>'
        )
    else:
        logo = f'<div style="font-size:64px;line-height:1;color:{TEKS};">✳</div>'

    st.markdown(
        f"""
        <style>
          [data-testid="stSidebar"],
          [data-testid="stSidebarCollapsedControl"],
          [data-testid="stHeader"],
          footer {{ display: none !important; }}
          .stApp {{ background: {BG}; }}
          .block-container {{ padding: 0 !important; }}
        </style>
        <div style="min-height:90vh;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;
                    text-align:center;padding:24px;gap:16px;">
          {logo}
          <div style="font-size:1.6rem;font-weight:700;color:{TEKS};">{APP_NAME}</div>
          <div style="font-size:1rem;color:{TEKS};opacity:.8;max-width:320px;">{PESAN}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def guard() -> None:
    """Panggil di app.py: kalau dibuka dari HP, tampilkan notice lalu hentikan app."""
    if is_mobile():
        render_mobile_notice()
        st.stop()
