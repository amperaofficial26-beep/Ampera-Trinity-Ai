# -*- coding: utf-8 -*-
"""Orkestrator Multi Trinity Agent untuk pengguna Trinity Pro."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    MODEL_CATALOG,
    MODEL_ID_TANPA_TEMPERATURE,
)
from engines.compatible_engine import (
    PROVIDER_CONFIG,
    build_compatible_client,
)
from engines.groq_engine import build_chat_client


# Batas token anggota panel.
PANEL_MAX_TOKENS = 2048

# Batas token retry anggota panel.
PANEL_RETRY_MAX_TOKENS = 4096

# Batas token penyusunan jawaban akhir.
SYNTHESIS_MAX_TOKENS = 4096

# Batas token retry penyusunan jawaban akhir.
SYNTHESIS_RETRY_MAX_TOKENS = 8192

# Jumlah riwayat terakhir yang dikirim kepada setiap model.
MAX_AGENT_HISTORY = 12


# Setiap model mendapat peran berbeda agar hasil panel tidak
# hanya berisi jawaban yang sama berulang kali.
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
        "Cari solusi paling sederhana yang bisa langsung dilakukan."
    ),
    "plugsky_lite": (
        "Berikan alternatif solusi yang lebih efisien."
    ),
    "aion_rp": (
        "Nilai sudut pandang manusia, komunikasi, "
        "dan dampak kepada pengguna."
    ),
    "aion_2": (
        "Periksa dampak keputusan dan risiko jangka menengah."
    ),
    "aion_3_mini": (
        "Audit detail teknis serta konsistensi logika."
    ),
    "aion_3": (
        "Bertindak sebagai kritikus; cari kesalahan, "
        "kelemahan, dan asumsi yang tidak kuat."
    ),
    "qwen3_6_27b": (
        "Uji penalaran, perhitungan, dan ketepatan kesimpulan."
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

Analisis permintaan User secara independen sesuai peran khususmu.

ATURAN:
- Jangan berbasa-basi.
- Fokus hanya pada permintaan User.
- Pahami konteks percakapan sebelum menjawab.
- Tulis temuan, solusi, risiko, dan asumsi penting.
- Periksa kemungkinan kesalahan pada solusi.
- Untuk permintaan kode, berikan rancangan atau potongan kode yang valid.
- Jika informasi belum cukup, sebutkan informasi apa yang diperlukan.
- Jangan mengaku sebagai jawaban akhir.
- Jangan menyebut proses internal panel.
- Hasilmu akan diperiksa dan disatukan oleh model penyintesis.
""".strip()


SYNTHESIS_SYSTEM = """
Kamu adalah Ketua Multi Trinity Agent.

Tugasmu menggabungkan laporan seluruh anggota panel menjadi SATU jawaban
profesional dalam bahasa yang digunakan User.

ATURAN UTAMA:
- Jawab permintaan User secara langsung.
- Utamakan kebenaran, relevansi, dan tindakan konkret.
- Hilangkan pengulangan dari laporan panel.
- Perbaiki kesalahan yang ditemukan dalam laporan.
- Selesaikan kontradiksi dengan penalaran terbaik.
- Jangan menyebut nama model.
- Jangan menyebut jumlah model.
- Jangan membicarakan proses internal panel.
- Jangan mengarang fakta yang tidak didukung laporan atau konteks.
- Bedakan fakta, asumsi, dan rekomendasi.
- Berikan langkah praktis jika relevan.
- Sebutkan risiko atau catatan penting jika memang ada.
- Berikan maksimal satu pertanyaan lanjutan.
- Jangan bertanya jika permintaan User sudah jelas.

ATURAN KHUSUS KODE:
- Jika User meminta dibuatkan kode, berikan kode lengkap dan siap digunakan.
- Jangan hanya memberi rancangan apabila User meminta hasil jadi.
- Gunakan blok kode Markdown dengan bahasa yang sesuai.
- Pastikan kode memiliki struktur yang valid.
- Berikan cara menjalankan secara singkat.
- Jangan memotong kode hanya untuk menghemat jawaban.
""".strip()


def _provider_ready(provider: str) -> bool:
    """Periksa apakah API key provider tersedia."""
    if provider == "groq":
        try:
            from config import GROQ_API_KEY

            return bool(GROQ_API_KEY)

        except Exception:
            return False

    provider_config = (
        PROVIDER_CONFIG.get(provider) or {}
    )

    return bool(
        provider_config.get("api_key")
    )


def _client(provider: str):
    """Bangun client API berdasarkan provider."""
    if provider == "groq":
        return build_chat_client()

    return build_compatible_client(provider)


def _is_token_error(exc: Exception) -> bool:
    """Periksa apakah error disebabkan batas output token."""
    error_text = str(exc).lower()

    token_error_markers = (
        "max_tokens",
        "max_completion_tokens",
        "output budget",
        "output token",
        "needed more than",
        "token limit",
        "completion limit",
        "maximum context length",
    )

    return any(
        marker in error_text
        for marker in token_error_markers
    )


def _history_messages(
    history: list[dict],
) -> list[dict]:
    """Ambil riwayat teks yang aman dikirim ke model."""
    messages: list[dict] = []

    for item in history[-MAX_AGENT_HISTORY:]:
        role = item.get("role")
        content = item.get("content")

        if role not in ("user", "assistant"):
            continue

        if not content:
            continue

        messages.append(
            {
                "role": role,
                "content": str(content),
            }
        )

    return messages


def _messages(
    history: list[dict],
    role: str,
    simulasi: str = "",
) -> list[dict]:
    """Susun pesan untuk satu anggota panel."""
    system_prompt = (
        AGENT_SYSTEM
        + "\n\nPERANMU: "
        + role
    )

    if simulasi:
        system_prompt += (
            "\n\n"
            + simulasi
        )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    for item in history[-12:]:
        if (
            item.get("role")
            not in ("user", "assistant")
        ):
            continue

        if not item.get("content"):
            continue

        messages.append(
            {
                "role": item["role"],
                "content": str(
                    item["content"]
                ),
            }
        )

    return messages
    

def _ask_one(
    model: dict,
    history: list[dict],
    simulasi: str = "",
) -> tuple[str, str]:
    """Kirim pertanyaan kepada satu anggota panel."""
    provider = model.get(
        "provider",
        "groq",
    )

    if not _provider_ready(provider):
        raise RuntimeError(
            f"Provider {provider} belum dikonfigurasi."
        )

    model_key = model.get("key") or ""

    agent_role = ROLES.get(
        model_key,
        "Analisis masalah secara kritis dan objektif.",
    )

    params = {
        "model": model["id"],
        "messages": _messages(
            history,
            ROLES.get(
                model["key"],
                "Analisis masalah secara kritis.",
            ),
            simulasi,
        ),
        "stream": False,

        # Model reasoning memakai sebagian budget token
        # untuk proses berpikir internal.
        "max_tokens": PANEL_MAX_TOKENS,
    }

    if (
        model["id"]
        not in MODEL_ID_TANPA_TEMPERATURE
    ):
        params["temperature"] = 0.45

    client = _client(provider)

    response = _create_completion_with_retry(
        client=client,
        params=params,
        retry_max_tokens=PANEL_RETRY_MAX_TOKENS,
    )

    text = (
        response.choices[0].message.content or ""
    ).strip()

    if not text:
        raise RuntimeError(
            "Model menghasilkan jawaban kosong."
        )

    return model["name"], text


def _reports_text(
    reports: list[tuple[str, str]],
) -> str:
    """Gabungkan laporan tanpa memperlihatkan nama model."""
    return "\n\n".join(
        (
            f"LAPORAN PANEL {index + 1}:\n"
            f"{text}"
        )
        for index, (_, text)
        in enumerate(reports)
    )


def _last_user_message(
    history: list[dict],
) -> str:
    """Ambil pertanyaan terakhir User."""
    return next(
        (
            str(message.get("content") or "")
            for message in reversed(history)
            if message.get("role") == "user"
        ),
        "",
    )


def _select_synthesis_model() -> dict:
    """Pilih model tertinggi dengan provider yang tersedia."""
    candidates = list(
        reversed(MODEL_CATALOG)
    )

    selected = next(
        (
            model
            for model in candidates
            if _provider_ready(
                model.get(
                    "provider",
                    "groq",
                )
            )
        ),
        None,
    )

    if selected is None:
        raise RuntimeError(
            "Tidak ada provider AI yang dikonfigurasi."
        )

    return selected


def _synthesize(
    history: list[dict],
    reports: list[tuple[str, str]],
    simulasi: str = "",
) -> str:
    """Satukan seluruh laporan panel menjadi satu jawaban akhir."""
    chosen = _select_synthesis_model()

    user_question = _last_user_message(
        history
    )

    panel_reports = _reports_text(
        reports
    )

    # Buat system prompt sebelum dipakai di dalam messages.
    synthesis_prompt = SYNTHESIS_SYSTEM

    if simulasi:
        synthesis_prompt += (
            "\n\n"
            + simulasi
        )

    messages = [
        {
            "role": "system",
            "content": synthesis_prompt,
        },
        {
            "role": "user",
            "content": (
                "PERTANYAAN USER:\n"
                f"{user_question}\n\n"
                "HASIL ANALISIS PANEL:\n"
                f"{panel_reports}"
            ),
        },
    ]

    params = {
        "model": chosen["id"],
        "messages": messages,
        "stream": False,

        # Model reasoning menggunakan sebagian token
        # untuk proses berpikir internal.
        "max_tokens": SYNTHESIS_MAX_TOKENS,
    }

    if (
        chosen["id"]
        not in MODEL_ID_TANPA_TEMPERATURE
    ):
        params["temperature"] = 0.35

    provider = chosen.get(
        "provider",
        "groq",
    )

    client = _client(
        provider
    )

    response = _create_completion_with_retry(
        client=client,
        params=params,
        retry_max_tokens=(
            SYNTHESIS_RETRY_MAX_TOKENS
        ),
    )

    answer = (
        response.choices[0].message.content
        or ""
    ).strip()

    if not answer:
        raise RuntimeError(
            "Model penyintesis tidak menghasilkan jawaban."
        )

    return answer


def run_multi_agent(
    history: list[dict],
) -> dict:
    """Panggil semua model paralel lalu sintesis hasilnya."""
    reports: list[tuple[str, str]] = []
    failures: list[str] = []
    # Deteksi dilakukan pada thread utama.
    # Worker model tidak boleh mengubah session_state.
    from simulation import simulation_instruction
    from interactive_simulation import (
        interactive_instruction,
    )

    roleplay_prompt = simulation_instruction(
        history,
        room="multi_agent",
    )

    interactive_prompt = interactive_instruction(
        history
    )

    instructions = [
        roleplay_prompt,
        interactive_prompt,
    ]

    simulasi = "\n\n".join(
        instruction
        for instruction in instructions
        if instruction
    )
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
                simulasi,
            ): model
        
            for model in MODEL_CATALOG
        }

        for future in as_completed(jobs):
            model = jobs[future]

            try:
                result = future.result()
                reports.append(result)

            except Exception:
                # Satu model gagal tidak menghentikan seluruh panel.
                failures.append(
                    model["name"]
                )

    if not reports:
        raise RuntimeError(
            "Semua model gagal merespons. "
            "Periksa API key, kuota, dan status provider."
        )

    answer = _synthesize(
        history=history,
        reports=reports,
        simulasi=simulasi,
    )

    return {
        "answer": answer,
        "success": len(reports),
        "failed": failures,
        "total": len(MODEL_CATALOG),
    }
