# -*- coding: utf-8 -*-
"""Toast sukses Trinity: glow, logo beranimasi, lalu tanda centang."""
from __future__ import annotations

import streamlit as st

from logo import LOGO_B64


# Durasi popup dalam milidetik.
# 7000 milidetik = 7 detik.
_DURASI_MS = 7000


def inject_toast_anim() -> None:
    """Pasang animasi untuk toast aplikasi.

    Fungsi ini aman dipanggil pada setiap proses rerun Streamlit.
    """
    logo = (
        f'url("data:image/png;base64,{LOGO_B64}")'
        if LOGO_B64
        else "none"
    )

    st.markdown(
        f"""
<style>

/* ================================================================
   WARNA UTAMA POPUP
   Ubah bagian ini jika ingin menyesuaikan warna popup.
   ================================================================ */
[data-testid="stToast"] {{
  position: relative !important;
  min-height: 92px !important;
  padding: 18px 46px 18px 78px !important;

  /* Warna tulisan mengikuti tema aplikasi. */
  color: var(--tr-text, #29232e) !important;

  /* Warna garis tepi mengikuti warna aksen aplikasi. */
  border: 1px solid color-mix(
    in srgb,
    var(--tr-accent, #4a3559) 34%,
    var(--tr-border, #d8cbb9)
  ) !important;

  /* Kelengkungan mengikuti pengaturan sudut aplikasi. */
  border-radius: min(
    var(--tr-radius, 18px),
    22px
  ) !important;

  /* Warna latar mengikuti warna kartu/permukaan aplikasi. */
  background: color-mix(
    in srgb,
    var(--tr-surface, #fffdf9) 94%,
    transparent
  ) !important;

  /* Efek kaca agar cocok ketika memakai wallpaper. */
  backdrop-filter: blur(18px) saturate(1.15) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.15) !important;

  /* Bayangan dan glow mengikuti warna aksen aplikasi. */
  box-shadow:
    0 12px 38px
      color-mix(
        in srgb,
        var(--tr-text, #29232e) 18%,
        transparent
      ),
    0 0 0 1px
      color-mix(
        in srgb,
        var(--tr-surface, #fffdf9) 78%,
        transparent
      ),
    0 0 30px
      color-mix(
        in srgb,
        var(--tr-accent, #4a3559) 34%,
        transparent
      ) !important;

  overflow: hidden !important;

  /* Total durasi popup adalah tujuh detik. */
  animation:
    trinityToast7s {_DURASI_MS}ms
    cubic-bezier(.2, .8, .2, 1)
    forwards !important;
}}


/* ================================================================
   IKON BAWAAN STREAMLIT
   Disembunyikan karena diganti logo Trinity dan tanda centang.
   ================================================================ */
[data-testid="stToast"]
> div:first-child:not([data-testid="stMarkdownContainer"]),
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  opacity: 0 !important;
}}


/* ================================================================
   LOGO TRINITY
   Logo timbul, meloncat pelan, berputar, lalu mengecil.
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

  /* Glow logo mengikuti warna aksen aplikasi. */
  filter: drop-shadow(
    0 4px 8px
    color-mix(
      in srgb,
      var(--tr-accent, #4a3559) 42%,
      transparent
    )
  );

  animation:
    trinityLogoJadiCentang 2.35s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   TANDA CENTANG
   Muncul setelah logo Trinity selesai berputar dan mengecil.
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

  /* Warna tanda centang mengikuti warna teks di atas aksen. */
  color: var(--tr-on-accent, #ffffff);

  /* Lingkaran centang memakai warna aksen aktif. */
  background: linear-gradient(
    145deg,
    color-mix(
      in srgb,
      var(--tr-accent, #4a3559) 82%,
      white
    ),
    color-mix(
      in srgb,
      var(--tr-accent, #4a3559) 84%,
      black
    )
  );

  /* Glow centang mengikuti warna aksen aktif. */
  box-shadow:
    0 5px 14px
      color-mix(
        in srgb,
        var(--tr-accent, #4a3559) 38%,
        transparent
      ),
    0 0 16px
      color-mix(
        in srgb,
        var(--tr-accent, #4a3559) 36%,
        transparent
      );

  font: 700 21px/1 Arial, sans-serif;

  opacity: 0;
  transform: scale(.2) rotate(-35deg);

  animation:
    trinityCentangMasuk .55s 2.02s
    cubic-bezier(.34, 1.56, .64, 1)
    forwards;
}}


/* ================================================================
   WARNA DAN ANIMASI TULISAN
   ================================================================ */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] p {{
  color: var(--tr-text, #29232e) !important;

  animation:
    trinityToastText .6s .72s
    ease both !important;
}}


/* ================================================================
   TOMBOL TUTUP POPUP
   ================================================================ */
[data-testid="stToast"] button {{
  color: var(--tr-text2, #756b7b) !important;
}}

[data-testid="stToast"] button:hover {{
  color: var(--tr-accent, #4a3559) !important;

  background: color-mix(
    in srgb,
    var(--tr-accent, #4a3559) 10%,
    transparent
  ) !important;
}}


/* ================================================================
   ANIMASI KOTAK POPUP
   ================================================================ */
@keyframes trinityToast7s {{
  0% {{
    opacity: 0;
    transform: translateY(16px) scale(.88);
    filter: brightness(1.25);
  }}

  7% {{
    opacity: 1;
    transform: translateY(-3px) scale(1.025);
  }}

  12% {{
    transform: translateY(0) scale(1);
  }}

  88% {{
    opacity: 1;
    transform: translateY(0) scale(1);
  }}

  100% {{
    opacity: 0;
    transform: translateY(-12px) scale(.97);
    visibility: hidden;
  }}
}}


/* ================================================================
   ANIMASI LOGO TRINITY
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
   ANIMASI TANDA CENTANG
   ================================================================ */
@keyframes trinityCentangMasuk {{
  to {{
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }}
}}


/* ================================================================
   ANIMASI TULISAN POPUP
   ================================================================ */
@keyframes trinityToastText {{
  from {{
    opacity: 0;
    transform: translateX(13px);
    filter: blur(3px);
  }}

  to {{
    opacity: 1;
    transform: translateX(0);
    filter: blur(0);
  }}
}}


/* ================================================================
   AKSESIBILITAS
   Animasi diminimalkan jika pengguna mematikan animasi dari perangkat.
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
    """Tampilkan toast sukses selama tujuh detik."""

    # "long" membuat elemen toast Streamlit tersedia cukup lama.
    # CSS di atas menyelesaikan animasinya tepat pada detik ketujuh.
    try:
        st.toast(
            pesan,
            icon=":material/check:",
            duration="long",
        )
    except TypeError:
        # Kompatibilitas dengan versi Streamlit yang belum mempunyai
        # parameter duration.
        st.toast(
            pesan,
            icon=":material/check:",
        )
