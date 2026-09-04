# -*- coding: utf-8 -*-

from __future__ import annotations

from openai import OpenAI

from config import (
    PLUGSKY_API_KEY,
    PLUGSKY_BASE_URL,
    MAX_HISTORY_MESSAGES,
    YUKI_SYSTEM_PROMPT,
    LANG_BY_CODE,
    DEFAULT_LANG_CODE,
    CARD_RULES,
    CLARIFY_RULES,
    CLARIFY_MODE_RULES,
    QUICK_REPLY_RULES,
    DESAIN_PROMPT,
    JADWAL_PROMPT,
)

from state import get_settings


PLUGSKY_MODEL = "openai/gpt-oss-120b"


def build_plugsky_client():
    if not PLUGSKY_API_KEY:
        raise RuntimeError(
            "PLUGSKY_API_KEY belum dikonfigurasi."
        )

    return OpenAI(
        api_key=PLUGSKY_API_KEY,
        base_url=PLUGSKY_BASE_URL,
    )


def build_system_prompt() -> str:
    s = get_settings()

    parts = [
        YUKI_SYSTEM_PROMPT,
        CARD_RULES,
    ]

    halaman = s.get("page") or "chat"

    if halaman == "desain":
        parts.append(DESAIN_PROMPT)

    elif halaman == "jadwal":
        parts.append(JADWAL_PROMPT)

    persona_map = {
        "Santai & kocak":
            "Pertahankan gaya santai, kocak, dan penuh candaan receh.",

        "Serius & ringkas":
            "Kurangi candaan. Jawab ringkas dan langsung ke inti.",

        "Mentor sabar":
            "Bersikap seperti mentor yang sabar dan jelaskan langkah demi langkah.",

        "Profesional formal":
            "Gunakan bahasa Indonesia formal dan profesional.",
    }

    personality = s.get("personality")

    if personality in persona_map:
        parts.append(persona_map[personality])

    clarify_mode = s.get("clarify_mode", "Seperlunya")

    if clarify_mode == "Mati":
        parts.append(CLARIFY_MODE_RULES["Mati"])
    else:
        parts.append(CLARIFY_RULES)

    parts.append(QUICK_REPLY_RULES)

    extra = CLARIFY_MODE_RULES.get(clarify_mode, "")

    if extra:
        parts.append(extra)

    lang = LANG_BY_CODE.get(
        s.get("yuki_lang") or DEFAULT_LANG_CODE
    )

    if lang and lang["code"] != "id":
        parts.append(
            f"Selalu jawab dalam bahasa {lang['name']}."
        )

    nickname = (
        s.get("custom_nickname") or ""
    ).strip()

    if nickname:
        parts.append(
            f"Panggil User dengan sebutan: {nickname}."
        )

    display_name = (
        s.get("display_name") or ""
    ).strip()

    if display_name and display_name.lower() != "user":
        parts.append(
            f"Nama User adalah {display_name}."
        )

    return "\n\n".join(parts)


def messages_for_plugsky(
    history: list[dict],
) -> list[dict]:

    trimmed = [
        m
        for m in history
        if (
            m.get("role") in ("user", "assistant")
            and m.get("type", "text") == "text"
        )
    ][-MAX_HISTORY_MESSAGES:]

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
        }
    ]

    for message in trimmed:
        messages.append(
            {
                "role": message["role"],
                "content": message.get("content") or "",
            }
        )

    return messages


def stream_plugsky_reply(
    client: OpenAI,
    history: list[dict],
    model: str = PLUGSKY_MODEL,
):

    response = client.chat.completions.create(
        model=model,
        messages=messages_for_plugsky(history),
        temperature=float(
            get_settings().get("temperature", 0.7)
        ),
        stream=True,
    )

    for chunk in response:
        try:
            content = chunk.choices[0].delta.content

            if content:
                yield content

        except Exception:
            continue
