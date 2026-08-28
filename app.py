#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

Fitur suara & gambar (via Groq, satu API key yang sama):
  - Mic 🎤       → bicara ke Yuki, ditranskrip dengan Whisper (whisper-large-v3-turbo)
  - Suara Yuki 🔊 → toggle "Suara"; jawaban dibacakan dengan TTS Orpheus
                   (canopylabs/orpheus-v1-english — paling pas utk teks Inggris)
  - Gambar 📎    → kirim/paste/drag-drop gambar, dianalisis model vision
                   Llama-4 Scout (meta-llama/llama-4-scout-17b-16e-instruct)
  - Menu ➕      → popup ala Claude: lampiran gambar, mode chat/gambar,
                   pencarian web (Compound), suara Yuki, unduh chat, chat baru

Catatan sesuai kesepakatan:
  - Style/CSS       : buatan sendiri (bukan bawaan app lama) — bebas diedit nanti
  - Loading/berpikir: custom ala Claude (bintang ✳ + teks shimmer perlahan)
  - Splash screen   : belum dibuat (nanti dibuat ulang)
  - Sidebar         : minimal dulu (nanti dibuat ulang + search percakapan)
  - Input foto      : tidak ada (tidak ada di ketiga app asal)

Kredensial (Streamlit Secrets atau environment variable):
  GROQ_API_KEY   → untuk semua model chat
  CF_ACCOUNT_ID  → untuk generate gambar (Cloudflare)
  CF_API_TOKEN   → untuk generate gambar (Cloudflare)
"""

from __future__ import annotations

import base64
import html
import inspect
import io
import os
import threading
import time
from datetime import datetime

import requests
import streamlit as st
from openai import OpenAI
from PIL import Image

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="Ampera Trinity AI",
    page_icon="🔱",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================================
# KONSTANTA
# ============================================================================
APP_NAME = "Ampera Trinity AI"
APP_TAGLINE = "Multi AI · Generate Foto · Chat — by Ampera Official"

# --- Multi AI (dari App 3: Ampera Multi AI) ---
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

VISION_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"
VISION_MODEL_LABEL = "Llama-4 Scout"
VISION_MODEL_FALLBACKS = (
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
)

GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

MAX_HISTORY_MESSAGES = 40

YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, menganalisis gambar yang dikirim User, sampai ide kreatif.
"""

CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4

STT_MODEL = "whisper-large-v3-turbo"
TTS_MODEL = "canopylabs/orpheus-v1-english"
TTS_VOICE = "tara"
TTS_MAX_CHARS = 1200
MAX_IMAGES_PER_MESSAGE = 5
IMAGE_INPUT_TYPES = ["png", "jpg", "jpeg", "webp", "gif"]
VISION_RECENT_MESSAGES = 4

_CHAT_INPUT_PARAMS = inspect.signature(st.chat_input).parameters
CHAT_INPUT_SUPPORTS_FILE = "accept_file" in _CHAT_INPUT_PARAMS
CHAT_INPUT_SUPPORTS_AUDIO = "accept_audio" in _CHAT_INPUT_PARAMS

def _get_secret(*keys: str) -> str:
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

GROQ_API_KEY = _get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = _get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = _get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

CHAT_READY = bool(GROQ_API_KEY)
IMAGE_READY = bool(CF_ACCOUNT_ID and CF_API_TOKEN)

def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #F0EEE6 !important;
    color: #3D3929;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ========== SIDEBAR ========== */
section[data-testid="stSidebar"] {
    background: #F5F4EF !important;
    border-right: 1px solid #E3E0D5 !important;
    width: 300px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.4rem 0.7rem 0.5rem;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    padding: 0 !important;
    min-height: 0 !important;
    height: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > * {
    position: absolute;
    top: 8px; right: 8px;
    z-index: 10;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 6px !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #3D3929 !important;
    z-index: 999990 !important;
}
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    color: #3D3929 !important;
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebarCollapseButton"] button { color: #73726C !important; }
[data-testid="stExpandSidebarButton"],
button[kind="headerNoPadding"] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #3D3929 !important;
}
[data-testid="stHeader"] {
    visibility: visible !important;
    pointer-events: auto !important;
}

.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.9rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 0 8px 16px;
    margin-top: 0;
    line-height: 1.1;
}

section[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 9px 12px !important;
    min-height: 44px !important;
    color: #3D3929 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
    color: #3D3929 !important;
}
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 1.05rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #EAE8DE !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #E3E0D5 !important;
}

.sb-group {
    font-size: 0.85rem; font-weight: 500; color: #8B887D;
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button {
    font-weight: 400 !important;
    color: #57544A !important;
    min-height: 36px !important;
    padding: 6px 12px 6px 12px !important;
    position: relative;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button::before {
    content: "";
    width: 8px; height: 8px;
    border: 1.5px solid #C9C6B9;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
    display: inline-block;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"] button p {
    font-size: 0.98rem !important;
    font-weight: 400 !important;
    color: #57544A !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
}
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #EAE8DE !important;
}

section[data-testid="stSidebar"] div.stDownloadButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 9px 12px !important;
    min-height: 44px !important;
    color: #3D3929 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button > div,
section[data-testid="stSidebar"] div.stDownloadButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    color: #3D3929 !important;
}
section[data-testid="stSidebar"] div.stDownloadButton > button p {
    text-align: left !important;
    font-size: 1.05rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

.sb-divider {
    height: 1px; background: #E3E0D5; margin: 10px 4px;
}

.sb-account {
    position: fixed;
    bottom: 0; left: 0;
    width: 300px;
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 999995;
    box-sizing: border-box;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 70px !important;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #D5D1C3;
}
.sb-account .name { font-size: 1rem; font-weight: 600; color: #3D3929; }
.sb-account .plan { font-size: 0.88rem; color: #A8A69E; font-weight: 400; }
.sb-account .caret { color: #A8A69E; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #73726C; font-size: 0.95rem;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D1C3; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #BFBAA8; }

::selection { background: rgba(218,119,86,0.25); }

/* ========== HEADER & GREETING ========== */
.trinity-head {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; padding: 4px 0 2px; margin-bottom: 6px;
}
.trinity-logo {
    width: 34px; height: 34px; border-radius: 10px;
    display: grid; place-items: center; font-size: 17px;
    background: #DA7756; color: #FFFFFF;
    flex-shrink: 0;
}
.trinity-head h1 {
    margin: 0;
    font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
    font-size: 1.45rem; font-weight: 600;
    color: #3D3929; letter-spacing: -0.01em;
}
.trinity-head p {
    margin: 0; color: #73726C; font-size: 0.78rem; font-weight: 400;
}
.trinity-sub {
    text-align: center; color: #73726C; font-size: 0.8rem;
    margin: 0 0 22px;
}

.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 3.4rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ========== CHAT MESSAGES ========== */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 12px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 4px 0 22px; }

[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
[data-testid="stMainBlockContainer"] .element-container {
    margin: 0 !important;
}
[data-testid="stMarkdownContainer"] {
    margin: 0 !important;
}
[data-testid="stMainBlockContainer"] div.stDownloadButton {
    margin: 6px 0 18px !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stImage"] {
    margin: 0 !important;
}

.bubble {
    font-size: 0.965rem; line-height: 1.65;
    word-break: break-word; overflow-wrap: anywhere;
    white-space: pre-wrap;
}
.bubble.user {
    max-width: 78%;
    background: #E8E5D8;
    color: #3D3929;
    border-radius: 18px;
    padding: 11px 16px;
    border: 1px solid rgba(61,57,41,0.05);
}
.bubble.ai {
    max-width: 100%;
    background: transparent;
    color: #3D3929;
    padding: 0 2px;
    border: none;
}
.bubble-meta {
    font-size: 0.7rem; color: #A8A69E;
    margin: 0 4px 4px; font-weight: 500;
}
.bubble-wrap { display: flex; flex-direction: column; max-width: 78%; }
.bubble-row.ai .bubble-wrap { max-width: 100%; }
.bubble-row.user .bubble-wrap { align-items: flex-end; }
.bubble-wrap .bubble { max-width: 100%; }

.bubble-imgs {
    display: flex; flex-wrap: wrap; gap: 6px;
    justify-content: flex-end; margin-top: 8px;
}
.bubble-img {
    max-width: 180px; max-height: 180px;
    border-radius: 12px; display: block;
    border: 1px solid rgba(61,57,41,0.08);
}

[data-testid="stAudio"] {
    max-width: 320px !important;
    margin: 2px 0 8px;
}

.ai-label {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.92rem; font-weight: 600; color: #3D3929;
    margin-bottom: 6px;
}

.logo-label {
    width: 30px; height: 30px;
    display: inline-block; vertical-align: middle;
}
.logo-greeting {
    width: 76px; height: 76px;
    display: inline-block; vertical-align: -16px;
    margin-right: 2px;
}
.logo-progress {
    width: 22px; height: 22px;
    display: inline-block; vertical-align: middle;
}

/* ========== CHAT INPUT ========== */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
[data-testid="stBottomBlockContainer"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 22px !important;
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
    padding: 6px 6px 4px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stBottomBlockContainer"]:focus-within {
    border-color: #DA7756 !important;
    box-shadow: 0 4px 18px rgba(218,119,86,0.16) !important;
}
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 6px !important;
}
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: transparent !important; border: none !important; box-shadow: none !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #3D3929 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #A8A69E !important;
}
[data-testid="stChatInput"] button {
    background: #DA7756 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    transition: background .18s ease !important;
}
[data-testid="stChatInput"] button:hover {
    background: #C15F3C !important;
}
[data-testid="stChatInput"] button svg { fill: #FFFFFF !important; color: #FFFFFF !important; }
[data-testid="stChatInput"] button:disabled {
    background: #E3E0D5 !important;
}
[data-testid="stChatInput"] button:disabled svg { fill: #A8A69E !important; color: #A8A69E !important; }

/* ========== CONTROLS INSIDE INPUT ========== */
.st-key-chat_controls {
    position: relative;
    margin-top: 0 !important;
    padding: 2px 4px 2px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(4) {
    flex: 1 1 auto !important;
}
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #A8A69E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #73726C !important;
}
/* ========== POPOVER MODEL (sederhana dengan bullet) ========== */
[data-testid="stPopoverBody"] div.stButton > button {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 6px 14px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    width: 100% !important;
    min-height: 32px !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    color: #3D3929 !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F5F4EF !important;
}
[data-testid="stPopoverBody"] .model-badge-premium {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    color: #C15F3C !important;
    background: rgba(218,119,86,0.12) !important;
    border: 1px solid rgba(218,119,86,0.2) !important;
    padding: 1px 8px !important;
    border-radius: 99px !important;
    margin-left: auto !important;
    flex-shrink: 0 !important;
}
[data-testid="stPopoverBody"] .model-check {
    color: #DA7756 !important;
    margin-left: 6px !important;
}
[data-testid="stPopoverBody"] .stButton + .stButton {
    border-top: 1px solid #F0EEE6 !important;
}
[data-testid="stPopoverBody"] {
    padding: 4px 0 !important;
    min-width: 200px !important;
    max-width: 260px !important;
}
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

[data-testid="stChatInput"] [data-testid="stChatInputFileUploadButton"] {
    display: none !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"],
[data-testid="stChatInput"] [data-testid="stChatInputCancelButton"],
[data-testid="stChatInput"] [data-testid="stChatInputApproveButton"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 10px !important;
    color: #57544A !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"] svg,
[data-testid="stChatInput"] [data-testid="stChatInputCancelButton"] svg,
[data-testid="stChatInput"] [data-testid="stChatInputApproveButton"] svg {
    fill: #57544A !important; color: #57544A !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"]:hover {
    border-color: #DA7756 !important;
}

/* Tombol + transparan */
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    min-width: 32px !important;
    width: 32px !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    font-size: 1.2rem !important;
    font-weight: 400 !important;
    color: #3D3929 !important;
    box-shadow: none !important;
    justify-content: center !important;
}
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button:hover {
    background: rgba(61,57,41,0.06) !important;
    border: none !important;
    color: #C15F3C !important;
}
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button svg:last-child,
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button [data-testid="stIconMaterial"]:last-child {
    display: none !important;
}
.plus-menu-hint {
    font-size: 0.72rem; color: #A8A69E;
    padding: 2px 4px 4px;
}

/* Uploader di popover: hanya teks */
.st-key-plus_upload_file [data-testid="stFileUploaderDropzone"],
.st-key-plus_upload_image [data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    min-height: 0 !important;
    cursor: pointer !important;
}
.st-key-plus_upload_file [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-plus_upload_image [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
.st-key-plus_upload_file [data-testid="stBaseButton-secondary"],
.st-key-plus_upload_image [data-testid="stBaseButton-secondary"] {
    display: none !important;
}
.st-key-plus_upload_file [data-testid="stFileUploaderDropzone"]::before {
    content: "📎  Upload file";
    display: block;
    font-size: 0.92rem;
    font-weight: 500;
    color: #3D3929;
    padding: 8px 12px;
    border-radius: 10px;
    width: 100%;
    text-align: left;
    transition: background 0.18s ease;
}
.st-key-plus_upload_image [data-testid="stFileUploaderDropzone"]::before {
    content: "📸  Upload gambar atau foto";
    display: block;
    font-size: 0.92rem;
    font-weight: 500;
    color: #3D3929;
    padding: 8px 12px;
    border-radius: 10px;
    width: 100%;
    text-align: left;
    transition: background 0.18s ease;
}
.st-key-plus_upload_file [data-testid="stFileUploaderDropzone"]:hover::before,
.st-key-plus_upload_image [data-testid="stFileUploaderDropzone"]:hover::before {
    background: #F0EEE6 !important;
}
.st-key-plus_upload_file [data-testid="stFileUploader"] label,
.st-key-plus_upload_image [data-testid="stFileUploader"] label {
    display: none !important;
}
.st-key-plus_upload_file [data-testid="stFileUploader"],
.st-key-plus_upload_image [data-testid="stFileUploader"] {
    margin: 0 !important;
}

/* ========== THUMBNAIL PREVIEW (lebih kecil & rapat ke input) ========== */
.st-key-preview_container {
    padding: 0 4px 2px !important;
    margin-bottom: 0 !important;
}
.st-key-preview_container [data-testid="stImage"] img {
    width: 56px !important;
    height: 56px !important;
    object-fit: cover !important;
    border-radius: 6px;
    border: 1px solid #E3E0D5;
}
.st-key-preview_container .stButton button {
    min-height: 20px !important;
    height: 20px !important;
    padding: 0 4px !important;
    font-size: 0.6rem !important;
    border-radius: 4px !important;
    background: rgba(61,57,41,0.06) !important;
    border: 1px solid #E3E0D5 !important;
    color: #3D3929 !important;
    box-shadow: none !important;
    width: 100% !important;
}
.st-key-preview_container .stButton button:hover {
    background: rgba(218,119,86,0.15) !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
}
.st-key-preview_container .stColumn {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 0 !important;
    min-width: 64px !important;
    padding: 0 2px !important;
}
.st-key-preview_container [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
}

/* ========== POPOVER MODEL (sederhana, rata kiri nama, badge kanan) ========== */
[data-testid="stPopoverBody"] {
    padding: 4px 0 !important;
    min-width: 200px !important;
    max-width: 260px !important;
    background: #FFFFFF !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 30px rgba(61,57,41,0.12) !important;
}
[data-testid="stPopoverBody"] .stButton {
    margin: 0 !important;
}
[data-testid="stPopoverBody"] div.stButton > button {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 6px 14px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    width: 100% !important;
    min-height: 32px !important;
    font-size: 0.9rem !important;
    font-weight: 400 !important;
    color: #3D3929 !important;
    text-align: left !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F5F4EF !important;
}
[data-testid="stPopoverBody"] .model-name {
    flex: 1 !important;
    text-align: left !important;
}
[data-testid="stPopoverBody"] .model-badge-premium {
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    color: #C15F3C !important;
    background: rgba(218,119,86,0.12) !important;
    border: 1px solid rgba(218,119,86,0.2) !important;
    padding: 1px 8px !important;
    border-radius: 99px !important;
    margin-left: 12px !important;
    flex-shrink: 0 !important;
}
[data-testid="stPopoverBody"] .model-check {
    color: #DA7756 !important;
    margin-left: 6px !important;
    flex-shrink: 0 !important;
}
[data-testid="stPopoverBody"] .stButton + .stButton {
    border-top: 1px solid #F0EEE6 !important;
}
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
/* Hilangkan separator antara tombol */
[data-testid="stPopoverBody"] .stButton + .stButton {
    border-top: 1px solid #F0EEE6 !important;
}

/* ========== TOGGLE ========== */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #3D3929 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #DA7756 !important;
}

/* ========== SPINNER & THINKING ========== */
[data-testid="stSpinner"] > div {
    border-top-color: #DA7756 !important;
}
[data-testid="stSpinner"] p { color: #73726C !important; }

.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}
.claude-think .logo-shimmer {
    position: relative;
    display: inline-block;
    width: 34px; height: 34px;
    flex-shrink: 0;
    overflow: hidden;
    border-radius: 6px;
    animation: logoPulse 3s ease-in-out infinite;
}
.claude-think .logo-shimmer img {
    width: 100%; height: 100%;
    display: block;
}
.claude-think .logo-shimmer::after {
    content: "";
    position: absolute;
    top: -30%; bottom: -30%;
    left: 0; width: 60%;
    background: linear-gradient(
        100deg,
        rgba(255,255,255,0) 0%,
        rgba(255,240,225,0.85) 50%,
        rgba(255,255,255,0) 100%
    );
    filter: blur(3px);
    mix-blend-mode: screen;
    transform: translateX(-130%) skewX(-16deg);
    animation: shineSweep 2.6s ease-in-out infinite;
    pointer-events: none;
}
@keyframes shineSweep {
    0%   { transform: translateX(-130%) skewX(-16deg); }
    60%  { transform: translateX(260%) skewX(-16deg); }
    100% { transform: translateX(260%) skewX(-16deg); }
}
@keyframes logoPulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.14); }
}
.claude-think .phrase {
    font-size: 0.92rem; font-weight: 500;
    background: linear-gradient(
        90deg,
        #A8A69E 0%, #A8A69E 35%,
        #3D3929 50%,
        #A8A69E 65%, #A8A69E 100%
    );
    background-size: 220% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerSweep 4s linear infinite, phraseIn 3s ease both;
}
@keyframes shimmerSweep {
    0%   { background-position: 110% 0; }
    100% { background-position: -110% 0; }
}
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
.claude-think .phrases { position: relative; height: 1.5em; min-width: 260px; }
.claude-think .phrases .phrase {
    position: absolute; left: 0; top: 0; white-space: nowrap;
    opacity: 0;
    animation: shimmerSweep 4s linear infinite,
               phraseCycle 16s ease-in-out infinite;
}
.claude-think .phrases .phrase:nth-child(1) { animation-delay: 0s, 0s; }
.claude-think .phrases .phrase:nth-child(2) { animation-delay: 0s, 4s; }
.claude-think .phrases .phrase:nth-child(3) { animation-delay: 0s, 8s; }
.claude-think .phrases .phrase:nth-child(4) { animation-delay: 0s, 12s; }
@keyframes phraseCycle {
    0%      { opacity: 0; filter: blur(4px); }
    3%      { opacity: 1; filter: blur(0); }
    21%     { opacity: 1; filter: blur(0); }
    25%     { opacity: 0; filter: blur(4px); }
    100%    { opacity: 0; }
}

.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #DA7756; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* Progress bar gambar */
.img-progress {
    padding: 14px 16px 16px;
    background: #FAF9F5;
    border: 1px solid #E3E0D5;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(61,57,41,0.06);
    animation: thinkFadeIn 1s ease both;
    margin: 6px 0 14px;
}
.img-progress-top {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 10px;
}
.img-progress-label {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.9rem; font-weight: 500;
    background: linear-gradient(
        90deg,
        #A8A69E 0%, #A8A69E 35%,
        #3D3929 50%,
        #A8A69E 65%, #A8A69E 100%
    );
    background-size: 220% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerSweep 4s linear infinite;
}
.img-progress-label .star {
    -webkit-text-fill-color: #DA7756;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block; font-size: 1rem;
}
.img-progress-pct {
    font-size: 0.92rem; font-weight: 600; color: #C15F3C;
    font-variant-numeric: tabular-nums;
}
.img-progress-track {
    height: 8px; border-radius: 99px;
    background: #E8E5D8; overflow: hidden;
    position: relative;
}
.img-progress-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #DA7756, #E89B7F, #DA7756);
    background-size: 200% 100%;
    animation: shimmerSweep 2.2s linear infinite;
    transition: width 0.5s ease;
    position: relative;
}
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

[data-testid="stAlert"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    color: #3D3929 !important;
}

.trinity-foot {
    text-align: center; color: #A8A69E; font-size: 0.6rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
.trinity-foot.in-chat {
    font-size: 0.5rem;
    color: #B8B6AC;
    margin-top: 22px;
}
</style>
""",
        unsafe_allow_html=True,
    )

# ============================================================================
# UTIL
# ============================================================================
def public_error_image(status, body, exc=None):
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."

def public_error_chat(exc):
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    if status == 401 or "invalid_api_key" in text or "unauthorized" in text or "authentication" in text:
        return "⚠️ Layanan chat sedang tidak tersedia (konfigurasi). Coba lagi nanti."
    if status == 404 or "model_not_found" in text or "decommissioned" in text or "does not exist" in text:
        return "⚠️ Model chat tidak tersedia lagi di provider. Coba pilih model lain."
    if status == 429 or "rate_limit" in text or "rate limit" in text or "quota" in text:
        return "⏳ Kuota chat sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Respons terlalu lama. Coba lagi."
    return "❌ Gagal membalas. Coba kirim ulang atau mulai obrolan baru."

def _is_model_unavailable_error(exc):
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )

def build_chat_client():
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

def messages_for_api(history):
    trimmed = [
        m for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    msgs = [{"role": "system", "content": YUKI_SYSTEM_PROMPT}]
    n = len(trimmed)
    for i, m in enumerate(trimmed):
        imgs = m.get("images") or []
        if imgs and i >= n - VISION_RECENT_MESSAGES:
            text_part = (m.get("content") or "").strip() or "Tolong analisis gambar ini ya."
            parts = [{"type": "text", "text": text_part}]
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

def resolve_model_chain(preferred, vision=False):
    base = VISION_MODEL_FALLBACKS if vision else (preferred, *GROQ_MODEL_FALLBACKS)
    chain = []
    for m in base:
        if m and m not in chain:
            chain.append(m)
    return chain

def stream_chat_reply(client, model, history):
    stream = client.chat.completions.create(
        model=model,
        messages=messages_for_api(history),
        temperature=0.7,
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

def stream_chat_with_fallback(client, preferred_model, history, vision=False):
    last_exc = None
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

def transcribe_audio(client, audio_bytes):
    resp = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=("suara.wav", audio_bytes, "audio/wav"),
        response_format="json",
    )
    return (getattr(resp, "text", "") or "").strip()

def synthesize_speech(client, text):
    clean = " ".join((text or "").split())
    if not clean:
        return None
    if len(clean) > TTS_MAX_CHARS:
        cut = clean[:TTS_MAX_CHARS]
        for punct in (". ", "! ", "? "):
            idx = cut.rfind(punct)
            if idx > 200:
                cut = cut[: idx + 1]
                break
        clean = cut
    try:
        resp = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=clean,
            response_format="wav",
        )
        return resp.content or None
    except Exception:
        return None

def normalize_image(data):
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

def collect_images(files):
    imgs = []
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

def extract_image_bytes(payload):
    if not isinstance(payload, dict):
        raise RuntimeError("invalid response")
    if payload.get("success") is False:
        raise RuntimeError(str(payload.get("errors") or payload))
    result = payload.get("result", payload)
    if isinstance(result, str):
        b64 = result
    elif isinstance(result, dict):
        b64 = result.get("image") or result.get("b64_json") or result.get("base64")
        if b64 is None and isinstance(result.get("data"), list) and result["data"]:
            first = result["data"][0]
            if isinstance(first, dict):
                b64 = first.get("b64_json") or first.get("image")
            elif isinstance(first, str):
                b64 = first
        if b64 is None:
            nested = result.get("result")
            if isinstance(nested, dict):
                b64 = nested.get("image")
            elif isinstance(nested, str):
                b64 = nested
    else:
        b64 = None
    if not b64 or not isinstance(b64, str):
        raise RuntimeError("no image")
    if "," in b64 and b64.strip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    raw = base64.b64decode(b64, validate=False)
    if not raw:
        raise RuntimeError("empty image")
    try:
        im = Image.open(io.BytesIO(raw))
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return raw

def generate_image(prompt):
    url = f"{CF_API_BASE}/{CF_ACCOUNT_ID}/ai/run/{CF_IMAGE_MODEL}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {"prompt": prompt, "steps": CF_DEFAULT_STEPS}
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=180)
    except requests.Timeout as e:
        raise RuntimeError("timeout") from e
    except requests.RequestException as e:
        raise RuntimeError(str(e)) from e
    content_type = (resp.headers.get("Content-Type") or "").lower()
    if "image/" in content_type:
        if resp.status_code >= 400:
            raise RuntimeError(public_error_image(resp.status_code, resp.text[:400]))
        raw = resp.content
        try:
            im = Image.open(io.BytesIO(raw))
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return raw
    try:
        payload = resp.json()
    except Exception:
        if resp.status_code >= 400:
            raise RuntimeError(public_error_image(resp.status_code, resp.text[:400]))
        raise RuntimeError("invalid response")
    if resp.status_code >= 400:
        err = payload.get("errors") if isinstance(payload, dict) else payload
        raise RuntimeError(public_error_image(resp.status_code, str(err)[:400]))
    return extract_image_bytes(payload)

def bubble_html(role, content, timestamp="", images_html="", meta_note=""):
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        meta = ""
    else:
        meta = f'<div class="ai-label">{logo_img_html("logo-label")} Yuki</div>'
    note = f'<div class="bubble-meta">{html.escape(meta_note)}</div>' if meta_note else ""
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}{images_html}</div>'
        f"{note}"
        f"</div></div>"
    )

def images_bubble_html(images):
    if not images:
        return ""
    parts = []
    for im in images:
        b64 = base64.b64encode(im["data"]).decode("ascii")
        alt = html.escape(str(im.get("name", "gambar")))
        parts.append(
            f'<img class="bubble-img" src="data:{im["mime"]};base64,{b64}" alt="{alt}"/>'
        )
    return f'<div class="bubble-imgs">{"".join(parts)}</div>'

def render_message(msg):
    if msg.get("type") == "image" and msg.get("image_bytes"):
        st.markdown(
            bubble_html("assistant", f"🎨 Hasil gambar untuk: {msg.get('prompt', '')}", msg.get("time", "")),
            unsafe_allow_html=True,
        )
        st.image(msg["image_bytes"], use_container_width=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="⬇️ Unduh PNG",
            data=msg["image_bytes"],
            file_name=f"trinity_{ts}.png",
            mime="image/png",
            key=f"dl_{msg.get('id', id(msg))}",
        )
    else:
        note = "🎙️ via suara" if msg.get("via_voice") else ""
        imgs_html = images_bubble_html(msg.get("images") or [])
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""),
                        msg.get("time", ""), imgs_html, note),
            unsafe_allow_html=True,
        )
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/wav")
        elif msg.get("audio_note"):
            st.markdown(
                f'<div class="bubble-meta">{html.escape(msg["audio_note"])}</div>',
                unsafe_allow_html=True,
            )

THINKING_PHRASES_CHAT = [
    "Berpikir",
    "Mencerna pertanyaan",
    "Menelusuri kemungkinan",
    "Merangkai jawaban",
]
THINKING_PHRASES_IMAGE = [
    "Berpikir",
    "Membayangkan gambarnya",
    "Menyiapkan kanvas",
    "Melukis perlahan",
]

THINKING_MIN_SECONDS = 10.0
IMAGE_MIN_SECONDS = 10.0
WORD_STREAM_DELAY = 0.03

@st.cache_data(show_spinner=False)
def _thinking_logo_b64():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "assets", "logo_thinking_small.png")
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode("ascii")
    except Exception:
        return ""

def logo_img_html(css_class="logo-inline"):
    b64 = _thinking_logo_b64()
    if b64:
        return f'<img class="{css_class}" src="data:image/png;base64,{b64}" alt="✳"/>'
    return '<span class="star">✳</span>'

def thinking_html(phrases):
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    logo_b64 = _thinking_logo_b64()
    if logo_b64:
        src = f"data:image/png;base64,{logo_b64}"
        icon = (
            '<span class="logo-shimmer">'
            f'<img src="{src}" alt=""/>'
            "</span>"
        )
    else:
        icon = '<span class="star">✳</span>'
    return (
        '<div class="claude-think">'
        f"{icon}"
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )

def image_progress_html(pct, label):
    pct = max(0.0, min(100.0, float(pct)))
    return (
        '<div class="img-progress">'
        '<div class="img-progress-top">'
        '<span class="img-progress-label">'
        f'{logo_img_html("logo-progress")}'
        f'{html.escape(label)}…</span>'
        f'<span class="img-progress-pct">{pct:.0f}%</span>'
        "</div>"
        '<div class="img-progress-track">'
        f'<div class="img-progress-fill" style="width:{pct:.1f}%;"></div>'
        "</div></div>"
    )

def stream_words(answer_slot, full_text):
    words = full_text.split(" ")
    acc = ""
    for i, word in enumerate(words):
        acc = word if not acc else f"{acc} {word}"
        is_last = i == len(words) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(WORD_STREAM_DELAY)

def get_chat_export_text():
    lines = [
        "# Riwayat Obrolan — Ampera Trinity AI",
        f"# Tanggal Ekspor: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "# by Ampera Official\n",
        "---\n",
    ]
    for m in st.session_state.get("messages", []):
        role_label = "👤 Pengguna" if m.get("role") == "user" else "🔱 Yuki"
        time_tag = f" [{m.get('time', '')}]" if m.get("time") else ""
        lines.append(f"### {role_label}{time_tag}\n")
        if m.get("type") == "image":
            lines.append(f"*(gambar dihasilkan — prompt: {m.get('prompt', '')})*")
        else:
            content = (m.get("content") or "").strip()
            if m.get("images"):
                content += "\n*(dengan lampiran gambar)*"
            if m.get("via_voice"):
                content += "\n*(dikirim via suara)*"
            lines.append(content)
        lines.append("\n---\n")
    return "\n".join(lines)

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model_key" not in st.session_state:
        st.session_state.selected_model_key = DEFAULT_MODEL_KEY
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "voice_reply" not in st.session_state:
        st.session_state.voice_reply = False
    if "pending_images" not in st.session_state:
        st.session_state.pending_images = []
    if "plus_uploader_gen" not in st.session_state:
        st.session_state.plus_uploader_gen = 0
    if "plus_popover_key" not in st.session_state:
        st.session_state.plus_popover_key = 0
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None

def next_msg_id():
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter

def _conversation_title(messages):
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"

def _archive_current_conversation():
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        for c in st.session_state.conversations:
            if c["id"] == conv_id:
                c["messages"] = msgs
                c["title"] = _conversation_title(msgs)
                return
    st.session_state.conv_counter += 1
    st.session_state.conversations.insert(0, {
        "id": st.session_state.conv_counter,
        "title": _conversation_title(msgs),
        "messages": msgs,
    })

def reset_conversation():
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()

def open_conversation(conv_id):
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sb-brand">Trinity</div>', unsafe_allow_html=True)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()
        with st.container(key="sb_menu_chat"):
            if st.button(":material/chat_bubble: &nbsp;Chat", use_container_width=True):
                st.session_state.image_mode = False
                st.rerun()
        with st.container(key="sb_menu_img"):
            if st.button(":material/palette: &nbsp;Gambar", use_container_width=True):
                st.session_state.image_mode = True
                st.rerun()
        with st.container(key="sb_download"):
            st.download_button(
                label=":material/download: &nbsp;Unduh Chat",
                data=get_chat_export_text(),
                file_name=f"trinity-chat-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        convs = st.session_state.get("conversations", [])
        if convs:
            st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}", use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()
        st.markdown(
            """
<div class="sb-account">
  <div class="ava">U</div>
  <div class="name">User <span class="plan">· Free</span></div>
  <span class="caret">▾</span>
  <div class="right-icons">⌕</div>
</div>
""",
            unsafe_allow_html=True,
        )

def handle_image_request(prompt):
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return
    progress_slot = st.empty()
    result = {"data": None, "error": None}
    def _worker():
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:
            result["error"] = exc
    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        if pct < 60:
            pct += 2.4
        elif pct < 85:
            pct += 1.1
        elif pct < 92:
            pct += 0.35
        label = stages[0][1]
        for threshold, name in stages:
            if pct >= threshold:
                label = name
        progress_slot.markdown(image_progress_html(pct, label), unsafe_allow_html=True)
        time.sleep(0.35)
        if not worker.is_alive() and (time.time() - t0) >= IMAGE_MIN_SECONDS:
            break
    worker.join(timeout=200)
    if result["error"] is None and result["data"]:
        progress_slot.markdown(image_progress_html(100, "Selesai"), unsafe_allow_html=True)
        time.sleep(0.6)
        progress_slot.empty()
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "image",
            "image_bytes": result["data"], "prompt": prompt,
            "time": datetime.now().strftime("%H:%M"),
        })
    else:
        progress_slot.empty()
        e = result["error"] or RuntimeError("no image")
        msg = str(e)
        if not msg.startswith(("⚠️", "⏳", "⌛", "❌")):
            msg = public_error_image(None, msg, e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": msg, "time": datetime.now().strftime("%H:%M"),
        })

def handle_chat_request(answer_slot):
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return
    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )
    last_user = next(
        (m for m in reversed(st.session_state.messages) if m.get("role") == "user"),
        None,
    )
    has_images = bool(last_user and last_user.get("images"))
    if has_images:
        model_id = VISION_MODEL_ID
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()
    try:
        client = build_chat_client()
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages, vision=has_images
            )
        )
        tts_box = {}
        tts_thread = None
        if st.session_state.get("voice_reply") and full:
            def _tts():
                tts_box["data"] = synthesize_speech(client, full)
            tts_thread = threading.Thread(target=_tts, daemon=True)
            tts_thread.start()
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()
        if not full:
            full = "…"
        stream_words(answer_slot, full)
        audio_wav = None
        if tts_thread is not None:
            tts_thread.join(timeout=90)
            audio_wav = tts_box.get("data")
        reply = {
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        }
        if audio_wav:
            reply["audio"] = audio_wav
            st.audio(audio_wav, format="audio/wav")
        elif tts_thread is not None:
            reply["audio_note"] = "🔇 Suara gagal dibuat (limit TTS / teks tak didukung)"
        st.session_state.messages.append(reply)
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })

def main():
    init_state()
    inject_css()
    render_sidebar()

    is_fresh = len(st.session_state.messages) == 0 and not st.session_state.pending_images

    if is_fresh:
        st.markdown(
            """
<style>
[data-testid="stBottom"] {
    transform: translateY(-26vh);
    background: transparent !important;
    transition: transform 0.35s ease;
}
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] [data-testid="stVerticalBlock"],
[data-testid="stBottom"] .element-container {
    background: transparent !important;
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
html, body {
    overflow: hidden !important;
}
</style>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="trinity-greeting" style="margin-top:18vh;">'
            f'{logo_img_html("logo-greeting")} Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        render_message(msg)

    # ========== CHAT INPUT ==========
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    chat_kwargs = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        # --- PREVIEW (di atas chat input, ukuran kecil & rapat) ---
        with st.container(key="preview_container"):
            pending = st.session_state.get("pending_images", [])
            if pending:
                cols = st.columns(len(pending) + 1)
                for i, im in enumerate(pending):
                    with cols[i]:
                        st.image(im["data"], width=56)
                        if st.button("✕", key=f"pending_rm_preview_{i}", help="Hapus"):
                            st.session_state.pending_images.pop(i)
                            st.rerun()
                with cols[-1]:
                    pass

        # --- CHAT INPUT ---
        user_input = st.chat_input(placeholder_text, **chat_kwargs)

        # --- CONTROLS (tombol +, toggle, model) ---
        with st.container(key="chat_controls"):
            ctrl_plus, ctrl_mode, ctrl_voice, _sp, ctrl_model = st.columns(
                [0.08, 0.2, 0.18, 1.04, 0.28]
            )

            with ctrl_plus:
                with st.container(key="plus_menu"):
                    popover_key = st.session_state.plus_popover_key
                    with st.popover(":material/add:", key=f"plus_popover_{popover_key}",
                                    use_container_width=False, help="Unggah file atau gambar"):
                        gen = st.session_state.get("plus_uploader_gen", 0)

                        def _stage_uploaded(files):
                            if not files:
                                return
                            staged = st.session_state.get("pending_images", [])
                            seen = {(im["name"], len(im["data"])) for im in staged}
                            added = False
                            for im in collect_images(files):
                                k = (im["name"], len(im["data"]))
                                if k not in seen:
                                    staged.append(im)
                                    seen.add(k)
                                    added = True
                            if added:
                                st.session_state.pending_images = staged
                                st.session_state.plus_popover_key += 1
                                st.session_state.plus_uploader_gen += 1
                                st.rerun()

                        with st.container(key="plus_upload_file"):
                            picked_file = st.file_uploader(
                                "Upload file", type=IMAGE_INPUT_TYPES,
                                accept_multiple_files=True,
                                label_visibility="collapsed",
                                key=f"plus_uploader_file_{gen}",
                            )
                        with st.container(key="plus_upload_image"):
                            picked_image = st.file_uploader(
                                "Upload gambar atau foto", type=IMAGE_INPUT_TYPES,
                                accept_multiple_files=True,
                                label_visibility="collapsed",
                                key=f"plus_uploader_image_{gen}",
                            )
                        _stage_uploaded(picked_file)
                        _stage_uploaded(picked_image)

            with ctrl_mode:
                st.session_state.image_mode = st.toggle(
                    "Gambar",
                    value=st.session_state.image_mode,
                    help="Nyalakan untuk membuat gambar dari teks. "
                         "Matikan untuk chat biasa dengan Yuki.",
                )

            with ctrl_voice:
                st.session_state.voice_reply = st.toggle(
                    "Suara",
                    value=st.session_state.get("voice_reply", False),
                    help="Saat aktif, Yuki membacakan jawabannya (TTS Groq Orpheus). "
                         "Paling pas untuk teks Inggris — teks Indonesia bisa "
                         "terdengar berlogat asing.",
                )

            with _sp:
                pending = st.session_state.get("pending_images", [])
                if not pending and not is_fresh:
                    st.markdown(
                        '<div class="input-disclaimer">'
                        "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                        "</div>",
                        unsafe_allow_html=True,
                    )

             with ctrl_model:
              current_key = st.session_state.selected_model_key
              current_model = MODEL_BY_KEY.get(current_key, MODEL_BY_KEY[DEFAULT_MODEL_KEY])
              current_name = current_model["name"]
              with st.popover(current_name, use_container_width=False):
                  for m in MODEL_CATALOG:
                      is_active = m["key"] == st.session_state.selected_model_key
                      # Buat label dengan struktur: nama di kiri, badge premium di kanan
                      # Kita gunakan markdown atau HTML di dalam button
                      # Karena st.button menerima string yang bisa berisi HTML, kita buat label dengan elemen span
                      name_span = f'<span class="model-name">• {m["name"]}</span>'
                      badge = f' <span class="model-badge-premium">Premium</span>' if m.get("premium") else ''
                      check = f' <span class="model-check">✓</span>' if is_active else ''
                      label_html = name_span + badge + check
                      if st.button(
                          label_html,
                          key=f"model_{m['key']}",
                          use_container_width=True,
                      ):
                          st.session_state.selected_model_key = m["key"]
                          st.rerun()
    # ========== PROCESS INPUT ==========
    if user_input is not None:
        if isinstance(user_input, str):
            raw_text, send_files, send_audio = user_input, [], None
        else:
            raw_text = getattr(user_input, "text", "") or ""
            send_files = list(getattr(user_input, "files", None) or [])
            send_audio = getattr(user_input, "audio", None)

        text = (raw_text or "").strip()
        via_voice = False

        if send_audio is not None and not text:
            if CHAT_READY:
                try:
                    with st.spinner("🎙️ Mentranskrip suara…"):
                        text = transcribe_audio(build_chat_client(), send_audio.getvalue())
                    via_voice = bool(text)
                except Exception:
                    text = ""
            if not text:
                st.session_state.messages.append({
                    "id": next_msg_id(), "role": "assistant", "type": "text",
                    "content": "🎙️ Hmm, suaranya belum kebaca nih. Coba rekam lagi "
                               "lebih dekat ke mikrofon, atau ketik saja ya!",
                    "time": datetime.now().strftime("%H:%M"),
                })
                st.rerun()

        images = collect_images(send_files)
        pending = st.session_state.get("pending_images", [])
        if pending:
            keys = {(im["name"], len(im["data"])) for im in images}
            for im in pending:
                k = (im["name"], len(im["data"]))
                if k not in keys:
                    images.append(im)
                    keys.add(k)
            st.session_state.pending_images = []
            st.session_state.plus_uploader_gen = (
                st.session_state.get("plus_uploader_gen", 0) + 1
            )
        images = images[:MAX_IMAGES_PER_MESSAGE]

        if text or images:
            now = datetime.now().strftime("%H:%M")
            if is_fresh:
                st.markdown(
                    """
<style>
[data-testid="stBottom"] { transform: translateY(0) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
html, body { overflow: auto !important; }
</style>
""",
                    unsafe_allow_html=True,
                )

            user_msg = {
                "id": next_msg_id(), "role": "user", "type": "text",
                "content": text, "time": now,
            }
            if images:
                user_msg["images"] = images
            if via_voice:
                user_msg["via_voice"] = True
            st.session_state.messages.append(user_msg)
            note = "🎙️ via suara" if via_voice else ""
            st.markdown(
                bubble_html("user", text, now, images_bubble_html(images), note),
                unsafe_allow_html=True,
            )

            if st.session_state.image_mode and not images:
                handle_image_request(text)
            else:
                answer_slot = st.empty()
                handle_chat_request(answer_slot)

            st.rerun()

    foot_class = "trinity-foot" if is_fresh else "trinity-foot in-chat"
    st.markdown(
        f'<p class="{foot_class}">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
