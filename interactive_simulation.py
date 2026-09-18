# -*- coding: utf-8 -*-
"""Deteksi, prompt, dan parser simulasi HTML interaktif otomatis."""
from __future__ import annotations

import re


# Permintaan aktif untuk membuat simulasi.
_START = re.compile(
    r"\b(?:buatkan|buat|berikan|bikin|rancang|tampilkan)\b"
    r".{0,55}"
    r"\b(?:simulasi|visualisasi|digital\s+twin|sandbox)\b|"
    r"\b(?:simulasi|visualisasi)\b"
    r".{0,55}"
    r"\b(?:interaktif|real[ -]?time)\b",
    re.I | re.S,
)


# Permintaan roleplay tidak boleh dianggap simulator visual.
_ROLEPLAY = re.compile(
    r"\b(?:wawancara|interview|negosiasi|percakapan|bahasa|"
    r"pelanggan|role\s*play|bermain\s+peran|jadilah|"
    r"berpura-pura)\b",
    re.I,
)


# Pertanyaan informatif tidak menjalankan simulator.
_INFO = re.compile(
    r"^\s*(?:apa|apakah|jelaskan|pengertian|definisi|"
    r"bagaimana)\b",
    re.I,
)


# Blok khusus yang akan dihasilkan AI.
_BLOCK = re.compile(
    r"\[\[SIMULASI_HTML\]\]"
    r"\s*(.*?)\s*"
    r"\[\[/SIMULASI_HTML\]\]",
    re.S | re.I,
)


def _last_user_text(
    history: list[dict],
) -> str:
    """Ambil pesan terakhir pengguna."""
    return next(
        (
            str(
                message.get("content") or ""
            ).strip()

            for message in reversed(history)

            if message.get("role") == "user"
        ),
        "",
    )


def interactive_instruction(
    history: list[dict],
) -> str:
    """Buat instruksi HTML jika User meminta simulator."""
    text = _last_user_text(history)

    if not text:
        return ""

    # Pertanyaan pengetahuan biasa.
    if _INFO.search(text):
        return ""

    # Wawancara, negosiasi, dan percakapan ditangani
    # sistem roleplay, bukan simulator HTML.
    if _ROLEPLAY.search(text):
        return ""

    # Tidak ada permintaan aktif membuat simulasi.
    if not _START.search(text):
        return ""

    return """
USER MEMINTA SIMULASI VISUAL INTERAKTIF.

Buat simulator yang benar-benar dapat digunakan, bukan hanya
penjelasan, tutorial, daftar langkah, atau dialog.

KETENTUAN HASIL:
- Hasil wajib berupa SATU dokumen HTML lengkap.
- Gunakan HTML, CSS, dan JavaScript dalam satu dokumen.
- Simulator harus berjalan langsung di browser.
- Simulator harus responsif untuk HP dan desktop.
- Jangan membutuhkan backend.
- Jangan meminta API key.
- Jangan menggunakan eval().
- Jangan membaca cookie.
- Jangan menggunakan localStorage.
- Jangan membuat form login.
- Jangan mengirim data ke parent window.
- Hindari library eksternal.
- Utamakan JavaScript browser murni.
- Gunakan Canvas, SVG, atau elemen DOM sesuai kebutuhan.

INTERAKSI:
- Sediakan kontrol yang relevan.
- Kontrol dapat berupa slider, tombol, pilihan, atau input angka.
- Tampilkan perubahan nilai secara real-time.
- Visual harus berubah ketika parameter diubah.
- Sediakan tombol mulai, jeda, atau reset jika relevan.
- Berikan label yang jelas pada setiap kontrol.
- Berikan nilai awal yang masuk akal.

FORMAT WAJIB:
Tulis satu kalimat pengantar singkat, kemudian hasil HTML harus
dibungkus persis seperti ini:

[[SIMULASI_HTML]]
<!doctype html>
<html>
  ...seluruh HTML, CSS, dan JavaScript...
</html>
[[/SIMULASI_HTML]]

Jangan membungkus SIMULASI_HTML di dalam pagar Markdown.
Jangan menggunakan ```html.
Jangan membuat file Python.
Hanya penyintesis akhir yang boleh menghasilkan blok ini.
""".strip()


def extract_interactive_html(
    text: str,
) -> tuple[str, str]:
    """Pisahkan simulator HTML dari teks jawaban."""
    match = _BLOCK.search(
        text or ""
    )

    if not match:
        return text, ""

    html_document = (
        match.group(1).strip()
    )

    # Toleransi jika model masih menambahkan pagar Markdown.
    html_document = re.sub(
        r"^```(?:html)?\s*",
        "",
        html_document,
        flags=re.I,
    )

    html_document = re.sub(
        r"\s*```$",
        "",
        html_document,
    ).strip()

    clean_text = _BLOCK.sub(
        "",
        text,
        count=1,
    ).strip()

    if not clean_text:
        clean_text = (
            "Simulasi interaktif siap digunakan."
        )

    return clean_text, html_document
