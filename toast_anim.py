# -*- coding: utf-8 -*-
"""Notifikasi (toast) Trinity — minimalis tetapi terlihat profesional.

Gaya lama (cokelat gelap, glow emas, huruf gotik, logo berubah jadi
centang) diganti kartu bersih bergaya produk: latar terang, garis tipis,
bayangan lembut, ikon kecil di dalam lingkaran, dan teks sans-serif.

>>> ATUR TAMPILAN NOTIFIKASI DI SINI <<<
"""
from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components

from icons import mi

# Berapa lama notifikasi terlihat sebelum memudar (milidetik).
DURASI_MS = 4200

# Durasi animasi geser masuk (kanan → kiri) dan keluar (kiri → kanan).
MASUK_MS = 340
KELUAR_MS = 300

# Warna dasar notifikasi — mengikuti palet premium krem + ungu Trinity.
WARNA_LATAR = "#FFFDF9"
WARNA_GARIS = "#E6DAC8"
WARNA_TEKS = "#2C1F33"
WARNA_AKSEN = "#4A3559"
WARNA_AKSEN_LEMBUT = "#F1E9F4"

# Lebar maksimum kartu notifikasi.
LEBAR_PX = 340


def inject_toast_anim() -> None:
    """Pasang gaya notifikasi minimalis pada setiap rerun."""
    st.markdown(
        f"""
<style>
/* ================================================================
   TOAST — kartu minimalis
   ================================================================ */
[data-testid="stToast"] {{
  box-sizing: border-box !important;
  min-height: 0 !important;
  width: min({LEBAR_PX}px, calc(100vw - 28px)) !important;
  padding: 12px 36px 12px 14px !important;

  color: {WARNA_TEKS} !important;
  border: 1px solid {WARNA_GARIS} !important;
  border-radius: 14px !important;
  background: {WARNA_LATAR} !important;

  box-shadow:
    0 10px 28px rgba(44, 31, 51, .12),
    0 1px 2px rgba(44, 31, 51, .06) !important;

  /* Animasi geser dijalankan dari JavaScript (lihat _pasang_pengamat_toast)
     agar tidak tertimpa animasi bawaan Streamlit. */
  will-change: transform, opacity !important;
}}

/* Garis aksen tipis di tepi kiri sebagai penanda merek. */
[data-testid="stToast"]::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: {WARNA_AKSEN};
}}

/* ---------------------------------------------------------------
   IKON BAWAAN STREAMLIT — dipertahankan, dibuat kecil & rapi
   --------------------------------------------------------------- */
[data-testid="stToast"] [data-testid="stToastIcon"],
[data-testid="stToast"] [data-testid="stIconMaterial"] {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  margin-right: 10px !important;
  border-radius: 9px !important;
  background: {WARNA_AKSEN_LEMBUT} !important;
  color: {WARNA_AKSEN} !important;
  font-size: 16px !important;
  line-height: 1 !important;
}}

/* ---------------------------------------------------------------
   TEKS
   --------------------------------------------------------------- */
[data-testid="stToast"] [data-testid="stMarkdownContainer"],
[data-testid="stToast"] [data-testid="stMarkdownContainer"] *,
[data-testid="stToast"] p {{
  margin: 0 !important;
  color: {WARNA_TEKS} !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system,
               "Segoe UI", sans-serif !important;
  font-size: .88rem !important;
  font-weight: 560 !important;
  line-height: 1.45 !important;
  letter-spacing: -.005em !important;
  text-shadow: none !important;
}}

/* ---------------------------------------------------------------
   TOMBOL TUTUP
   --------------------------------------------------------------- */
[data-testid="stToast"] button {{
  top: 7px !important;
  right: 7px !important;
  width: 24px !important;
  height: 24px !important;
  border-radius: 8px !important;
  color: #9A8F9A !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  opacity: .75 !important;
  transition: background .15s ease, color .15s ease, opacity .15s ease !important;
}}
[data-testid="stToast"] button:hover {{
  background: #F4ECE1 !important;
  color: {WARNA_TEKS} !important;
  opacity: 1 !important;
}}

/* ---------------------------------------------------------------
   ANIMASI — halus dan singkat, tanpa kilau berlebihan
   --------------------------------------------------------------- */
/* Masuk: meluncur dari kanan ke kiri. */
@keyframes trinityToastMasuk {{
  from {{ opacity: 0; transform: translateX(calc(100% + 32px)); }}
  60%  {{ opacity: 1; }}
  to   {{ opacity: 1; transform: translateX(0); }}
}}

/* Keluar: meluncur dari kiri ke kanan. */
@keyframes trinityToastKeluar {{
  from {{ opacity: 1; transform: translateX(0); }}
  to   {{ opacity: 0; transform: translateX(calc(100% + 32px)); }}
}}

@media (max-width: 640px) {{
  [data-testid="stToast"] {{
    width: calc(100vw - 20px) !important;
    padding: 11px 32px 11px 12px !important;
  }}
  [data-testid="stToast"] p {{ font-size: .84rem !important; }}
}}

/* ---------------------------------------------------------------
   Streamlit membungkus toast dalam beberapa lapis div yang punya
   transform/animation sendiri. Lapisan itu dinetralkan, lalu animasi
   geser dipasang pada pembungkus terluar supaya benar-benar terlihat.
   --------------------------------------------------------------- */
[data-testid="stToastContainer"],
div:has(> [data-testid="stToast"]) {{
  animation: none !important;
  transition: none !important;
  overflow: visible !important;
}}
div:has(> [data-testid="stToast"]) {{
  will-change: transform, opacity !important;
}}

/* ================================================================
   NOTIFIKASI KUSTOM (pengganti st.toast) — animasi geser milik sendiri
   ================================================================ */
.tr-toast-wrap {{
  position: fixed !important;
  right: 18px;
  bottom: calc(18px + var(--tr-toast-i, 0) * 62px);
  z-index: 1000000;
  pointer-events: none;
  animation:
    trToastMasuk {MASUK_MS}ms cubic-bezier(.22, 1, .36, 1) both,
    trToastKeluar {KELUAR_MS}ms cubic-bezier(.4, 0, .9, .3)
      {DURASI_MS}ms forwards;
}}
.tr-toast {{
  display: flex;
  align-items: center;
  gap: 10px;
  box-sizing: border-box;
  width: min({LEBAR_PX}px, calc(100vw - 28px));
  padding: 12px 15px;
  border: 1px solid {WARNA_GARIS};
  border-left: 3px solid {WARNA_AKSEN};
  border-radius: 14px;
  background: {WARNA_LATAR};
  color: {WARNA_TEKS};
  box-shadow:
    0 10px 28px rgba(44, 31, 51, .12),
    0 1px 2px rgba(44, 31, 51, .06);
  pointer-events: auto;
}}
.tr-toast-ic {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 26px;
  width: 26px;
  height: 26px;
  border-radius: 9px;
  background: {WARNA_AKSEN_LEMBUT};
  color: {WARNA_AKSEN};
}}
.tr-toast-ic .mi {{ font-size: 16px; }}
.tr-toast-teks {{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system,
               "Segoe UI", sans-serif;
  font-size: .88rem;
  font-weight: 560;
  line-height: 1.45;
  letter-spacing: -.005em;
}}

/* Masuk: dari kanan ke kiri. Keluar: dari kiri ke kanan. */
@keyframes trToastMasuk {{
  from {{ opacity: 0; transform: translateX(calc(100% + 40px)); }}
  to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes trToastKeluar {{
  from {{ opacity: 1; transform: translateX(0); visibility: visible; }}
  to   {{ opacity: 0; transform: translateX(calc(100% + 40px));
         visibility: hidden; }}
}}

@media (prefers-reduced-motion: reduce) {{
  [data-testid="stToast"],
  div:has(> [data-testid="stToast"]),
  .tr-toast-wrap {{ animation: none !important; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )
    # st.toast diganti sekali saja per sesi proses.
    if getattr(st, "_tr_toast_asli", None) is None:
        st._tr_toast_asli = st.toast
        st.toast = _toast_kustom

    st.session_state["_tr_toast_n"] = 0
    st.session_state["_tr_run"] = int(st.session_state.get("_tr_run", 0)) + 1

    # Banyak tempat memanggil st.toast lalu langsung st.rerun(). Notifikasi
    # seperti itu dititipkan di antrean dan baru digambar pada run berikut
    # supaya tetap sempat terlihat.
    antrean = st.session_state.get("_tr_toast_q") or []
    sekarang = st.session_state["_tr_run"]
    tersisa = []
    for run_id, pesan, ikon in antrean:
        if run_id < sekarang:
            _gambar_toast(pesan, ikon)
        else:
            tersisa.append((run_id, pesan, ikon))
    st.session_state["_tr_toast_q"] = tersisa


def _html_toast(pesan: str, ikon: str | None) -> str:
    """Satu kartu notifikasi beserta animasi gesernya."""
    bagian_ikon = ""
    if ikon:
        if ikon.startswith(":material"):
            bagian_ikon = f'<span class="tr-toast-ic">{mi(ikon)}</span>'
        else:
            bagian_ikon = f'<span class="tr-toast-ic">{html.escape(ikon)}</span>'
    return (
        '<div class="tr-toast">'
        + bagian_ikon
        + '<span class="tr-toast-teks">'
        + html.escape(str(pesan))
        + "</span></div>"
    )


def _gambar_toast(pesan: str, ikon: str | None) -> None:
    """Gambar satu notifikasi di pojok kanan bawah (bertumpuk ke atas)."""
    urutan = int(st.session_state.get("_tr_toast_n", 0))
    st.session_state["_tr_toast_n"] = urutan + 1
    st.markdown(
        '<div class="tr-toast-wrap" style="--tr-toast-i:'
        + str(urutan)
        + ';">'
        + _html_toast(pesan, ikon)
        + "</div>",
        unsafe_allow_html=True,
    )


def _toast_kustom(body: str, *, icon: str | None = None, **_lain) -> None:
    """Pengganti st.toast dengan animasi geser yang pasti terlihat.

    st.toast bawaan dirender React dengan transform sendiri sehingga CSS
    kita selalu kalah. Notifikasi digambar sendiri sebagai elemen biasa
    berposisi fixed, jadi animasinya sepenuhnya milik kita.
    """
    _gambar_toast(body, icon)
    # Dititipkan juga ke antrean: kalau run ini diakhiri st.rerun(),
    # notifikasinya tetap muncul di run berikutnya.
    antrean = st.session_state.get("_tr_toast_q") or []
    antrean.append((int(st.session_state.get("_tr_run", 0)), str(body), icon))
    st.session_state["_tr_toast_q"] = antrean[-4:]


def toast_sukses(pesan: str) -> None:
    """Notifikasi sukses ringkas dengan ikon centang kecil."""
    try:
        st.toast(pesan, icon=":material/check_circle:", duration="short")
    except TypeError:
        st.toast(pesan, icon=":material/check_circle:")
