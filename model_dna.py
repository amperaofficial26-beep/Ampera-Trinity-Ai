# -*- coding: utf-8 -*-
"""
POPOVER PEMILIH MODEL — tampilan "DNA DOUBLE HELIX".

Konsep:
  - Bagian atas popover: untai DNA beranimasi — dua untai titik (emas & krem)
    saling silang naik-turun seperti heliks yang berputar, dihubungkan
    "anak tangga" basa. Murni CSS, tanpa gambar/JS.
  - Daftar model di bawahnya: tiap model = SATU ANAK TANGGA DNA (dua titik
    basa kiri + garis pasangan), tersambung tulang punggung ke bawah.
  - Model aktif: basanya menyala emas & berdenyut.
  - Tema gelap HANYA untuk popover ini (scoped pakai :has(.dna-wrap)).

Dipakai chat_handlers.py:
    from model_dna import DNA_CSS, dna_header_html, active_node_css

>>> ATUR WARNA & UKURAN DI SINI <<<
"""

from __future__ import annotations

import html

# ============================================================================
# PENGATURAN
# ============================================================================
WARNA_LATAR = "#000000"      # latar popover (ungu ruang angkasa)
WARNA_GARIS = "#FFFFFF"      # garis tepi popover & node
WARNA_AKSEN = "#E8B04B"      # emas: untai 1, basa aktif, glow
WARNA_UNTAI2 = "#EDE2D1"     # krem: untai 2
WARNA_TEKS = "#FFFFFF"       # teks utama
WARNA_REDUP = "#FFFFFF"      # teks deskripsi
TINGGI_DNA_PX = 130          # tinggi area animasi DNA
JUMLAH_KOLOM = 11            # jumlah "anak tangga" heliks di header
PERIODE_S = 2.8              # 1 putaran heliks (detik)


def _kolom_css() -> str:
    """Delay bertingkat per kolom supaya gelombangnya membentuk heliks."""
    aturan = []
    for i in range(1, JUMLAH_KOLOM + 1):
        d = -(i - 1) * (PERIODE_S / JUMLAH_KOLOM)
        aturan.append(
            f".dna-col:nth-child({i}) .da{{animation-delay:{d:.2f}s;}}"
            f".dna-col:nth-child({i}) .db{{animation-delay:{d - PERIODE_S / 2:.2f}s;}}"
            f".dna-col:nth-child({i})::before{{animation-delay:{d:.2f}s;}}"
        )
    return "".join(aturan)


# ============================================================================
# CSS — heliks DNA + node basa (di-inject sekali di dalam popover)
# ============================================================================
DNA_CSS = (
    "<style>"
    # ---- tema gelap KHUSUS popover yang berisi .dna-wrap ------------------
    "[data-testid='stPopoverBody']:has(.dna-wrap){"
    f"background:{WARNA_LATAR}!important;"
    f"border:1px solid {WARNA_GARIS}!important;"
    "border-radius:18px!important;min-width:330px!important;}"
    # ---- panggung DNA -----------------------------------------------------
    ".dna-wrap{position:relative;width:100%;"
    f"height:{TINGGI_DNA_PX}px;margin:2px 0 10px;"
    "display:flex;flex-direction:column;align-items:center;"
    "justify-content:center;overflow:hidden;border-radius:14px;"
    "background:"
    "radial-gradient(1px 1px at 18% 30%,rgba(255,255,255,.35),transparent),"
    "radial-gradient(1px 1px at 76% 22%,rgba(255,255,255,.25),transparent),"
    "radial-gradient(1.5px 1.5px at 62% 74%,rgba(255,255,255,.3),transparent),"
    "radial-gradient(1px 1px at 34% 82%,rgba(255,255,255,.2),transparent);}"
    # ---- heliks: kolom-kolom titik silang ----------------------------------
    ".dna-helix{display:flex;gap:13px;height:64px;margin-bottom:10px;}"
    ".dna-col{position:relative;width:9px;height:64px;}"
    # anak tangga (garis penghubung dua basa) — ikut "bernapas"
    ".dna-col::before{content:'';position:absolute;left:4px;top:6px;bottom:6px;"
    "width:1.5px;background:linear-gradient("
    "rgba(232,176,75,.45),rgba(237,226,209,.25));"
    f"animation:dnaBar {PERIODE_S}s ease-in-out infinite;}}"
    # dua basa: emas & krem, bertukar posisi atas-bawah (fase beda 180 derajat)
    ".dna-col .da,.dna-col .db{position:absolute;left:0;width:9px;height:9px;"
    f"border-radius:50%;animation:dnaWave {PERIODE_S}s ease-in-out infinite;}}"
    f".dna-col .da{{background:{WARNA_AKSEN};"
    "box-shadow:0 0 7px rgba(232,176,75,.85);}"
    f".dna-col .db{{background:{WARNA_UNTAI2};"
    "box-shadow:0 0 6px rgba(237,226,209,.6);}"
    # gelombang: turun-naik + membesar-mengecil (kesan depan/belakang)
    "@keyframes dnaWave{"
    "0%{top:0;transform:scale(1.15);z-index:2;opacity:1;}"
    "50%{top:55px;transform:scale(.72);z-index:1;opacity:.65;}"
    "100%{top:0;transform:scale(1.15);z-index:2;opacity:1;}}"
    "@keyframes dnaBar{0%,100%{opacity:.9;}50%{opacity:.35;}}"
    + _kolom_css() +
    # ---- label model aktif di bawah heliks ---------------------------------
    ".dna-title{text-align:center;"
    f"color:{WARNA_TEKS};font-size:12px;font-weight:700;letter-spacing:.12em;"
    "text-transform:uppercase;}"
    f".dna-title small{{display:block;color:{WARNA_REDUP};font-weight:500;"
    "letter-spacing:0;text-transform:none;font-size:11px;margin-top:1px;}"
    # ---- DAFTAR MODEL = ANAK TANGGA DNA ------------------------------------
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']{"
    "position:relative;margin:0 0 6px!important;}"
    # tombol: kartu gelap, ruang kiri untuk pasangan basa
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_'] button{"
    "width:100%!important;text-align:left!important;"
    "background:rgba(255,255,255,.045)!important;"
    f"border:1px solid {WARNA_GARIS}!important;border-radius:12px!important;"
    f"color:{WARNA_TEKS}!important;padding:8px 12px 8px 38px!important;"
    "box-shadow:none!important;transition:all .18s ease!important;}"
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_'] button:hover{"
    f"border-color:{WARNA_AKSEN}!important;"
    "box-shadow:0 0 12px rgba(232,176,75,.35)!important;"
    "transform:translateX(3px)!important;}"
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_'] button p{"
    f"color:{WARNA_TEKS}!important;}}"
    # pasangan basa di kiri: titik emas + titik krem bertumpuk
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']::before{"
    "content:'';position:absolute;left:14px;top:calc(50% - 9px);"
    f"width:7px;height:7px;border-radius:50%;background:{WARNA_AKSEN};"
    "opacity:.75;z-index:2;transition:all .18s ease;}"
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_'] > div::before{"
    "content:'';position:absolute;left:14px;top:calc(50% + 2px);"
    f"width:7px;height:7px;border-radius:50%;background:{WARNA_UNTAI2};"
    "opacity:.55;z-index:2;transition:all .18s ease;}"
    # tulang punggung penghubung antar anak tangga (atas -> bawah)
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']::after{"
    "content:'';position:absolute;left:17px;top:calc(50% + 10px);height:16px;"
    "width:1.5px;background:linear-gradient("
    "rgba(232,176,75,.45),rgba(237,226,209,.10));z-index:1;}"
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']:last-child::after{"
    "display:none;}"
    # hover: kedua basa menyala
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']:hover::before{"
    "opacity:1;box-shadow:0 0 8px rgba(232,176,75,.9);}"
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='model_row_']:hover > div::before{"
    "opacity:1;box-shadow:0 0 8px rgba(237,226,209,.8);}"
    # ---- badge Premium versi tema gelap (menimpa gaya terang styles.py) ----
    "[data-testid='stPopoverBody']:has(.dna-wrap) [class*='_premium']::after{"
    "content:'\\2726 Premium';"  # ✦ Premium
    f"color:{WARNA_AKSEN}!important;"
    "background:rgba(232,176,75,.12)!important;"
    "border:1px solid rgba(232,176,75,.45)!important;"
    "top:4px!important;right:6px!important;height:auto!important;"
    "width:auto!important;left:auto!important;"
    "font-size:0.55rem!important;font-weight:700!important;"
    "border-radius:999px!important;padding:1px 7px!important;"
    "position:absolute!important;z-index:3!important;"
    "background-image:none!important;}"
    "</style>"
)


# ============================================================================
# HTML
# ============================================================================
def dna_header_html(nama_aktif: str, desc_aktif: str = "") -> str:
    """Panggung DNA: heliks beranimasi + label model aktif."""
    kolom = "".join(
        '<div class="dna-col"><span class="da"></span><span class="db"></span></div>'
        for _ in range(JUMLAH_KOLOM)
    )
    sub = f"<small>{html.escape(desc_aktif)}</small>" if desc_aktif else ""
    return (
        '<div class="dna-wrap">'
        f'<div class="dna-helix">{kolom}</div>'
        f'<div class="dna-title">{html.escape(nama_aktif)}{sub}</div>'
        "</div>"
    )


def active_node_css(row_key: str) -> str:
    """CSS kecil untuk MENYALAKAN pasangan basa model yang sedang aktif."""
    return (
        "<style>"
        f"[data-testid='stPopoverBody']:has(.dna-wrap) .st-key-{row_key}::before{{"
        "opacity:1!important;box-shadow:0 0 10px rgba(232,176,75,1)!important;"
        "animation:basePulse 1.6s ease-in-out infinite;}"
        f"[data-testid='stPopoverBody']:has(.dna-wrap) .st-key-{row_key} > div::before{{"
        "opacity:1!important;box-shadow:0 0 10px rgba(237,226,209,.9)!important;"
        "animation:basePulse 1.6s ease-in-out infinite .8s;}"
        f"[data-testid='stPopoverBody']:has(.dna-wrap) .st-key-{row_key} button{{"
        f"border-color:{WARNA_AKSEN}!important;"
        "background:rgba(232,176,75,.08)!important;}"
        "@keyframes basePulse{0%,100%{transform:scale(1);}50%{transform:scale(1.4);}}"
        "</style>"
    )
