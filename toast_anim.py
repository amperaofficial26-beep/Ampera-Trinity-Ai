# -*- coding: utf-8 -*-
"""Toast sukses Trinity: glow, logo beranimasi, lalu tanda centang."""
from __future__ import annotations

import streamlit as st

from logo import LOGO_B64


# Durasi popup: 7.000 milidetik = 7 detik.
_DURASI_MS = 7000


def inject_toast_anim() -> None:
    """Pasang tampilan dan animasi popup Trinity."""
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
   Warna utama popup diatur pada bagian ini.
   ================================================================ */
[data-testid="stToast"] {{
  position: relative !important;

  min-height: 92px !important;
  padding: 18px 46px 18px 78px !important;

  /* Warna teks utama. */
  color: #342b3a !important;

  /* Garis cokelat-beige lembut. */
  border: 1px solid #b9a58c !important;
  border-radius: 18px !important;

  /* Latar beige agar menyatu dengan tampilan aplikasi. */
  background: rgba(247, 236, 216, .98) !important;

  /* Efek kaca lembut. */
  backdrop-filter:
    blur(18px)
    saturate(1.12) !important;

  -webkit-backdrop-filter:
    blur(18px)
    saturate(1.12) !important;

  /* Bayangan gelap dan glow ungu Trinity. */
  box-shadow:
    0 12px 34px rgba(52, 43, 58, .20),
    0 0 0 1px rgba(255, 252, 245, .88),
    0 0 28px rgba(111, 82, 128, .26) !important;

  overflow: hidden !important;

  animation:
    trinityToast7s {_DURASI_MS}ms
    cubic-bezier(.2, .8, .2, 1)
    forwards !important;
}}


/* ================================================================
   IKON BAWAAN STREAMLIT
   Hanya glyph ikon yang disembunyikan.

   Jangan menyembunyikan div pertama karena pada Streamlit terbaru
   div tersebut juga membungkus tulisan popup.
   ================================================================ */
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  opacity: 0 !important;

  width: 0 !important;
  min-width: 0 !important;

  margin: 0 !important;
}}


/* ================================================================
   LOGO TRINITY
   ================================================================ */
[data-testid="stToast"]::before {{
  content: "";

  position: absolute;
  z-index: 3;

  left: 25px;
  top: 27px;

  width: 38px;
  height: 38px;

  background-image: {logo};
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;

  filter:
    drop-shadow(
      0 4px 8px
      rgba(91, 66, 109, .38)
    );

  animation:
    trinityLogoJadiCentang 2.35s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   TANDA CENTANG
   Muncul setelah logo mengecil.
   ================================================================ */
[data-testid="stToast"]::after {{
  content: "✓";

  position: absolute;
  z-index: 4;

  left: 27px;
  top: 29px;

  width: 34px;
  height: 34px;

  display: grid;
  place-items: center;

  border-radius: 50%;

  /* Warna centang. */
  color: #ffffff;

  /* Ungu Trinity. */
  background:
    linear-gradient(
      145deg,
      #765c87,
      #4a3559
    );

  box-shadow:
    0 5px 14px rgba(74, 53, 89, .35),
    0 0 16px rgba(183, 148, 212, .32);

  font:
    700 21px/1
    Arial,
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
   Selector dibuat lebih kuat agar aturan tema Streamlit tidak
   membuat tulisan transparan atau sama dengan latarnya.
   ================================================================ */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
[data-testid="stToast"] p {{
  color: #342b3a !important;
  opacity: 1;

  font-weight: 500 !important;

  animation:
    trinityToastText .6s .72s
    ease both !important;
}}


/* ================================================================
   TOMBOL TUTUP
   ================================================================ */
[data-testid="stToast"] button {{
  color: #5e5267 !important;
}}

[data-testid="stToast"] button:hover {{
  color: #4a3559 !important;
  background: rgba(74, 53, 89, .10) !important;
}}


/* ================================================================
   ANIMASI KOTAK POPUP
   ================================================================ */
@keyframes trinityToast7s {{
  0% {{
    opacity: 0;

    transform:
      translateY(16px)
      scale(.88);

    filter: brightness(1.25);
  }}

  7% {{
    opacity: 1;

    transform:
      translateY(-3px)
      scale(1.025);
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
      translateY(13px)
      scale(.35)
      rotate(0deg);
  }}

  24% {{
    opacity: 1;

    transform:
      translateY(-8px)
      scale(1.12)
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
      scale(1.02)
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
      translateX(13px);

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
    """Tampilkan popup sukses dengan durasi visual tujuh detik."""
    try:
        st.toast(
            pesan,
            icon=":material/check:",
            duration="long",
        )
    except TypeError:
        st.toast(
            pesan,
            icon=":material/check:",
        )
