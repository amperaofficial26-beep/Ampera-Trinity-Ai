# -*- coding: utf-8 -*-
"""Deteksi otomatis dan konteks simulasi percakapan/roleplay."""
from __future__ import annotations

import re

import streamlit as st


# Pola permintaan yang benar-benar meminta simulasi dimulai.
_START_RE = re.compile(
    r"\b(?:buatkan|buat|mulai(?:kan)?|berikan|beri|ayo|mari|"
    r"coba|lakukan)\b.{0,45}"
    r"\b(?:contoh\s+)?(?:simulasi|role\s*play|"
    r"bermain\s+peran|latihan)\b|"
    r"\b(?:jadilah|jadi|berpura-puralah|berperanlah|"
    r"bertindaklah)\s+sebagai\b",
    re.I | re.S,
)


# Pola perintah untuk mengakhiri simulasi.
_STOP_RE = re.compile(
    r"\b(?:akhiri|hentikan|stop|selesai(?:kan)?|"
    r"keluar(?:lah)?\s+dari|berhenti)\b.{0,25}"
    r"\b(?:simulasi|role\s*play|bermain\s+peran|latihan)\b|"
    r"\b(?:kembali\s+ke\s+chat\s+biasa|"
    r"keluar\s+dari\s+karakter)\b",
    re.I | re.S,
)


# Pertanyaan informatif tidak boleh mengaktifkan simulasi.
#
# Contoh:
# "Apa itu simulasi wawancara?"
# harus dijawab normal, bukan memulai roleplay.
_INFO_RE = re.compile(
    r"^\s*(?:apa|apakah|jelaskan|pengertian|definisi|"
    r"manfaat|fungsi|beda|perbedaan|"
    r"bagaimana\s+cara\s+kerja)\b",
    re.I,
)
_CONVERSATION_RE = re.compile(
    r"\b(?:"
    r"wawancara|"
    r"interview|"
    r"negosiasi|"
    r"percakapan|"
    r"bahasa|"
    r"pelanggan|"
    r"komplain|"
    r"pewawancara|"
    r"guru|"
    r"mentor|"
    r"customer|"
    r"role\s*play|"
    r"bermain\s+peran|"
    r"jadilah|"
    r"berpura-pura|"
    r"berperan"
    r")\b",
    re.IGNORECASE,
)

def _room_key(room: str) -> str:
    """Tentukan kunci state berdasarkan room."""
    safe_room = (
        "multi_agent"
        if room == "multi_agent"
        else "chat"
    )

    return f"{safe_room}_simulation_context"


def _last_user_text(
    history: list[dict],
) -> str:
    """Ambil pesan User terakhir."""
    return next(
        (
            str(
                message.get("content") or ""
            ).strip()

            for message in reversed(history)

            if (
                message.get("role") == "user"
                and message.get("content")
            )
        ),
        "",
    )


def update_simulation_context(
    history: list[dict],
    room: str = "chat",
) -> dict | None:
    """Aktifkan atau akhiri roleplay dari pesan terakhir.

    Konteks Chat biasa dan Multi Trinity Agent disimpan terpisah
    agar simulasi di satu room tidak memengaruhi room lainnya.
    """
    key = _room_key(room)

    text = _last_user_text(history)

    current = st.session_state.get(key)

    if not text:
        if (
            isinstance(current, dict)
            and current.get("active")
        ):
            return current

        return None

    # Pengguna meminta simulasi diakhiri.
    if _STOP_RE.search(text):
        st.session_state.pop(
            key,
            None,
        )

        return None

    # Pertanyaan informatif tidak mengaktifkan simulasi.
    informative_question = bool(
        _INFO_RE.search(text)
    )

    start_request = bool(
        _START_RE.search(text)
    )

    conversation_request = bool(
        _CONVERSATION_RE.search(text)
    )

    if (
        not informative_question
        and start_request
        and conversation_request
    ):
        current = {
            "active": True,

            # Simpan permintaan awal agar model mempertahankan
            # skenario pada pesan-pesan selanjutnya.
            "scenario": " ".join(
                text.split()
            )[:700],
        }

        st.session_state[key] = current

    if (
        isinstance(current, dict)
        and current.get("active")
    ):
        return current

    return None


def simulation_instruction(
    history: list[dict],
    room: str = "chat",
) -> str:
    """Buat prompt tambahan untuk simulasi yang sedang aktif."""
    context = update_simulation_context(
        history,
        room,
    )

    if not context:
        return ""

    scenario = (
        context.get("scenario")
        or "simulasi percakapan yang diminta User"
    )

    return f"""
MODE SIMULASI PERCAKAPAN AKTIF.

Permintaan awal User:
{scenario}

ATURAN WAJIB:
- Masuk ke peran yang diminta dan pertahankan karakter pada
  giliran berikutnya.
- Jalankan simulasi secara interaktif, SATU giliran percakapan
  pada satu waktu.
- Jangan menulis seluruh dialog kedua pihak sekaligus, kecuali
  User meminta contoh naskah lengkap.
- Beri situasi dan ucapan karakter secara ringkas, lalu tunggu
  respons User.
- Bersikap realistis sesuai skenario, tingkat pengalaman, dan
  tujuan User.
- Jangan keluar dari karakter untuk menjelaskan teori, kecuali
  User meminta evaluasi atau bantuan.
- Jika User meminta evaluasi, berhenti sejenak dari karakter,
  lalu beri penilaian konkret dan saran perbaikan.
- Jika User meminta simulasi diakhiri, akhiri dengan ringkasan
  singkat lalu kembali ke percakapan normal.
- Jangan mengklaim simulasi ini sebagai kejadian nyata.
""".strip()
