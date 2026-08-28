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
  - Gambar 📎    → kirim/paste/drag-drop gambar, dianalisis model vision
                   Llama-4 Scout (meta-llama/llama-4-scout-17b-16e-instruct)
  - Menu ➕      → popup minimalist ala Claude: upload file/gambar, tip
                   tangkapan layar, toggle pencarian web (Compound)

Fitur ala Claude tambahan:
  - Sidebar   → Proyek (grup ringan), Artefak (kode panjang tertangkap
                otomatis), Sesuaikan (panggilan & instruksi custom Yuki),
                riwayat percakapan ("Hari ini")
  - Balasan Yuki → baris aksi kecil: salin jawaban, feedback 👍/, jam kirim

Catatan: fitur "Suara Yuki" (TTS) sudah dihapus karena tidak berfungsi.

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
import re
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
# Setiap entri punya "key" unik (dipakai internal & sebagai Streamlit key)
# terpisah dari "name" (label tampilan) karena dua model boleh berbagi nama
# tier yang sama (mis. dua model "Trinity Normal").
# Diurutkan dari tingkat termudah → tertinggi; tier Hard & Extreme = premium.
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

# Model vision (wajib dipakai saat pesan membawa gambar)
VISION_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"
VISION_MODEL_LABEL = "Llama-4 Scout"
VISION_MODEL_FALLBACKS = (
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
)

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
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, menganalisis gambar yang dikirim User, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4

# --- Suara (Groq — pakai GROQ_API_KEY yang sama) ---
STT_MODEL = "whisper-large-v3-turbo"          # transkrip suara → teks (mic tetap ada)
MAX_IMAGES_PER_MESSAGE = 5                    # batas model vision (Llama-4)
IMAGE_INPUT_TYPES = ["png", "jpg", "jpeg", "webp", "gif"]
VISION_RECENT_MESSAGES = 4  # pesan terakhir yang gambarnya ikut ke API

# Fitur mic/lampiran hanya jalan di Streamlit yang mendukung (1.47+);
# di versi lama otomatis nonaktif tanpa error.
_CHAT_INPUT_PARAMS = inspect.signature(st.chat_input).parameters
CHAT_INPUT_SUPPORTS_FILE = "accept_file" in _CHAT_INPUT_PARAMS
CHAT_INPUT_SUPPORTS_AUDIO = "accept_audio" in _CHAT_INPUT_PARAMS


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
    width: 260px !important;
    display: flex !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0.4rem 0.7rem 0.5rem;
}
/* konten sidebar DIPENTOK KE ATAS: buang ruang kosong bawaan di atasnya */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    padding: 0 !important;
    min-height: 0 !important;
    height: 0 !important;
}
/* tombol tutup sidebar « melayang di pojok, tidak memakan ruang */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] > * {
    position: absolute;
    top: 8px; right: 8px;
    z-index: 10;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 6px !important;
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

/* judul brand serif ala "Claude" — rapat ke atas, besar */
.sb-brand {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.5rem; font-weight: 700; color: #1a1915;
    letter-spacing: -0.02em;
    padding: 0 6px 8px;
    margin-top: 0;
    line-height: 1.1;
}

/* tombol menu sidebar: baris teks polos RATA KIRI, hover krem (ala Claude) */
section[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 6px 10px !important;
    min-height: 34px !important;
    color: #3D3929 !important;
    font-size: 0.9rem !important;
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
    font-size: 0.9rem !important;
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
    font-size: 0.85rem; font-weight: 500; color: #8B887D;
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
    font-size: 0.98rem !important;
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
    border-radius: 8px !important;
    width: 100% !important;
    display: flex !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 6px 10px !important;
    min-height: 34px !important;
    color: #3D3929 !important;
    font-size: 0.9rem !important;
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
    font-size: 0.9rem !important;
    color: #3D3929 !important;
    margin: 0 !important;
}

/* garis pemisah tipis */
.sb-divider {
    height: 1px; background: #E3E0D5; margin: 6px 2px;
}

/* baris akun ala Claude — DIPAKU di dasar layar, selebar sidebar */
.sb-account {
    position: fixed;
    bottom: 0; left: 0;
    width: 260px;              /* = lebar sidebar */
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px 14px;
    border-top: 1px solid #E3E0D5;
    background: #F5F4EF;
    z-index: 999995;
    box-sizing: border-box;
}
/* beri ruang bawah agar konten sidebar tidak tertutup baris akun */
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
    font-size: 3.4rem; font-weight: 500; color: #3D3929;
    text-align: center; margin: 26px 0 4px;
    letter-spacing: -0.02em;
}
.trinity-greeting .star { color: #DA7756; }

/* ---------- pesan: gaya percakapan Claude ---------- */
/* User: bubble krem membulat di kanan */
.bubble-row { display: flex; width: 100%; margin-bottom: 4px; }
.bubble-row.user { justify-content: flex-end; margin: 12px 0; }
.bubble-row.ai   { justify-content: flex-start; margin: 4px 0 22px; }

/* ---------- jarak antar pesan: rapat & konsisten ala Claude ---------- */
/* Streamlit menambah spasi sendiri antar elemen (gap 1rem antar container
   + hack margin -1rem pada markdown) sehingga jarak antar bubble membengkak
   dan tidak menentu. Dimatikan total di area chat — jarak sepenuhnya
   dikendalikan margin .bubble-row di atas agar rapat seperti Claude. */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
[data-testid="stMainBlockContainer"] .element-container {
    margin: 0 !important;
}
[data-testid="stMarkdownContainer"] {
    margin: 0 !important;
}
/* elemen mode gambar tetap diberi jarak wajar */
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

/* lampiran gambar di bubble user (thumbnail rapi ala Claude) */
.bubble-imgs {
    display: flex; flex-wrap: wrap; gap: 6px;
    justify-content: flex-end; margin-top: 8px;
}
.bubble-img {
    max-width: 180px; max-height: 180px;
    border-radius: 12px; display: block;
    border: 1px solid rgba(61,57,41,0.08);
}

/* ---------- baris aksi kecil di bawah jawaban Yuki (ala Claude) ---------- */
.msg-action-btn {
    background: transparent; border: none; cursor: pointer;
    color: #A8A69E; font-size: 0.95rem; line-height: 1;
    padding: 4px 6px; border-radius: 8px;
    transition: background .15s ease, color .15s ease;
}
.msg-action-btn:hover { background: #EAE8DE; color: #57544A; }
[class*="st-key-msg_actions_"] { margin: -4px 0 4px !important; }
[class*="st-key-msg_actions_"] [data-testid="stHorizontalBlock"] {
    gap: 0 !important; align-items: center !important;
}
[class*="st-key-msg_actions_"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 6px !important;
    min-height: 26px !important;
    height: 26px !important;
    font-size: 0.85rem !important;
    color: #A8A69E !important;
}
[class*="st-key-msg_actions_"] div.stButton > button:hover {
    background: #EAE8DE !important;
    border: none !important;
    box-shadow: none !important;
}
.msg-action-time {
    font-size: 0.7rem; color: #B8B6AC; padding: 6px 4px 0;
}

/* label "Yuki" dengan logo custom di atas jawaban AI */
.ai-label {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.92rem; font-weight: 600; color: #3D3929;
    margin-bottom: 6px;
}
/* bintang ✳ fallback di label jawaban Yuki: tanpa warna latar belakang,
   ukuran disamakan dengan logo agar layout tidak lompat */
.ai-label .star {
    background: transparent !important;
    background-color: transparent !important;
    border: none; box-shadow: none;
    color: #DA7756;
    font-size: 1.45rem; line-height: 1;
    width: 30px; height: 30px;
    display: inline-flex; align-items: center; justify-content: center;
}

/* ===== ukuran logo custom di berbagai tempat (statis, tanpa animasi) ===== */
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

/* ---------- chat input: kartu putih membulat ala Claude ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: #F0EEE6 !important; border: none !important; box-shadow: none !important;
}
/* KARTU GABUNGAN ala Claude: kotak teks + baris kontrol (+, toggle, model)
   dibungkus jadi SATU kartu membulat, supaya tombol + terlihat menyatu
   di dalam kotak chat input (bukan komponen terpisah di bawahnya). */
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
/* kotak input itu sendiri melebur transparan ke dalam kartu gabungan */
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

/* ---------- baris kontrol DI DALAM kartu, tepat di bawah teks (ala Claude) ---------- */
/* Berada di dok bawah Streamlit (satu wadah dengan st.chat_input)
   → otomatis ikut bergeser saat sidebar dibuka/ditutup.
   Layout: [+] [toggle Gambar] [toggle Suara] ......... [Nama Model] */
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
/* kolom kiri & kanan menyusut mengikuti isi, spacer tengah melar */
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
}
.st-key-chat_controls [data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(3) {
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

/* ---------- MENU ➕ ALA CLAUDE (minimalist: upload saja) ---------- */
/* sembunyikan tombol lampiran bawaan Streamlit (diganti menu ➕);
   drag-drop & paste Ctrl+V tetap berfungsi (ditangani elemen lain) */
[data-testid="stChatInput"] [data-testid="stChatInputFileUploadButton"] {
    display: none !important;
}
/* tombol mic / rekam: bulat putih senada (bukan terracotta) */
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
/* tombol ➕ di baris kontrol: lingkaran putih bersih ala Claude, menyatu
   di dalam kartu (tanpa bayangan berlebih karena kartu sudah punya shadow) */
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important;
    border-radius: 999px !important;
    min-width: 32px !important;
    width: 32px !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    color: #3D3929 !important;
    box-shadow: none !important;
    justify-content: center !important;
}
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button:hover {
    background: #F5F4EF !important;
    border-color: #DA7756 !important;
    color: #C15F3C !important;
}
/* Streamlit menambahkan ikon panah kecil di ujung tombol popover secara
   otomatis (indikator dropdown) — disembunyikan supaya tombol ➕ tetap
   polos, hanya ikon plus saja tanpa panah di sebelahnya. */
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button svg:last-child,
.st-key-chat_controls .st-key-plus_menu [data-testid="stPopover"] button [data-testid="stIconMaterial"]:last-child {
    display: none !important;
}
/* isi popover ➕ minimalist: cukup tombol unggah, tanpa label/hint besar */
.plus-menu-hint {
    font-size: 0.72rem; color: #A8A69E;
    padding: 2px 4px 4px;
}
.plus-menu-divider {
    height: 1px; background: #E3E0D5; margin: 6px 4px;
}
/* baris menu tambahan di popover + (screenshot, pencarian web) —
   sama gayanya dengan item lain: teks polos, hover krem */
[data-testid="stPopoverBody"] .st-key-plus_menu div.stButton > button,
.st-key-plus_menu [data-testid="stPopoverBody"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 8px 12px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
}
/* ---- reskin st.file_uploader jadi baris menu polos: ikon + teks saja,
   TANPA tombol "Upload"/"Browse files" terpisah yang terlihat.
   Triknya: dropzone (berisi tombol upload bawaan) dibuat transparan penuh
   dan direntangkan menutupi seluruh baris (overlay), sedangkan LABEL
   uploader (teks ikon+nama yang kita isi dari Python) tetap terlihat
   sebagai satu-satunya representasi visual — klik di mana saja pada
   baris tetap membuka dialog pilih file karena overlay ada di atasnya. */
.st-key-plus_upload_file, .st-key-plus_upload_image {
    position: relative !important;
    border-radius: 10px !important;
    transition: background .15s ease;
}
.st-key-plus_upload_file:hover, .st-key-plus_upload_image:hover {
    background: #F0EEE6 !important;
}
.st-key-plus_upload_file [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-plus_upload_image [data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
.st-key-plus_upload_file [data-testid="stFileUploaderDropzone"],
.st-key-plus_upload_image [data-testid="stFileUploaderDropzone"] {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
}
.st-key-plus_upload_file [data-testid="stFileUploader"],
.st-key-plus_upload_image [data-testid="stFileUploader"] {
    margin: 0 !important;
}
.st-key-plus_upload_file [data-testid="stWidgetLabel"],
.st-key-plus_upload_image [data-testid="stWidgetLabel"] {
    position: relative !important;
    z-index: 0 !important;
    display: flex !important;
    align-items: center !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    pointer-events: none !important;  /* klik tembus ke overlay dropzone */
}
.st-key-plus_upload_file [data-testid="stWidgetLabel"] p,
.st-key-plus_upload_image [data-testid="stWidgetLabel"] p {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #3D3929 !important;
    margin: 0 !important;
}
/* strip lampiran yang menunggu dikirim (hasil menu ➕) */
.st-key-pending_strip { padding: 2px 2px 0; }
.st-key-pending_strip [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: flex-start !important;
}
.st-key-pending_strip [data-testid="stImage"] { margin: 0 !important; }
.st-key-pending_strip button {
    min-height: 24px !important;
    height: 24px !important;
    font-size: 0.72rem !important;
    padding: 0 10px !important;
    border-radius: 8px !important;
}

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
/* label PREMIUM kecil di sebelah nama model (tier Hard & Extreme) */
.model-premium-badge {
    display: inline-block;
    font-size: 0.62rem; font-weight: 700;
    color: #C15F3C;
    background: rgba(218,119,86,0.12);
    border: 1px solid rgba(218,119,86,0.35);
    border-radius: 999px;
    padding: 1px 7px;
    margin-left: 6px;
    letter-spacing: 0.03em;
    vertical-align: middle;
}
/* label PREMIUM: dipojokkan kecil di sudut kanan-atas tiap baris model
   (bukan menempel di sebelah nama) — ukuran & huruf dibuat mini */
[data-testid="stPopoverBody"] [class*="_premium"] {
    position: relative;
}
[data-testid="stPopoverBody"] [class*="_premium"]::after {
    content: "Premium";
    position: absolute;
    top: 4px; right: 6px;
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: #B0774F;
    background: rgba(218,119,86,0.10);
    border: 1px solid rgba(218,119,86,0.25);
    border-radius: 999px;
    padding: 1px 6px;
    pointer-events: none;
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
/* bintang ✳ fallback: pastikan tidak pernah ada warna latar belakang/kotak */
.star {
    background: transparent !important;
    background-color: transparent !important;
    border: none; box-shadow: none;
}
/* bintang ✳ terracotta berdenyut & berputar pelan (fallback) */
.claude-think .star {
    font-size: 1.05rem; color: #DA7756; line-height: 1;
    animation: starPulse 2.2s ease-in-out infinite;
    display: inline-block;
}
@keyframes starPulse {
    0%, 100% { transform: scale(1) rotate(0deg);   opacity: 0.85; }
    50%      { transform: scale(1.25) rotate(90deg); opacity: 1; }
}

/* ===== LOGO THINKING: shimmer glow BERJALAN yang halus + denyut ===== */
/* Pita cahaya lembut (gradasi transparan→putih→transparan + blur +
   blend screen) menyapu melintasi logo dari kiri ke kanan terus-menerus.
   Tepinya gradasi & di-blur → mulus tanpa garis patah. */
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
/* pita cahaya berjalan */
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
    text-align: center; color: #A8A69E; font-size: 0.6rem;
    margin-top: 34px; font-family: 'Inter', sans-serif;
}
/* versi saat chat berjalan: lebih kecil lagi dari versi halaman awal */
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


def build_system_prompt() -> str:
    """Gabungkan persona dasar Yuki + preferensi dari halaman "Sesuaikan"
    (panggilan & instruksi tambahan), bila diisi user."""
    parts = [YUKI_SYSTEM_PROMPT]
    nickname = (st.session_state.get("custom_nickname") or "").strip()
    if nickname:
        parts.append(f"Panggil User dengan sebutan: {nickname}.")
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


# ============================================================================
# ENGINE 3: SUARA & GAMBAR (Groq — Whisper STT, Llama-4 vision)
# ============================================================================
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
def bubble_html(role: str, content: str, timestamp: str = "",
                images_html: str = "", meta_note: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = f'<div class="ai-label">{logo_img_html("logo-label")} Yuki</div>'
    note = f'<div class="bubble-meta">{html.escape(meta_note)}</div>' if meta_note else ""
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}{images_html}</div>'
        f"{note}"
        f"</div></div>"
    )


def images_bubble_html(images: list[dict]) -> str:
    """Thumbnail lampiran gambar (base64) untuk ditampilkan di bubble user."""
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


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble, bisa + gambar lampiran/suara) atau gambar."""
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
        # baris aksi kecil ala Claude: copy jawaban, feedback (👍/👎), jam kirim
        if msg.get("role") == "assistant":
            render_message_actions(msg)


def _copy_button_html(text: str, key: str) -> str:
    """Tombol salin ala Claude (ikon polos) — teks disisipkan sebagai
    base64 di atribut data-* supaya aman dari karakter kutip/baris baru,
    lalu didekode & disalin ke clipboard lewat sedikit JS di sisi klien."""
    b64 = base64.b64encode((text or "").encode("utf-8")).decode("ascii")
    return (
        f'<button class="msg-action-btn" data-b64="{b64}" '
        f'onclick="const t=atob(this.dataset.b64);'
        f"navigator.clipboard.writeText(decodeURIComponent(escape(t)));"
        f"const o=this.innerHTML;this.innerHTML='✓';"
        f'setTimeout(()=>{{this.innerHTML=o;}},1200);" '
        f'title="Salin jawaban">⧉</button>'
    )


def render_message_actions(msg: dict) -> None:
    """Baris kecil di bawah jawaban Yuki: salin, feedback 👍/👎, jam kirim."""
    mid = msg.get("id", id(msg))
    feedback = msg.get("feedback")
    with st.container(key=f"msg_actions_{mid}"):
        cols = st.columns([0.05, 0.05, 0.05, 0.85])
        with cols[0]:
            st.markdown(_copy_button_html(msg.get("content", ""), f"copy_{mid}"),
                        unsafe_allow_html=True)
        with cols[1]:
            up_active = feedback == "up"
            if st.button("👍" if not up_active else "👍🏻", key=f"fb_up_{mid}",
                         help="Jawaban membantu"):
                msg["feedback"] = None if up_active else "up"
                st.rerun()
        with cols[2]:
            down_active = feedback == "down"
            if st.button("👎" if not down_active else "👎🏻", key=f"fb_down_{mid}",
                         help="Jawaban kurang membantu"):
                msg["feedback"] = None if down_active else "down"
                st.rerun()
        with cols[3]:
            if msg.get("time"):
                st.markdown(
                    f'<div class="msg-action-time">{html.escape(msg["time"])}</div>',
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

# Durasi minimum proses berpikir (detik) — ±10 detik ala Claude
THINKING_MIN_SECONDS = 10.0

# Durasi minimum progress bar gambar (detik) — biar animasi % terasa
IMAGE_MIN_SECONDS = 10.0

# Delay antar kata saat jawaban diketik kata per kata (cepat & tetap natural)
WORD_STREAM_DELAY = 0.03


@st.cache_data(show_spinner=False)
def _thinking_logo_b64() -> str:
    """Logo custom (PNG transparan) sebagai base64 untuk inline HTML."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "assets", "logo_thinking_small.png")
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode("ascii")
    except Exception:
        return ""


def logo_img_html(css_class: str = "logo-inline") -> str:
    """Tag <img> logo custom; fallback ke bintang ✳ bila file tidak ada."""
    b64 = _thinking_logo_b64()
    if b64:
        return f'<img class="{css_class}" src="data:image/png;base64,{b64}" alt="✳"/>'
    return '<span class="star">✳</span>'


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    logo_b64 = _thinking_logo_b64()
    if logo_b64:
        # Logo dengan glow halus bernapas (halo radial + drop-shadow
        # bertingkat + denyut) — semua ease-in-out, mulus.
        src = f"data:image/png;base64,{logo_b64}"
        icon = (
            '<span class="logo-shimmer">'
            f'<img src="{src}" alt=""/>'
            "</span>"
        )
    else:
        icon = '<span class="star">✳</span>'  # fallback bila file logo hilang
    return (
        '<div class="claude-think">'
        f"{icon}"
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
        f'{logo_img_html("logo-progress")}'
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
def _capture_artifacts_from_reply(full_text: str) -> None:
    """Deteksi blok kode (```...```) di jawaban Yuki & simpan sebagai
    "Artefak" ringan ala Claude — supaya kode panjang gampang dibuka lagi
    / disalin lewat sidebar, tanpa harus scroll riwayat chat."""
    blocks = re.findall(r"```(\w*)\n(.*?)```", full_text or "", flags=re.S)
    for lang, code in blocks:
        code = code.strip("\n")
        if len(code) < 40:  # blok terlalu pendek, tidak perlu dijadikan artefak
            continue
        first_line = code.splitlines()[0][:40] if code.splitlines() else "Kode"
        st.session_state.artifacts.insert(0, {
            "id": len(st.session_state.artifacts) + 1,
            "title": f"{lang or 'kode'} · {first_line}",
            "content": code,
            "lang": lang,
            "time": datetime.now().strftime("%H:%M"),
        })


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
            content = (m.get("content") or "").strip()
            if m.get("images"):
                content += "\n*(dengan lampiran gambar)*"
            if m.get("via_voice"):
                content += "\n*(dikirim via suara)*"
            lines.append(content)
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
    if "selected_model_key" not in st.session_state:
        st.session_state.selected_model_key = DEFAULT_MODEL_KEY
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "web_search_on" not in st.session_state:
        st.session_state.web_search_on = False
    # Sesuaikan (custom instruction persona Yuki)
    if "custom_nickname" not in st.session_state:
        st.session_state.custom_nickname = ""
    if "custom_instruction" not in st.session_state:
        st.session_state.custom_instruction = ""
    # Proyek ringan: nama & catatan/instruksi khusus per proyek
    if "projects" not in st.session_state:
        st.session_state.projects = []  # list[{id, name}]
    if "project_counter" not in st.session_state:
        st.session_state.project_counter = 0
    if "active_project_id" not in st.session_state:
        st.session_state.active_project_id = None
    # Artefak: kode/tulisan panjang dari jawaban Yuki, dikumpulkan otomatis
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []  # list[{id, title, content, time}]
    # Lampiran yang di-stage lewat menu ➕ (menunggu dikirim bersama pesan)
    if "pending_images" not in st.session_state:
        st.session_state.pending_images = []
    if "plus_uploader_gen" not in st.session_state:
        st.session_state.plus_uploader_gen = 0
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
HAS_DIALOG = hasattr(st, "dialog")


def _register_dialog(title: str, func):
    """Bungkus fungsi jadi @st.dialog kalau tersedia; kalau versi Streamlit
    lama tidak mendukung, tampilkan pesan singkat sebagai fallback."""
    if HAS_DIALOG:
        return st.dialog(title)(func)

    def _fallback(*a, **kw):
        st.info("Fitur ini butuh Streamlit versi lebih baru untuk tampil sebagai jendela popup.")
    return _fallback


def _proyek_dialog_body() -> None:
    st.text_input("Cari proyek", key="proj_search", placeholder="Cari proyek…",
                  label_visibility="collapsed")
    query = (st.session_state.get("proj_search") or "").strip().lower()
    projects = st.session_state.get("projects", [])
    shown = [p for p in projects if query in p["name"].lower()] if query else projects

    if not shown:
        st.caption("Belum ada proyek." if not projects else "Tidak ada proyek yang cocok.")
    else:
        for p in shown:
            active = st.session_state.get("active_project_id") == p["id"]
            label = f"📁 {p['name']}" + ("  ✓" if active else "")
            if st.button(label, key=f"proj_pick_{p['id']}", use_container_width=True):
                st.session_state.active_project_id = None if active else p["id"]
                st.rerun()

    st.divider()
    new_name = st.text_input("Nama proyek baru", key="proj_new_name",
                              placeholder="Nama proyek baru…", label_visibility="collapsed")
    if st.button("＋ Mulai proyek baru", use_container_width=True):
        name = (new_name or "").strip()
        if name:
            st.session_state.project_counter += 1
            st.session_state.projects.append({"id": st.session_state.project_counter, "name": name})
            st.rerun()


def _artefak_dialog_body() -> None:
    artifacts = st.session_state.get("artifacts", [])
    if not artifacts:
        st.caption("Belum ada artefak. Kode panjang dari jawaban Yuki akan "
                   "otomatis muncul di sini.")
        return
    for art in artifacts[:20]:
        with st.expander(f"🧩 {art['title']}  ·  {art.get('time', '')}"):
            st.code(art["content"], language=art.get("lang") or None)


def _sesuaikan_dialog_body() -> None:
    st.text_input(
        "Bagaimana Yuki memanggil Anda?",
        key="custom_nickname_input",
        value=st.session_state.get("custom_nickname", ""),
        placeholder="mis. Kak Budi",
    )
    st.text_area(
        "Instruksi tambahan untuk Yuki",
        key="custom_instruction_input",
        value=st.session_state.get("custom_instruction", ""),
        placeholder="mis. Jawab selalu singkat & pakai bahasa santai.",
        height=120,
    )
    if st.button("Simpan", type="primary", use_container_width=True):
        st.session_state.custom_nickname = st.session_state.get("custom_nickname_input", "")
        st.session_state.custom_instruction = st.session_state.get("custom_instruction_input", "")
        st.rerun()


show_proyek_dialog = _register_dialog("Proyek", _proyek_dialog_body)
show_artefak_dialog = _register_dialog("Artefak", _artefak_dialog_body)
show_sesuaikan_dialog = _register_dialog("Sesuaikan", _sesuaikan_dialog_body)


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

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        with st.container(key="sb_menu_proyek"):
            if st.button(":material/deployed_code: &nbsp;Proyek", use_container_width=True):
                show_proyek_dialog()
        with st.container(key="sb_menu_artefak"):
            n_art = len(st.session_state.get("artifacts", []))
            art_label = f":material/data_object: &nbsp;Artefak" + (f"  ({n_art})" if n_art else "")
            if st.button(art_label, use_container_width=True):
                show_artefak_dialog()
        with st.container(key="sb_menu_sesuaikan"):
            if st.button(":material/tune: &nbsp;Sesuaikan", use_container_width=True):
                show_sesuaikan_dialog()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

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
        st.session_state.selected_model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )
    # Pesan bergambar WAJIB lewat model vision (model teks tidak bisa lihat gambar)
    last_user = next(
        (m for m in reversed(st.session_state.messages) if m.get("role") == "user"),
        None,
    )
    has_images = bool(last_user and last_user.get("images"))
    if has_images:
        model_id = VISION_MODEL_ID
    elif st.session_state.get("web_search_on"):
        # Toggle "Pencarian web" ala Claude → pakai model Compound
        # (satu-satunya model Groq di katalog ini yang bisa browsing).
        model_id = AVAILABLE_MODELS["compound"]

    # Thinking ala Claude — frasa berganti-ganti selama beberapa detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, st.session_state.messages, vision=has_images
            )
        )

        # Tahan sampai proses berpikir genap minimal beberapa detik
        elapsed = time.time() - t0
        if elapsed < THINKING_MIN_SECONDS:
            time.sleep(THINKING_MIN_SECONDS - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul kata per kata dengan delay agak lambat
        stream_words(answer_slot, full)

        reply = {
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        }
        st.session_state.messages.append(reply)
        _capture_artifacts_from_reply(full)
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
            f'{logo_img_html("logo-greeting")} Semangat lagi!'
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
    # Mic 🎤 & lampiran 📎 native Streamlit (kirim gambar, paste, drag-drop);
    # otomatis nonaktif bila versi Streamlit belum mendukung.
    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True
    user_input = st.chat_input(placeholder_text, **chat_kwargs)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    # Dirender ke dok bawah Streamlit (wadah yang sama dengan st.chat_input)
    # → otomatis ikut bergeser saat sidebar dibuka/ditutup (seperti Claude).
    # CSS menariknya naik (margin-top negatif) ke ruang padding kotak input.
    # (st._bottom deprecated di Streamlit baru → pakai st.bottom bila tersedia)
    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="chat_controls"):

            # ---- Strip lampiran yang menunggu dikirim (dari menu ➕) ----
            pending = st.session_state.get("pending_images", [])
            if pending:
                with st.container(key="pending_strip"):
                    pcols = st.columns([0.1] * len(pending) + [1.0])
                    for i, im in enumerate(pending):
                        with pcols[i]:
                            st.image(im["data"], width=54)
                            if st.button("✕", key=f"pending_rm_{i}",
                                         use_container_width=True):
                                st.session_state.pending_images.pop(i)
                                st.rerun()
                    with pcols[-1]:
                        st.markdown(
                            '<div class="plus-menu-hint">Siap dikirim…</div>',
                            unsafe_allow_html=True,
                        )

            # [➕ menu] [Gambar] ....spacer.... [Nama Model]
            ctrl_plus, ctrl_mode, _sp, ctrl_model = st.columns(
                [0.08, 0.22, 1.22, 0.28]
            )

            # ---- Menu ➕ ala Claude: MINIMALIST — hanya 2 baris ikon+teks
            #      (📎 Upload file · 📸 Upload gambar atau foto). Mode chat/
            #      gambar, pencarian web, suara, unduh & chat baru sudah ada
            #      di luar popup ini, jadi tidak diduplikasi di sini. ----
            with ctrl_plus:
                with st.container(key="plus_menu"):
                    with st.popover(":material/add:", use_container_width=False,
                                    help="Unggah file atau gambar"):
                        gen = st.session_state.get("plus_uploader_gen", 0)

                        def _stage_uploaded(files) -> bool:
                            if not files:
                                return False
                            staged = st.session_state.get("pending_images", [])
                            seen = {(im["name"], len(im["data"])) for im in staged}
                            added = False
                            for im in collect_images(files):
                                k = (im["name"], len(im["data"]))
                                if k not in seen:
                                    staged.append(im)
                                    seen.add(k)
                                    added = True
                            st.session_state.pending_images = staged
                            return added

                        with st.container(key="plus_upload_file"):
                            picked_file = st.file_uploader(
                                "📎  Upload file", type=IMAGE_INPUT_TYPES,
                                accept_multiple_files=True,
                                label_visibility="visible",
                                key=f"plus_uploader_file_{gen}",
                            )
                        with st.container(key="plus_upload_image"):
                            picked_image = st.file_uploader(
                                "📸  Upload gambar atau foto", type=IMAGE_INPUT_TYPES,
                                accept_multiple_files=True,
                                label_visibility="visible",
                                key=f"plus_uploader_image_{gen}",
                            )
                        added_file = _stage_uploaded(picked_file)
                        added_image = _stage_uploaded(picked_image)
                        if added_file or added_image:
                            # tutup popover & langsung tampilkan thumbnail
                            # lampiran di dalam kotak chat input (ala Claude)
                            st.rerun()

                        st.markdown('<div class="plus-menu-divider"></div>',
                                    unsafe_allow_html=True)

                        # Ambil tangkapan layar — browser murni tidak bisa
                        # memicu screen-capture dari Streamlit, jadi diarahkan
                        # ke cara tercepat: screenshot OS lalu tempel (Ctrl+V).
                        if st.button("📷  Ambil tangkapan layar", key="pm_screenshot",
                                     use_container_width=True):
                            st.toast("Ambil screenshot dengan tombol OS kamu, lalu "
                                     "tempel (Ctrl+V) di kotak chat.", icon="📷")

                        # Pencarian web — beralih otomatis ke model Compound
                        # (browsing) tanpa mengubah pilihan model utama.
                        web_check = " :orange[✓]" if st.session_state.get("web_search_on") else ""
                        if st.button(f"🌐  Pencarian web{web_check}", key="pm_web",
                                     use_container_width=True):
                            st.session_state.web_search_on = not st.session_state.get("web_search_on", False)
                            st.rerun()

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
                current_key = st.session_state.selected_model_key
                current_name = MODEL_BY_KEY.get(current_key, MODEL_BY_KEY[DEFAULT_MODEL_KEY])["name"]
                with st.popover(current_name, use_container_width=False):
                    # Daftar model ala Claude, sudah terurut dari tingkat
                    # termudah → tertinggi. Tier Hard & Extreme diberi
                    # label PREMIUM kecil di sebelah nama.
                    for m in MODEL_CATALOG:
                        is_active = m["key"] == st.session_state.selected_model_key
                        check = " :orange[✓]" if is_active else ""
                        label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                        row_key = f"model_row_{m['key']}" + ("_premium" if m.get("premium") else "")
                        with st.container(key=row_key):
                            if st.button(label, key=f"model_{m['key']}", use_container_width=True):
                                st.session_state.selected_model_key = m["key"]
                                st.rerun()

    # ---------- Proses kiriman (teks / lampiran gambar / rekaman suara) ----------
    if user_input is not None:
        # Bongkar nilai chat input: teks + lampiran + rekaman (bila didukung)
        if isinstance(user_input, str):
            raw_text, send_files, send_audio = user_input, [], None
        else:
            raw_text = getattr(user_input, "text", "") or ""
            send_files = list(getattr(user_input, "files", None) or [])
            send_audio = getattr(user_input, "audio", None)

        text = (raw_text or "").strip()
        via_voice = False

        # Kiriman suara tanpa teks → transkrip dulu dengan Groq Whisper
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
        # Gabungkan lampiran yang di-stage lewat menu ➕ (hindari duplikat)
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

            # simpan & tampilkan pesan user (+ thumbnail lampiran)
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

            # Ada lampiran gambar → selalu chat vision (Yuki melihat gambarnya),
            # walau toggle "Gambar" sedang aktif sekalipun.
            if st.session_state.image_mode and not images:
                handle_image_request(text)
            else:
                answer_slot = st.empty()
                handle_chat_request(answer_slot)

            st.rerun()

    # ---------- Footer ----------
    # Halaman awal: ukuran normal. Saat chat berjalan: lebih kecil lagi.
    foot_class = "trinity-foot" if is_fresh else "trinity-foot in-chat"
    st.markdown(
        f'<p class="{foot_class}">🔱 Ampera Trinity AI · by Ampera Official · 2026</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
