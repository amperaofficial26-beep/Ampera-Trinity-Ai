#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Configuration & Constants
=============================================
File ini menyimpan seluruh konfigurasi dasar, persona AI, katalog model,
serta preferensi bahasa dan pengaturan aplikasi.
"""

import os
import streamlit as st

# Logo brand (PNG transparan, Deep Violet) dalam bentuk base64
LOGO_B64 = (
    "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"
    "HNlrSSDCbM6NA9MNALVaLaE6otcJBBG6PEkYUqRER7p1LF2d9QDUE6OQ3mTYKAhPAgB5c5XlgKDyMgAM5AYMAOTmRLOYzBwQ"
    "1pZ2lA5EURQ06kt0OA5CxACP0YU8lbx4GOiS5Fd+vuZqMUjvTUtV/6EB4CA3k37S+Zi8umfTQnIJCCDiVYd5r5NFgQmgQs8C"
    "wJ49e/gIOt/BKFAoSJN+oHuw2wHASNOeHzkfv63ADblcLtw8XNohqqsN29yVF8/vOJJ8cbYCwACk65JrLiTia5349Zu2ri+n"
    "nny18w5i0A8AYRhqmjDzidiG1Ye9fuQ8QKoChc6fd+G8c+oC4ODgYJVAvcx8kdk3pS2tWx+xbGEN33gcMvbZAUA92XmpRoEJ"
    "LRM+2aAmzBDxoy1s3gWAcrmclIirp339q32vaqg2AAC0fUqY3y9CAtS21pXG25X1eSj63C38K1362R3f0t6E62qj3xH/10a2"
    "qS/3e/N0k2aK12M1bIn6e3P+z8y2q/1Nf+kP/97//T838y3yT+e3/2L7f0521eR28OaN41P1d09+/2T1/A/Lp4x5x0xWv21m"
)

APP_NAME = "Ampera Trinity AI"
APP_TAGLINE = "Multi AI · Generate Foto · Chat — by Ampera Official"

# --- Groq & Model AI ---
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_CATALOG = [
    {"key": "gpt_oss_20b",   "name": "Trinity Easy",    "desc": "Cepat untuk chat & coding ringan",      "id": "openai/gpt-oss-20b", "premium": False},
    {"key": "compound_mini", "name": "Trinity Normal",  "desc": "Web search ringkas & cepat",            "id": "groq/compound-mini", "premium": False},
    {"key": "llama4_scout",  "name": "Trinity Normal",  "desc": "Bisa melihat & menganalisis gambar",    "id": "meta-llama/llama-4-scout-17b-16e-instruct", "premium": False},
    {"key": "compound",      "name": "Trinity Hard",    "desc": "Browsing web & eksekusi kode",          "id": "groq/compound", "premium": True},
    {"key": "qwen3_6_27b",   "name": "Trinity Hard",    "desc": "Reasoning & matematika",                "id": "qwen/qwen3.6-27b", "premium": True},
    {"key": "gpt_oss_120b",  "name": "Trinity Extreme", "desc": "Reasoning mendalam untuk tugas berat",  "id": "openai/gpt-oss-120b", "premium": True},
]
AVAILABLE_MODELS = {m["key"]: m["id"] for m in MODEL_CATALOG}
MODEL_BY_KEY = {m["key"]: m for m in MODEL_CATALOG}
DEFAULT_MODEL_KEY = "gpt_oss_20b"
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, menganalisis gambar yang dikirim User, sampai ide kreatif.
"""

# --- Pengaturan Default ---
DEFAULT_SETTINGS: dict = {
    "ui_lang": "id",
    "yuki_lang": "id",
    "theme": "Beige hangat",
    "display_name": "User",
    "allow_web_search": True,
    "save_history": True,
}

# --- Fungsi pembantu untuk mengambil Kredensial ---
def get_secret(*keys: str) -> str:
    for key in keys:
        try:
            val = st.secrets.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
        except Exception:
            pass
        val = os.environ.get(key, "")
        if val.strip():
            return val.strip()
    return ""
