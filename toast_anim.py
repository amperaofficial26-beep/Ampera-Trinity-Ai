# -*- coding: utf-8 -*-
"""Notifikasi (toast) Trinity — minimalis tetapi terlihat profesional.

Gaya lama (cokelat gelap, glow emas, huruf gotik, logo berubah jadi
centang) diganti kartu bersih bergaya produk: latar terang, garis tipis,
bayangan lembut, ikon kecil di dalam lingkaran, dan teks sans-serif.

>>> ATUR TAMPILAN NOTIFIKASI DI SINI <<<
"""
from __future__ import annotations

import streamlit as st

# Berapa lama notifikasi terlihat sebelum memudar (milidetik).
DURASI_MS = 4200

# Warna dasar notifikasi — mengikuti palet premium krem + ungu Trinity.
WARNA_LATAR = "#FFFDF9"
WARNA_GARIS = "#E6DAC8"
WARNA_TEKS = "#2C1F33"
WARNA_AKSEN = "#4A3559"
WARNA_AKSEN_LEMBUT = "#F1E9F4"

# Lebar maksimum kartu notifikasi.
LEBAR_PX = 340


def inject_toast_anim() -> None:
    """Pasang gaya notifikasi minimalis pada setiap rerun."""
    st.markdown(
        f"""
<style>
/* ================================================================
   TOAST — kartu minimalis
   ================================================================ */
[data-testid="stToast"] {{
  box-sizing: border-box !important;
  min-height: 0 !important;
  width: min({LEBAR_PX}px, calc(100vw - 28px)) !important;
  padding: 12px 36px 12px 14px !important;

  color: {WARNA_TEKS} !important;
  border: 1px solid {WARNA_GARIS} !important;
  border-radius: 14px !important;
  background: {WARNA_LATAR} !important;

  box-shadow:
    0 10px 28px rgba(44, 31, 51, .12),
    0 1px 2px rgba(44, 31, 51, .06) !important;

  animation:
    trinityToastMasuk 220ms cubic-bezier(.2, .8, .2, 1) both,
    trinityToastKeluar 260ms ease-in {DURASI_MS}ms forwards !important;
}}

/* Garis aksen tipis di tepi kiri sebagai penanda merek. */
[data-testid="stToast"]::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: {WARNA_AKSEN};
}}

/* ---------------------------------------------------------------
   IKON BAWAAN STREAMLIT — dipertahankan, dibuat kecil & rapi
   --------------------------------------------------------------- */
[data-testid="stToast"] [data-testid="stToastIcon"],
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  margin-right: 10px !important;
  border-radius: 9px !important;
  background: {WARNA_AKSEN_LEMBUT} !important;
  color: {WARNA_AKSEN} !important;
  font-size: 16px !important;
  line-height: 1 !important;
}}

/* ---------------------------------------------------------------
   TEKS
   --------------------------------------------------------------- */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
[data-testid="stToast"] p {{
  margin: 0 !important;
  color: {WARNA_TEKS} !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system,
               "Segoe UI", sans-serif !important;
  font-size: .88rem !important;
  font-weight: 560 !important;
  line-height: 1.45 !important;
  letter-spacing: -.005em !important;
  text-shadow: none !important;
}}

/* ---------------------------------------------------------------
   TOMBOL TUTUP
   --------------------------------------------------------------- */
[data-testid="stToast"] button {{
  top: 7px !important;
  right: 7px !important;
  width: 24px !important;
  height: 24px !important;
  border-radius: 8px !important;
  color: #9A8F9A !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  opacity: .75 !important;
  transition: background .15s ease, color .15s ease, opacity .15s ease !important;
}}
[data-testid="stToast"] button:hover {{
  background: #F4ECE1 !important;
  color: {WARNA_TEKS} !important;
  opacity: 1 !important;
}}

/* ---------------------------------------------------------------
   ANIMASI — halus dan singkat, tanpa kilau berlebihan
   --------------------------------------------------------------- */
@keyframes trinityToastMasuk {{
  from {{ opacity: 0; transform: translateY(10px) scale(.985); }}
  to   {{ opacity: 1; transform: none; }}
}}

@keyframes trinityToastKeluar {{
  from {{ opacity: 1; transform: none; }}
  to   {{ opacity: 0; transform: translateY(-6px) scale(.99); }}
}}

@media (max-width: 640px) {{
  [data-testid="stToast"] {{
    width: calc(100vw - 20px) !important;
    padding: 11px 32px 11px 12px !important;
  }}
  [data-testid="stToast"] p {{ font-size: .84rem !important; }}
}}

@media (prefers-reduced-motion: reduce) {{
  [data-testid="stToast"] {{ animation: none !important; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def toast_sukses(pesan: str) -> None:
    """Notifikasi sukses ringkas dengan ikon centang kecil."""
    try:
        st.toast(pesan, icon=":material/check_circle:", duration="short")
    except TypeError:
        st.toast(pesan, icon=":material/check_circle:")
