# -*- coding: utf-8 -*-
"""Toast sukses Trinity: glow, logo beranimasi, lalu tanda centang."""
from __future__ import annotations

import streamlit as st

from logo import LOGO_B64


_DURASI_MS = 7000


def inject_toast_anim() -> None:
    """Pasang animasi untuk toast aplikasi (aman dipanggil setiap rerun)."""
    logo = (
        f'url("data:image/png;base64,{LOGO_B64}")'
        if LOGO_B64 else "none"
    )
    st.markdown(
        f"""
<style>
/* Toast Trinity: total tampil tepat 7 detik. */
[data-testid="stToast"] {{
  position: relative !important;
  min-height: 92px !important;
  padding: 18px 46px 18px 78px !important;
  border: 1px solid rgba(164, 120, 72, .28) !important;
  border-radius: 18px !important;
  background: rgba(255, 253, 249, .97) !important;
  box-shadow: 0 12px 38px rgba(77, 51, 25, .18),
              0 0 0 1px rgba(255,255,255,.8),
              0 0 28px rgba(206, 153, 87, .34) !important;
  overflow: hidden !important;
  animation: trinityToast7s {_DURASI_MS}ms cubic-bezier(.2,.8,.2,1) forwards !important;
}}

/* Sembunyikan ikon bawaan; ikon khusus dibuat lewat ::before/::after. */
[data-testid="stToast"] > div:first-child:not([data-testid="stMarkdownContainer"]),
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  opacity: 0 !important;
}}

/* Logo Trinity: timbul, meloncat pelan, lalu satu putaran. */
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
  filter: drop-shadow(0 4px 7px rgba(112, 72, 31, .30));
  animation: trinityLogoJadiCentang 2.35s cubic-bezier(.34,1.56,.64,1) forwards;
}}

/* Centang muncul persis setelah logo mengecil. */
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
  color: #fff;
  background: linear-gradient(145deg, #9a7046, #6f4d2e);
  box-shadow: 0 5px 14px rgba(105, 70, 37, .30), 0 0 14px rgba(190,137,75,.35);
  font: 700 21px/1 Arial, sans-serif;
  opacity: 0;
  transform: scale(.2) rotate(-35deg);
  animation: trinityCentangMasuk .55s 2.02s cubic-bezier(.34,1.56,.64,1) forwards;
}}

/* Tulisan menyusul sesudah kotak dan logo mulai muncul. */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] p {{
  animation: trinityToastText .6s .72s ease both !important;
}}

@keyframes trinityToast7s {{
  0%   {{ opacity:0; transform:translateY(16px) scale(.88); filter:brightness(1.25); }}
  7%   {{ opacity:1; transform:translateY(-3px) scale(1.025); }}
  12%  {{ transform:translateY(0) scale(1); }}
  88%  {{ opacity:1; transform:translateY(0) scale(1); }}
  100% {{ opacity:0; transform:translateY(-12px) scale(.97); visibility:hidden; }}
}}
@keyframes trinityLogoJadiCentang {{
  0%   {{ opacity:0; transform:translateY(13px) scale(.35) rotate(0deg); }}
  24%  {{ opacity:1; transform:translateY(-8px) scale(1.12) rotate(0deg); }}
  43%  {{ transform:translateY(2px) scale(.96) rotate(0deg); }}
  68%  {{ opacity:1; transform:translateY(-3px) scale(1.02) rotate(360deg); }}
  84%  {{ opacity:1; transform:scale(.92) rotate(360deg); }}
  100% {{ opacity:0; transform:scale(.12) rotate(405deg); }}
}}
@keyframes trinityCentangMasuk {{
  to {{ opacity:1; transform:scale(1) rotate(0deg); }}
}}
@keyframes trinityToastText {{
  from {{ opacity:0; transform:translateX(13px); filter:blur(3px); }}
  to   {{ opacity:1; transform:translateX(0); filter:blur(0); }}
}}
@media (prefers-reduced-motion: reduce) {{
  [data-testid="stToast"], [data-testid="stToast"]::before,
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
    """Tampilkan toast sukses; CSS menutup visualnya tepat setelah 7 detik."""
    # "long" membuat node Streamlit bertahan cukup lama; animasi CSS di atas
    # menghilangkannya tepat pada detik ke-7.
    try:
        st.toast(pesan, icon=":material/check:", duration="long")
    except TypeError:  # Kompatibel dengan Streamlit lama.
        st.toast(pesan, icon=":material/check:")
