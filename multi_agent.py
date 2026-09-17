# -*- coding: utf-8 -*-
"""Orkestrator Multi Trinity Agent untuk pengguna Trinity Pro."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from config import MODEL_CATALOG, MODEL_ID_TANPA_TEMPERATURE
from engines.compatible_engine import (
    PROVIDER_CONFIG,
    build_compatible_client,
)
from engines.groq_engine import build_chat_client


# Peran berbeda mencegah semua model memberi jawaban yang sama.
ROLES = {
    "gpt_oss_20b": (
        "Jawab inti masalah secara cepat, jelas, dan praktis."
    ),
    "compound_mini": (
        "Temukan konteks atau informasi penting yang terlewat."
    ),
    "llama4_scout": (
        "Analisis struktur masalah dan hubungan antarbagiannya."
    ),
    "plugsky_micro": (
        "Cari solusi paling sederhana yang dapat langsung dilakukan."
    ),
    "plugsky_lite": (
        "Berikan alternatif yang lebih efisien."
    ),
    "aion_rp": (
        "Nilai sudut pandang manusia, komunikasi, dan dampak "
        "ke pengguna."
    ),
    "aion_2": (
        "Periksa dampak keputusan dan risiko jangka menengah."
    ),
    "aion_3_mini": (
        "Audit detail teknis serta konsistensi logika."
    ),
    "aion_3": (
        "Bertindak sebagai kritikus; cari kesalahan dan asumsi lemah."
    ),
    "qwen3_6_27b": (
        "Uji penalaran, hitungan, dan ketepatan kesimpulan."
    ),
    "compound": (
        "Periksa kebutuhan fakta terbaru dan konteks eksternal."
    ),
    "finalrouter_deepseek_v4": (
        "Cari solusi mendalam yang belum dipertimbangkan."
    ),
    "gpt_oss_120b": (
        "Buat rekomendasi strategis tingkat lanjut."
    ),
    "finalrouter_gpt5_mini": (
        "Susun kerangka jawaban profesional dan lengkap."
    ),
}


AGENT_SYSTEM = """
Kamu adalah salah satu anggota panel Multi Trinity Agent.

Analisis permintaan User secara independen sesuai peranmu.

ATURAN:
- Jangan berbasa-basi.
- Fokus pada masalah yang ditanyakan.
- Tulis temuan, solusi, risiko, dan asumsi penting.
- Periksa kemungkinan kesalahan.
- Jika benar-benar diperlukan, berikan satu pertanyaan klarifikasi.
- Jangan mengaku sebagai jawaban akhir.
- Hasilmu akan diperiksa dan disatukan oleh model penyintesis.
"""


SYNTHESIS_SYSTEM = """
Kamu adalah Ketua Multi Trinity Agent.

Tugasmu menggabungkan laporan dari seluruh panel menjadi SATU jawaban
profesional dalam bahasa yang digunakan User.

ATURAN:
- Utamakan kebenaran, relevansi, dan tindakan konkret.
- Hilangkan pengulangan.
- Jangan menyebut nama model atau proses internal.
- Jangan mengatakan bahwa jawaban dibuat oleh beberapa AI.
- Selesaikan kontradiksi menggunakan penalaran terbaik.
- Jangan mengarang fakta yang tidak didukung laporan atau konteks.
- Bedakan fakta, asumsi, dan rekomendasi.
- Berikan jawaban utama terlebih dahulu.
- Tambahkan langkah atau saran konkret bila relevan.
- Jelaskan risiko atau catatan penting bila ada.
- Berikan maksimal satu pertanyaan lanjutan.
- Jangan bertanya jika permintaan User sudah jelas.
"""


def _provider_ready(provider: str) -> bool:
    """Periksa apakah API key provider tersedia."""
    if provider == "groq":
        try:
            from config import GROQ_API_KEY

            return bool(GROQ_API_KEY)
        except Exception:
            return False

    konfigurasi = PROVIDER_CONFIG.get(provider) or {}

    return bool(konfigurasi.get("api_key"))


def _client(provider: str):
    """Buat client sesuai provider model."""
    if provider == "groq":
        return build_chat_client()

    return build_compatible_client(provider)


def _messages(
    history: list[dict],
    role: str,
) -> list[dict]:
    """Susun riwayat yang dikirim kepada satu anggota panel."""
    messages = [
        {
            "role": "system",
            "content": (
                AGENT_SYSTEM
                + "\n\nPERAN KHUSUSMU:\n"
                + role
            ),
        }
    ]

    # Batasi riwayat agar pemakaian token tidak terlalu besar.
    for item in history[-12:]:
        message_role = item.get("role")
        content = item.get("content")

        if message_role not in ("user", "assistant"):
            continue

        if not content:
            continue

        messages.append(
            {
                "role": message_role,
                "content": str(content),
            }
        )

    return messages


def _ask_one(
    model: dict,
    history: list[dict],
) -> tuple[str, str]:
    """Kirim pertanyaan kepada satu model."""
    provider = model.get("provider", "groq")

    if not _provider_ready(provider):
        raise RuntimeError(
            f"Provider {provider} belum dikonfigurasi."
        )

    params = {
        "model": model["id"],
        "messages": _messages(
            history,
            ROLES.get(
                model["key"],
                "Analisis masalah secara kritis.",
            ),
        ),
        "stream": False,

        # Jawaban anggota panel tidak perlu terlalu panjang.
        "max_tokens": 700,
    }

    if model["id"] not in MODEL_ID_TANPA_TEMPERATURE:
        params["temperature"] = 0.45

    client = _client(provider)

    response = client.chat.completions.create(**params)

    text = (
        response.choices[0].message.content or ""
    ).strip()

    if not text:
        raise RuntimeError("Model menghasilkan jawaban kosong.")

    return model["name"], text


def _synthesize(
    history: list[dict],
    reports: list[tuple[str, str]],
) -> str:
    """Satukan seluruh hasil panel menjadi satu jawaban."""
    # Katalog dibalik agar model dengan tingkatan tertinggi
    # diprioritaskan sebagai penyintesis.
    candidates = list(reversed(MODEL_CATALOG))

    chosen = next(
        (
            model
            for model in candidates
            if _provider_ready(
                model.get("provider", "groq")
            )
        ),
        None,
    )

    if chosen is None:
        raise RuntimeError(
            "Tidak ada provider AI yang dikonfigurasi."
        )

    reports_text = "\n\n".join(
        (
            f"LAPORAN PANEL {index + 1}:\n"
            f"{text}"
        )
        for index, (_, text) in enumerate(reports)
    )

    user_last = next(
        (
            str(message.get("content"))
            for message in reversed(history)
            if message.get("role") == "user"
        ),
        "",
    )

    messages = [
        {
            "role": "system",
            "content": SYNTHESIS_SYSTEM,
        },
        {
            "role": "user",
            "content": (
                "PERTANYAAN USER:\n"
                f"{user_last}\n\n"
                "HASIL ANALISIS PANEL:\n"
                f"{reports_text}"
            ),
        },
    ]

    params = {
        "model": chosen["id"],
        "messages": messages,
        "stream": False,
        "max_tokens": 1500,
    }

    if chosen["id"] not in MODEL_ID_TANPA_TEMPERATURE:
        params["temperature"] = 0.35

    provider = chosen.get("provider", "groq")
    client = _client(provider)

    response = client.chat.completions.create(**params)

    answer = (
        response.choices[0].message.content or ""
    ).strip()

    return answer


def run_multi_agent(history: list[dict]) -> dict:
    """Jalankan seluruh model secara paralel dan sintesis hasilnya."""
    reports: list[tuple[str, str]] = []
    failures: list[str] = []

    worker_count = min(
        14,
        len(MODEL_CATALOG),
    )

    with ThreadPoolExecutor(
        max_workers=worker_count
    ) as executor:
        jobs = {
            executor.submit(
                _ask_one,
                model,
                history,
            ): model
            for model in MODEL_CATALOG
        }

        for future in as_completed(jobs):
            model = jobs[future]

            try:
                reports.append(future.result())
            except Exception:
                # Model yang gagal tidak menghentikan panel.
                failures.append(model["name"])

    if not reports:
        raise RuntimeError(
            "Semua model gagal merespons. "
            "Periksa API key dan kuota provider."
        )

    answer = _synthesize(
        history,
        reports,
    )

    if not answer:
        raise RuntimeError(
            "Penyintesis menghasilkan jawaban kosong."
        )

    return {
        "answer": answer,
        "success": len(reports),
        "failed": failures,
        "total": len(MODEL_CATALOG),
    }
