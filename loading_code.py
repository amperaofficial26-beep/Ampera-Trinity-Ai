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
        return 

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
