# -*- coding: utf-8 -*-
"""
POPOVER PEMILIH MODEL — tampilan "AI ORBIT + NEURAL NETWORK".

Konsep:
  - Bagian atas popover: INTI (logo Trinity) berdenyut dengan glow, dikelilingi
    3 cincin orbit yang berputar beda arah/kecepatan + titik "elektron" menyala.
  - Daftar model di bawahnya: tiap model = NODE neural network (titik sinaps
    bercahaya) yang tersambung garis sinaps dari atas ke bawah.
  - Tema gelap (ungu ruang angkasa) HANYA untuk popover ini — popover lain
    (menu +, preview file) tidak ikut berubah (pakai selector :has()).

Dipakai chat_handlers.py:
    from model_orbit import ORBIT_CSS, orbit_header_html, active_node_css

>>> ATUR WARNA & UKURAN DI SINI <<<
"""

from __future__ import annotations

import html

try:
    from logo import LOGO_B64
except Exception:
    LOGO_B64 = ""

# ============================================================================
# PENGATURAN
# ============================================================================
WARNA_LATAR = "#DBCEB9"      # latar popover (ungu ruang angkasa)
WARNA_GARIS = "#E0D2BB"      # garis tepi popover & node
WARNA_AKSEN = "#E2D6C1"      # emas: elektron, node aktif, glow
WARNA_TEKS = "#E0D2BB"       # teks utama
WARNA_REDUP = "#E0D2BB"      # teks deskripsi
TINGGI_ORBIT_PX = 150        # tinggi area animasi orbit


# ============================================================================
# CSS — orbit + node neural (di-inject sekali di dalam popover)
# ============================================================================
ORBIT_CSS = (
    "<style>"
    # ---- tema gelap KHUSUS popover yang berisi .orbit-wrap ----------------
    f"[data-testid='stPopoverBody']:has(.orbit-wrap){{"
    f"background:{WARNA_LATAR}!important;"
    f"border:1px solid {WARNA_GARIS}!important;"
    "border-radius:18px!important;min-width:330px!important;}"
    # ---- panggung orbit ---------------------------------------------------
    ".orbit-wrap{position:relative;width:100%;"
    f"height:{TINGGI_ORBIT_PX}px;margin:2px 0 10px;"
    "display:flex;align-items:center;justify-content:center;overflow:hidden;"
    # bintang-bintang halus di latar (murni gradient, tanpa gambar)
    "background:"
    "radial-gradient(1px 1px at 18% 30%,rgba(255,255,255,.35),transparent),"
    "radial-gradient(1px 1px at 76% 22%,rgba(255,255,255,.25),transparent),"
    "radial-gradient(1.5px 1.5px at 62% 74%,rgba(255,255,255,.3),transparent),"
    "radial-gradient(1px 1px at 34% 82%,rgba(255,255,255,.2),transparent);"
    "border-radius:14px;}"
    # ---- inti (logo Trinity) berdenyut + glow -----------------------------
    ".orbit-core{position:absolute;width:40px;height:40px;z-index:3;"
    "animation:corePulse 2.4s ease-in-out infinite;}"
    ".orbit-core img{width:100%;height:100%;object-fit:contain;display:block;}"
    ".orbit-core .core-fallback{font-size:26px;line-height:40px;display:block;"
    f"text-align:center;color:{WARNA_AKSEN};}}"
    "@keyframes corePulse{"
    f"0%,100%{{transform:scale(1);filter:drop-shadow(0 0 6px rgba(232,176,75,.5));}}"
    f"50%{{transform:scale(1.15);filter:drop-shadow(0 0 16px rgba(232,176,75,.9));}}}}"
    # ---- cincin orbit (3 lapis, arah & kecepatan beda) --------------------
    ".orbit-ring{position:absolute;border-radius:50%;"
    f"border:1px dashed rgba(232,176,75,.28);}}"
    ".ring1{width:70px;height:70px;animation:orbitSpin 6s linear infinite;}"
    ".ring2{width:110px;height:110px;animation:orbitSpin 11s linear infinite reverse;}"
    ".ring3{width:146px;height:146px;animation:orbitSpin 17s linear infinite;}"
    "@keyframes orbitSpin{to{transform:rotate(360deg);}}"
    # ---- elektron menyala di tiap cincin ----------------------------------
    ".orbit-nd{position:absolute;width:8px;height:8px;border-radius:50%;"
    f"background:{WARNA_AKSEN};box-shadow:0 0 8px rgba(232,176,75,.95);}}"
    ".ring1 .orbit-nd{top:-4px;left:50%;}"
    ".ring2 .orbit-nd.a{top:-4px;left:50%;}"
    ".ring2 .orbit-nd.b{bottom:6px;left:8px;width:6px;height:6px;opacity:.8;}"
    ".ring3 .orbit-nd{top:30%;right:-4px;}"
    # ---- label model aktif di bawah orbit ---------------------------------
    ".orbit-title{position:absolute;bottom:8px;left:0;right:0;text-align:center;"
    f"color:{WARNA_TEKS};font-size:12px;font-weight:700;letter-spacing:.12em;"
    "text-transform:uppercase;}"
    f".orbit-title small{{display:block;color:{WARNA_REDUP};font-weight:500;"
    "letter-spacing:0;text-transform:none;font-size:11px;margin-top:1px;}"
    # ---- DAFTAR MODEL = NODE NEURAL NETWORK -------------------------------
    # baris node
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_']{"
    "position:relative;margin:0 0 6px!important;}"
    # tombolnya: kartu gelap, teks kiri, ruang untuk titik sinaps
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_'] button{"
    "width:100%!important;text-align:left!important;"
    "background:rgba(255,255,255,.045)!important;"
    f"border:1px solid {WARNA_GARIS}!important;border-radius:12px!important;"
    f"color:{WARNA_TEKS}!important;padding:8px 12px 8px 32px!important;"
    "box-shadow:none!important;transition:all .18s ease!important;}"
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_'] button:hover{"
    f"border-color:{WARNA_AKSEN}!important;"
    "box-shadow:0 0 12px rgba(232,176,75,.35)!important;"
    "transform:translateX(3px)!important;}"
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_'] button p{"
    f"color:{WARNA_TEKS}!important;}}"
    # titik sinaps di kiri tiap node
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_']::before{"
    "content:'';position:absolute;left:13px;top:50%;transform:translateY(-50%);"
    f"width:8px;height:8px;border-radius:50%;background:{WARNA_REDUP};"
    "z-index:2;transition:all .18s ease;}"
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_']:hover::before{"
    f"background:{WARNA_AKSEN};box-shadow:0 0 8px rgba(232,176,75,.9);}}"
    # garis sinaps penghubung antar node (atas -> bawah)
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_']::after{"
    "content:'';position:absolute;left:16px;top:calc(50% + 7px);height:14px;"
    "width:1.5px;background:linear-gradient(rgba(232,176,75,.45),rgba(232,176,75,.08));"
    "z-index:1;}"
    "[data-testid='stPopoverBody']:has(.orbit-wrap) [class*='model_row_']:last-child::after{"
    "display:none;}"
    "</style>"
)


# ============================================================================
# HTML
# ============================================================================
def orbit_header_html(nama_aktif: str, desc_aktif: str = "") -> str:
    """Panggung orbit: inti Trinity + 3 cincin + elektron + label model aktif."""
    if LOGO_B64:
        core = f'<img src="data:image/png;base64,{LOGO_B64}" alt="Trinity"/>'
    else:
        core = '<span class="core-fallback">&#10035;</span>'
    sub = f"<small>{html.escape(desc_aktif)}</small>" if desc_aktif else ""
    return (
        '<div class="orbit-wrap">'
        f'<div class="orbit-core">{core}</div>'
        '<div class="orbit-ring ring1"><span class="orbit-nd"></span></div>'
        '<div class="orbit-ring ring2"><span class="orbit-nd a"></span>'
        '<span class="orbit-nd b"></span></div>'
        '<div class="orbit-ring ring3"><span class="orbit-nd"></span></div>'
        f'<div class="orbit-title">{html.escape(nama_aktif)}{sub}</div>'
        "</div>"
    )


def active_node_css(row_key: str) -> str:
    """CSS kecil untuk MENYALAKAN titik sinaps model yang sedang aktif."""
    return (
        "<style>"
        f"[data-testid='stPopoverBody']:has(.orbit-wrap) .st-key-{row_key}::before{{"
        f"background:{WARNA_AKSEN}!important;"
        "box-shadow:0 0 10px rgba(232,176,75,1)!important;"
        "animation:ndPulse 1.6s ease-in-out infinite;}"
        f"[data-testid='stPopoverBody']:has(.orbit-wrap) .st-key-{row_key} button{{"
        f"border-color:{WARNA_AKSEN}!important;"
        "background:rgba(232,176,75,.08)!important;}"
        "@keyframes ndPulse{0%,100%{transform:translateY(-50%) scale(1);}"
        "50%{transform:translateY(-50%) scale(1.35);}}"
        "</style>"
    )
