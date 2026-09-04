# -*- coding: utf-8 -*-
"""
Engine untuk provider AI yang menggunakan OpenAI-compatible API.

Provider:
- Plugsky
- Aion Labs
- Final Router
"""

from __future__ import annotations

from typing import Iterator

from openai import OpenAI

from config import (
    PLUGSKY_API_KEY,
    PLUGSKY_BASE_URL,
    AION_API_KEY,
    AION_BASE_URL,
    FINAL_ROUTER_API_KEY,
    FINAL_ROUTER_BASE_URL,
)


PROVIDER_CONFIG = {
    "plugsky": {
        "api_key": PLUGSKY_API_KEY,
        "base_url": PLUGSKY_BASE_URL,
    },
    "aion": {
        "api_key": AION_API_KEY,
        "base_url": AION_BASE_URL,
    },
    "final_router": {
        "api_key": FINAL_ROUTER_API_KEY,
        "base_url": FINAL_ROUTER_BASE_URL,
    },
}


def build_compatible_client(provider: str) -> OpenAI:
    """
    Membuat OpenAI client berdasarkan provider.
    """

    config = PROVIDER_CONFIG.get(provider)

    if not config:
        raise ValueError(f"Provider tidak dikenal: {provider}")

    api_key = config["api_key"]
    base_url = config["base_url"]

    if not api_key:
        raise RuntimeError(
            f"API key untuk provider '{provider}' belum dikonfigurasi."
        )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def stream_compatible_reply(
    client: OpenAI,
    history: list[dict],
    model: str,
    system_prompt: str | None = None,
) -> Iterator[str]:
    """
    Mengirim chat ke provider OpenAI-compatible
    dan mengembalikan respons secara streaming.
    """

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt,
        })

    for message in history:
        role = message.get("role")

        if role not in ("user", "assistant"):
            continue

        content = message.get("content", "")

        if not content:
            continue

        # Untuk sementara engine ini hanya menangani teks.
        # Vision tetap menggunakan routing Groq yang sudah ada.
        if isinstance(content, str):
            messages.append({
                "role": role,
                "content": content,
            })

    if not messages:
        return

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        stream=True,
    )

    for chunk in response:
        try:
            content = chunk.choices[0].delta.content
        except (AttributeError, IndexError):
            content = None

        if content:
            yield content
