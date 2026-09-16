# -*- coding: utf-8 -*-
"""
PENAMBAL — perbaiki stream_chat_reply() di engines/groq_engine.py.

Gejala yang diperbaiki:

    SyntaxError / IndentationError di engines/groq_engine.py
    saat app.py mengimpor chat_handlers.

Penyebabnya: saat mengganti stream_chat_reply() secara manual, bagian
ATAS fungsi tertimpa versi baru tapi SISA argumen versi lama tertinggal
di bawahnya:

    stream = client.chat.completions.create(**kwargs)
        temperature=float(...),      <-- sisa versi lama
        stream=True,                 <-- sisa versi lama
    )                                <-- sisa versi lama

Python melihat baris menjorok yang tidak menempel ke apa pun.

Skrip ini menulis ulang SELURUH fungsi stream_chat_reply() dengan versi
yang benar, jadi sisa potongan apa pun ikut tersapu.

Cara pakai — dari folder root repo:

    python patch_tampilan/perbaiki_groq_engine.py
"""

from __future__ import annotations

import os
import py_compile
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "engines", "groq_engine.py")

FUNGSI_BENAR = '''def stream_chat_reply(client: OpenAI, model: str, history: list[dict],
                      vision: bool = False):
    kwargs: dict = {
        "model": model,
        "messages": messages_for_api(history),
        # Suhu jawaban (0,3 = kaku, 1,2 = liar); default 0,7 dari
        # DEFAULT_SETTINGS. Dibaca tiap request supaya perubahan langsung terasa.
        "temperature": float(get_settings().get("temperature", 0.7)),
        "stream": True,
    }
    # Permintaan bergambar dibatasi keluarannya. Tanpa ini, Groq memakai
    # perkiraan bawaan 2.048 token yang MELEBIHI jatah OTPM tier gratis
    # (1.000/menit), sehingga ditolak 429 "Request too large" — padahal
    # jawabannya sendiri belum tentu sepanjang itu.
    if vision:
        kwargs["max_tokens"] = VISION_MAX_TOKENS
    stream = client.chat.completions.create(**kwargs)
    for chunk in stream:
        try:
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None)
            if piece:
                yield piece
        except Exception:
            continue

'''


def gagal(pesan: str) -> None:
    print(f"\n  GAGAL: {pesan}\n")
    sys.exit(1)


def main() -> None:
    print("\n=== Perbaiki engines/groq_engine.py ===\n")

    if not os.path.exists(TARGET):
        gagal("engines/groq_engine.py tidak ditemukan. "
              "Jalankan dari folder root repo.")

    src = open(TARGET, encoding="utf-8").read()
    shutil.copy(TARGET, TARGET + ".bak")
    print("  cadangan  : engines/groq_engine.py.bak")

    # --- 1. import VISION_MAX_TOKENS ---------------------------------
    if "VISION_MAX_TOKENS" in src.split("def ")[0]:
        print("  [lewat]   import VISION_MAX_TOKENS sudah ada")
    else:
        jangkar = "MAX_IMAGES_PER_MESSAGE, STT_MODEL, VISION_MODEL_FALLBACKS,"
        if jangkar not in src:
            gagal("blok 'from config import (...)' tidak dikenali.")
        src = src.replace(jangkar, jangkar + "\n    VISION_MAX_TOKENS,", 1)
        print("  [ok]      import VISION_MAX_TOKENS")

    # --- 2. tulis ulang stream_chat_reply ----------------------------
    # Diambil dari 'def stream_chat_reply' sampai tepat sebelum
    # 'def stream_chat_with_fallback' — apa pun isinya di antara itu
    # (termasuk sisa potongan rusak) diganti seluruhnya.
    mulai = src.find("def stream_chat_reply(")
    if mulai == -1:
        gagal("fungsi stream_chat_reply() tidak ditemukan.")
    akhir = src.find("def stream_chat_with_fallback(", mulai)
    if akhir == -1:
        gagal("fungsi stream_chat_with_fallback() tidak ditemukan.")

    src = src[:mulai] + FUNGSI_BENAR + src[akhir:]
    print("  [ok]      stream_chat_reply() ditulis ulang")

    # --- 3. teruskan vision=vision ke pemanggil ----------------------
    lama = "stream_iter = stream_chat_reply(client, model, history)"
    baru = ("stream_iter = stream_chat_reply(client, model, history,\n"
            "                                            vision=vision)")
    if lama in src:
        src = src.replace(lama, baru, 1)
        print("  [ok]      teruskan vision=vision")
    elif "vision=vision)" in src:
        print("  [lewat]   vision=vision sudah diteruskan")
    else:
        print("  [!]       pemanggil stream_chat_reply tidak dikenali "
              "— periksa manual")

    # --- tulis & verifikasi ------------------------------------------
    open(TARGET, "w", encoding="utf-8").write(src)
    try:
        py_compile.compile(TARGET, doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy(TARGET + ".bak", TARGET)
        gagal(f"hasil tidak lolos kompilasi:\n{e}\n"
              "File sudah dikembalikan dari cadangan.")

    print("\n  SELESAI — engines/groq_engine.py lolos kompilasi.")
    print("  Jalankan ulang aplikasinya.\n")


if __name__ == "__main__":
    main()
