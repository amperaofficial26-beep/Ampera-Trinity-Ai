#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

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
# Katalog model ala Claude: nama polos + deskripsi kecil (tanpa emoji)
MODEL_CATALOG = [
    {"name": "GPT-OSS 20B",   "desc": "Cepat untuk chat & coding ringan",      "id": "openai/gpt-oss-20b"},
    {"name": "GPT-OSS 120B",  "desc": "Reasoning mendalam untuk tugas berat",  "id": "openai/gpt-oss-120b"},
    {"name": "Compound",      "desc": "Browsing web & eksekusi kode",          "id": "groq/compound"},
    {"name": "Compound Mini", "desc": "Web search ringkas & cepat",            "id": "groq/compound-mini"},
    {"name": "Qwen3.6 27B",   "desc": "Reasoning & matematika",                "id": "qwen/qwen3.6-27b"},
]
AVAILABLE_MODELS = {m["name"]: m["id"] for m in MODEL_CATALOG}
DEFAULT_MODEL_LABEL = "GPT-OSS 20B"

# Fallback jika model terpilih sudah tidak tersedia di provider (dari App 1)
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier (dari App 1)
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki (dari App 3) ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4


# ============================================================================
# KREDENSIAL (Secrets → Environment Variable)
# ============================================================================
def _get_secret(*keys: str) -> str:
    """Ambil kredensial dari st.secrets lalu fallback ke env var."""
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


# ============================================================================
# CSS — TEMA ALA CLAUDE.AI (buatan sendiri)
#   Latar krem hangat, judul serif, aksen terracotta, UI kalem & bersih
# ============================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ============ PALET WARNA CLAUDE ============
   Latar utama : #F0EEE6 (krem hangat)
   Permukaan   : #FAF9F5 (putih gading)
   Bubble user : #E8E5D8 / #EDEAE0
   Teks utama  : #3D3929 (cokelat gelap hangat)
   Teks sekunder: #73726C
   Aksen       : #DA7756 (terracotta) / hover #C15F3C
   Border      : #E3E0D5
============================================== */

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #F0EEE6 !important;
    color: #3D3929;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ---------- SIDEBAR ala Claude ---------- */
section[data-testid="stSidebar"] {
    background: #F5F4EF !important;
    border-right: 1px solid #E3E0D5 !important;
    width: 300px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.7rem 0.5rem;
}
/* tombol buka sidebar (saat tertutup) HARUS selalu terlihat */
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
/* varian testid tombol expand sidebar di Streamlit versi baru */
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

/* judul brand serif ala "Claude" */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 6px 8px 16px;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
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
    padding: 8px 12px !important;
    min-height: 40px !important;
    color: #3D3929 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
    color: #3D3929 !important;
}
/* paksa SEMUA lapisan dalam tombol rata kiri (markdown container ikut) */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
/* tombol "+ Baru" menonjol sedikit (latar krem seperti Claude) */
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #EAE8DE !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #E3E0D5 !important;
}

/* label grup riwayat: "Hari ini" abu kecil */
.sb-group {
    font-size: 0.8rem; font-weight: 500; color: #8B887D;
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
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
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: #57544A !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
}
/* item riwayat aktif */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #EAE8DE !important;
}

/* tombol unduh di sidebar: sama polosnya dengan menu lain */
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
    padding: 7px 10px !important;
    min-height: 36px !important;
    color: #3D3929 !important;
    font-size: 0.92rem !important;
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
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #E3E0D5; margin: 10px 4px;
}

/* baris akun bawah ala Claude — DITEMPEL di dasar sidebar */
.sb-account {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 5;
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 64px !important;
    position: relative;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #D5D1C3;
}
.sb-account .name { font-size: 0.92rem; font-weight: 600; color: #3D3929; }
.sb-account .plan { font-size: 0.82rem; color: #A8A69E; font-weight: 400; }
.sb-account .caret { color: #A8A69E; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #73726C; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

/* scrollbar halus ala Claude */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D1C3; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #BFBAA8; }

::selection { background: rgba(218,119,86,0.25); }

/* ---------- header app (minimal, serif ala Claude) ---------- */
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

/* sapaan besar serif ala halaman awal Claude */
.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.9rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 14px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 6px 0 18px; }

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
/* AI: teks polos di atas latar — persis gaya Claude */
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

/* label kecil "Yuki" dengan titik aksen di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem; font-weight: 600; color: #3D3929;
    margin-bottom: 4px;
}
.ai-label::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%;
    background: #DA7756; display: inline-block;
}

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
/* kotak input 1 BARIS ala Claude (kontrol ada DI BAWAH kotak, bukan di dalam) */
[data-testid="stChatInput"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
    padding: 4px 8px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stChatInput"]:hover {
    border-color: #D5D1C3 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #DA7756 !important;
    box-shadow: 0 4px 18px rgba(218,119,86,0.16) !important;
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
/* tombol kirim: bulat terracotta khas Claude */
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

/* ---------- baris kontrol DI BAWAH kotak chat input (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [toggle Gambar] ......... [Nama Model]  (model di kanan spt Claude) */
.st-key-chat_controls {
    position: relative;
    margin-top: 2px !important;
    padding: 0 6px 6px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
}
/* disclaimer kecil di tengah (ala Claude) */
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #A8A69E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
/* toggle Gambar: teks kecil abu senada */
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #73726C !important;
}
/* tombol model = TULISAN BIASA tanpa kotak (ala Claude) */
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls [data-testid="stPopover"] > div > button,
.st-key-chat_controls button[data-testid="stBaseButton-secondary"],
.st-key-chat_controls button[data-testid="stPopoverButton"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    min-height: 30px !important;
    height: 30px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #73726C !important;
    box-shadow: none !important;
    white-space: nowrap;
    justify-content: flex-start !important;
    width: auto !important;
}
.st-key-chat_controls [data-testid="stPopover"] button:hover,
.st-key-chat_controls button[data-testid="stPopoverButton"]:hover {
    background: rgba(61,57,41,0.06) !important;
    color: #3D3929 !important;
    border: none !important;
    box-shadow: none !important;
}
/* hilangkan kotak pembungkus milik popover itu sendiri */
.st-key-chat_controls [data-testid="stPopover"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] {
    margin: 0 !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.78rem !important;
    color: #73726C !important;
    white-space: nowrap;
}
/* rapikan tinggi elemen di baris kontrol */
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

/* ---------- tombol & popover: pill lembut ala Claude ---------- */
div.stButton > button, [data-testid="stPopover"] > button,
div.stDownloadButton > button {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    color: #3D3929 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(61,57,41,0.05) !important;
    transition: all .18s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover,
div.stDownloadButton > button:hover {
    background: #F5F4EF !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
    box-shadow: 0 2px 8px rgba(218,119,86,0.14) !important;
}
/* ---------- pop-up model ala Claude: SATU panel, item = teks polos ---------- */
[data-testid="stPopoverBody"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 48px rgba(61,57,41,0.18) !important;
    min-width: 300px !important;
    padding: 8px 6px !important;
}
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] div {
    color: #3D3929;
}
/* item model: TANPA kotak sendiri-sendiri — hanya teks, hover baru menyala */
[data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    display: flex !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F0EEE6 !important;
    border: none !important;
    box-shadow: none !important;
    color: inherit !important;
}
/* isi tombol (markdown) dipaksa RATA KIRI penuh */
[data-testid="stPopoverBody"] div.stButton > button > div,
[data-testid="stPopoverBody"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
/* nama model (baris pertama) tebal gelap, deskripsi kecil abu */
[data-testid="stPopoverBody"] div.stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
    line-height: 1.45 !important;
}
/* rapatkan jarak antar item */
[data-testid="stPopoverBody"] .element-container { margin: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 2px !important; }

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #3D3929 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
/* warna track toggle saat aktif → terracotta */
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #DA7756 !important;
}

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.img {
    background: rgba(218,119,86,0.10);
    border: 1px solid rgba(218,119,86,0.35); color: #C15F3C;
}

/* ---------- spinner ala Claude ---------- */
[data-testid="stSpinner"] > div {
    border-top-color: #DA7756 !important;
}
[data-testid="stSpinner"] p { color: #73726C !important; }

/* ---------- thinking indicator ala Claude ---------- */
.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
/* bintang ✳ terracotta berdenyut & berputar pelan */
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}
/* teks dengan shimmer lembut menyapu perlahan (gaya Claude) */
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
/* teks muncul perlahan-lahan (fade masuk lambat) */
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
/* frasa berganti-ganti pelan (rotasi via CSS, jalan terus di browser
   walau server sedang sibuk memanggil API) */
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

/* caret berkedip saat jawaban diketik kata per kata */
.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #DA7756; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* ---------- progress bar gambar: % + shimmer (ala Claude) ---------- */
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
    /* teks shimmer sama seperti thinking */
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
/* kilau putih menyapu di atas bar */
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    color: #3D3929 !important;
}

/* ---------- footer ---------- */
.trinity-foot {
    text-align: center; color: #A8A69E; font-size: 0.74rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# UTIL: ERROR PUBLIK (dari App 1 — pesan ramah untuk pengguna umum)
# ============================================================================
def public_error_image(status: int | None, body: str, exc: Exception | None = None) -> str:
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
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


def _is_model_unavailable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )


# ============================================================================
# ENGINE 1: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
# ============================================================================
def build_chat_client() -> OpenAI:
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier)."""
    trimmed = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    return [{"role": "system", "content": YUKI_SYSTEM_PROMPT}, *trimmed]


def resolve_model_chain(preferred: str) -> list[str]:
    chain: list[str] = []
    for m in (preferred, *GROQ_MODEL_FALLBACKS):
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
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


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict]):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model):
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


# ============================================================================
# ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX — dari App 1)
# ============================================================================
def extract_image_bytes(payload: dict) -> bytes:
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


def generate_image(prompt: str) -> bytes:
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


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = '<div class="ai-label">Yuki</div>'
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}</div>'
        f"</div></div>"
    )


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble) atau gambar."""
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
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""), msg.get("time", "")),
            unsafe_allow_html=True,
        )


# ============================================================================
# THINKING INDICATOR ALA CLAUDE
#   Bintang ✳ berdenyut + frasa dengan shimmer yang muncul perlahan
#   dan berganti-ganti lambat (animasi murni CSS → tetap jalan
#   walau server sedang menunggu respons API).
# ============================================================================
# Frasa ala Claude — berganti tiap ~4 detik selama proses berpikir (~12s+)
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

# Durasi minimum proses berpikir (detik) — sesuai permintaan ±12 detik
THINKING_MIN_SECONDS = 12.0

# Durasi minimum progress bar gambar (detik) — biar animasi % terasa
IMAGE_MIN_SECONDS = 10.0

# Delay antar kata saat jawaban diketik kata per kata (agak lambat)
WORD_STREAM_DELAY = 0.14


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    return (
        '<div class="claude-think">'
        '<span class="star">✳</span>'
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )


def image_progress_html(pct: float, label: str) -> str:
    """Kartu progress bar % + shimmer untuk proses pembuatan gambar."""
    pct = max(0.0, min(100.0, float(pct)))
    return (
        '<div class="img-progress">'
        '<div class="img-progress-top">'
        '<span class="img-progress-label">'
        '<span class="star">✳</span>'
        f'{html.escape(label)}…</span>'
        f'<span class="img-progress-pct">{pct:.0f}%</span>'
        "</div>"
        '<div class="img-progress-track">'
        f'<div class="img-progress-fill" style="width:{pct:.1f}%;"></div>'
        "</div></div>"
    )


def stream_words(answer_slot, full_text: str) -> None:
    """Tampilkan jawaban kata per kata dengan delay agak lambat + caret ✳."""
    words = full_text.split(" ")
    acc = ""
    for i, word in enumerate(words):
        acc = word if not acc else f"{acc} {word}"
        is_last = i == len(words) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            # sisipkan caret sebelum penutup bubble
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(WORD_STREAM_DELAY)


# ============================================================================
# EXPORT CHAT (.md — diadaptasi dari App 2)
# ============================================================================
def get_chat_export_text() -> str:
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
            lines.append((m.get("content") or "").strip())
        lines.append("\n---\n")
    return "\n".join(lines)


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state() -> None:
    # Halaman awal bersih ala Claude: tanpa pesan sambutan,
    # hanya sapaan besar + input di tengah.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model_label" not in st.session_state:
        st.session_state.selected_model_label = DEFAULT_MODEL_LABEL
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    # Riwayat percakapan (untuk sidebar ala Claude)
    if "conversations" not in st.session_state:
        st.session_state.conversations = []  # list[{id, title, messages}]
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def _conversation_title(messages: list[dict]) -> str:
    """Judul percakapan = potongan pesan user pertama (ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"


def _archive_current_conversation() -> None:
    """Simpan obrolan aktif ke daftar riwayat (kalau ada isi dari user)."""
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        # update entri yang sudah ada
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


def reset_conversation() -> None:
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return


# ============================================================================
# SIDEBAR ALA CLAUDE
#   Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah
# ============================================================================
def render_sidebar() -> None:
    with st.sidebar:
        # Brand serif ala "Claude"
        st.markdown('<div class="sb-brand">Trinity</div>', unsafe_allow_html=True)

        # + Baru (latar krem menonjol seperti Claude)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()

        # Menu ala Claude (ikon garis tipis + teks rata kiri)
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

        # Riwayat percakapan (grup "Hari ini" seperti Claude)
        convs = st.session_state.get("conversations", [])
        if convs:
            st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}", use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()

        # Baris akun di dasar sidebar ala Claude: (U) User · Free  ⌄ | ikon
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


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Progress bar % + shimmer (generate jalan di thread background,
    # persentase naik perlahan mengikuti tahapan label)
    progress_slot = st.empty()

    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:  # simpan untuk ditampilkan di thread utama
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Tahapan label + target % (label berganti seiring progress naik)
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        # naik perlahan, melambat mendekati 92% selama masih menunggu
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
        # sentuhan akhir: lompat mulus ke 100%
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


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback."""
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_label,
        AVAILABLE_MODELS[DEFAULT_MODEL_LABEL],
    )

    # Thinking ala Claude — frasa berganti-ganti selama ±12 detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages
            )
        )

        # Tahan sampai proses berpikir genap ±12 detik
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul kata per kata dengan delay agak lambat
        stream_words(answer_slot, full)

        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    is_fresh = len(st.session_state.messages) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        # Sapaan besar serif di tengah + input diangkat ke tengah layar (CSS)
        st.markdown(
            """
<style>
/* angkat dok input ke tengah layar saat belum ada percakapan
   (turun sedikit agar tidak menutupi judul sapaan) */
[data-testid="stBottom"] {
    transform: translateY(-26vh);
    background: transparent !important;
    transition: transform 0.35s ease;
}
/* SEMUA lapisan dok harus transparan agar tidak menutupi judul sapaan */
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] [data-testid="stVerticalBlock"],
[data-testid="stBottom"] .element-container {
    background: transparent !important;
    background-color: transparent !important;
}
/* HALAMAN AWAL TIDAK BISA DI-SCROLL (atas/bawah) */
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
            '<span class="star">✳</span> Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    # ---------- Riwayat chat ----------
    for msg in st.session_state.messages:
        render_message(msg)

    # ---------- Chat input ----------
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    user_text = st.chat_input(placeholder_text)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    # Dirender ke dok bawah Streamlit (wadah yang sama dengan st.chat_input)
    # → otomatis ikut bergeser saat sidebar dibuka/ditutup (seperti Claude).
    # CSS menariknya naik (margin-top negatif) ke ruang padding kotak input.
    with st._bottom:
        with st.container(key="chat_controls"):
            # [toggle Gambar] ....spacer.... [Nama Model] — model di kanan ala Claude
            ctrl_mode, _sp, ctrl_model = st.columns([0.3, 1.4, 0.3])

            with ctrl_mode:
                st.session_state.image_mode = st.toggle(
                    "Gambar",
                    value=st.session_state.image_mode,
                    help="Nyalakan untuk membuat gambar dari teks. "
                         "Matikan untuk chat biasa dengan Yuki.",
                )

            with _sp:
                if not is_fresh:
                    st.markdown(
                        '<div class="input-disclaimer">'
                        "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                        "</div>",
                        unsafe_allow_html=True,
                    )

            with ctrl_model:
                current = st.session_state.selected_model_label
                with st.popover(current, use_container_width=False):
                    # Daftar model ala Claude: baris teks polos (nama + deskripsi),
                    # tanpa kotak per item — model aktif ditandai ✓
                    for m in MODEL_CATALOG:
                        is_active = m["name"] == st.session_state.selected_model_label
                        check = " :orange[✓]" if is_active else ""
                        label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                        if st.button(label, key=f"model_{m['name']}", use_container_width=True):
                            st.session_state.selected_model_label = m["name"]
                            st.rerun()

    if user_text and user_text.strip():
        text = user_text.strip()
        now = datetime.now().strftime("%H:%M")

        # Begitu KIRIM ditekan: kotak input langsung turun ke bawah
        # dan scroll diaktifkan lagi (menimpa CSS halaman awal).
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

        # simpan & tampilkan pesan user
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "user", "type": "text",
            "content": text, "time": now,
        })
        st.markdown(bubble_html("user", text, now), unsafe_allow_html=True)

        if st.session_state.image_mode:
            handle_image_request(text)
        else:
            answer_slot = st.empty()
            handle_chat_request(answer_slot)

        st.rerun()

    # ---------- Footer ----------
    st.markdown(
        '<p class="trinity-foot">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

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
# Katalog model ala Claude: nama polos + deskripsi kecil (tanpa emoji)
MODEL_CATALOG = [
    {"name": "GPT-OSS 20B",   "desc": "Cepat untuk chat & coding ringan",      "id": "openai/gpt-oss-20b"},
    {"name": "GPT-OSS 120B",  "desc": "Reasoning mendalam untuk tugas berat",  "id": "openai/gpt-oss-120b"},
    {"name": "Compound",      "desc": "Browsing web & eksekusi kode",          "id": "groq/compound"},
    {"name": "Compound Mini", "desc": "Web search ringkas & cepat",            "id": "groq/compound-mini"},
    {"name": "Qwen3.6 27B",   "desc": "Reasoning & matematika",                "id": "qwen/qwen3.6-27b"},
]
AVAILABLE_MODELS = {m["name"]: m["id"] for m in MODEL_CATALOG}
DEFAULT_MODEL_LABEL = "GPT-OSS 20B"

# Fallback jika model terpilih sudah tidak tersedia di provider (dari App 1)
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier (dari App 1)
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki (dari App 3) ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4


# ============================================================================
# KREDENSIAL (Secrets → Environment Variable)
# ============================================================================
def _get_secret(*keys: str) -> str:
    """Ambil kredensial dari st.secrets lalu fallback ke env var."""
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


# ============================================================================
# CSS — TEMA ALA CLAUDE.AI (buatan sendiri)
#   Latar krem hangat, judul serif, aksen terracotta, UI kalem & bersih
# ============================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ============ PALET WARNA CLAUDE ============
   Latar utama : #F0EEE6 (krem hangat)
   Permukaan   : #FAF9F5 (putih gading)
   Bubble user : #E8E5D8 / #EDEAE0
   Teks utama  : #3D3929 (cokelat gelap hangat)
   Teks sekunder: #73726C
   Aksen       : #DA7756 (terracotta) / hover #C15F3C
   Border      : #E3E0D5
============================================== */

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #F0EEE6 !important;
    color: #3D3929;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ---------- SIDEBAR ala Claude ---------- */
section[data-testid="stSidebar"] {
    background: #F5F4EF !important;
    border-right: 1px solid #E3E0D5 !important;
    width: 300px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.7rem 0.5rem;
}
/* tombol buka sidebar (saat tertutup) HARUS selalu terlihat */
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
/* varian testid tombol expand sidebar di Streamlit versi baru */
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

/* judul brand serif ala "Claude" */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 6px 8px 16px;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
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
    padding: 8px 12px !important;
    min-height: 40px !important;
    color: #3D3929 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
    color: #3D3929 !important;
}
/* paksa SEMUA lapisan dalam tombol rata kiri (markdown container ikut) */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
/* tombol "+ Baru" menonjol sedikit (latar krem seperti Claude) */
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #EAE8DE !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #E3E0D5 !important;
}

/* label grup riwayat: "Hari ini" abu kecil */
.sb-group {
    font-size: 0.8rem; font-weight: 500; color: #8B887D;
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
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
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: #57544A !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
}
/* item riwayat aktif */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #EAE8DE !important;
}

/* tombol unduh di sidebar: sama polosnya dengan menu lain */
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
    padding: 7px 10px !important;
    min-height: 36px !important;
    color: #3D3929 !important;
    font-size: 0.92rem !important;
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
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #E3E0D5; margin: 10px 4px;
}

/* baris akun bawah ala Claude — DITEMPEL di dasar sidebar */
.sb-account {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 5;
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 64px !important;
    position: relative;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #D5D1C3;
}
.sb-account .name { font-size: 0.92rem; font-weight: 600; color: #3D3929; }
.sb-account .plan { font-size: 0.82rem; color: #A8A69E; font-weight: 400; }
.sb-account .caret { color: #A8A69E; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #73726C; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

/* scrollbar halus ala Claude */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D1C3; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #BFBAA8; }

::selection { background: rgba(218,119,86,0.25); }

/* ---------- header app (minimal, serif ala Claude) ---------- */
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

/* sapaan besar serif ala halaman awal Claude */
.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.9rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 14px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 6px 0 18px; }

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
/* AI: teks polos di atas latar — persis gaya Claude */
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

/* label kecil "Yuki" dengan titik aksen di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem; font-weight: 600; color: #3D3929;
    margin-bottom: 4px;
}
.ai-label::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%;
    background: #DA7756; display: inline-block;
}

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
/* kotak input 1 BARIS ala Claude (kontrol ada DI BAWAH kotak, bukan di dalam) */
[data-testid="stChatInput"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
    padding: 4px 8px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stChatInput"]:hover {
    border-color: #D5D1C3 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #DA7756 !important;
    box-shadow: 0 4px 18px rgba(218,119,86,0.16) !important;
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
/* tombol kirim: bulat terracotta khas Claude */
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

/* ---------- baris kontrol DI BAWAH kotak chat input (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [toggle Gambar] ......... [Nama Model]  (model di kanan spt Claude) */
.st-key-chat_controls {
    position: relative;
    margin-top: 2px !important;
    padding: 0 6px 6px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
}
/* disclaimer kecil di tengah (ala Claude) */
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #A8A69E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
/* toggle Gambar: teks kecil abu senada */
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #73726C !important;
}
/* tombol model = TULISAN BIASA tanpa kotak (ala Claude) */
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls [data-testid="stPopover"] > div > button,
.st-key-chat_controls button[data-testid="stBaseButton-secondary"],
.st-key-chat_controls button[data-testid="stPopoverButton"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    min-height: 30px !important;
    height: 30px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #73726C !important;
    box-shadow: none !important;
    white-space: nowrap;
    justify-content: flex-start !important;
    width: auto !important;
}
.st-key-chat_controls [data-testid="stPopover"] button:hover,
.st-key-chat_controls button[data-testid="stPopoverButton"]:hover {
    background: rgba(61,57,41,0.06) !important;
    color: #3D3929 !important;
    border: none !important;
    box-shadow: none !important;
}
/* hilangkan kotak pembungkus milik popover itu sendiri */
.st-key-chat_controls [data-testid="stPopover"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] {
    margin: 0 !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.78rem !important;
    color: #73726C !important;
    white-space: nowrap;
}
/* rapikan tinggi elemen di baris kontrol */
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

/* ---------- tombol & popover: pill lembut ala Claude ---------- */
div.stButton > button, [data-testid="stPopover"] > button,
div.stDownloadButton > button {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    color: #3D3929 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(61,57,41,0.05) !important;
    transition: all .18s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover,
div.stDownloadButton > button:hover {
    background: #F5F4EF !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
    box-shadow: 0 2px 8px rgba(218,119,86,0.14) !important;
}
/* ---------- pop-up model ala Claude: SATU panel, item = teks polos ---------- */
[data-testid="stPopoverBody"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 48px rgba(61,57,41,0.18) !important;
    min-width: 300px !important;
    padding: 8px 6px !important;
}
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] div {
    color: #3D3929;
}
/* item model: TANPA kotak sendiri-sendiri — hanya teks, hover baru menyala */
[data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    display: flex !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F0EEE6 !important;
    border: none !important;
    box-shadow: none !important;
    color: inherit !important;
}
/* isi tombol (markdown) dipaksa RATA KIRI penuh */
[data-testid="stPopoverBody"] div.stButton > button > div,
[data-testid="stPopoverBody"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
/* nama model (baris pertama) tebal gelap, deskripsi kecil abu */
[data-testid="stPopoverBody"] div.stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
    line-height: 1.45 !important;
}
/* rapatkan jarak antar item */
[data-testid="stPopoverBody"] .element-container { margin: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 2px !important; }

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #3D3929 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
/* warna track toggle saat aktif → terracotta */
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #DA7756 !important;
}

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.img {
    background: rgba(218,119,86,0.10);
    border: 1px solid rgba(218,119,86,0.35); color: #C15F3C;
}

/* ---------- spinner ala Claude ---------- */
[data-testid="stSpinner"] > div {
    border-top-color: #DA7756 !important;
}
[data-testid="stSpinner"] p { color: #73726C !important; }

/* ---------- thinking indicator ala Claude ---------- */
.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
/* bintang ✳ terracotta berdenyut & berputar pelan */
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}
/* teks dengan shimmer lembut menyapu perlahan (gaya Claude) */
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
/* teks muncul perlahan-lahan (fade masuk lambat) */
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
/* frasa berganti-ganti pelan (rotasi via CSS, jalan terus di browser
   walau server sedang sibuk memanggil API) */
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

/* caret berkedip saat jawaban diketik kata per kata */
.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #DA7756; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* ---------- progress bar gambar: % + shimmer (ala Claude) ---------- */
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
    /* teks shimmer sama seperti thinking */
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
/* kilau putih menyapu di atas bar */
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    color: #3D3929 !important;
}

/* ---------- footer ---------- */
.trinity-foot {
    text-align: center; color: #A8A69E; font-size: 0.74rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# UTIL: ERROR PUBLIK (dari App 1 — pesan ramah untuk pengguna umum)
# ============================================================================
def public_error_image(status: int | None, body: str, exc: Exception | None = None) -> str:
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
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


def _is_model_unavailable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )


# ============================================================================
# ENGINE 1: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
# ============================================================================
def build_chat_client() -> OpenAI:
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier)."""
    trimmed = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    return [{"role": "system", "content": YUKI_SYSTEM_PROMPT}, *trimmed]


def resolve_model_chain(preferred: str) -> list[str]:
    chain: list[str] = []
    for m in (preferred, *GROQ_MODEL_FALLBACKS):
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
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


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict]):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model):
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


# ============================================================================
# ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX — dari App 1)
# ============================================================================
def extract_image_bytes(payload: dict) -> bytes:
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


def generate_image(prompt: str) -> bytes:
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


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = '<div class="ai-label">Yuki</div>'
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}</div>'
        f"</div></div>"
    )


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble) atau gambar."""
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
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""), msg.get("time", "")),
            unsafe_allow_html=True,
        )


# ============================================================================
# THINKING INDICATOR ALA CLAUDE
#   Bintang ✳ berdenyut + frasa dengan shimmer yang muncul perlahan
#   dan berganti-ganti lambat (animasi murni CSS → tetap jalan
#   walau server sedang menunggu respons API).
# ============================================================================
# Frasa ala Claude — berganti tiap ~4 detik selama proses berpikir (~12s+)
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

# Durasi minimum proses berpikir (detik) — sesuai permintaan ±12 detik
THINKING_MIN_SECONDS = 12.0

# Durasi minimum progress bar gambar (detik) — biar animasi % terasa
IMAGE_MIN_SECONDS = 10.0

# Delay antar kata saat jawaban diketik kata per kata (agak lambat)
WORD_STREAM_DELAY = 0.14


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    return (
        '<div class="claude-think">'
        '<span class="star">✳</span>'
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )


def image_progress_html(pct: float, label: str) -> str:
    """Kartu progress bar % + shimmer untuk proses pembuatan gambar."""
    pct = max(0.0, min(100.0, float(pct)))
    return (
        '<div class="img-progress">'
        '<div class="img-progress-top">'
        '<span class="img-progress-label">'
        '<span class="star">✳</span>'
        f'{html.escape(label)}…</span>'
        f'<span class="img-progress-pct">{pct:.0f}%</span>'
        "</div>"
        '<div class="img-progress-track">'
        f'<div class="img-progress-fill" style="width:{pct:.1f}%;"></div>'
        "</div></div>"
    )


def stream_words(answer_slot, full_text: str) -> None:
    """Tampilkan jawaban kata per kata dengan delay agak lambat + caret ✳."""
    words = full_text.split(" ")
    acc = ""
    for i, word in enumerate(words):
        acc = word if not acc else f"{acc} {word}"
        is_last = i == len(words) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            # sisipkan caret sebelum penutup bubble
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(WORD_STREAM_DELAY)


# ============================================================================
# EXPORT CHAT (.md — diadaptasi dari App 2)
# ============================================================================
def get_chat_export_text() -> str:
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
            lines.append((m.get("content") or "").strip())
        lines.append("\n---\n")
    return "\n".join(lines)


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state() -> None:
    # Halaman awal bersih ala Claude: tanpa pesan sambutan,
    # hanya sapaan besar + input di tengah.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model_label" not in st.session_state:
        st.session_state.selected_model_label = DEFAULT_MODEL_LABEL
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    # Riwayat percakapan (untuk sidebar ala Claude)
    if "conversations" not in st.session_state:
        st.session_state.conversations = []  # list[{id, title, messages}]
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def _conversation_title(messages: list[dict]) -> str:
    """Judul percakapan = potongan pesan user pertama (ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"


def _archive_current_conversation() -> None:
    """Simpan obrolan aktif ke daftar riwayat (kalau ada isi dari user)."""
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        # update entri yang sudah ada
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


def reset_conversation() -> None:
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return


# ============================================================================
# SIDEBAR ALA CLAUDE
#   Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah
# ============================================================================
def render_sidebar() -> None:
    with st.sidebar:
        # Brand serif ala "Claude"
        st.markdown('<div class="sb-brand">Trinity</div>', unsafe_allow_html=True)

        # + Baru (latar krem menonjol seperti Claude)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()

        # Menu ala Claude (ikon garis tipis + teks rata kiri)
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

        # Riwayat percakapan (grup "Hari ini" seperti Claude)
        convs = st.session_state.get("conversations", [])
        if convs:
            st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}", use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()

        # Baris akun di dasar sidebar ala Claude: (U) User · Free  ⌄ | ikon
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


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Progress bar % + shimmer (generate jalan di thread background,
    # persentase naik perlahan mengikuti tahapan label)
    progress_slot = st.empty()

    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:  # simpan untuk ditampilkan di thread utama
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Tahapan label + target % (label berganti seiring progress naik)
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        # naik perlahan, melambat mendekati 92% selama masih menunggu
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
        # sentuhan akhir: lompat mulus ke 100%
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


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback."""
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_label,
        AVAILABLE_MODELS[DEFAULT_MODEL_LABEL],
    )

    # Thinking ala Claude — frasa berganti-ganti selama ±12 detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages
            )
        )

        # Tahan sampai proses berpikir genap ±12 detik
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul kata per kata dengan delay agak lambat
        stream_words(answer_slot, full)

        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    is_fresh = len(st.session_state.messages) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        # Sapaan besar serif di tengah + input diangkat ke tengah layar (CSS)
        st.markdown(
            """
<style>
/* angkat dok input ke tengah layar saat belum ada percakapan
   (turun sedikit agar tidak menutupi judul sapaan) */
[data-testid="stBottom"] {
    transform: translateY(-26vh);
    background: transparent !important;
    transition: transform 0.35s ease;
}
/* SEMUA lapisan dok harus transparan agar tidak menutupi judul sapaan */
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] [data-testid="stVerticalBlock"],
[data-testid="stBottom"] .element-container {
    background: transparent !important;
    background-color: transparent !important;
}
/* HALAMAN AWAL TIDAK BISA DI-SCROLL (atas/bawah) */
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
            '<span class="star">✳</span> Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    # ---------- Riwayat chat ----------
    for msg in st.session_state.messages:
        render_message(msg)

    # ---------- Chat input ----------
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    user_text = st.chat_input(placeholder_text)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    # Dirender ke dok bawah Streamlit (wadah yang sama dengan st.chat_input)
    # → otomatis ikut bergeser saat sidebar dibuka/ditutup (seperti Claude).
    # CSS menariknya naik (margin-top negatif) ke ruang padding kotak input.
    with st._bottom:
        with st.container(key="chat_controls"):
            # [toggle Gambar] ....spacer.... [Nama Model] — model di kanan ala Claude
            ctrl_mode, _sp, ctrl_model = st.columns([0.3, 1.4, 0.3])

            with ctrl_mode:
                st.session_state.image_mode = st.toggle(
                    "Gambar",
                    value=st.session_state.image_mode,
                    help="Nyalakan untuk membuat gambar dari teks. "
                         "Matikan untuk chat biasa dengan Yuki.",
                )

            with _sp:
                if not is_fresh:
                    st.markdown(
                        '<div class="input-disclaimer">'
                        "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                        "</div>",
                        unsafe_allow_html=True,
                    )

            with ctrl_model:
                current = st.session_state.selected_model_label
                with st.popover(current, use_container_width=False):
                    # Daftar model ala Claude: baris teks polos (nama + deskripsi),
                    # tanpa kotak per item — model aktif ditandai ✓
                    for m in MODEL_CATALOG:
                        is_active = m["name"] == st.session_state.selected_model_label
                        check = " :orange[✓]" if is_active else ""
                        label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                        if st.button(label, key=f"model_{m['name']}", use_container_width=True):
                            st.session_state.selected_model_label = m["name"]
                            st.rerun()

    if user_text and user_text.strip():
        text = user_text.strip()
        now = datetime.now().strftime("%H:%M")

        # Begitu KIRIM ditekan: kotak input langsung turun ke bawah
        # dan scroll diaktifkan lagi (menimpa CSS halaman awal).
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

        # simpan & tampilkan pesan user
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "user", "type": "text",
            "content": text, "time": now,
        })
        st.markdown(bubble_html("user", text, now), unsafe_allow_html=True)

        if st.session_state.image_mode:
            handle_image_request(text)
        else:
            answer_slot = st.empty()
            handle_chat_request(answer_slot)

        st.rerun()

    # ---------- Footer ----------
    st.markdown(
        '<p class="trinity-foot">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

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
# Katalog model ala Claude: nama polos + deskripsi kecil (tanpa emoji)
MODEL_CATALOG = [
    {"name": "GPT-OSS 20B",   "desc": "Cepat untuk chat & coding ringan",      "id": "openai/gpt-oss-20b"},
    {"name": "GPT-OSS 120B",  "desc": "Reasoning mendalam untuk tugas berat",  "id": "openai/gpt-oss-120b"},
    {"name": "Compound",      "desc": "Browsing web & eksekusi kode",          "id": "groq/compound"},
    {"name": "Compound Mini", "desc": "Web search ringkas & cepat",            "id": "groq/compound-mini"},
    {"name": "Qwen3.6 27B",   "desc": "Reasoning & matematika",                "id": "qwen/qwen3.6-27b"},
]
AVAILABLE_MODELS = {m["name"]: m["id"] for m in MODEL_CATALOG}
DEFAULT_MODEL_LABEL = "GPT-OSS 20B"

# Fallback jika model terpilih sudah tidak tersedia di provider (dari App 1)
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier (dari App 1)
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki (dari App 3) ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4


# ============================================================================
# KREDENSIAL (Secrets → Environment Variable)
# ============================================================================
def _get_secret(*keys: str) -> str:
    """Ambil kredensial dari st.secrets lalu fallback ke env var."""
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


# ============================================================================
# CSS — TEMA ALA CLAUDE.AI (buatan sendiri)
#   Latar krem hangat, judul serif, aksen terracotta, UI kalem & bersih
# ============================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ============ PALET WARNA CLAUDE ============
   Latar utama : #F0EEE6 (krem hangat)
   Permukaan   : #FAF9F5 (putih gading)
   Bubble user : #E8E5D8 / #EDEAE0
   Teks utama  : #3D3929 (cokelat gelap hangat)
   Teks sekunder: #73726C
   Aksen       : #DA7756 (terracotta) / hover #C15F3C
   Border      : #E3E0D5
============================================== */

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #F0EEE6 !important;
    color: #3D3929;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ---------- SIDEBAR ala Claude ---------- */
section[data-testid="stSidebar"] {
    background: #F5F4EF !important;
    border-right: 1px solid #E3E0D5 !important;
    width: 300px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.7rem 0.5rem;
}
/* tombol buka sidebar (saat tertutup) HARUS selalu terlihat */
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
/* varian testid tombol expand sidebar di Streamlit versi baru */
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

/* judul brand serif ala "Claude" */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 6px 8px 16px;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
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
    padding: 8px 12px !important;
    min-height: 40px !important;
    color: #3D3929 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
    color: #3D3929 !important;
}
/* paksa SEMUA lapisan dalam tombol rata kiri (markdown container ikut) */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
/* tombol "+ Baru" menonjol sedikit (latar krem seperti Claude) */
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #EAE8DE !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #E3E0D5 !important;
}

/* label grup riwayat: "Hari ini" abu kecil */
.sb-group {
    font-size: 0.8rem; font-weight: 500; color: #8B887D;
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
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
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: #57544A !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
}
/* item riwayat aktif */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #EAE8DE !important;
}

/* tombol unduh di sidebar: sama polosnya dengan menu lain */
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
    padding: 7px 10px !important;
    min-height: 36px !important;
    color: #3D3929 !important;
    font-size: 0.92rem !important;
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
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #E3E0D5; margin: 10px 4px;
}

/* baris akun bawah ala Claude — DITEMPEL di dasar sidebar */
.sb-account {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 5;
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 64px !important;
    position: relative;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #D5D1C3;
}
.sb-account .name { font-size: 0.92rem; font-weight: 600; color: #3D3929; }
.sb-account .plan { font-size: 0.82rem; color: #A8A69E; font-weight: 400; }
.sb-account .caret { color: #A8A69E; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #73726C; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

/* scrollbar halus ala Claude */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D1C3; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #BFBAA8; }

::selection { background: rgba(218,119,86,0.25); }

/* ---------- header app (minimal, serif ala Claude) ---------- */
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

/* sapaan besar serif ala halaman awal Claude */
.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.9rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 14px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 6px 0 18px; }

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
/* AI: teks polos di atas latar — persis gaya Claude */
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

/* label kecil "Yuki" dengan titik aksen di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem; font-weight: 600; color: #3D3929;
    margin-bottom: 4px;
}
.ai-label::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%;
    background: #DA7756; display: inline-block;
}

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
/* kotak input 1 BARIS ala Claude (kontrol ada DI BAWAH kotak, bukan di dalam) */
[data-testid="stChatInput"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
    padding: 4px 8px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stChatInput"]:hover {
    border-color: #D5D1C3 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #DA7756 !important;
    box-shadow: 0 4px 18px rgba(218,119,86,0.16) !important;
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
/* tombol kirim: bulat terracotta khas Claude */
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

/* ---------- baris kontrol DI BAWAH kotak chat input (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [toggle Gambar] ......... [Nama Model]  (model di kanan spt Claude) */
.st-key-chat_controls {
    position: relative;
    margin-top: 2px !important;
    padding: 0 6px 6px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
}
/* disclaimer kecil di tengah (ala Claude) */
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #A8A69E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
/* toggle Gambar: teks kecil abu senada */
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #73726C !important;
}
/* tombol model = TULISAN BIASA tanpa kotak (ala Claude) */
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls [data-testid="stPopover"] > div > button,
.st-key-chat_controls button[data-testid="stBaseButton-secondary"],
.st-key-chat_controls button[data-testid="stPopoverButton"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    min-height: 30px !important;
    height: 30px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #73726C !important;
    box-shadow: none !important;
    white-space: nowrap;
    justify-content: flex-start !important;
    width: auto !important;
}
.st-key-chat_controls [data-testid="stPopover"] button:hover,
.st-key-chat_controls button[data-testid="stPopoverButton"]:hover {
    background: rgba(61,57,41,0.06) !important;
    color: #3D3929 !important;
    border: none !important;
    box-shadow: none !important;
}
/* hilangkan kotak pembungkus milik popover itu sendiri */
.st-key-chat_controls [data-testid="stPopover"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] {
    margin: 0 !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.78rem !important;
    color: #73726C !important;
    white-space: nowrap;
}
/* rapikan tinggi elemen di baris kontrol */
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

/* ---------- tombol & popover: pill lembut ala Claude ---------- */
div.stButton > button, [data-testid="stPopover"] > button,
div.stDownloadButton > button {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    color: #3D3929 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(61,57,41,0.05) !important;
    transition: all .18s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover,
div.stDownloadButton > button:hover {
    background: #F5F4EF !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
    box-shadow: 0 2px 8px rgba(218,119,86,0.14) !important;
}
/* ---------- pop-up model ala Claude: SATU panel, item = teks polos ---------- */
[data-testid="stPopoverBody"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 48px rgba(61,57,41,0.18) !important;
    min-width: 300px !important;
    padding: 8px 6px !important;
}
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] div {
    color: #3D3929;
}
/* item model: TANPA kotak sendiri-sendiri — hanya teks, hover baru menyala */
[data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    display: flex !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F0EEE6 !important;
    border: none !important;
    box-shadow: none !important;
    color: inherit !important;
}
/* isi tombol (markdown) dipaksa RATA KIRI penuh */
[data-testid="stPopoverBody"] div.stButton > button > div,
[data-testid="stPopoverBody"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
/* nama model (baris pertama) tebal gelap, deskripsi kecil abu */
[data-testid="stPopoverBody"] div.stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
    line-height: 1.45 !important;
}
/* rapatkan jarak antar item */
[data-testid="stPopoverBody"] .element-container { margin: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 2px !important; }

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #3D3929 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
/* warna track toggle saat aktif → terracotta */
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #DA7756 !important;
}

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.img {
    background: rgba(218,119,86,0.10);
    border: 1px solid rgba(218,119,86,0.35); color: #C15F3C;
}

/* ---------- spinner ala Claude ---------- */
[data-testid="stSpinner"] > div {
    border-top-color: #DA7756 !important;
}
[data-testid="stSpinner"] p { color: #73726C !important; }

/* ---------- thinking indicator ala Claude ---------- */
.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
/* bintang ✳ terracotta berdenyut & berputar pelan */
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}
/* teks dengan shimmer lembut menyapu perlahan (gaya Claude) */
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
/* teks muncul perlahan-lahan (fade masuk lambat) */
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
/* frasa berganti-ganti pelan (rotasi via CSS, jalan terus di browser
   walau server sedang sibuk memanggil API) */
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

/* caret berkedip saat jawaban diketik kata per kata */
.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #DA7756; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* ---------- progress bar gambar: % + shimmer (ala Claude) ---------- */
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
    /* teks shimmer sama seperti thinking */
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
/* kilau putih menyapu di atas bar */
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    color: #3D3929 !important;
}

/* ---------- footer ---------- */
.trinity-foot {
    text-align: center; color: #A8A69E; font-size: 0.74rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# UTIL: ERROR PUBLIK (dari App 1 — pesan ramah untuk pengguna umum)
# ============================================================================
def public_error_image(status: int | None, body: str, exc: Exception | None = None) -> str:
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
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


def _is_model_unavailable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )


# ============================================================================
# ENGINE 1: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
# ============================================================================
def build_chat_client() -> OpenAI:
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier)."""
    trimmed = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    return [{"role": "system", "content": YUKI_SYSTEM_PROMPT}, *trimmed]


def resolve_model_chain(preferred: str) -> list[str]:
    chain: list[str] = []
    for m in (preferred, *GROQ_MODEL_FALLBACKS):
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
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


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict]):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model):
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


# ============================================================================
# ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX — dari App 1)
# ============================================================================
def extract_image_bytes(payload: dict) -> bytes:
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


def generate_image(prompt: str) -> bytes:
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


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = '<div class="ai-label">Yuki</div>'
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}</div>'
        f"</div></div>"
    )


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble) atau gambar."""
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
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""), msg.get("time", "")),
            unsafe_allow_html=True,
        )


# ============================================================================
# THINKING INDICATOR ALA CLAUDE
#   Bintang ✳ berdenyut + frasa dengan shimmer yang muncul perlahan
#   dan berganti-ganti lambat (animasi murni CSS → tetap jalan
#   walau server sedang menunggu respons API).
# ============================================================================
# Frasa ala Claude — berganti tiap ~4 detik selama proses berpikir (~12s+)
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

# Durasi minimum proses berpikir (detik) — sesuai permintaan ±12 detik
THINKING_MIN_SECONDS = 12.0

# Durasi minimum progress bar gambar (detik) — biar animasi % terasa
IMAGE_MIN_SECONDS = 10.0

# Delay antar kata saat jawaban diketik kata per kata (agak lambat)
WORD_STREAM_DELAY = 0.14


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    return (
        '<div class="claude-think">'
        '<span class="star">✳</span>'
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )


def image_progress_html(pct: float, label: str) -> str:
    """Kartu progress bar % + shimmer untuk proses pembuatan gambar."""
    pct = max(0.0, min(100.0, float(pct)))
    return (
        '<div class="img-progress">'
        '<div class="img-progress-top">'
        '<span class="img-progress-label">'
        '<span class="star">✳</span>'
        f'{html.escape(label)}…</span>'
        f'<span class="img-progress-pct">{pct:.0f}%</span>'
        "</div>"
        '<div class="img-progress-track">'
        f'<div class="img-progress-fill" style="width:{pct:.1f}%;"></div>'
        "</div></div>"
    )


def stream_words(answer_slot, full_text: str) -> None:
    """Tampilkan jawaban kata per kata dengan delay agak lambat + caret ✳."""
    words = full_text.split(" ")
    acc = ""
    for i, word in enumerate(words):
        acc = word if not acc else f"{acc} {word}"
        is_last = i == len(words) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            # sisipkan caret sebelum penutup bubble
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(WORD_STREAM_DELAY)


# ============================================================================
# EXPORT CHAT (.md — diadaptasi dari App 2)
# ============================================================================
def get_chat_export_text() -> str:
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
            lines.append((m.get("content") or "").strip())
        lines.append("\n---\n")
    return "\n".join(lines)


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state() -> None:
    # Halaman awal bersih ala Claude: tanpa pesan sambutan,
    # hanya sapaan besar + input di tengah.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model_label" not in st.session_state:
        st.session_state.selected_model_label = DEFAULT_MODEL_LABEL
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    # Riwayat percakapan (untuk sidebar ala Claude)
    if "conversations" not in st.session_state:
        st.session_state.conversations = []  # list[{id, title, messages}]
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def _conversation_title(messages: list[dict]) -> str:
    """Judul percakapan = potongan pesan user pertama (ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"


def _archive_current_conversation() -> None:
    """Simpan obrolan aktif ke daftar riwayat (kalau ada isi dari user)."""
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        # update entri yang sudah ada
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


def reset_conversation() -> None:
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return


# ============================================================================
# SIDEBAR ALA CLAUDE
#   Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah
# ============================================================================
def render_sidebar() -> None:
    with st.sidebar:
        # Brand serif ala "Claude"
        st.markdown('<div class="sb-brand">Trinity</div>', unsafe_allow_html=True)

        # + Baru (latar krem menonjol seperti Claude)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()

        # Menu ala Claude (ikon garis tipis + teks rata kiri)
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

        # Riwayat percakapan (grup "Hari ini" seperti Claude)
        convs = st.session_state.get("conversations", [])
        if convs:
            st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}", use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()

        # Baris akun di dasar sidebar ala Claude: (U) User · Free  ⌄ | ikon
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


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Progress bar % + shimmer (generate jalan di thread background,
    # persentase naik perlahan mengikuti tahapan label)
    progress_slot = st.empty()

    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:  # simpan untuk ditampilkan di thread utama
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Tahapan label + target % (label berganti seiring progress naik)
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        # naik perlahan, melambat mendekati 92% selama masih menunggu
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
        # sentuhan akhir: lompat mulus ke 100%
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


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback."""
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_label,
        AVAILABLE_MODELS[DEFAULT_MODEL_LABEL],
    )

    # Thinking ala Claude — frasa berganti-ganti selama ±12 detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages
            )
        )

        # Tahan sampai proses berpikir genap ±12 detik
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul kata per kata dengan delay agak lambat
        stream_words(answer_slot, full)

        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    is_fresh = len(st.session_state.messages) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        # Sapaan besar serif di tengah + input diangkat ke tengah layar (CSS)
        st.markdown(
            """
<style>
/* angkat dok input ke tengah layar saat belum ada percakapan
   (turun sedikit agar tidak menutupi judul sapaan) */
[data-testid="stBottom"] {
    transform: translateY(-26vh);
    background: transparent !important;
    transition: transform 0.35s ease;
}
/* SEMUA lapisan dok harus transparan agar tidak menutupi judul sapaan */
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] [data-testid="stVerticalBlock"],
[data-testid="stBottom"] .element-container {
    background: transparent !important;
    background-color: transparent !important;
}
/* HALAMAN AWAL TIDAK BISA DI-SCROLL (atas/bawah) */
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
            '<span class="star">✳</span> Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    # ---------- Riwayat chat ----------
    for msg in st.session_state.messages:
        render_message(msg)

    # ---------- Chat input ----------
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    user_text = st.chat_input(placeholder_text)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    # Dirender ke dok bawah Streamlit (wadah yang sama dengan st.chat_input)
    # → otomatis ikut bergeser saat sidebar dibuka/ditutup (seperti Claude).
    # CSS menariknya naik (margin-top negatif) ke ruang padding kotak input.
    with st._bottom:
        with st.container(key="chat_controls"):
            # [toggle Gambar] ....spacer.... [Nama Model] — model di kanan ala Claude
            ctrl_mode, _sp, ctrl_model = st.columns([0.3, 1.4, 0.3])

            with ctrl_mode:
                st.session_state.image_mode = st.toggle(
                    "Gambar",
                    value=st.session_state.image_mode,
                    help="Nyalakan untuk membuat gambar dari teks. "
                         "Matikan untuk chat biasa dengan Yuki.",
                )

            with _sp:
                if not is_fresh:
                    st.markdown(
                        '<div class="input-disclaimer">'
                        "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                        "</div>",
                        unsafe_allow_html=True,
                    )

            with ctrl_model:
                current = st.session_state.selected_model_label
                with st.popover(current, use_container_width=False):
                    # Daftar model ala Claude: baris teks polos (nama + deskripsi),
                    # tanpa kotak per item — model aktif ditandai ✓
                    for m in MODEL_CATALOG:
                        is_active = m["name"] == st.session_state.selected_model_label
                        check = " :orange[✓]" if is_active else ""
                        label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                        if st.button(label, key=f"model_{m['name']}", use_container_width=True):
                            st.session_state.selected_model_label = m["name"]
                            st.rerun()

    if user_text and user_text.strip():
        text = user_text.strip()
        now = datetime.now().strftime("%H:%M")

        # Begitu KIRIM ditekan: kotak input langsung turun ke bawah
        # dan scroll diaktifkan lagi (menimpa CSS halaman awal).
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

        # simpan & tampilkan pesan user
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "user", "type": "text",
            "content": text, "time": now,
        })
        st.markdown(bubble_html("user", text, now), unsafe_allow_html=True)

        if st.session_state.image_mode:
            handle_image_request(text)
        else:
            answer_slot = st.empty()
            handle_chat_request(answer_slot)

        st.rerun()

    # ---------- Footer ----------
    st.markdown(
        '<p class="trinity-foot">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

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
# Katalog model ala Claude: nama polos + deskripsi kecil (tanpa emoji)
MODEL_CATALOG = [
    {"name": "GPT-OSS 20B",   "desc": "Cepat untuk chat & coding ringan",      "id": "openai/gpt-oss-20b"},
    {"name": "GPT-OSS 120B",  "desc": "Reasoning mendalam untuk tugas berat",  "id": "openai/gpt-oss-120b"},
    {"name": "Compound",      "desc": "Browsing web & eksekusi kode",          "id": "groq/compound"},
    {"name": "Compound Mini", "desc": "Web search ringkas & cepat",            "id": "groq/compound-mini"},
    {"name": "Qwen3.6 27B",   "desc": "Reasoning & matematika",                "id": "qwen/qwen3.6-27b"},
]
AVAILABLE_MODELS = {m["name"]: m["id"] for m in MODEL_CATALOG}
DEFAULT_MODEL_LABEL = "GPT-OSS 20B"

# Fallback jika model terpilih sudah tidak tersedia di provider (dari App 1)
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier (dari App 1)
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki (dari App 3) ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4


# ============================================================================
# KREDENSIAL (Secrets → Environment Variable)
# ============================================================================
def _get_secret(*keys: str) -> str:
    """Ambil kredensial dari st.secrets lalu fallback ke env var."""
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


# ============================================================================
# CSS — TEMA ALA CLAUDE.AI (buatan sendiri)
#   Latar krem hangat, judul serif, aksen terracotta, UI kalem & bersih
# ============================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ============ PALET WARNA CLAUDE ============
   Latar utama : #F0EEE6 (krem hangat)
   Permukaan   : #FAF9F5 (putih gading)
   Bubble user : #E8E5D8 / #EDEAE0
   Teks utama  : #3D3929 (cokelat gelap hangat)
   Teks sekunder: #73726C
   Aksen       : #DA7756 (terracotta) / hover #C15F3C
   Border      : #E3E0D5
============================================== */

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #F0EEE6 !important;
    color: #3D3929;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }

/* ---------- SIDEBAR ala Claude ---------- */
section[data-testid="stSidebar"] {
    background: #F5F4EF !important;
    border-right: 1px solid #E3E0D5 !important;
    width: 300px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.7rem 0.7rem 0.5rem;
}
/* tombol buka sidebar (saat tertutup) HARUS selalu terlihat */
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
/* varian testid tombol expand sidebar di Streamlit versi baru */
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

/* judul brand serif ala "Claude" */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 6px 8px 16px;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
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
    padding: 8px 12px !important;
    min-height: 40px !important;
    color: #3D3929 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
    color: #3D3929 !important;
}
/* paksa SEMUA lapisan dalam tombol rata kiri (markdown container ikut) */
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    text-align: left !important;
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
/* tombol "+ Baru" menonjol sedikit (latar krem seperti Claude) */
section[data-testid="stSidebar"] .st-key-sb_new button {
    background: #EAE8DE !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new button:hover {
    background: #E3E0D5 !important;
}

/* label grup riwayat: "Hari ini" abu kecil */
.sb-group {
    font-size: 0.8rem; font-weight: 500; color: #8B887D;
    padding: 16px 12px 6px; letter-spacing: 0.01em;
}
/* item riwayat: bulatan kecil ○ di depan + teks abu gelap, elipsis 1 baris */
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
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: #57544A !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 210px;
}
/* item riwayat aktif */
section[data-testid="stSidebar"] [class*="st-key-sb_hist_"].sb-active button {
    background: #EAE8DE !important;
}

/* tombol unduh di sidebar: sama polosnya dengan menu lain */
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
    padding: 7px 10px !important;
    min-height: 36px !important;
    color: #3D3929 !important;
    font-size: 0.92rem !important;
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
    font-size: 0.92rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #E3E0D5; margin: 10px 4px;
}

/* baris akun bawah ala Claude — DITEMPEL di dasar sidebar */
.sb-account {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 5;
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 64px !important;
    position: relative;
}
.sb-account .ava {
    width: 28px; height: 28px; border-radius: 50%;
    background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.78rem; font-weight: 600;
    flex-shrink: 0;
    border: 1px solid #D5D1C3;
}
.sb-account .name { font-size: 0.92rem; font-weight: 600; color: #3D3929; }
.sb-account .plan { font-size: 0.82rem; color: #A8A69E; font-weight: 400; }
.sb-account .caret { color: #A8A69E; font-size: 0.7rem; margin-left: 2px; }
.sb-account .right-icons {
    margin-left: auto;
    display: flex; align-items: center; gap: 12px;
    color: #73726C; font-size: 0.95rem;
}
/* rapatkan jarak antar elemen sidebar */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 2px !important; }
section[data-testid="stSidebar"] .element-container { margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 768px;
    padding-top: 1.2rem !important;
    padding-bottom: 10rem !important;
}

/* scrollbar halus ala Claude */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D5D1C3; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #BFBAA8; }

::selection { background: rgba(218,119,86,0.25); }

/* ---------- header app (minimal, serif ala Claude) ---------- */
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

/* sapaan besar serif ala halaman awal Claude */
.trinity-greeting {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.9rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 14px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 6px 0 18px; }

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
/* AI: teks polos di atas latar — persis gaya Claude */
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

/* label kecil "Yuki" dengan titik aksen di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.78rem; font-weight: 600; color: #3D3929;
    margin-bottom: 4px;
}
.ai-label::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%;
    background: #DA7756; display: inline-block;
}

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
/* kotak input 1 BARIS ala Claude (kontrol ada DI BAWAH kotak, bukan di dalam) */
[data-testid="stChatInput"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
    padding: 4px 8px !important;
    transition: border-color .18s ease, box-shadow .18s ease !important;
}
[data-testid="stChatInput"]:hover {
    border-color: #D5D1C3 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #DA7756 !important;
    box-shadow: 0 4px 18px rgba(218,119,86,0.16) !important;
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
/* tombol kirim: bulat terracotta khas Claude */
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

/* ---------- baris kontrol DI BAWAH kotak chat input (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [toggle Gambar] ......... [Nama Model]  (model di kanan spt Claude) */
.st-key-chat_controls {
    position: relative;
    margin-top: 2px !important;
    padding: 0 6px 6px;
    background: transparent !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 2px !important;
    flex-wrap: nowrap !important;
}
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
}
/* disclaimer kecil di tengah (ala Claude) */
.input-disclaimer {
    text-align: center;
    font-size: 0.76rem;
    color: #A8A69E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 4px 8px 0;
}
/* toggle Gambar: teks kecil abu senada */
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.8rem !important;
    color: #73726C !important;
}
/* tombol model = TULISAN BIASA tanpa kotak (ala Claude) */
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls [data-testid="stPopover"] > div > button,
.st-key-chat_controls button[data-testid="stBaseButton-secondary"],
.st-key-chat_controls button[data-testid="stPopoverButton"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    border-radius: 8px !important;
    padding: 2px 8px !important;
    min-height: 30px !important;
    height: 30px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #73726C !important;
    box-shadow: none !important;
    white-space: nowrap;
    justify-content: flex-start !important;
    width: auto !important;
}
.st-key-chat_controls [data-testid="stPopover"] button:hover,
.st-key-chat_controls button[data-testid="stPopoverButton"]:hover {
    background: rgba(61,57,41,0.06) !important;
    color: #3D3929 !important;
    border: none !important;
    box-shadow: none !important;
}
/* hilangkan kotak pembungkus milik popover itu sendiri */
.st-key-chat_controls [data-testid="stPopover"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stPopover"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] {
    margin: 0 !important;
}
.st-key-chat_controls [data-testid="stCheckbox"] label p {
    font-size: 0.78rem !important;
    color: #73726C !important;
    white-space: nowrap;
}
/* rapikan tinggi elemen di baris kontrol */
.st-key-chat_controls [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-chat_controls .element-container { margin: 0 !important; }

/* ---------- tombol & popover: pill lembut ala Claude ---------- */
div.stButton > button, [data-testid="stPopover"] > button,
div.stDownloadButton > button {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    color: #3D3929 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(61,57,41,0.05) !important;
    transition: all .18s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover,
div.stDownloadButton > button:hover {
    background: #F5F4EF !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
    box-shadow: 0 2px 8px rgba(218,119,86,0.14) !important;
}
/* ---------- pop-up model ala Claude: SATU panel, item = teks polos ---------- */
[data-testid="stPopoverBody"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 48px rgba(61,57,41,0.18) !important;
    min-width: 300px !important;
    padding: 8px 6px !important;
}
[data-testid="stPopoverBody"] p, [data-testid="stPopoverBody"] div {
    color: #3D3929;
}
/* item model: TANPA kotak sendiri-sendiri — hanya teks, hover baru menyala */
[data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
    padding: 8px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    display: flex !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
    background: #F0EEE6 !important;
    border: none !important;
    box-shadow: none !important;
    color: inherit !important;
}
/* isi tombol (markdown) dipaksa RATA KIRI penuh */
[data-testid="stPopoverBody"] div.stButton > button > div,
[data-testid="stPopoverBody"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
/* nama model (baris pertama) tebal gelap, deskripsi kecil abu */
[data-testid="stPopoverBody"] div.stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
    line-height: 1.45 !important;
}
/* rapatkan jarak antar item */
[data-testid="stPopoverBody"] .element-container { margin: 0 !important; }
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 2px !important; }

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p {
    color: #3D3929 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
/* warna track toggle saat aktif → terracotta */
[data-testid="stCheckbox"] [data-checked="true"],
.stToggle [aria-checked="true"] > div:first-child {
    background: #DA7756 !important;
}

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.img {
    background: rgba(218,119,86,0.10);
    border: 1px solid rgba(218,119,86,0.35); color: #C15F3C;
}

/* ---------- spinner ala Claude ---------- */
[data-testid="stSpinner"] > div {
    border-top-color: #DA7756 !important;
}
[data-testid="stSpinner"] p { color: #73726C !important; }

/* ---------- thinking indicator ala Claude ---------- */
.claude-think {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 2px 6px;
    animation: thinkFadeIn 1.4s ease both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: none; }
}
/* bintang ✳ terracotta berdenyut & berputar pelan */
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}
/* teks dengan shimmer lembut menyapu perlahan (gaya Claude) */
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
/* teks muncul perlahan-lahan (fade masuk lambat) */
@keyframes phraseIn {
    from { opacity: 0; filter: blur(3px); }
    to   { opacity: 1; filter: blur(0); }
}
/* frasa berganti-ganti pelan (rotasi via CSS, jalan terus di browser
   walau server sedang sibuk memanggil API) */
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

/* caret berkedip saat jawaban diketik kata per kata */
.type-caret {
    display: inline-block; width: 7px; height: 1.05em;
    margin-left: 3px; vertical-align: -2px;
    background: #DA7756; border-radius: 2px;
    animation: caretBlink 0.8s step-end infinite;
}
@keyframes caretBlink { 50% { opacity: 0; } }

/* ---------- progress bar gambar: % + shimmer (ala Claude) ---------- */
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
    /* teks shimmer sama seperti thinking */
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
/* kilau putih menyapu di atas bar */
.img-progress-fill::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(90deg,
        transparent 0%, rgba(255,255,255,0.55) 50%, transparent 100%);
    background-size: 180% 100%;
    animation: shimmerSweep 1.8s linear infinite;
    border-radius: 99px;
}

/* ---------- alert / error ---------- */
[data-testid="stAlert"] {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 12px !important;
    color: #3D3929 !important;
}

/* ---------- footer ---------- */
.trinity-foot {
    text-align: center; color: #A8A69E; font-size: 0.74rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# UTIL: ERROR PUBLIK (dari App 1 — pesan ramah untuk pengguna umum)
# ============================================================================
def public_error_image(status: int | None, body: str, exc: Exception | None = None) -> str:
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
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


def _is_model_unavailable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )


# ============================================================================
# ENGINE 1: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
# ============================================================================
def build_chat_client() -> OpenAI:
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier)."""
    trimmed = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    return [{"role": "system", "content": YUKI_SYSTEM_PROMPT}, *trimmed]


def resolve_model_chain(preferred: str) -> list[str]:
    chain: list[str] = []
    for m in (preferred, *GROQ_MODEL_FALLBACKS):
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
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


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict]):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model):
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


# ============================================================================
# ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX — dari App 1)
# ============================================================================
def extract_image_bytes(payload: dict) -> bytes:
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


def generate_image(prompt: str) -> bytes:
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


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = '<div class="ai-label">Yuki</div>'
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}</div>'
        f"</div></div>"
    )


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble) atau gambar."""
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
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""), msg.get("time", "")),
            unsafe_allow_html=True,
        )


# ============================================================================
# THINKING INDICATOR ALA CLAUDE
#   Bintang ✳ berdenyut + frasa dengan shimmer yang muncul perlahan
#   dan berganti-ganti lambat (animasi murni CSS → tetap jalan
#   walau server sedang menunggu respons API).
# ============================================================================
# Frasa ala Claude — berganti tiap ~4 detik selama proses berpikir (~12s+)
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

# Durasi minimum proses berpikir (detik) — sesuai permintaan ±12 detik
THINKING_MIN_SECONDS = 12.0

# Durasi minimum progress bar gambar (detik) — biar animasi % terasa
IMAGE_MIN_SECONDS = 10.0

# Delay antar kata saat jawaban diketik kata per kata (agak lambat)
WORD_STREAM_DELAY = 0.14


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    return (
        '<div class="claude-think">'
        '<span class="star">✳</span>'
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )


def image_progress_html(pct: float, label: str) -> str:
    """Kartu progress bar % + shimmer untuk proses pembuatan gambar."""
    pct = max(0.0, min(100.0, float(pct)))
    return (
        '<div class="img-progress">'
        '<div class="img-progress-top">'
        '<span class="img-progress-label">'
        '<span class="star">✳</span>'
        f'{html.escape(label)}…</span>'
        f'<span class="img-progress-pct">{pct:.0f}%</span>'
        "</div>"
        '<div class="img-progress-track">'
        f'<div class="img-progress-fill" style="width:{pct:.1f}%;"></div>'
        "</div></div>"
    )


def stream_words(answer_slot, full_text: str) -> None:
    """Tampilkan jawaban kata per kata dengan delay agak lambat + caret ✳."""
    words = full_text.split(" ")
    acc = ""
    for i, word in enumerate(words):
        acc = word if not acc else f"{acc} {word}"
        is_last = i == len(words) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            # sisipkan caret sebelum penutup bubble
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(WORD_STREAM_DELAY)


# ============================================================================
# EXPORT CHAT (.md — diadaptasi dari App 2)
# ============================================================================
def get_chat_export_text() -> str:
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
            lines.append((m.get("content") or "").strip())
        lines.append("\n---\n")
    return "\n".join(lines)


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state() -> None:
    # Halaman awal bersih ala Claude: tanpa pesan sambutan,
    # hanya sapaan besar + input di tengah.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model_label" not in st.session_state:
        st.session_state.selected_model_label = DEFAULT_MODEL_LABEL
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1
    # Riwayat percakapan (untuk sidebar ala Claude)
    if "conversations" not in st.session_state:
        st.session_state.conversations = []  # list[{id, title, messages}]
    if "conv_counter" not in st.session_state:
        st.session_state.conv_counter = 0
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def _conversation_title(messages: list[dict]) -> str:
    """Judul percakapan = potongan pesan user pertama (ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            title = " ".join(str(m["content"]).split())
            return title[:48] + ("…" if len(title) > 48 else "")
    return "Percakapan baru"


def _archive_current_conversation() -> None:
    """Simpan obrolan aktif ke daftar riwayat (kalau ada isi dari user)."""
    msgs = st.session_state.get("messages", [])
    has_user = any(m.get("role") == "user" for m in msgs)
    if not has_user:
        return
    conv_id = st.session_state.get("active_conv_id")
    if conv_id is not None:
        # update entri yang sudah ada
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


def reset_conversation() -> None:
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return


# ============================================================================
# SIDEBAR ALA CLAUDE
#   Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah
# ============================================================================
def render_sidebar() -> None:
    with st.sidebar:
        # Brand serif ala "Claude"
        st.markdown('<div class="sb-brand">Trinity</div>', unsafe_allow_html=True)

        # + Baru (latar krem menonjol seperti Claude)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()

        # Menu ala Claude (ikon garis tipis + teks rata kiri)
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

        # Riwayat percakapan (grup "Hari ini" seperti Claude)
        convs = st.session_state.get("conversations", [])
        if convs:
            st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}", use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()

        # Baris akun di dasar sidebar ala Claude: (U) User · Free  ⌄ | ikon
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


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Progress bar % + shimmer (generate jalan di thread background,
    # persentase naik perlahan mengikuti tahapan label)
    progress_slot = st.empty()

    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:  # simpan untuk ditampilkan di thread utama
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Tahapan label + target % (label berganti seiring progress naik)
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        # naik perlahan, melambat mendekati 92% selama masih menunggu
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
        # sentuhan akhir: lompat mulus ke 100%
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


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback."""
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_label,
        AVAILABLE_MODELS[DEFAULT_MODEL_LABEL],
    )

    # Thinking ala Claude — frasa berganti-ganti selama ±12 detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages
            )
        )

        # Tahan sampai proses berpikir genap ±12 detik
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul kata per kata dengan delay agak lambat
        stream_words(answer_slot, full)

        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    is_fresh = len(st.session_state.messages) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        # Sapaan besar serif di tengah + input diangkat ke tengah layar (CSS)
        st.markdown(
            """
<style>
/* angkat dok input ke tengah layar saat belum ada percakapan
   (turun sedikit agar tidak menutupi judul sapaan) */
[data-testid="stBottom"] {
    transform: translateY(-26vh);
    background: transparent !important;
    transition: transform 0.35s ease;
}
/* SEMUA lapisan dok harus transparan agar tidak menutupi judul sapaan */
[data-testid="stBottom"] > div,
[data-testid="stBottom"] [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] [data-testid="stVerticalBlock"],
[data-testid="stBottom"] .element-container {
    background: transparent !important;
    background-color: transparent !important;
}
/* HALAMAN AWAL TIDAK BISA DI-SCROLL (atas/bawah) */
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
            '<span class="star">✳</span> Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    # ---------- Riwayat chat ----------
    for msg in st.session_state.messages:
        render_message(msg)

    # ---------- Chat input ----------
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    user_text = st.chat_input(placeholder_text)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    # Dirender ke dok bawah Streamlit (wadah yang sama dengan st.chat_input)
    # → otomatis ikut bergeser saat sidebar dibuka/ditutup (seperti Claude).
    # CSS menariknya naik (margin-top negatif) ke ruang padding kotak input.
    with st._bottom:
        with st.container(key="chat_controls"):
            # [toggle Gambar] ....spacer.... [Nama Model] — model di kanan ala Claude
            ctrl_mode, _sp, ctrl_model = st.columns([0.3, 1.4, 0.3])

            with ctrl_mode:
                st.session_state.image_mode = st.toggle(
                    "Gambar",
                    value=st.session_state.image_mode,
                    help="Nyalakan untuk membuat gambar dari teks. "
                         "Matikan untuk chat biasa dengan Yuki.",
                )

            with _sp:
                if not is_fresh:
                    st.markdown(
                        '<div class="input-disclaimer">'
                        "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                        "</div>",
                        unsafe_allow_html=True,
                    )

            with ctrl_model:
                current = st.session_state.selected_model_label
                with st.popover(current, use_container_width=False):
                    # Daftar model ala Claude: baris teks polos (nama + deskripsi),
                    # tanpa kotak per item — model aktif ditandai ✓
                    for m in MODEL_CATALOG:
                        is_active = m["name"] == st.session_state.selected_model_label
                        check = " :orange[✓]" if is_active else ""
                        label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                        if st.button(label, key=f"model_{m['name']}", use_container_width=True):
                            st.session_state.selected_model_label = m["name"]
                            st.rerun()

    if user_text and user_text.strip():
        text = user_text.strip()
        now = datetime.now().strftime("%H:%M")

        # Begitu KIRIM ditekan: kotak input langsung turun ke bawah
        # dan scroll diaktifkan lagi (menimpa CSS halaman awal).
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

        # simpan & tampilkan pesan user
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "user", "type": "text",
            "content": text, "time": now,
        })
        st.markdown(bubble_html("user", text, now), unsafe_allow_html=True)

        if st.session_state.image_mode:
            handle_image_request(text)
        else:
            answer_slot = st.empty()
            handle_chat_request(answer_slot)

        st.rerun()

    # ---------- Footer ----------
    st.markdown(
        '<p class="trinity-foot">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
