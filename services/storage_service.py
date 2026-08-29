#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Storage & Export Service Module
===================================================
Menangani pembuatan riwayat percakapan, ekspor dokumen (JSON, TXT, Markdown),
dan manajemen penyimpanan riwayat lokal.
"""

import json
import time


class StorageService:
    @staticmethod
    def export_to_json(messages: list) -> str:
        """Mengubah riwayat pesan menjadi format JSON string."""
        export_data = {
            "app": "Ampera Trinity AI",
            "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "messages": messages
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_txt(messages: list) -> str:
        """Mengubah riwayat pesan menjadi dokumen teks biasa (TXT)."""
        output = f"=== AMPERA TRINITY AI - CHAT HISTORY ===\nExported: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for idx, msg in enumerate(messages, start=1):
            role = "Yuki (AI)" if msg.get("role") == "assistant" else "User"
            content = msg.get("content", "")
            output += f"[{idx}] {role}:\n{content}\n" + "-"*40 + "\n"
        return output

    @staticmethod
    def export_to_markdown(messages: list) -> str:
        """Mengubah riwayat pesan menjadi dokumen Markdown."""
        output = f"# ⚡ Ampera Trinity AI — Chat History\n*_Exported on {time.strftime('%Y-%m-%d %H:%M:%S')}_*\n\n---\n\n"
        for msg in messages:
            role = "**Yuki**" if msg.get("role") == "assistant" else "**User**"
            content = msg.get("content", "")
            output += f"### {role}\n{content}\n\n"
        return output
