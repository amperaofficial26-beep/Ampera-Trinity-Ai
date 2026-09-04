# -*- coding: utf-8 -*-
"""
LOADING KHUSUS PEMBUATAN KODE / FILE.
Menggunakan animasi CSS murni (tanpa JavaScript) agar kompatibel dengan st.markdown.
Durasi total sekitar 25 detik.
"""

from __future__ import annotations

import html

import streamlit as st

# ============================================================================
# PENGATURAN — sesuaikan daftar teks dan warna di sini
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

# Durasi per tampilan teks (detik) - total durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
DURASI_PER_TEKS = 2.8   # 2.8 * 9 = 25.2 detik (total ~25 detik)

WARNA_AKSEN = "#3C3489"          # warna titik & bar
WARNA_TEKS_REDUP = "#6B6172"
LEBAR_MAKS_PX = 460
# ============================================================================

def inject_code_loading_css() -> None:
    """Suntikkan CSS untuk loader. Dipanggil sekali sebelum loader dipakai."""
    total_durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
    css = f"""
<style>
.cl-loader {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    color: {WARNA_TEKS_REDUP};
    padding: 1rem 0;
    max-width: {LEBAR_MAKS_PX}px;
    animation: clFadeIn 0.35s ease both;
}}
@keyframes clFadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.cl-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {WARNA_AKSEN};
    display: inline-block;
    flex-shrink: 0;
    animation: clDotPulse 1.2s ease-in-out infinite;
}}
@keyframes clDotPulse {{
    0%, 100% {{ opacity: 0.3; transform: scale(0.8); }}
    50%     {{ opacity: 1;   transform: scale(1.2); }}
}}
.cl-text-wrap {{
    position: relative;
    height: 1.4em;
    overflow: hidden;
    flex: 1;
}}
.cl-text {{
    position: absolute;
    left: 0;
    top: 0;
    white-space: nowrap;
    opacity: 0;
    animation: clTextCycle {total_durasi}s linear infinite;
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
    position: relative;
    height: 2px;
    background: #E2D6C1;
    border-radius: 99px;
    overflow: hidden;
    margin-top: 4px;
}
.cl-fill {
    height: 100%;
    width: 30%;
    border-radius: 99px;
    background: """ + WARNA_AKSEN + """;
    animation: clBarRun 1.8s ease-in-out infinite;
}
@keyframes clBarRun {
    0%   { margin-left: -30%; }
    100% { margin-left: 100%; }
}
.cl-filename {
    font-size: 0.7rem;
    color: #A095AC;
    text-align: right;
    margin-top: 2px;
}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader statis dengan animasi CSS. Render SEKALI saja."""
    if done:
        # Tampilan selesai: titik hijau, teks "Selesai", nama file
        return f'''
<div class="cl-loader">
  <span class="cl-dot" style="animation: none; background: #4CAF50;"></span>
  <span style="font-weight: 500; color: #2C1F33;">Selesai</span>
  <span style="font-size: 0.8rem; color: #8E8398;">{html.escape(nama_file or "Berkas siap")}</span>
</div>
'''
    # Mode loading
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
