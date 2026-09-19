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
    r"\[\[SIMULASI_HTML\]\]\s*(.*?)\s*\[\[/SIMULASI_HTML\]\]",
    re.S | re.I,
)
_OPEN_BLOCK = re.compile(
    r"\[\[SIMULASI_HTML\]\]\s*(.*?</html\s*>)",
    re.S | re.I,
)
_RAW_HTML = re.compile(
    r"(?:```html\s*)?(<!doctype\s+html\b.*?</html\s*>)(?:\s*```)?",
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


def is_interactive_request(history: list[dict]) -> bool:
    """Periksa apakah pesan user terakhir meminta simulator visual."""
    text = next(
        (
            str(message.get("content") or "").strip()
            for message in reversed(history)
            if message.get("role") == "user"
        ),
        "",
    )
    return bool(
        text
        and not _INFO.search(text)
        and not _ROLEPLAY.search(text)
        and _START.search(text)
    )


def interactive_instruction(history: list[dict]) -> str:
    """Kembalikan instruksi HTML hanya jika pesan terakhir meminta simulator."""
    if not is_interactive_request(history):
        return ""

    return """

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
Buat kode seringkas mungkin: maksimal 180 baris, tanpa komentar panjang, tanpa
penjelasan langkah kerja, dan tanpa kode yang tidak dipakai. Setelah satu
pengantar singkat, bungkus HTML persis dengan:
[[SIMULASI_HTML]]
<!doctype html>...seluruh kode...
[[/SIMULASI_HTML]]
Marker penutup wajib ditulis segera setelah </html>; jangan menulis apa pun
setelah marker penutup. Jangan pakai pagar Markdown ``` atau membuat file
Python. Hanya penyintesis akhir yang boleh menghasilkan blok ini.
""".strip()


def extract_interactive_html(
    text: str,
    *,
    allow_raw: bool = False,
) -> tuple[str, str]:
    """Pisahkan blok simulator atau HTML mentah dari model yang tidak patuh."""
    source = text or ""
    match = _BLOCK.search(source)
    complete_marker = match is not None
    raw_html = False

    # Beberapa provider memutus stream tepat setelah dokumen HTML selesai,
    # sebelum marker penutup terkirim. Dokumen tetap aman dipakai jika sudah
    # memiliki </html>; JavaScript yang benar-benar terpotong tidak diterima.
    if match is None:
        match = _OPEN_BLOCK.search(source)

    # GPT-5 Mini/Trinity Sovereign kadang mengabaikan marker dan langsung
    # mengirim dokumen HTML. Terima bentuk itu hanya ketika pesan user memang
    # terdeteksi sebagai permintaan simulator, bukan pada permintaan kode biasa.
    if match is None and allow_raw:
        match = _RAW_HTML.search(source)
        raw_html = match is not None

    if match is None:
        return text, ""

    html_doc = match.group(1).strip()
    html_doc = re.sub(r"^```(?:html)?\s*", "", html_doc, flags=re.I)
    html_doc = re.sub(r"\s*```$", "", html_doc).strip()

    if complete_marker:
        clean = _BLOCK.sub("", source, count=1).strip()
    elif raw_html:
        clean = (source[:match.start()] + source[match.end():]).strip()
    else:
        clean = source[:match.start()].strip()

    return clean or "Simulasi interaktif siap digunakan.", html_doc
