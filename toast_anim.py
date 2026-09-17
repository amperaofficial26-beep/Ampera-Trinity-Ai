# -*- coding: utf-8 -*-
"""Notifikasi sukses Trinity: emas elegan, glow, logo, lalu centang."""
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
@import url(
  'https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&display=swap'
);


/* ================================================================
   KOTAK POPUP
   Warna cokelat gelap dengan garis dan glow emas.
   ================================================================ */
[data-testid="stToast"] {{
  position: relative !important;
  box-sizing: border-box !important;

  min-height: 82px !important;
  width: min(390px, calc(100vw - 28px)) !important;
  padding: 16px 42px 16px 78px !important;

  color: #fff8e8 !important;

  border:
    1px solid
    rgba(224, 184, 91, .72) !important;

  border-radius: 18px !important;

  background:
    linear-gradient(
      145deg,
      rgba(48, 38, 29, .985),
      rgba(27, 22, 19, .985)
    ) !important;

  backdrop-filter:
    blur(20px)
    saturate(1.18) !important;

  -webkit-backdrop-filter:
    blur(20px)
    saturate(1.18) !important;

  box-shadow:
    0 18px 42px rgba(38, 27, 17, .42),
    inset 0 1px 0 rgba(255, 235, 177, .18),
    0 0 0 1px rgba(119, 84, 28, .30),
    0 0 36px rgba(218, 166, 55, .48) !important;

  overflow: hidden !important;

  animation:
    trinityToast7s {_DURASI_MS}ms
    cubic-bezier(.2, .8, .2, 1)
    forwards !important;
}}


/* ================================================================
   SEMBUNYIKAN IKON BAWAAN STREAMLIT
   Mencegah munculnya dua tanda centang.
   ================================================================ */
[data-testid="stToast"] [data-testid="stToastIcon"],
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  display: none !important;
}}


/* ================================================================
   LOGO TRINITY
   Logo diubah menjadi emas agar terlihat di atas latar gelap.
   ================================================================ */
[data-testid="stToast"]::before {{
  content: "";

  position: absolute;
  z-index: 3;

  left: 20px;
  top: 19px;

  width: 44px;
  height: 44px;

  background-image: {logo};
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;

  /*
   * Bagian ini mengubah warna logo menjadi emas.
   * Drop-shadow menambahkan glow emas di sekeliling logo.
   */
  filter:
    brightness(0)
    saturate(100%)
    invert(79%)
    sepia(65%)
    saturate(653%)
    hue-rotate(355deg)
    brightness(103%)
    contrast(93%)
    drop-shadow(
      0 5px 11px
      rgba(246, 199, 91, .62)
    );

  animation:
    trinityLogoJadiCentang 2.35s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   TANDA CENTANG EMAS
   Muncul setelah animasi logo selesai.
   ================================================================ */
[data-testid="stToast"]::after {{
  content: "✓";

  position: absolute;
  z-index: 4;

  left: 22px;
  top: 21px;
    
  width: 40px;
  height: 40px;


  display: grid;
  place-items: center;

  border:
    1px solid
    rgba(255, 226, 151, .68);

  border-radius: 50%;

  color: #241b12;

  background:
    linear-gradient(
      145deg,
      #f3d47d,
      #bd8125
    );

  box-shadow:
    0 7px 18px rgba(20, 13, 8, .42),
    inset 0 1px 1px rgba(255, 249, 218, .55),
    0 0 22px rgba(235, 181, 55, .66);

  font:
    700 24px/1
    "Manrope",
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
   Menggunakan Manrope agar modern dan tidak terlalu formal.
   ================================================================ */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
[data-testid="stToast"] p {{
  color: #fff8e8 !important;

  font-family:
    "UnifrakturCook",
    "Old English Text MT",
    "Lucida Blackletter",
    fantasy !important;

  font-size: 20px !important;
  font-weight: 700 !important;
  line-height: 1.3 !important;
  letter-spacing: .025em !important;

  text-shadow:
    0 1px 8px rgba(246, 206, 112, .15),
    0 0 15px rgba(218, 166, 55, .10);
    
  opacity: 1;

  animation:
    trinityToastText .62s .70s
    ease both !important;
}}


/* ================================================================
   TOMBOL TUTUP
   ================================================================ */
[data-testid="stToast"] button {{
  color: #e8cf91 !important;
  border-radius: 50% !important;
}}

[data-testid="stToast"] button:hover {{
  color: #fff5d6 !important;
  background: rgba(224, 178, 72, .15) !important;
}}


/* ================================================================
   ANIMASI KOTAK POPUP
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
   Logo timbul, meloncat, berputar, kemudian mengecil.
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
/* LETAKKAN KODE RESPONSIVE MOBILE DI SINI */
@media (max-width: 600px) {{
  [data-testid="stToast"] {{
    width: calc(100vw - 24px) !important;
    min-height: 78px !important;

    padding:
      14px
      38px
      14px
      72px !important;
  }}

  [data-testid="stToast"] [data-testid="stMarkdownContainer"],
  [data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
  [data-testid="stToast"] p {{
    font-size: 17px !important;
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
