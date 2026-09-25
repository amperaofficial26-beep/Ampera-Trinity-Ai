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
    ("Rapat / meeting",
     "Buatkan checklist persiapan rapat yang rapi, termasuk agenda, "
     "peserta, materi, dan tindak lanjut."),
    ("Tugas harian",
     "Bantu aku menyusun daftar tugas harian berdasarkan prioritas dan "
     "waktu yang tersedia hari ini."),
    ("Rencana mingguan",
     "Buatkan rencana mingguan yang realistis untuk mengatur pekerjaan, "
     "istirahat, dan target utama selama 7 hari."),
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


def _kirim_form() -> None:
    judul = (st.session_state.get("jd_new_title") or "").strip()
    kapan = (st.session_state.get("jd_new_when") or "").strip()
    waktu = (st.session_state.get("jd_new_time") or "").strip()
    catatan = (st.session_state.get("jd_new_note") or "").strip()
    gaya = st.session_state.get("jd_schedule_style") or "Otomatis"
    detail = " ".join(x for x in (judul, kapan, waktu, catatan) if x)
    if not detail:
        detail = "kebutuhan jadwal saya"
    st.session_state["pending_prompt_mode"] = (
        f"Buatkan jadwal dengan gaya {gaya} berdasarkan kebutuhan berikut: {detail}. "
        "Susun langkah yang realistis dan masukkan tugas penting ke daftar tugasku."
    )


def _tambah_manual() -> None:
    judul = (st.session_state.get("jd_new_title") or "").strip()
    if not judul:
        return
    kapan = " ".join(
        x for x in (
            st.session_state.get("jd_new_when") or "",
            st.session_state.get("jd_new_time") or "",
        ) if x
    )
    add_task(
        judul,
        kapan,
        st.session_state.get("jd_new_prio") or "sedang",
        st.session_state.get("jd_new_note") or "",
    )
    st.session_state["jd_new_title"] = ""
    st.session_state["jd_new_when"] = ""
    st.session_state["jd_new_time"] = ""
    st.session_state["jd_new_note"] = ""


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
        render_pending_preview, fragmen_jawaban_yuki, chat_input_atau_hentikan,
        render_loader_yuki,
    )

    thread = mode_thread("jadwal")
    punya_data = bool(tasks()) or bool(thread)
    st.markdown('<div class="scheduler-page-shell"></div>', unsafe_allow_html=True)

    st.markdown(
        f'''
        <div class="scheduler-topbar">
          <div class="scheduler-heading">
            <div class="scheduler-heading-icon">{mi(":material/calendar_month:")}</div>
            <div>
              <h1>AI Penjadwal</h1>
              <p>Atur jadwal, rencana, dan tugas harian dengan bantuan AI.</p>
            </div>
          </div>
          <div class="scheduler-brand">
            <span>{mi(":material/auto_awesome:")} Trinity AI</span>
            <i></i>
            <small>Lebih cerdas, lebih produktif.</small>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    if not punya_data:
        st.markdown(
            f'''
            <section class="scheduler-hero">
              <div class="scheduler-hero-copy">
                <div class="scheduler-hero-icon">{mi(":material/auto_awesome:")}</div>
                <div>
                  <h2>Jadwalkan dengan lebih mudah</h2>
                  <p>Tulis kebutuhan kamu, dan AI akan membantu membuat jadwal yang rapi,
                  teratur, dan sesuai dengan prioritasmu.</p>
                </div>
              </div>
              <div class="scheduler-hero-art" aria-hidden="true">
                <div class="scheduler-calendar">
                  <b></b><b></b><b></b><b></b><b></b><b></b>
                  <span></span><span></span><span></span>
                </div>
                <div class="scheduler-clock">{mi(":material/schedule:")}</div>
                <div class="scheduler-check">{mi(":material/check:")}</div>
              </div>
            </section>
            ''',
            unsafe_allow_html=True,
        )

        with st.container(key="jadwal_builder"):
            st.markdown(
                f'''
                <div class="scheduler-builder-heading">
                  <div class="scheduler-builder-icon">{mi(":material/calendar_month:")}</div>
                  <div>
                    <h2>Buat Jadwal Baru</h2>
                    <p>Ceritakan kebutuhan jadwalmu, dan AI akan membuatnya untukmu.</p>
                  </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns([1.7, 0.9, 0.9], gap="medium")
            with c1:
                st.text_input(
                    "Judul / Kegiatan",
                    key="jd_new_title",
                    placeholder="Contoh: Rencana belajar, meeting, atau kegiatan harian...",
                )
            with c2:
                st.text_input(
                    "Tanggal",
                    key="jd_new_when",
                    placeholder="Pilih tanggal",
                )
            with c3:
                st.selectbox(
                    "Prioritas",
                    ["tinggi", "sedang", "rendah"],
                    index=1,
                    key="jd_new_prio",
                )

            c4, c5 = st.columns([0.9, 1.7], gap="medium")
            with c4:
                st.text_input(
                    "Waktu",
                    key="jd_new_time",
                    placeholder="Pilih waktu (opsional)",
                )
            with c5:
                st.text_area(
                    "Deskripsi / Catatan (opsional)",
                    key="jd_new_note",
                    placeholder="Tambahkan detail, tujuan, atau catatan penting lainnya...",
                    height=88,
                )

            st.markdown('<div class="scheduler-style-label">Pilih gaya penjadwalan</div>',
                        unsafe_allow_html=True)
            style_col, action_col = st.columns([2.3, 0.7], gap="medium")
            with style_col:
                st.radio(
                    "Gaya penjadwalan",
                    ["Otomatis", "Terstruktur", "Fleksibel"],
                    index=0,
                    key="jd_schedule_style",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            with action_col:
                st.button(
                    ":material/auto_awesome:  Buat Jadwal  →",
                    key="jd_make_schedule",
                    type="primary",
                    use_container_width=True,
                    on_click=_kirim_form,
                )

        st.markdown(
            '<div class="scheduler-quick-label">'
            f'{mi(":material/bolt:")} <span>Aksi cepat</span></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="jadwal_quick"):
            cols = st.columns(4, gap="medium")
            quick_visuals = ["study", "meeting", "daily", "weekly"]
            quick_icons = [
                ":material/calendar_month:",
                ":material/business_center:",
                ":material/task_alt:",
                ":material/star:",
            ]
            quick_desc = [
                "Buat jadwal belajar yang efektif",
                "Atur jadwal meeting dengan mudah",
                "Kelola tugas dan to-do list",
                "Buat rencana untuk 7 hari ke depan",
            ]
            for i, (label, prompt) in enumerate(TOMBOL_CEPAT):
                with cols[i]:
                    with st.container(key=f"jadwal_quick_card_{i}"):
                        st.markdown(
                            f'<div class="scheduler-quick-visual scheduler-visual-{quick_visuals[i]}">'
                            f'<div class="scheduler-quick-icon">{mi(quick_icons[i])}</div>'
                            '<div class="scheduler-quick-art"></div></div>',
                            unsafe_allow_html=True,
                        )
                        st.button(
                            f"**{label}**  \n:gray[{quick_desc[i]}]  \n→",
                            key=f"jadwal_q_{i}",
                            use_container_width=True,
                            on_click=_kirim,
                            args=(prompt,),
                        )
    else:
        _render_panel_tugas()
        st.markdown('<div class="sec-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-label">Obrolan</div>',
                    unsafe_allow_html=True)

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    # Jawaban yang sedang mengalir + tombol "Hentikan respons".
    fragmen_jawaban_yuki()
    render_loader_yuki()

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
        user_input = chat_input_atau_hentikan("Minta dibuatkan jadwal…", **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("jadwal", show_mode=False)

    antre = (st.session_state.pop("pending_prompt_mode", "") or "").strip()
    if antre and user_input is None:
        user_input = antre

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=bool(thread))
