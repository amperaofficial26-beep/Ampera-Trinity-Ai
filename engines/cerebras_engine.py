# -*- coding: utf-8 -*-

"""
ENGINE CEREBRAS
Chat AI menggunakan Cerebras melalui OpenAI-compatible API.
"""

from __future__ import annotations

import streamlit as st
from openai import OpenAI

from config import (
    CEREBRAS_API_KEY,
    CEREBRAS_BASE_URL,
    MAX_HISTORY_MESSAGES,
    YUKI_SYSTEM_PROMPT,
    LANG_BY_CODE,
    DEFAULT_LANG_CODE,
)
from state import get_settings


def build_cerebras_client():
    if not CEREBRAS_API_KEY:
        raise RuntimeError("CEREBRAS_API_KEY belum dikonfigurasi.")

    return OpenAI(
        api_key=CEREBRAS_API_KEY,
        base_url=CEREBRAS_BASE_URL,
    )


def build_system_prompt() -> str:
    settings = get_settings()

    parts = [YUKI_SYSTEM_PROMPT]

    lang = LANG_BY_CODE.get(
        settings.get("yuki_lang") or DEFAULT_LANG_CODE
    )

    if lang and lang["code"] != "id":
        parts.append(
            f"Selalu jawab dalam bahasa {lang['name']}."
        )

    display_name = (
        settings.get("display_name") or ""
    ).strip()

    if display_name and display_name.lower() != "user":
        parts.append(
            f"Nama User adalah {display_name}."
        )

    return "\n\n".join(parts)


def messages_for_cerebras(history: list[dict]) -> list[dict]:
    trimmed = [
        m
        for m in history
        if m.get("role") in ("user", "assistant")
        and m.get("type", "text") == "text"
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


def stream_cerebras_reply(
    client: OpenAI,
    model: str,
    history: list[dict],
):
    stream = client.chat.completions.create(
        model=model,
        messages=messages_for_cerebras(history),
        temperature=float(
            get_settings().get("temperature", 0.7)
        ),
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
