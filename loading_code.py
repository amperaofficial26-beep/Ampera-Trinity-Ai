# -*- coding: utf-8 -*-
"""
LOADING KHUSUS PEMBUATAN KODE / FILE.
Menggunakan inline style + CSS keyframes agar tampil rapi.
Durasi total ~25 detik.
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

DURASI_PER_TEKS = 2.8   # total = 2.8 * 9 = 25.2 detik
WARNA_AKSEN = "#3C3489"
WARNA_TEKS_REDUP = "#6B6172"
LEBAR_MAKS_PX = 460
# ============================================================================

def inject_code_loading_css() -> None:
    """Suntikkan CSS keyframes dan aturan untuk menyembunyikan loader lama."""
    total_durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
    css = f"""
<style>
/* ===== SEMBUNYIKAN LOADER LAMA (jika masih ada) ===== */
.cl-box, .cl-loader, .cl-dot, .cl-text-wrap, .cl-stage, .cl-lines, .cl-bar, .cl-fill,
.cl-top, .cl-ic, .cl-name, .cl-line {{
    display: none !important;
}}

/* ===== LOADER BARU DENGAN KEYFRAMES ===== */
@keyframes tlFadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes tlDotPulse {{
    0%, 100% {{ opacity: 0.3; transform: scale(0.8); }}
    50%     {{ opacity: 1;   transform: scale(1.2); }}
}}
@keyframes tlTextCycle {{
    0%   {{ opacity: 0; transform: translateY(4px); }}
    4%   {{ opacity: 1; transform: translateY(0); }}
    20%  {{ opacity: 1; transform: translateY(0); }}
    24%  {{ opacity: 0; transform: translateY(-4px); }}
    100% {{ opacity: 0; }}
}}
@keyframes tlBarRun {{
    0%   {{ margin-left: -30%; }}
    100% {{ margin-left: 100%; }}
}}

/* Aturan delay untuk tiap teks */
"""
    for i, _ in enumerate(TEKS_TAHAP):
        delay = i * DURASI_PER_TEKS
        css += f".tl-text-{i} {{ animation-delay: {delay}s; }}\n"

    css += """
/* Keadaan selesai */
.tl-loader.tl-done .tl-dot { animation: none !important; background: #4CAF50 !important; }
.tl-loader.tl-done .tl-text { animation: none !important; opacity: 0 !important; }
.tl-loader.tl-done .tl-text:first-child { opacity: 1 !important; }
.tl-loader.tl-done .tl-fill { animation: none !important; width: 100% !important; margin-left: 0 !important; }
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader dengan inline style dan class untuk animasi."""
    if done:
        return f'''
<div class="tl-loader tl-done" style="display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;font-size:14px;color:{WARNA_TEKS_REDUP};padding:0.8rem 0;animation:tlFadeIn 0.35s ease both;">
  <span class="tl-dot" style="width:7px;height:7px;border-radius:50%;background:#4CAF50;display:inline-block;flex-shrink:0;"></span>
  <span style="font-weight:500;color:#2C1F33;">Selesai</span>
  <span style="font-size:0.8rem;color:#8E8398;">{html.escape(nama_file or "Berkas siap")}</span>
</div>
'''

    # Bangun teks berganti dengan class individual
    texts = ''.join(
        f'<span class="tl-text tl-text-{i}" style="position:absolute;left:0;top:0;white-space:nowrap;opacity:0;animation:tlTextCycle {DURASI_PER_TEKS * len(TEKS_TAHAP)}s linear infinite;">{html.escape(t)}</span>'
        for i, t in enumerate(TEKS_TAHAP)
    )

    return f'''
<div class="tl-loader" style="display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;font-size:14px;color:{WARNA_TEKS_REDUP};padding:0.8rem 0;max-width:{LEBAR_MAKS_PX}px;animation:tlFadeIn 0.35s ease both;">
  <span class="tl-dot" style="width:7px;height:7px;border-radius:50%;background:{WARNA_AKSEN};display:inline-block;flex-shrink:0;animation:tlDotPulse 1.2s ease-in-out infinite;"></span>
  <div style="position:relative;height:1.4em;overflow:hidden;flex:1;">
    {texts}
  </div>
  <div style="flex:1;min-width:0;">
    <div style="position:relative;height:2px;background:#E2D6C1;border-radius:99px;overflow:hidden;margin-top:4px;">
      <span class="tl-fill" style="display:block;height:100%;width:30%;border-radius:99px;background:{WARNA_AKSEN};animation:tlBarRun 1.8s ease-in-out infinite;"></span>
    </div>
    <div style="font-size:0.7rem;color:#A095AC;text-align:right;margin-top:2px;">{html.escape(nama_file or "menyiapkan berkas")}</div>
  </div>
</div>
'''
