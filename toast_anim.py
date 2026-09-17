# -*- coding: utf-8 -*-
"""Notifikasi sukses Trinity: gelap elegan, glow, logo, lalu centang."""
from __future__ import annotations

import streamlit as st

from logo import LOGO_B64


_DURASI_MS = 7000


def inject_toast_anim() -> None:
    """Pasang desain dan animasi toast Trinity pada setiap rerun."""
    logo = (
        f'url("data:image/png;base64,{LOGO_B64}")'
        if LOGO_B64
        else "none"
    )

    st.markdown(
        f"""
<style>

/* ================================================================
   KOTAK POPUP
   ================================================================ */
[data-testid="stToast"] {{
  position: relative !important;
  box-sizing: border-box !important;

  min-height: 104px !important;
  padding: 22px 48px 22px 94px !important;

  color: #f8f1e8 !important;

  border:
    1px solid
    rgba(190, 164, 205, .52) !important;

  border-radius: 22px !important;

  background:
    linear-gradient(
      145deg,
      rgba(52, 43, 58, .98),
      rgba(35, 29, 41, .98)
    ) !important;

  backdrop-filter:
    blur(20px)
    saturate(1.18) !important;

  -webkit-backdrop-filter:
    blur(20px)
    saturate(1.18) !important;

  box-shadow:
    0 18px 42px rgba(30, 22, 35, .38),
    inset 0 1px 0 rgba(255, 255, 255, .13),
    0 0 0 1px rgba(73, 55, 82, .24),
    0 0 34px rgba(156, 113, 181, .44) !important;

  overflow: hidden !important;

  animation:
    trinityToast7s {_DURASI_MS}ms
    cubic-bezier(.2, .8, .2, 1)
    forwards !important;
}}


/* ================================================================
   SEMBUNYIKAN IKON BAWAAN STREAMLIT
   ================================================================ */
[data-testid="stToast"] [data-testid="stToastIcon"],
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  display: none !important;
}}


/* ================================================================
   LOGO TRINITY
   Ukuran logo diperbesar menjadi 48px.
   ================================================================ */
[data-testid="stToast"]::before {{
  content: "";

  position: absolute;
  z-index: 3;

  left: 25px;
  top: 27px;

  width: 48px;
  height: 48px;

  background-image: {logo};
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;

  filter:
    drop-shadow(
      0 5px 10px
      rgba(195, 151, 220, .48)
    );

  animation:
    trinityLogoJadiCentang 2.35s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   TANDA CENTANG BUATAN
   Hanya centang ini yang akan tampil.
   ================================================================ */
[data-testid="stToast"]::after {{
  content: "✓";

  position: absolute;
  z-index: 4;

  left: 27px;
  top: 29px;

  width: 44px;
  height: 44px;

  display: grid;
  place-items: center;

  border-radius: 50%;

  color: #fffaf2;

  background:
    linear-gradient(
      145deg,
      #9270a6,
      #5c3f6c
    );

  box-shadow:
    0 7px 18px rgba(20, 13, 24, .36),
    inset 0 1px 1px rgba(255, 255, 255, .24),
    0 0 20px rgba(183, 135, 211, .58);

  font:
    700 27px/1
    "Inter",
    "Segoe UI",
    sans-serif;

  opacity: 0;

  transform:
    scale(.2)
    rotate(-35deg);

  animation:
    trinityCentangMasuk .55s 2.02s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   TULISAN POPUP
   ================================================================ */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
[data-testid="stToast"] p {{
  color: #f8f1e8 !important;

  font-family:
    "Inter",
    "Segoe UI",
    system-ui,
    sans-serif !important;

  font-size: 16px !important;
  font-weight: 600 !important;
  line-height: 1.48 !important;
  letter-spacing: .01em !important;

  opacity: 1;

  animation:
    trinityToastText .62s .70s
    ease both !important;
}}


/* ================================================================
   TOMBOL TUTUP
   ================================================================ */
[data-testid="stToast"] button {{
  color: #d8c8df !important;
  border-radius: 50% !important;
}}

[data-testid="stToast"] button:hover {{
  color: #ffffff !important;
  background: rgba(196, 153, 220, .15) !important;
}}


/* ================================================================
   ANIMASI POPUP
   ================================================================ */
@keyframes trinityToast7s {{
  0% {{
    opacity: 0;

    transform:
      translateY(17px)
      scale(.88);

    filter: brightness(1.28);
  }}

  7% {{
    opacity: 1;

    transform:
      translateY(-3px)
      scale(1.018);
  }}

  12% {{
    transform:
      translateY(0)
      scale(1);
  }}

  88% {{
    opacity: 1;

    transform:
      translateY(0)
      scale(1);
  }}

  100% {{
    opacity: 0;
    visibility: hidden;

    transform:
      translateY(-12px)
      scale(.97);
  }}
}}


/* ================================================================
   ANIMASI LOGO
   ================================================================ */
@keyframes trinityLogoJadiCentang {{
  0% {{
    opacity: 0;

    transform:
      translateY(14px)
      scale(.32)
      rotate(0deg);
  }}

  24% {{
    opacity: 1;

    transform:
      translateY(-9px)
      scale(1.13)
      rotate(0deg);
  }}

  43% {{
    transform:
      translateY(2px)
      scale(.96)
      rotate(0deg);
  }}

  68% {{
    opacity: 1;

    transform:
      translateY(-3px)
      scale(1.03)
      rotate(360deg);
  }}

  84% {{
    opacity: 1;

    transform:
      scale(.92)
      rotate(360deg);
  }}

  100% {{
    opacity: 0;

    transform:
      scale(.12)
      rotate(405deg);
  }}
}}


/* ================================================================
   ANIMASI CENTANG
   ================================================================ */
@keyframes trinityCentangMasuk {{
  to {{
    opacity: 1;

    transform:
      scale(1)
      rotate(0deg);
  }}
}}


/* ================================================================
   ANIMASI TULISAN
   ================================================================ */
@keyframes trinityToastText {{
  from {{
    opacity: 0;

    transform:
      translateX(14px);

    filter: blur(3px);
  }}

  to {{
    opacity: 1;

    transform:
      translateX(0);

    filter: blur(0);
  }}
}}


/* ================================================================
   AKSESIBILITAS
   ================================================================ */
@media (prefers-reduced-motion: reduce) {{
  [data-testid="stToast"],
  [data-testid="stToast"]::before,
  [data-testid="stToast"]::after,
  [data-testid="stToast"] [data-testid="stMarkdownContainer"] {{
    animation-duration: .01ms !important;
    animation-delay: 0ms !important;
  }}
}}

</style>
""",
        unsafe_allow_html=True,
    )


def toast_sukses(pesan: str) -> None:
    """Tampilkan toast tanpa ikon bawaan agar centang tidak menjadi dua."""
    try:
        st.toast(
            pesan,
            icon=None,
            duration="long",
        )
    except TypeError:
        st.toast(
            pesan,
            icon=None,
        )
