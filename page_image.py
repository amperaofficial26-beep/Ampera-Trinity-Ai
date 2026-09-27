# -*- coding: utf-8 -*-
"""
HALAMAN: AI IMAGE (ala Canva Magic Media)

Halaman khusus text-to-image: ketik prompt → Yuki menggambarnya dengan
engine FLUX (Cloudflare), hasilnya muncul sebagai balasan di percakapan
halaman ini (thread sendiri: mode_thread("image")).

Tata letak mengikuti pola halaman mode lain (page_desain / page_jadwal):
    1. Judul halaman (page-head ala aplikasi lain)
    2. Hero + kartu contoh prompt   (hanya saat percakapan kosong)
    3. Percakapan: prompt User → gambar dari Yuki (bisa diunduh)
    4. Baris kontrol di kotak bawah: chip GAYA + chip RASIO
       - Gaya  : menambahkan kata kunci gaya ke prompt (efek nyata)
       - Rasio : gambar persegi FLUX dipotong otomatis ke format pilihan
"""

from __future__ import annotations

import streamlit as st

from config import (
    CHAT_INPUT_SUPPORTS_AUDIO, IMAGE_READY, IMAGE_RATIOS, IMAGE_STYLES,
)
from icons import mi
from state import mode_thread
from ui_helpers import _page_footer, render_message

# ============================================================================
# >>> ATUR KARTU CONTOH PROMPT DI SINI <<<
#   (ikon material, judul singkat, prompt lengkap yang dikirim ke Yuki)
#   Ditata 3 kolom; tambah/kurangi bebas, barisnya menyesuaikan.
# ============================================================================
CONTOH_PROMPT = [
    (":material/pets:", "Kucing astronot",
     "Kucing oranye mengambang di luar angkasa dengan helm astronot "
     "bundar, bintang-bintang dan galaksi ungu di latar belakang, "
     "cahaya lembut, foto sinematik"),
    (":material/emoji_food_beverage:", "Kopi pagi",
     "Secangkir kopi hangat di meja kayu dekat jendela, cahaya pagi "
     "lembut, uap tipis mengepul, kroisan di piring kecil, suasana "
     "hangat dan tenang"),
    (":material/beach_access:", "Pantai tropis",
     "Pantai tropis berpasir putih dengan air laut toska jernih, perahu "
     "kecil tertaruh di tepi air, pohon kelapa melengkung, langit senja "
     "jingga keunguan"),
    (":material/smart_toy:", "Maskot brand",
     "Maskot robot ungu lucu tersenyum memegang bohlam menyala, gaya 3D "
     "render mengkilap, latar pastel lembut, pencahayaan studio"),
    (":material/location_city:", "Kota neon",
     "Kota futuristik di malam hari dengan lampu neon ungu dan biru, "
     "jalan basah memantulkan cahaya setelah hujan tipis, suasana "
     "cyberpunk"),
    (":material/ramen_dining:", "Mie ayam",
     "Semangkuk mie ayam Indonesia yang menggugah selera, kuah bening "
     "mengepul, taburan bawang goreng dan daun bawang, gaya ilustrasi "
     "hangat"),
]

GAYA_AKTIF_DEFAULT = "otomatis"
RASIO_AKTIF_DEFAULT = "1:1"


def _kirim(teks: str) -> None:
    """Kirim prompt kartu contoh seolah User mengetiknya sendiri."""
    st.session_state["pending_prompt_mode"] = teks


def _pilih_gaya(key: str) -> None:
    st.session_state["aiimg_gaya"] = key


def _pilih_rasio(key: str) -> None:
    st.session_state["aiimg_rasio"] = key


# --- sinkronisasi nilai widget st.pills -> state yang dipakai engine ------
def _sync_gaya() -> None:
    nilai = st.session_state.get("aiimg_gaya_pills")
    if not nilai:                       # pil diklik ulang (batal pilih)
        nilai = GAYA_AKTIF_DEFAULT
        st.session_state["aiimg_gaya_pills"] = nilai
    st.session_state["aiimg_gaya"] = nilai


def _sync_rasio() -> None:
    nilai = st.session_state.get("aiimg_rasio_pills")
    if not nilai:
        nilai = RASIO_AKTIF_DEFAULT
        st.session_state["aiimg_rasio_pills"] = nilai
    st.session_state["aiimg_rasio"] = nilai


def _label_gaya(key: str) -> str:
    for s in IMAGE_STYLES:
        if s["key"] == key:
            return f"{s['icon']} {s['label']}"
    return key


def _label_rasio(key: str) -> str:
    for r in IMAGE_RATIOS:
        if r["key"] == key:
            return f"{r['icon']} {r['label']}"
    return key


# ----------------------------------------------------------------------------
# Kartu contoh prompt (hero) — hanya tampil saat percakapan masih kosong.
# ----------------------------------------------------------------------------
def _hero_dan_contoh() -> None:
    st.markdown(
        f'''
        <div class="aiimg-hero">
          <div class="aiimg-hero-blob blob-a"></div>
          <div class="aiimg-hero-blob blob-b"></div>
          <div class="aiimg-hero-frame frame-a">{mi(":material/image:")}</div>
          <div class="aiimg-hero-frame frame-b">{mi(":material/brush:")}</div>
          <div class="aiimg-hero-frame frame-c">{mi(":material/auto_awesome:")}</div>
          <div class="aiimg-hero-badge">{mi(":material/auto_awesome:")} AI IMAGE</div>
          <h2>Ubah kata-kata jadi gambar</h2>
          <p>Tulis apa pun yang kamu bayangkan — potret, pemandangan, ilustrasi,
          sampai maskot brand. Yuki menggambarnya lewat engine FLUX dalam
          hitungan detik.</p>
          <div class="aiimg-hero-tags">
            <span>{mi(":material/bolt:")} Hasil cepat</span>
            <span>{mi(":material/palette:")} {len(IMAGE_STYLES)} gaya</span>
            <span>{mi(":material/aspect_ratio:")} {len(IMAGE_RATIOS)} format</span>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'''
        <div class="aiimg-section-title">
          <span class="aiimg-section-icon">{mi(":material/bolt:")}</span>
          <span>Coba salah satu ini</span><i></i>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    for i in range(0, len(CONTOH_PROMPT), 3):
        baris = CONTOH_PROMPT[i:i + 3]
        cols = st.columns(len(baris), gap="medium")
        for j, (icon, judul, prompt) in enumerate(baris):
            with cols[j]:
                with st.container(key=f"aiimg_sug_{i + j}"):
                    st.markdown(
                        f'<div class="aiimg-sug-visual">'
                        f'<div class="aiimg-sug-icon">{mi(icon)}</div>'
                        f'<div class="aiimg-sug-art"></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.button(
                        f"**{judul}**  \n:gray[Buat sekarang]  \n→",
                        key=f"aiimg_sug_btn_{i + j}",
                        use_container_width=True,
                        on_click=_kirim,
                        args=(prompt,),
                    )

    st.markdown(
        f'''
        <div class="aiimg-tips">
          <span class="aiimg-tips-icon">{mi(":material/lightbulb:")}</span>
          <span><b>Tips:</b> semakin detail prompt — subjek, gaya, cahaya,
          suasana — semakin pas gambar yang dihasilkan.</span>
        </div>
        ''',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# PANEL KANAN — pengaturan GAYA & FORMAT.
#
# Dulu kedua deret chip ini menempel di kotak input bawah; sekarang pindah
# ke kartu melayang di sisi kanan layar (lihat .st-key-aiimg_panel di
# styles/part12_ai_image.py) supaya kotak input bisa naik & lega.
# Di layar sempit (<= 1200px) panelnya otomatis jadi kartu biasa di atas
# percakapan — bukan melayang — jadi tidak pernah menutupi isi halaman.
# ----------------------------------------------------------------------------
def _pills(label: str, opsi: list, fmt, default, key: str, on_change) -> None:
    """st.pills dengan wrap=True bila versi Streamlit mendukungnya."""
    kw = dict(
        options=opsi,
        format_func=fmt,
        default=default,
        key=key,
        on_change=on_change,
        label_visibility="collapsed",
    )
    try:
        st.pills(label, wrap=True, **kw)
    except TypeError:                   # Streamlit lama: belum ada `wrap`
        st.pills(label, **kw)


def _panel_kanan() -> None:
    """Kartu pengaturan di sisi kanan: pilih gaya & format gambar."""
    gaya_aktif = st.session_state.get("aiimg_gaya", GAYA_AKTIF_DEFAULT)
    rasio_aktif = st.session_state.get("aiimg_rasio", RASIO_AKTIF_DEFAULT)

    with st.container(key="aiimg_panel"):
        st.markdown(
            f'<div class="aiimg-panel-head">'
            f'<span class="aiimg-panel-head-icon">'
            f'{mi(":material/tune:")}</span>'
            f'<span>Pengaturan gambar</span></div>',
            unsafe_allow_html=True,
        )

        # Streamlit terlalu tua (tanpa st.pills) → pakai tombol biasa.
        if not hasattr(st, "pills"):
            _panel_tombol(gaya_aktif, rasio_aktif)
            return

        st.markdown(
            f'<div class="aiimg-chip-label">{mi(":material/palette:")}'
            f' Gaya</div>',
            unsafe_allow_html=True,
        )
        _pills(
            "Gaya",
            [s["key"] for s in IMAGE_STYLES],
            _label_gaya,
            gaya_aktif,
            "aiimg_gaya_pills",
            _sync_gaya,
        )

        st.markdown(
            f'<div class="aiimg-chip-label aiimg-chip-label-2">'
            f'{mi(":material/aspect_ratio:")} Format</div>',
            unsafe_allow_html=True,
        )
        _pills(
            "Format",
            [r["key"] for r in IMAGE_RATIOS],
            _label_rasio,
            rasio_aktif,
            "aiimg_rasio_pills",
            _sync_rasio,
        )

        hint = next(
            (r["hint"] for r in IMAGE_RATIOS if r["key"] == rasio_aktif), ""
        )
        st.markdown(
            f'<div class="aiimg-panel-hint">{mi(":material/info:")}'
            f'<span>{hint}'
            f'{" &middot; dipotong otomatis" if rasio_aktif != "1:1" else ""}'
            f'</span></div>',
            unsafe_allow_html=True,
        )


def _panel_tombol(gaya_aktif: str, rasio_aktif: str) -> None:
    """Isi panel versi cadangan (Streamlit < 1.40, belum ada st.pills)."""
    st.markdown(
        f'<div class="aiimg-chip-label">{mi(":material/palette:")} Gaya</div>',
        unsafe_allow_html=True,
    )
    for s in IMAGE_STYLES:
        aktif = s["key"] == gaya_aktif
        with st.container(
            key=("aiimg_gaya_on_" if aktif else "aiimg_gaya_") + s["key"]
        ):
            st.button(
                f"{s['icon']} &nbsp;{s['label']}",
                key=f"aiimg_gbtn_{s['key']}",
                use_container_width=True,
                on_click=_pilih_gaya,
                args=(s["key"],),
            )

    st.markdown(
        f'<div class="aiimg-chip-label aiimg-chip-label-2">'
        f'{mi(":material/aspect_ratio:")} Format</div>',
        unsafe_allow_html=True,
    )
    for r in IMAGE_RATIOS:
        aktif = r["key"] == rasio_aktif
        with st.container(
            key=("aiimg_rasio_on_" if aktif else "aiimg_rasio_") + r["key"]
        ):
            st.button(
                f"{r['icon']} &nbsp;{r['label']}",
                key=f"aiimg_rbtn_{r['key']}",
                use_container_width=True,
                on_click=_pilih_rasio,
                args=(r["key"],),
            )


# ============================================================================
# HALAMAN UTAMA
# ============================================================================
def page_image() -> None:
    from chat_handlers import (
        maybe_run_yuki, process_user_input, fragmen_jawaban_yuki,
        chat_input_atau_hentikan, render_loader_yuki,
    )

    thread = mode_thread("image")
    st.markdown('<div class="aiimg-page-shell"></div>', unsafe_allow_html=True)

    st.markdown(
        f'''
        <div class="page-head">
          <div class="page-head-icon aiimg-head-icon">{mi(":material/auto_awesome:")}</div>
          <div>
            <h2 class="page-title">AI Image</h2>
            <p class="page-sub">Text-to-image ala Canva: pilih gaya &amp; format,
            tulis idemu, hasilnya muncul sebagai balasan di halaman ini.</p>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Peringatan lembut bila engine gambar belum dikonfigurasi pemilik.
    if not IMAGE_READY:
        st.markdown(
            '<div class="aiimg-warning">Engine gambar belum dikonfigurasi '
            'pemilik aplikasi (CF_ACCOUNT_ID / CF_API_TOKEN). Prompt tetap '
            'terkirim, tapi Yuki akan menjelaskan lewat balasan.</div>',
            unsafe_allow_html=True,
        )

    # ---- Panel pengaturan (gaya & format) di sisi kanan layar ----
    _panel_kanan()

    # ---- Hero + contoh: hanya saat percakapan masih kosong ----
    if not thread:
        _hero_dan_contoh()

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()
    fragmen_jawaban_yuki()
    render_loader_yuki()

    # ruang kosong supaya isi terakhir tidak tertutup kotak input
    st.markdown('<div class="dock-spacer"></div>', unsafe_allow_html=True)

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        # Kotak bawah kini HANYA berisi kolom input — chip gaya & format
        # sudah pindah ke panel kanan, jadi kolom chat bisa naik dan lega.
        user_input = chat_input_atau_hentikan(
            "Deskripsikan gambar yang ingin dibuat…", **chat_kwargs
        )

    antre = (st.session_state.pop("pending_prompt_mode", "") or "").strip()

    if antre and user_input is None:
        user_input = antre

    # Halaman ini murni text-to-image: lampiran yang mungkin tertinggal
    # dari halaman lain tidak ikut dikirim di sini.
    if user_input:
        st.session_state.pending_images = []

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=bool(thread))
