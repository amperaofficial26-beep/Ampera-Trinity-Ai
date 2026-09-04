# -*- coding: utf-8 -*-
"""
LOADING PEMBUATAN KODE / FILE.
Menggunakan inline style + CSS di dalam HTML.
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

DURASI_PER_TEKS = 2.8   # 2.8 * 9 = 25.2 detik
WARNA_AKSEN = "#3C3489"
WARNA_TEKS_REDUP = "#6B6172"
LEBAR_MAKS_PX = 460
# ============================================================================

def inject_code_loading_css() -> None:
    """Kosongkan karena CSS sudah ada di HTML."""
    pass

def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    """HTML loader dengan CSS internal."""
    if done:
        return f'''
<div style="display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;font-size:14px;color:{WARNA_TEKS_REDUP};padding:0.8rem 0;animation:tlFadeIn 0.35s ease both;max-width:{LEBAR_MAKS_PX}px;">
  <style>
    /* Sembunyikan semua loader lama */
    .cl-box, .cl-loader, .cl-dot, .cl-text-wrap, .cl-stage, .cl-lines, .cl-bar, .cl-fill,
    .cl-top, .cl-ic, .cl-name, .cl-line, .cl-filename {{ display: none !important; }}
    @keyframes tlFadeIn {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}
  </style>
  <span style="width:7px;height:7px;border-radius:50%;background:#4CAF50;display:inline-block;flex-shrink:0;"></span>
  <span style="font-weight:500;color:#2C1F33;">Selesai</span>
  <span style="font-size:0.8rem;color:#8E8398;">{html.escape(nama_file or "Berkas siap")}</span>
</div>
'''

    total_durasi = DURASI_PER_TEKS * len(TEKS_TAHAP)
    # Bangun CSS delay untuk tiap teks
    delays = ""
    for i in range(len(TEKS_TAHAP)):
        delays += f".tl-text-{i} {{ animation-delay: {i * DURASI_PER_TEKS}s; }}\n"

    # Bangun elemen teks
    texts = ''.join(
        f'<span class="tl-text tl-text-{i}">{html.escape(t)}</span>'
        for i, t in enumerate(TEKS_TAHAP)
    )

    return f'''
<div style="display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;font-size:14px;color:{WARNA_TEKS_REDUP};padding:0.8rem 0;max-width:{LEBAR_MAKS_PX}px;animation:tlFadeIn 0.35s ease both;">
  <style>
    /* Sembunyikan semua loader lama */
    .cl-box, .cl-loader, .cl-dot, .cl-text-wrap, .cl-stage, .cl-lines, .cl-bar, .cl-fill,
    .cl-top, .cl-ic, .cl-name, .cl-line, .cl-filename {{ display: none !important; }}
    @keyframes tlFadeIn {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @keyframes tlDotPulse {{ 0%,100% {{ opacity:0.3; transform:scale(0.8); }} 50% {{ opacity:1; transform:scale(1.2); }} }}
    @keyframes tlTextCycle {{
      0%   {{ opacity:0; transform:translateY(4px); }}
      4%   {{ opacity:1; transform:translateY(0); }}
      20%  {{ opacity:1; transform:translateY(0); }}
      24%  {{ opacity:0; transform:translateY(-4px); }}
      100% {{ opacity:0; }}
    }}
    @keyframes tlBarRun {{
      0%   {{ margin-left:-30%; }}
      100% {{ margin-left:100%; }}
    }}
    .tl-text {{
      position: absolute;
      left: 0;
      top: 0;
      white-space: nowrap;
      opacity: 0;
      animation: tlTextCycle {total_durasi}s linear infinite;
    }}
    {delays}
  </style>
  <span style="width:7px;height:7px;border-radius:50%;background:{WARNA_AKSEN};display:inline-block;flex-shrink:0;animation:tlDotPulse 1.2s ease-in-out infinite;"></span>
  <div style="position:relative;height:1.4em;overflow:hidden;flex:1;">
    {texts}
  </div>
  <div style="flex:1;min-width:0;">
    <div style="position:relative;height:2px;background:#E2D6C1;border-radius:99px;overflow:hidden;margin-top:4px;">
      <span style="display:block;height:100%;width:30%;border-radius:99px;background:{WARNA_AKSEN};animation:tlBarRun 1.8s ease-in-out infinite;"></span>
    </div>
    <div style="font-size:0.7rem;color:#A095AC;text-align:right;margin-top:2px;">{html.escape(nama_file or "menyiapkan berkas")}</div>
  </div>
</div>
'''
