#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Groq Service Module
=======================================
Menangani komunikasi API ke Groq, auto-routing model berdasarkan
kompleksitas prompt, analisis gambar (Vision), dan streaming response.
"""

import time
import base64
from openai import OpenAI
from config import GROQ_BASE_URL, YUKI_SYSTEM_PROMPT, MAX_HISTORY_MESSAGES, MODEL_BY_KEY


class GroqService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(base_url=GROQ_BASE_URL, api_key=api_key) if api_key else None

    def auto_route_model(self, prompt: str, user_selected_key: str) -> str:
        """
        Secara otomatis memilih model yang optimal jika pengguna menggunakan mode default,
        atau mendeteksi kata kunci khusus seperti koding, analisis, matematika.
        """
        if user_selected_key != "gpt_oss_20b":
            return MODEL_BY_KEY.get(user_selected_key, {}).get("id", "openai/gpt-oss-20b")
        
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["code", "python", "script", "function", "bug", "error"]):
            return "openai/gpt-oss-20b"
        elif any(kw in prompt_lower for kw in ["hitung", "matematika", "rumus", "reasoning", "logika"]):
            return "qwen/qwen3.6-27b"
        elif any(kw in prompt_lower for kw in ["cari", "berita", "terbaru", "search", "siapa"]):
            return "groq/compound-mini"
        
        return "openai/gpt-oss-20b"

    def stream_chat_response(self, messages: list, model_key: str, image_b64: str = None):
        """
        Mengirim riwayat chat + gambar (opsional) ke Groq dengan streaming.
        Mencatat waktu respon (latency).
        """
        if not self.client:
            raise ValueError("Groq API Key belum dikonfigurasi.")

        start_time = time.time()
        
        # Tentukan model ID
        if image_b64:
            model_id = "meta-llama/llama-4-scout-17b-16e-instruct"
        else:
            last_prompt = messages[-1]["content"] if messages else ""
            model_id = self.auto_route_model(last_prompt, model_key)

        # Susun payload pesan
        formatted_messages = [{"role": "system", "content": YUKI_SYSTEM_PROMPT}]
        
        for msg in messages[-MAX_HISTORY_MESSAGES:-1]:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
        # Tambahkan pesan terakhir
        last_msg = messages[-1]
        if image_b64:
            content_payload = [
                {"type": "text", "text": last_msg["content"]},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
            formatted_messages.append({"role": last_msg["role"], "content": content_payload})
        else:
            formatted_messages.append({"role": last_msg["role"], "content": last_msg["content"]})

        stream = self.client.chat.completions.create(
            model=model_id,
            messages=formatted_messages,
            stream=True,
        )

        return stream, model_id, start_time
