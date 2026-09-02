# -*- coding: utf-8 -*-
"""
Pengelolaan st.session_state: inisialisasi, pengaturan (settings), dan
thread pesan (chat utama, artefak, kursus, riwayat percakapan).

Halaman & engine lain HANYA boleh membaca/menulis session_state lewat
fungsi-fungsi di modul ini supaya struktur data tetap konsisten.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from config import DEFAULT_SETTINGS

# ============================================================================
# PENGATURAN
# ============================================================================
def get_settings() -> dict:
    """Pengaturan user (halaman Pengaturan) — nilai yang belum diset
    otomatis diisi dari DEFAULT_SETTINGS, jadi aman walau state lama."""
    base = dict(DEFAULT_SETTINGS)
    base.update(st.session_state.get("settings") or {})
    return base


# ============================================================================
# THREAD PESAN
#   Chat utama, halaman Artefak, dan halaman Trinity Kursus punya riwayat
#   sendiri-sendiri supaya jawaban Yuki tidak tercampur antar halaman.
# ============================================================================
def main_thread() -> list[dict]:
    return st.session_state.messages


def artifact_thread(art_id: int) -> list[dict]:
    key = f"artifact_msgs_{art_id}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def course_thread(cid: str) -> list[dict]:
    key = f"course_msgs_{cid}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def mode_thread(nama: str) -> list[dict]:
    """Riwayat pesan untuk halaman ber-mode khusus (desain, jadwal)."""
    key = f"mode_msgs_{nama}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


# ============================================================================
# DAFTAR TUGAS (AI Penjadwal)
# ============================================================================
def tasks() -> list[dict]:
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    return st.session_state.tasks


def add_task(judul: str, kapan: str = "", prioritas: str = "sedang",
             catatan: str = "") -> dict:
    """Tambah satu tugas. `kapan` bebas teks (mis. 'Senin', '12 Sep', 'Hari ini')."""
    st.session_state["task_counter"] = st.session_state.get("task_counter", 0) + 1
    t = {
        "id": st.session_state["task_counter"],
        "judul": (judul or "").strip(),
        "kapan": (kapan or "").strip(),
        "prioritas": (prioritas or "sedang").strip().lower(),
        "catatan": (catatan or "").strip(),
        "selesai": False,
    }
    tasks().append(t)
    return t


def toggle_task(tid: int) -> None:
    for t in tasks():
        if t["id"] == tid:
            t["selesai"] = not t["selesai"]
            return


def drop_task(tid: int) -> None:
    st.session_state.tasks = [t for t in tasks() if t["id"] != tid]


def clear_done_tasks() -> None:
    st.session_state.tasks = [t for t in tasks() if not t["selesai"]]


def active_thread() -> list[dict]:
    """Riwayat pesan milik halaman yang sedang dibuka."""
    page = st.session_state.get("page", "chat")
    if page in ("desain", "jadwal"):
        return mode_thread(page)
    if page == "artefak":
        aid = st.session_state.get("artifact_active_id")
        if aid is not None:
            return artifact_thread(aid)
        return []
    if page == "kursus":
        cid = st.session_state.get("course_active_key")
        if cid:
            return course_thread(cid)
        return []
    return st.session_state.messages


def init_state() -> None:
    # Halaman awal bersih ala Claude: tanpa pesan sambutan,
    # hanya sapaan besar + input di tengah.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Daftar tugas untuk AI Penjadwal
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "task_counter" not in st.session_state:
        st.session_state.task_counter = 0
    # Halaman aktif (routing internal): chat / artefak / pengaturan / bahasa /
    # bantuan / tingkatkan / aplikasi / kursus / pelajari
    if "page" not in st.session_state:
        st.session_state.page = "chat"
    # Pengaturan lengkap (halaman Pengaturan, 9 tab)
    if "settings" not in st.session_state:
        st.session_state.settings = dict(DEFAULT_SETTINGS)
    # Artefak yang sedang dikerjakan (halaman Artefak) + thread kursusnya
    if "artifact_active_id" not in st.session_state:
        st.session_state.artifact_active_id = None
    if "artifact_counter" not in st.session_state:
        st.session_state.artifact_counter = 0
    if "course_active_key" not in st.session_state:
        st.session_state.course_active_key = None
    if "logged_out" not in st.session_state:
        st.session_state.logged_out = False
    if "selected_model_key" not in st.session_state:
        from config import DEFAULT_MODEL_KEY
        st.session_state.selected_model_key = DEFAULT_MODEL_KEY
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "web_search_on" not in st.session_state:
        st.session_state.web_search_on = False
    # Sesuaikan (custom instruction persona Yuki)
    if "custom_nickname" not in st.session_state:
        st.session_state.custom_nickname = ""
    if "custom_instruction" not in st.session_state:
        st.session_state.custom_instruction = ""
    # Proyek ringan: nama & catatan/instruksi khusus per proyek
    if "projects" not in st.session_state:
        st.session_state.projects = []  # list[{id, name}]
    if "project_counter" not in st.session_state:
        st.session_state.project_counter = 0
    if "active_project_id" not in st.session_state:
        st.session_state.active_project_id = None
    # Artefak: kode/tulisan panjang dari jawaban Yuki, dikumpulkan otomatis
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []  # list[{id, title, content, time}]
    # Lampiran yang di-stage lewat menu ➕ (menunggu dikirim bersama pesan)
    if "pending_images" not in st.session_state:
        st.session_state.pending_images = []
    if "plus_uploader_gen" not in st.session_state:
        st.session_state.plus_uploader_gen = 0
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    # Riwayat percakapan (untuk sidebar ala Claude)
    if "conversations" not in st.session_state:
        st.session_state.conversations = []  # list[{id, title, messages}]
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def _conversation_title(messages: list[dict]) -> str:
    """Judul percakapan = potongan pesan user pertama (ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"


def _archive_current_conversation() -> None:
    """Simpan obrolan aktif ke daftar riwayat (kalau ada isi dari user)."""
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        # update entri yang sudah ada
        for c in st.session_state.conversations:
            if c["id"] == conv_id:
                c["messages"] = msgs
                c["title"] = _conversation_title(msgs)
                return
    st.session_state.conv_counter += 1
    st.session_state.conversations.insert(0, {
        "id": st.session_state.conv_counter,
        "title": _conversation_title(msgs),
        "messages": msgs,
    })


def reset_conversation() -> None:
    """Chat baru: arsipkan obrolan utama, lalu kosongkan thread utama."""
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()
    st.session_state.page = "chat"


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.page = "chat"
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return
