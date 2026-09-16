def stream_chat_reply(client: OpenAI, model: str, history: list[dict],
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

