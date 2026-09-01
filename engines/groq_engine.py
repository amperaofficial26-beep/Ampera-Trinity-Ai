# -*- coding: utf-8 -*-
"""
ENGINE 1 & 3: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
          + SUARA & GAMBAR MASUK (Whisper STT, siapkan gambar utk vision)
"""

from __future__ import annotations

import base64
import io

import streamlit as st
from PIL import Image

# Impor pustaka openai dibuat "tahan banting": kalau paketnya gagal dimuat
# (mis. versi Python di server terlalu baru sehingga wheel pydantic-core
# belum tersedia), aplikasi TETAP jalan dan fitur gambar tetap bisa dipakai.
# Sebelumnya kegagalan di sini membuat seluruh app.py crash saat import
# dengan pesan menyesatkan: KeyError: 'engines.groq_engine'.
try:
    from openai import OpenAI
except Exception as _exc:  # pragma: no cover
    OpenAI = None
    OPENAI_IMPORT_ERROR: Exception | None = _exc
else:
    OPENAI_IMPORT_ERROR = None
from config import (
    GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL_FALLBACKS, MAX_HISTORY_MESSAGES,
    MAX_IMAGES_PER_MESSAGE, STT_MODEL, VISION_MODEL_FALLBACKS,
    VISION_RECENT_MESSAGES, YUKI_SYSTEM_PROMPT, LANG_BY_CODE, DEFAULT_LANG_CODE,
    CLARIFY_RULES, CLARIFY_MODE_RULES,
)
from errors import _is_model_unavailable_error
from state import get_settings


def build_chat_client():
    if OpenAI is None:
        raise RuntimeError(
            "Pustaka 'openai' gagal dimuat di server "
            f"({type(OPENAI_IMPORT_ERROR).__name__}: {OPENAI_IMPORT_ERROR}). "
            "Fitur chat sementara tidak tersedia."
        )
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def build_system_prompt() -> str:
    """Gabungkan persona dasar Yuki + preferensi dari halaman "Sesuaikan",
    Pengaturan (kepribadian, bahasa, memori, refleksi), dan konteks mode."""
    s = get_settings()
    parts = [YUKI_SYSTEM_PROMPT]

    persona_map = {
        "Santai & kocak": "Pertahankan gaya santai, kocak, dan penuh candaan receh.",
        "Serius & ringkas": (
            "Kurangi candaan. Jawab ringkas, langsung ke inti, "
            "pakai poin-poin bila perlu."
        ),
        "Mentor sabar": (
            "Bersikaplah seperti mentor yang sabar: jelaskan langkah demi "
            "langkah, beri contoh, dan cek pemahaman User."
        ),
        "Profesional formal": (
            "Gunakan bahasa Indonesia formal dan profesional, "
            "tanpa emoji berlebihan."
        ),
    }
        if s.get("personality") in persona_map:
        parts.append(persona_map[s["personality"]])

    # Aturan bertanya balik: hanya untuk permintaan yang benar-benar kabur.
    # Mode "Mati" mengganti aturan itu dengan larangan bertanya.
    clarify_mode = s.get("clarify_mode", "Seperlunya")
    if clarify_mode == "Mati":
        parts.append(CLARIFY_MODE_RULES["Mati"])
    else:
        parts.append(CLARIFY_RULES)
        extra = CLARIFY_MODE_RULES.get(clarify_mode, "")
        if extra:
            parts.append(extra)
                  
    lang = LANG_BY_CODE.get(s.get("yuki_lang") or DEFAULT_LANG_CODE)
    if lang and lang["code"] != "id":
        parts.append(f"Selalu jawab dalam bahasa {lang['name']}.")

    nickname = (st.session_state.get("custom_nickname") or "").strip()
    if nickname:
        parts.append(f"Panggil User dengan sebutan: {nickname}.")

    display_name = (s.get("display_name") or "").strip()
    if display_name and display_name.lower() != "user":
        parts.append(f"Nama User adalah {display_name}.")

    if s.get("memory_on"):
        facts = [str(f).strip() for f in (s.get("memories") or []) if str(f).strip()]
        if facts:
            parts.append(
                "MEMORI JANGKA PANJANG tentang User (pakai seperlunya, "
                "jangan disebut satu per satu):\n- " + "\n- ".join(facts)
            )

    goal = (s.get("reflection_goal") or "").strip()
    habit = (s.get("reflection_habit") or "").strip()
    if goal or habit:
        refl = []
        if goal:
            refl.append(f"Target: {goal}")
        if habit:
            refl.append(f"Kebiasaan yang dilatih: {habit}")
        parts.append(
            "REFLEKSI USER — dukung dia mencapai ini, sesekali tanyakan "
            "kemajuannya:\n" + "\n".join(refl)
        )

    extra = (st.session_state.get("custom_instruction") or "").strip()
    if extra:
        parts.append(f"Instruksi tambahan dari User yang harus selalu diikuti:\n{extra}")
    return "\n\n".join(parts)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier).
    Pesan yang membawa gambar dikirim sebagai konten multimodal (vision),
    tapi hanya untuk beberapa pesan terakhir agar token tetap hemat."""
    trimmed = [
        m for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    msgs: list[dict] = [{"role": "system", "content": build_system_prompt()}]
    n = len(trimmed)
    for i, m in enumerate(trimmed):
        imgs = m.get("images") or []
        if imgs and i >= n - VISION_RECENT_MESSAGES:
            text_part = (m.get("content") or "").strip() or "Tolong analisis gambar ini ya."
            parts: list[dict] = [{"type": "text", "text": text_part}]
            for im in imgs:
                b64 = base64.b64encode(im["data"]).decode("ascii")
                parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{im['mime']};base64,{b64}"},
                })
            msgs.append({"role": m["role"], "content": parts})
        else:
            msgs.append({"role": m["role"], "content": m.get("content") or ""})
    return msgs


def resolve_model_chain(preferred: str, vision: bool = False) -> list[str]:
    base = VISION_MODEL_FALLBACKS if vision else (preferred, *GROQ_MODEL_FALLBACKS)
    chain: list[str] = []
    for m in base:
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
    stream = client.chat.completions.create(
        model=model,
        messages=messages_for_api(history),
        # Suhu bisa diatur user di Pengaturan → Trinity Code (0,3 = kaku,
        # 1,2 = liar). Dibaca tiap request supaya perubahan langsung terasa.
        temperature=float(get_settings().get("temperature", 0.7)),
        stream=True,
    )
    for chunk in stream:
        try:
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None)
            if piece:
                yield piece
        except Exception:
            continue


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict],
                              vision: bool = False):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback.
    vision=True → pakai rantai model vision (untuk pesan bergambar)."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model, vision=vision):
        try:
            stream_iter = stream_chat_reply(client, model, history)
            first = next(stream_iter, None)
            if first:
                yield first
            for piece in stream_iter:
                yield piece
            return
        except Exception as e:
            last_exc = e
            if _is_model_unavailable_error(e):
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("no chat model available")


def transcribe_audio(client: OpenAI, audio_bytes: bytes) -> str:
    """Ubah rekaman suara (wav) menjadi teks dengan Groq Whisper."""
    resp = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=("suara.wav", audio_bytes, "audio/wav"),
        response_format="json",
    )
    return (getattr(resp, "text", "") or "").strip()


def normalize_image(data: bytes) -> tuple[bytes, str]:
    """Resize/kompres gambar (maks 1024px) supaya payload ke model ringan."""
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        w, h = im.size
        if max(w, h) > 1024:
            scale = 1024 / max(w, h)
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        buf = io.BytesIO()
        if im.mode in ("RGBA", "LA", "P"):
            im.convert("RGBA").save(buf, format="PNG")
            return buf.getvalue(), "image/png"
        im.convert("RGB").save(buf, format="JPEG", quality=88)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return data, "image/jpeg"


def collect_images(files) -> list[dict]:
    """Ambil gambar dari lampiran chat input → [{mime, data, name}]."""
    imgs: list[dict] = []
    for f in files or []:
        try:
            data = f.getvalue()
        except Exception:
            continue
        mime = (getattr(f, "type", "") or "").lower()
        if not data or not mime.startswith("image/"):
            continue
        data, mime = normalize_image(data)
        imgs.append({"mime": mime, "data": data, "name": getattr(f, "name", "gambar")})
        if len(imgs) >= MAX_IMAGES_PER_MESSAGE:
            break
    return imgs
