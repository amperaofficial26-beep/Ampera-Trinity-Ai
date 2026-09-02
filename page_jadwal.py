# -*- coding: utf-8 -*-
"""
HALAMAN: AI PENJADWAL

Persona perencana (JADWAL_PROMPT di config.py) + daftar tugas tersimpan.

Tata letak SATU LAJUR dari atas ke bawah supaya tidak berdesakan:
    1. Judul halaman
    2. Ringkasan kemajuan  (hanya bila ada tugas)
    3. Panel daftar tugas  (dikelompokkan: Hari ini / Besok / Minggu ini / Nanti)
    4. Tambah tugas sendiri (terlipat)
    5. Tombol mulai cepat  (hanya saat obrolan masih kosong)
    6. Obrolan dengan Yuki
"""

from __future__ import annotations

import html
import re

import streamlit as st

from config import CHAT_INPUT_SUPPORTS_AUDIO, CHAT_INPUT_SUPPORTS_FILE, IMAGE_INPUT_TYPES
from icons import mi
from state import (
    add_task, clear_done_tasks, drop_task, mode_thread, tasks, toggle_task,
)
from ui_helpers import _page_footer, render_message

# ============================================================================
# >>> ATUR TOMBOL CEPAT, KELOMPOK AGENDA & WARNA PRIORITAS DI SINI <<<
# ============================================================================
TOMBOL_CEPAT = [
    ("Rencana belajar",
     "Buatkan rencana belajar Python selama 7 hari untuk pemula, "
     "1-2 jam sehari. Masukkan ke daftar tugasku."),
    ("Rapikan minggu ini",
     "Bantu aku menyusun prioritas minggu ini. Tanyakan dulu apa saja "
     "yang harus kukerjakan."),
    ("Pecah tugas besar",
     "Aku punya satu tugas besar yang bikin menunda terus. Bantu pecah "
     "jadi langkah kecil yang jelas selesainya."),
]

KELOMPOK = [
    ("Hari ini", ("hari ini", "sekarang", "today", "segera")),
    ("Besok", ("besok", "tomorrow")),
    ("Minggu ini", ("senin", "selasa", "rabu", "kamis", "jumat", "sabtu",
                    "minggu ini", "pekan ini", "this week")),
]
WARNA_PRIORITAS = {"tinggi": "#C4703F", "sedang": "#8E8398", "rendah": "#B7AEC2"}

_TUGAS_RE = re.compile(
    r"[`*_]*\[{1,2}\s*TUGAS\s*\]{1,2}[`*_]*(.*?)[`*_]*\[{1,2}\s*/\s*TUGAS\s*\]{1,2}[`*_]*",
    re.S | re.I,
)


def serap_blok_tugas(teks: str) -> tuple[str, int]:
    """Ambil blok [[TUGAS]] dari jawaban Yuki -> masukkan ke daftar tugas.

    Mengembalikan (teks_tanpa_blok, jumlah_tugas_baru).
    """
    raw = teks or ""
    if "TUGAS" not in raw.upper():
        return raw, 0
    cocok = _TUGAS_RE.search(raw)
    if not cocok:
        return raw, 0

    jumlah = 0
    for baris in cocok.group(1).splitlines():
        b = re.sub(r"^(\d+[.)]|[-*•])\s*", "", baris.strip().strip("`")).strip()
        if not b or "|" not in b:
            continue
        bagian = [x.strip() for x in b.split("|")]
        judul = bagian[0]
        kapan = bagian[1] if len(bagian) > 1 else ""
        prio = (bagian[2] if len(bagian) > 2 else "sedang").lower()
        catatan = bagian[3] if len(bagian) > 3 else ""
        if prio not in WARNA_PRIORITAS:
            prio = "sedang"
        if judul:
            add_task(judul, kapan, prio, catatan)
            jumlah += 1
        if jumlah >= 10:
            break

    bersih = raw.replace(cocok.group(0), "").strip()
    return re.sub(r"\n{3,}", "\n\n", bersih), jumlah


def _kelompok_dari(kapan: str) -> str:
    k = (kapan or "").lower()
    for nama, kata in KELOMPOK:
        if any(x in k for x in kata):
            return nama
    return "Nanti"


def _kirim(teks: str) -> None:
    st.session_state["pending_prompt_mode"] = teks


def _tambah_manual() -> None:
    judul = (st.session_state.get("jd_new_title") or "").strip()
    if not judul:
        return
    add_task(judul,
             st.session_state.get("jd_new_when") or "",
             st.session_state.get("jd_new_prio") or "sedang")
    st.session_state["jd_new_title"] = ""
    st.session_state["jd_new_when"] = ""


def _render_ringkasan(daftar: list[dict]) -> None:
    selesai = sum(1 for t in daftar if t["selesai"])
    persen = int(selesai / len(daftar) * 100) if daftar else 0
    st.markdown(
        '<div class="jd-progress-wrap">'
        '<div class="jd-progress-text">' + str(selesai) + " dari "
        + str(len(daftar)) + " tugas selesai</div>"
        '<div class="jd-progress-bar"><div class="jd-progress-fill" '
        'style="width:' + str(persen) + '%"></div></div></div>',
        unsafe_allow_html=True,
    )


def _render_baris_tugas(t: dict) -> None:
    with st.container(key=f"jd_row_{t['id']}"):
        c_cek, c_isi, c_hapus = st.columns([0.08, 1.0, 0.08])
        with c_cek:
            st.button("✓" if t["selesai"] else "○", key=f"jd_tog_{t['id']}",
                      help="Tandai selesai", on_click=toggle_task, args=(t["id"],))
        with c_isi:
            coret = " jd-done" if t["selesai"] else ""
            warna = WARNA_PRIORITAS.get(t["prioritas"], "#8E8398")
            meta = []
            if t["kapan"]:
                meta.append(html.escape(t["kapan"]))
            meta.append(html.escape(t["prioritas"]))
            if t["catatan"]:
                meta.append(html.escape(t["catatan"]))
            st.markdown(
                '<div class="jd-item' + coret + '">'
                '<span class="jd-dot" style="background:' + warna + '"></span>'
                '<span class="jd-title">' + html.escape(t["judul"]) + "</span>"
                '<span class="jd-meta">' + " · ".join(meta) + "</span>"
                "</div>",
                unsafe_allow_html=True,
            )
        with c_hapus:
            st.button("×", key=f"jd_del_{t['id']}", help="Hapus",
                      on_click=drop_task, args=(t["id"],))


def _render_panel_tugas() -> None:
    daftar = tasks()

    st.markdown('<div class="sec-label">Daftar tugas</div>',
                unsafe_allow_html=True)

    if not daftar:
        st.markdown(
            '<div class="empty-card">Belum ada tugas. Minta Yuki menyusun '
            "rencana lewat kotak chat di bawah, atau tambah sendiri.</div>",
            unsafe_allow_html=True,
        )
    else:
        _render_ringkasan(daftar)
        with st.container(key="jd_panel"):
            for nama in ("Hari ini", "Besok", "Minggu ini", "Nanti"):
                anggota = [t for t in daftar if _kelompok_dari(t["kapan"]) == nama]
                if not anggota:
                    continue
                st.markdown('<div class="jd-group">' + html.escape(nama) + "</div>",
                            unsafe_allow_html=True)
                for t in anggota:
                    _render_baris_tugas(t)

        selesai = sum(1 for t in daftar if t["selesai"])
        if selesai:
            with st.container(key="jd_clear_wrap"):
                st.button(f":material/delete_sweep:  Bersihkan {selesai} tugas selesai",
                          key="jd_clear", use_container_width=True,
                          on_click=clear_done_tasks)

    with st.expander(":material/add:  Tambah tugas sendiri"):
        st.text_input("Judul tugas", key="jd_new_title",
                      placeholder="mis. Selesaikan laporan")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Kapan", key="jd_new_when",
                          placeholder="Hari ini / Senin / 12 Sep")
        with c2:
            st.selectbox("Prioritas", ["tinggi", "sedang", "rendah"],
                         index=1, key="jd_new_prio")
        st.button("Tambahkan", key="jd_add", type="primary",
                  use_container_width=True, on_click=_tambah_manual)


def page_jadwal() -> None:
    from chat_handlers import (
        maybe_run_yuki, process_user_input, render_input_controls,
        render_pending_preview,
    )

    thread = mode_thread("jadwal")

    st.markdown(
        '<div class="page-head"><div class="page-head-icon">'
        + mi("calendar_month")
        + '</div><div><h2 class="page-title">AI Penjadwal</h2>'
        '<p class="page-sub">Pecah tujuan besar jadi langkah kecil, lalu '
        'susun jadi jadwal yang masuk akal.</p></div></div>',
        unsafe_allow_html=True,
    )

    _render_panel_tugas()

    st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)

    if not thread:
        st.markdown('<div class="sec-label">Mulai cepat</div>',
                    unsafe_allow_html=True)
        with st.container(key="jadwal_quick"):
            cols = st.columns(len(TOMBOL_CEPAT))
            for i, (label, prompt) in enumerate(TOMBOL_CEPAT):
                with cols[i]:
                    st.button(label, key=f"jadwal_q_{i}", use_container_width=True,
                              on_click=_kirim, args=(prompt,))
    else:
        st.markdown('<div class="sec-label">Obrolan</div>',
                    unsafe_allow_html=True)

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    st.markdown('<div class="dock-spacer"></div>', unsafe_allow_html=True)

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="pending_preview"):
            render_pending_preview("jadwal")
        user_input = st.chat_input("Minta dibuatkan jadwal…", **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("jadwal", show_mode=False)

    antre = (st.session_state.pop("pending_prompt_mode", "") or "").strip()
    if antre and user_input is None:
        user_input = antre

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=bool(thread))
