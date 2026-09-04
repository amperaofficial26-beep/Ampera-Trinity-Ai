# -*- coding: utf-8 -*-
"""
LOADING KHUSUS PEMBUATAN KODE / FILE.
Menggunakan animasi CSS murni (tanpa JavaScript).
Durasi total sekitar 25 detik.
"""

from __future__ import annotations

import html

import streamlit as st

# ============================================================================
# PENGATURAN
# ============================================================================
TEKS_TAHAP = [
    "Menyalakan mode coding",
    "Menghitung  ∇·F = ρ/ε₀",
    "Merangkai  ⊗ ⊙ ⊚ ⊛",
    "Memproses  arr[42] processed",
    "KV cache [████████░░] 64%",
    "A:1234 >>> B:1189  Δ=45",
    "PPL: 85 [████████░░] BAD",
    "top-p: [████████░░] p=0.78",
    "hash: 0x3F2A",
]

DURASI_PER_TEKS = 2.8   # 2.8 * 9 = 25.2 detik
WARNA_AKSEN = "#3C3489"
WARNA_TEKS_REDUP = "#6B6172"
LEBAR_MAKS_PX = 460
# ============================================================================

def inject_code_loading_css() -> None:
    """Suntikkan CSS untuk loader. Dipanggil sekali sebelum loader dipakai."""
    total_durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
    css = f"""
<style>
/* Reset total gaya lama yang mungkin tersisa */
.cl-loader, .cl-loader * {{
    all: unset;
    display: revert;
    box-sizing: border-box;
}}
.cl-loader {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    color: {WARNA_TEKS_REDUP} !important;
    padding: 1rem 0 !important;
    max-width: {LEBAR_MAKS_PX}px !important;
    animation: clFadeIn 0.35s ease both !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
}}
@keyframes clFadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.cl-dot {{
    width: 7px !important;
    height: 7px !important;
    border-radius: 50% !important;
    background: {WARNA_AKSEN} !important;
    display: inline-block !important;
    flex-shrink: 0 !important;
    animation: clDotPulse 1.2s ease-in-out infinite !important;
}}
@keyframes clDotPulse {{
    0%, 100% {{ opacity: 0.3; transform: scale(0.8); }}
    50%     {{ opacity: 1;   transform: scale(1.2); }}
}}
.cl-text-wrap {{
    position: relative !important;
    height: 1.4em !important;
    overflow: hidden !important;
    flex: 1 !important;
}}
.cl-text {{
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    white-space: nowrap !important;
    opacity: 0 !important;
    animation: clTextCycle {total_durasi}s linear infinite !important;
}}
"""
    for i, _ in enumerate(TEKS_TAHAP):
        delay = i * DURASI_PER_TEKS
        css += f".cl-text:nth-child({i+1}) {{ animation-delay: {delay}s; }}\n"

    css += """
@keyframes clTextCycle {
    0%   { opacity: 0; transform: translateY(4px); }
    4%   { opacity: 1; transform: translateY(0); }
    20%  { opacity: 1; transform: translateY(0); }
    24%  { opacity: 0; transform: translateY(-4px); }
    100% { opacity: 0; }
}
.cl-bar {
    position: relative !important;
    height: 2px !important;
    background: #E2D6C1 !important;
    border-radius: 99px !important;
    overflow: hidden !important;
    margin-top: 4px !important;
}
.cl-fill {
    height: 100% !important;
    width: 30% !important;
    border-radius: 99px !important;
    background: """ + WARNA_AKSEN + """ !important;
    animation: clBarRun 1.8s ease-in-out infinite !important;
}
@keyframes clBarRun {
    0%   { margin-left: -30%; }
    100% { margin-left: 100%; }
}
.cl-filename {
    font-size: 0.7rem !important;
    color: #A095AC !important;
    text-align: right !important;
    margin-top: 2px !important;
}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader statis dengan animasi CSS. Render SEKALI saja."""
    if done:
        return f'''
<div class="cl-loader">
  <span class="cl-dot" style="animation: none; background: #4CAF50;"></span>
  <span style="font-weight: 500; color: #2C1F33;">Selesai</span>
  <span style="font-size: 0.8rem; color: #8E8398;">{html.escape(nama_file or "Berkas siap")}</span>
</div>
'''
    texts = ''.join(f'<span class="cl-text">{html.escape(t)}</span>' for t in TEKS_TAHAP)
    return f'''
<div class="cl-loader">
  <span class="cl-dot"></span>
  <div class="cl-text-wrap">
    {texts}
  </div>
  <div style="flex: 1; min-width: 0;">
    <div class="cl-bar"><div class="cl-fill"></div></div>
    <div class="cl-filename">{html.escape(nama_file or "menyiapkan berkas")}</div>
  </div>
</div>
'''
