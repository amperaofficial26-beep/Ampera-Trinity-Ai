# -*- coding: utf-8 -*-
"""
LOADING KHUSUS PEMBUATAN KODE / FILE.
Menggunakan CSS dengan class unik (tl-*) dan inline style untuk memastikan
tampil rapi tanpa bentrok dengan CSS lama. Durasi total ~25 detik.
"""

from __future__ import annotations

import html

import streamlit as st

# ============================================================================
# PENGATURAN — ubah di sini sesuai keinginan
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

DURASI_PER_TEKS = 2.8   # total = 2.8 * 9 = 25.2 detik
WARNA_AKSEN = "#3C3489"
WARNA_TEKS_REDUP = "#6B6172"
LEBAR_MAKS_PX = 460
# ============================================================================

def inject_code_loading_css() -> None:
    """Suntikkan CSS untuk loader. Dipanggil SEKALI sebelum loader dipakai."""
    total_durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
    css = f"""
<style>
/* ===== LOADER TRINITY UNIK (tl-*) ===== */
.tl-loader {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    color: {WARNA_TEKS_REDUP} !important;
    padding: 0.8rem 0 !important;
    max-width: {LEBAR_MAKS_PX}px !important;
    animation: tlFadeIn 0.35s ease both !important;
}}
@keyframes tlFadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.tl-dot {{
    width: 7px !important;
    height: 7px !important;
    border-radius: 50% !important;
    background: {WARNA_AKSEN} !important;
    display: inline-block !important;
    flex-shrink: 0 !important;
    animation: tlDotPulse 1.2s ease-in-out infinite !important;
}}
@keyframes tlDotPulse {{
    0%, 100% {{ opacity: 0.3; transform: scale(0.8); }}
    50%     {{ opacity: 1;   transform: scale(1.2); }}
}}
.tl-text-wrap {{
    position: relative !important;
    height: 1.4em !important;
    overflow: hidden !important;
    flex: 1 !important;
}}
.tl-text {{
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    white-space: nowrap !important;
    opacity: 0 !important;
    animation: tlTextCycle {total_durasi}s linear infinite !important;
}}
"""
    for i, _ in enumerate(TEKS_TAHAP):
        delay = i * DURASI_PER_TEKS
        css += f".tl-text:nth-child({i+1}) {{ animation-delay: {delay}s; }}\n"

    css += f"""
@keyframes tlTextCycle {{
    0%   {{ opacity: 0; transform: translateY(4px); }}
    4%   {{ opacity: 1; transform: translateY(0); }}
    20%  {{ opacity: 1; transform: translateY(0); }}
    24%  {{ opacity: 0; transform: translateY(-4px); }}
    100% {{ opacity: 0; }}
}}
.tl-bar {{
    position: relative !important;
    height: 2px !important;
    background: #E2D6C1 !important;
    border-radius: 99px !important;
    overflow: hidden !important;
    margin-top: 4px !important;
}}
.tl-fill {{
    height: 100% !important;
    width: 30% !important;
    border-radius: 99px !important;
    background: {WARNA_AKSEN} !important;
    animation: tlBarRun 1.8s ease-in-out infinite !important;
}}
@keyframes tlBarRun {{
    0%   {{ margin-left: -30%; }}
    100% {{ margin-left: 100%; }}
}}
.tl-filename {{
    font-size: 0.7rem !important;
    color: #A095AC !important;
    text-align: right !important;
    margin-top: 2px !important;
}}
.tl-loader.tl-done .tl-dot {{
    animation: none !important;
    background: #4CAF50 !important;
}}
.tl-loader.tl-done .tl-text {{
    animation: none !important;
    opacity: 0 !important;
}}
.tl-loader.tl-done .tl-text:first-child {{
    opacity: 1 !important;
}}
.tl-loader.tl-done .tl-fill {{
    animation: none !important;
    width: 100% !important;
    margin-left: 0 !important;
}}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader dengan class tl-*. Render SEKALI saja."""
    if done:
        return f'''
<div class="tl-loader tl-done">
  <span class="tl-dot"></span>
  <span style="font-weight: 500; color: #2C1F33;">Selesai</span>
  <span style="font-size: 0.8rem; color: #8E8398;">{html.escape(nama_file or "Berkas siap")}</span>
</div>
'''
    # Mode loading
    texts = ''.join(f'<span class="tl-text">{html.escape(t)}</span>' for t in TEKS_TAHAP)
    return f'''
<div class="tl-loader">
  <span class="tl-dot"></span>
  <div class="tl-text-wrap">
    {texts}
  </div>
  <div style="flex: 1; min-width: 0;">
    <div class="tl-bar"><div class="tl-fill"></div></div>
    <div class="tl-filename">{html.escape(nama_file or "menyiapkan berkas")}</div>
  </div>
</div>
'''
