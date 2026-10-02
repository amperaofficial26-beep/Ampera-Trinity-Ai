# -*- coding: utf-8 -*-
"""
HALAMAN: TENTANG KAMI

Profil Ampera Official Group Indonesia — dibuat mengikuti desain referensi:
panel hero bergambar maskot "Aogi" + lencana AOG, lalu empat kartu
(tentang logo, produk kami, nilai & visi, serta kutipan penutup).

>>> SEMUA ISI TEKS HALAMAN DIATUR DI BAGIAN KONSTANTA DI BAWAH <<<
"""
from __future__ import annotations

import streamlit as st

from icons import mi
from logo import LOGO_B64
from maskot import MASKOT_URL
from ui_helpers import _page_footer

# ============================================================================
# >>> ISI HALAMAN — UBAH DI SINI <<<
# ============================================================================
NAMA_GRUP = "Ampera Official Group Indonesia"
SLOGAN = "Satu Visi, Banyak Karya, Untuk Masa Depan."
DESKRIPSI = (
    "Ampera Official Group Indonesia adalah sebuah grup kreatif yang "
    "berfokus pada pengembangan teknologi, desain, dan solusi digital "
    "untuk mendukung produktivitas, kreativitas, serta kemajuan bersama "
    "di era modern."
)
LOKASI = "Palembang - Indonesia"
DEVELOPER = "Pebrian Saputra"
NAMA_MASKOT = "Aogi"

# Tiga unsur yang diwakili logo Bintang Trinity.
UNSUR_LOGO = [
    (":material/palette:", "Desain",
     "Melambangkan kreativitas dan estetika."),
    (":material/favorite:", "Kenyamanan",
     "Memberikan pengalaman pengguna yang terbaik."),
    (":material/rocket_launch:", "Masa Depan",
     "Berorientasi pada inovasi dan teknologi."),
]

# Produk digital grup.
PRODUK = [
    (":material/edit_note:", "A. Scribe",
     "Aplikasi pencatat cerdas dengan AI."),
    (":material/auto_awesome:", "Ampera Upscale Studio",
     "Solusi peningkatan gambar berbasis AI."),
    (":material/star:", "Trinity Ai",
     "Asisten AI untuk produktivitas dan kreativitas."),
    (":material/brush:", "Ampera Desain",
     "Layanan desain kreatif untuk berbagai kebutuhan."),
]

# Nilai & visi.
NILAI = [
    (":material/lightbulb:", "Inovasi",
     "Selalu menghadirkan solusi terbaru dan relevan."),
    (":material/groups:", "Kolaborasi",
     "Bersama membangun ide menjadi karya nyata."),
    (":material/verified_user:", "Integritas",
     "Menjunjung tinggi kepercayaan dan kejujuran."),
    (":material/eco:", "Dampak Positif",
     "Memberikan manfaat nyata bagi pengguna dan masyarakat."),
]

KUTIPAN = ("Teknologi, Desain, dan Kreativitas untuk "
           "Masa Depan yang Lebih Baik.")


def _logo_img(kelas: str) -> str:
    if not LOGO_B64:
        return ""
    return (f'<img class="{kelas}" src="data:image/png;base64,{LOGO_B64}" '
            f'alt="Logo Trinity">')


def _kartu_kecil(ikon: str, judul: str, teks: str, kelas: str) -> str:
    return (f'<div class="{kelas}">'
            f'<span class="ab-mini-ic">{mi(ikon)}</span>'
            f'<span class="ab-mini-name">{judul}</span>'
            f'<span class="ab-mini-desc">{teks}</span>'
            "</div>")


def page_tentang() -> None:
    """Gambar halaman Tentang Kami."""
    # Penanda shell: halaman memakai lebar penuh & latar yang sama dengan
    # halaman "Tingkatkan paket" / "Dapatkan aplikasi".
    st.markdown('<div class="about-page-shell"></div>', unsafe_allow_html=True)

    # ---- HERO -------------------------------------------------------------
    st.markdown(
        '<div class="ab-hero">'
        '<div class="ab-hero-copy">'
        '<span class="ab-badge">Tentang Kami</span>'
        f"<h1>{NAMA_GRUP}</h1>"
        f'<p class="ab-slogan">{SLOGAN}</p>'
        f'<p class="ab-desc">{DESKRIPSI}</p>'
        '<div class="ab-chips">'
        f'<span class="ab-chip">{mi(":material/location_on:")}{LOKASI}</span>'
        f'<span class="ab-chip">{mi(":material/person:")}'
        f"Developer : {DEVELOPER}</span>"
        "</div>"
        "</div>"
        '<div class="ab-hero-art">'
        f'<img class="ab-maskot" src="{MASKOT_URL}" alt="Maskot {NAMA_MASKOT}">'
        f'<span class="ab-maskot-tag">{NAMA_MASKOT}'
        "<small>Our Mascot</small></span>"
        "</div>"
        '<div class="ab-hero-brand">'
        f'<span class="ab-brand-mark">{_logo_img("ab-brand-logo")}</span>'
        '<span class="ab-brand-name">AOG</span>'
        '<span class="ab-brand-sub">AMPERA OFFICIAL GROUP</span>'
        '<span class="ab-brand-sub2">INDONESIA</span>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ---- BARIS 1: logo aplikasi & produk ----------------------------------
    kiri, kanan = st.columns([1, 1.25], gap="medium")

    with kiri:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-head">'
            f'<span class="ab-head-ic">{_logo_img("ab-head-logo")}</span>'
            "<div><b>Tentang Logo Aplikasi</b>"
            "<i>Bintang Trinity</i></div>"
            "</div>"
            '<p class="ab-card-text">Logo aplikasi kami, Bintang Trinity, '
            "menggabungkan tiga elemen utama.</p>"
            '<div class="ab-mini-grid ab-mini-3">'
            + "".join(_kartu_kecil(i, j, t, "ab-mini")
                      for i, j, t in UNSUR_LOGO)
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with kanan:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-head">'
            f'<span class="ab-head-ic ab-head-ic-sq">'
            f'{mi(":material/grid_view:")}</span>'
            "<div><b>Produk Kami</b>"
            "<i>Beragam produk digital untuk mendukung kebutuhan Anda.</i>"
            "</div></div>"
            '<div class="ab-mini-grid ab-mini-4">'
            + "".join(_kartu_kecil(i, j, t, "ab-mini ab-mini-prod")
                      for i, j, t in PRODUK)
            + "</div></div>",
            unsafe_allow_html=True,
        )

    # ---- BARIS 2: nilai & kutipan -----------------------------------------
    kiri2, kanan2 = st.columns([1.25, 1], gap="medium")

    with kiri2:
        st.markdown(
            '<div class="ab-card">'
            '<div class="ab-card-head">'
            f'<span class="ab-head-ic ab-head-ic-sq">'
            f'{mi(":material/favorite:")}</span>'
            "<div><b>Nilai &amp; Visi Kami</b></div></div>"
            '<div class="ab-mini-grid ab-mini-4">'
            + "".join(_kartu_kecil(i, j, t, "ab-mini") for i, j, t in NILAI)
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with kanan2:
        st.markdown(
            '<div class="ab-quote">'
            '<div class="ab-quote-sky"></div>'
            '<div class="ab-quote-city"></div>'
            f'<p class="ab-quote-text">“{KUTIPAN}”</p>'
            f'<span class="ab-quote-by">— {NAMA_GRUP}</span>'
            "</div>",
            unsafe_allow_html=True,
        )

    _page_footer()
