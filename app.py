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
_LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "logo_thinking_small.png"
)
st.set_page_config(
    page_title="Ampera Trinity AI",
    page_icon=_LOGO_PATH if os.path.exists(_LOGO_PATH) else "🔱",
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
# ============================================================================
# KATALOG HALAMAN BARU
#   (halaman Artefak, Bahasa, Pengaturan, Bantuan, Trinity Pro, Aplikasi,
#    Trinity Kursus, Pelajari lebih lanjut)
# ============================================================================

# --- Bahasa yang bisa dipakai (halaman "Bahasa") ---
SUPPORTED_LANGUAGES = [
    {"code": "id", "flag": "🇮🇩", "name": "Bahasa Indonesia", "native": "Baku",  "level": "Penuh",       "yuki": True},
    {"code": "en", "flag": "🇬🇧", "name": "English",          "native": "British", "level": "Penuh",     "yuki": True},
    {"code": "ms", "flag": "🇲🇾", "name": "Bahasa Melayu",    "native": "Malaysia", "level": "Penuh",    "yuki": True},
    {"code": "su", "flag": "🇮🇩", "name": "Basa Sunda",       "native": "Sunda",    "level": "Beta",     "yuki": True},
    {"code": "jv", "flag": "🇮🇩", "name": "Basa Jawa",        "native": "Ngoko",    "level": "Beta",     "yuki": True},
    {"code": "ja", "flag": "🇯🇵", "name": "日本語",           "native": "Nihongo",  "level": "Penuh",    "yuki": True},
    {"code": "ko", "flag": "🇰🇷", "name": "한국어",           "native": "Hangugeo", "level": "Penuh",    "yuki": True},
    {"code": "zh", "flag": "🇨🇳", "name": "中文",             "native": "简体",     "level": "Penuh",    "yuki": True},
    {"code": "es", "flag": "🇪🇸", "name": "Español",          "native": "España",   "level": "Penuh",    "yuki": True},
    {"code": "pt", "flag": "🇧🇷", "name": "Português",        "native": "Brasil",   "level": "Penuh",    "yuki": True},
    {"code": "fr", "flag": "🇫🇷", "name": "Français",         "native": "France",   "level": "Penuh",    "yuki": True},
    {"code": "de", "flag": "🇩🇪", "name": "Deutsch",          "native": "Deutsch",  "level": "Penuh",    "yuki": True},
    {"code": "ar", "flag": "🇸🇦", "name": "العربية",          "native": "Fusha",    "level": "Beta",     "yuki": True},
    {"code": "hi", "flag": "🇮🇳", "name": "हिन्दी",            "native": "Hindi",    "level": "Beta",     "yuki": True},
]
LANG_BY_CODE = {l["code"]: l for l in SUPPORTED_LANGUAGES}
DEFAULT_LANG_CODE = "id"

# --- Kotak kategori halaman Artefak (ala Claude) ---
ARTIFACT_CATEGORIES = [
    {"key": "app",  "icon": ":material/public:",        "title": "Aplikasi dan situs web",
     "desc": "Landing page, dashboard, web app interaktif",
     "brief": ("Aku ingin membuat APLIKASI / SITUS WEB. Tawarkan 3 ide konkret "
               "(judul + 1 kalimat), lalu tanyakan mana yang mau dikerjakan. "
               "Setelah aku memilih, langsung buatkan kode lengkapnya "
               "(HTML + CSS + JavaScript dalam satu file supaya gampang "
               "dijalankan) beserta penjelasan singkat cara pakainya.")},
    {"key": "doc",  "icon": ":material/description:",   "title": "Dokumen dan templat",
     "desc": "Proposal, CV, surat, laporan, template siap pakai",
     "brief": ("Aku ingin membuat DOKUMEN / TEMPLATE. Tawarkan 3 opsi dokumen "
               "yang paling berguna untukku, lalu tanyakan mana yang dibuat. "
               "Setelah aku memilih, tuliskan dokumen lengkapnya dengan "
               "struktur rapi (judul, sub-bagian, tabel bila perlu) dan beri "
               "versi siap salin.")},
    {"key": "game", "icon": ":material/sports_esports:", "title": "Permainan",
     "desc": "Game mini di browser: teka-teki, arcade, kuis",
     "brief": ("Aku ingin membuat PERMAINAN. Tawarkan 3 ide game sederhana yang "
               "bisa jalan di browser, lalu tanyakan pilihanku. Setelah aku "
               "memilih, buatkan kode lengkapnya dalam satu file HTML "
               "(Canvas / JavaScript) plus cara mainnya.")},
    {"key": "prod", "icon": ":material/task_alt:",      "title": "Alat produktivitas",
     "desc": "To-do list, kalkulator, tracker, timer fokus",
     "brief": ("Aku butuh ALAT PRODUKTIVITAS. Tawarkan 3 ide alat (to-do, "
               "tracker, kalkulator, timer) yang paling membantu pekerjaanku, "
               "lalu tanyakan pilihanku dan langsung buatkan alatnya dalam "
               "satu file HTML yang bisa langsung kupakai.")},
    {"key": "kre",  "icon": ":material/brush:",         "title": "Proyek kreatif",
     "desc": "Cerita, puisi, skrip, konsep desain, lirik",
     "brief": ("Aku ingin mengerjakan PROYEK KREATIF. Tawarkan 3 konsep kreatif "
               "yang seru, lalu tanyakan mana yang mau dibuat. Setelah aku "
               "memilih, buatkan hasil lengkapnya (naskah/cerita/konsep) "
               "dengan gaya yang hidup.")},
    {"key": "quiz", "icon": ":material/quiz:",          "title": "Kuis atau survei",
     "desc": "Kuis interaktif, formulir survei, penilaian",
     "brief": ("Aku ingin membuat KUIS / SURVEI. Tanyakan dulu topiknya dan "
               "berapa soal yang kubutuhkan, lalu buatkan kuis interaktif "
               "dalam satu file HTML (ada skor otomatis di akhir) atau daftar "
               "pertanyaan survei yang rapi.")},
    {"key": "new",  "icon": ":material/add_circle:",    "title": "Mulai dari awal",
     "desc": "Kanvas kosong — jelaskan idemu sendiri",
     "brief": ("Aku mau mulai ARTEFAK BARU dari nol. Tanyakan dulu apa yang "
               "ingin kubuat, untuk siapa, dan batasan apa saja. Setelah itu "
               "susun rencananya lalu kerjakan.")},
]
ARTIFACT_BY_KEY = {c["key"]: c for c in ARTIFACT_CATEGORIES}

# --- Katalog kursus Trinity (halaman "Trinity kursus") ---
COURSE_CATALOG = [
    {"key": "pemasaran",  "icon": ":material/campaign:",         "title": "Pemasaran",
     "desc": "Strategi promosi, branding, dan funnel", "level": "Pemula → Lanjut"},
    {"key": "penjualan",  "icon": ":material/handshake:",        "title": "Penjualan",
     "desc": "Closing, negosiasi, follow-up pelanggan", "level": "Pemula → Lanjut"},
    {"key": "desain",     "icon": ":material/palette:",          "title": "Desain",
     "desc": "Visual, layout, warna, dan tipografi", "level": "Pemula → Lanjut"},
    {"key": "copywriting","icon": ":material/edit_note:",        "title": "Copywriting",
     "desc": "Tulisan yang menjual & menggerakkan", "level": "Pemula → Menengah"},
    {"key": "branding",   "icon": ":material/auto_awesome:",     "title": "Branding",
     "desc": "Identitas merek yang diingat orang", "level": "Menengah"},
    {"key": "keuangan",   "icon": ":material/payments:",         "title": "Keuangan",
     "desc": "Atur uang usaha & arus kas", "level": "Pemula"},
    {"key": "produktivitas","icon": ":material/timer:",          "title": "Produktivitas",
     "desc": "Fokus, prioritas, dan sistem kerja", "level": "Pemula"},
    {"key": "publik",     "icon": ":material/record_voice_over:","title": "Public speaking",
     "desc": "Bicara di depan orang tanpa gemetar", "level": "Pemula → Menengah"},
    {"key": "konten",     "icon": ":material/photo_camera:",     "title": "Konten kreator",
     "desc": "Ide, skrip, dan jadwal konten", "level": "Pemula → Lanjut"},
    {"key": "ai",         "icon": ":material/smart_toy:",        "title": "AI untuk bisnis",
     "desc": "Pakai AI untuk kerja sehari-hari", "level": "Pemula"},
]
COURSE_BY_KEY = {c["key"]: c for c in COURSE_CATALOG}


def course_curriculum(course: dict) -> list[str]:
    """Susun 4 modul belajar otomatis dari topik kursus yang dipilih."""
    t = course["title"]
    return [
        f"Modul 1 · Fondasi {t} — istilah penting & peta besar",
        f"Modul 2 · Alat & workflow {t} yang benar-benar terpakai",
        f"Modul 3 · Strategi tingkat lanjut + studi kasus nyata",
        "Modul 4 · Proyek praktik & evaluasi hasil belajar",
    ]


# --- Nilai bawaan seluruh Pengaturan (9 tab) ---
DEFAULT_SETTINGS: dict = {
    # Umum
    "ui_lang": DEFAULT_LANG_CODE,
    "yuki_lang": DEFAULT_LANG_CODE,
    "theme": "Krem (Claude)",
    "font_size": "Normal",
    "compact_mode": False,
    "stream_speed": "Sedang",
    "min_think_seconds": 10.0,
    "personality": "Santai & kocak",
    "default_mode": "Chat",
    # Akun
    "display_name": "User",
    "email": "",
    "username": "user",
    "bio": "",
    # Privasi
    "allow_web_search": True,
    "save_history": True,
    "keep_voice": False,
    "analytics": True,
    "personalization": True,
    "cloud_sync": False,
    # Penagihan
    "plan": "Free",
    "billing_cycle": "Bulanan",
    "payment_method": "Belum ada metode pembayaran",
    # Kemampuan
    "cap_web_search": True,
    "cap_artifacts": True,
    "cap_voice": True,
    "cap_vision": True,
    "cap_image": True,
    # Memori
    "memories": [],
    "memory_on": True,
    "memory_auto": False,
    # Refleksi
    "reflection_goal": "",
    "reflection_habit": "",
    "reflection_freq": "Setiap hari",
    "reflection_tone": "Mendorong",
    # Waktu dan fokus
    "focus_minutes": 25,
    "break_minutes": 5,
    "work_start": "09:00",
    "work_end": "18:00",
    "tz_label": "Asia/Jakarta (WIB)",
    "focus_reminder": True,
    # Trinity Code
    "groq_key": "",
    "cf_account_id": "",
    "cf_token": "",
    "temperature": 0.7,
    "advanced_errors": False,
}

PAGE_TITLES = {
    "artefak": "Artefak",
    "bahasa": "Bahasa",
    "pengaturan": "Pengaturan",
    "bantuan": "Dapatkan bantuan",
    "tingkatkan": "Tingkatkan paket",
    "aplikasi": "Dapatkan aplikasi",
    "kursus": "Trinity kursus",
    "pelajari": "Pelajari lebih lanjut",
}

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
/* LAPISAN TAMBAHAN: beberapa versi Streamlit menaruh latar putih di elemen
   dalam tombol (style emotion) atau memberi class key per tombol — paksa
   transparan semuanya supaya baris feedback benar-benar polos tanpa kotak. */
[class*="st-key-msg_actions_"] [data-testid^="stBaseButton"],
[class*="st-key-fb_up_"] button, [class*="st-key-fb_down_"] button,
[class*="st-key-msg_actions_"] div.stButton > button > div,
[class*="st-key-fb_up_"] button > div, [class*="st-key-fb_down_"] button > div,
[class*="st-key-msg_actions_"] div.stButton > button p,
[class*="st-key-msg_actions_"] [data-testid="stMarkdownContainer"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ---------- ikon SVG garis tipis ala Claude (stroke = warna teks) ---------- */
.icon-svg {
    width: 15px; height: 15px;
    display: inline-block; vertical-align: -2px; flex-shrink: 0;
}
.msg-action-btn .icon-svg { width: 15px; height: 15px; }
.bubble-meta .icon-svg { width: 12px; height: 12px; margin-right: 3px; }
.bubble > .icon-svg { width: 16px; height: 16px; margin-right: 6px; vertical-align: -3px; }
.sb-account .icon-svg { width: 14px; height: 14px; color: #A8A69E; }
.sb-account .right-icons .icon-svg { width: 16px; height: 16px; color: #73726C; }
.trinity-foot .logo-foot { width: 12px; height: 12px; vertical-align: -2px; margin-right: 4px; }

/* ikon material di baris aksi: ukuran rapi; state aktif (primary) terracotta */
[class*="st-key-msg_actions_"] [data-testid="stIconMaterial"] {
    font-size: 1.05rem !important;
}
[class*="st-key-msg_actions_"] div.stButton > button[kind="primary"],
[class*="st-key-msg_actions_"] [data-testid="stBaseButton-primary"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #C15F3C !important;
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

/* caret berkedip saat jawaban muncul bertahap */
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
/* ============ HALAMAN BARU (Artefak · Pengaturan · Bahasa ·
   Bantuan · Trinity Pro · Aplikasi · Trinity Kursus · Pelajari) ============ */
/* --- baris akun + menu titik tiga --- */
.sb-account {
    padding-right: 48px;            /* ruang untuk tombol menu ⋯ */
    border-top: none;
    pointer-events: none;           /* teksnya saja; tombol di sebelahnya */
}
.st-key-sb_account [data-testid="stVerticalBlock"] { gap: 0 !important; }
.st-key-sb_account [data-testid="stColumn"]:first-child { padding-right: 0 !important; }
.st-key-acct_menu {
    position: fixed; bottom: 12px; left: 208px; z-index: 999996;
}
.st-key-acct_menu [data-testid="stPopover"] > div { width: auto !important; }
.st-key-acct_menu button[data-testid="stPopoverButton"],
.st-key-acct_menu [data-testid="stPopover"] button {
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    color: #73726C !important;
    width: 32px !important; min-width: 32px !important; height: 32px !important;
    border-radius: 8px !important; padding: 0 !important;
    display: grid !important; place-items: center !important;
}
.st-key-acct_menu button:hover {
    background: #E8E5D8 !important; color: #3D3929 !important;
}
.st-key-acct_menu button svg { width: 20px !important; height: 20px !important; }

/* --- judul halaman --- */
.page-head {
    display: flex; align-items: flex-start; gap: 14px;
    margin: 4px 0 18px;
}
.page-head-icon {
    width: 40px; height: 40px; flex-shrink: 0;
    border-radius: 12px;
    background: #E8E5D8; border: 1px solid #D5D1C3;
    display: grid; place-items: center;
    color: #C15F3C;
}
.page-head-icon [data-testid="stIconMaterial"],
.page-head-icon span[data-testid="stIconMaterial"] { font-size: 21px !important; }
.page-head h2.page-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.55rem; font-weight: 600; color: #1a1915;
    margin: 0 0 2px; line-height: 1.15; letter-spacing: -0.01em;
}
.page-head p.page-sub {
    margin: 0; font-size: 0.9rem; color: #73726C; line-height: 1.45;
}

/* --- tombol besar bergaya kartu (kategori artefak, kursus) --- */
button[kind="secondary"] > div > p > strong,
div.stButton > button p strong { color: #3D3929; }
.st-key-cat_app button, .st-key-cat_doc button, .st-key-cat_game button,
.st-key-cat_prod button, .st-key-cat_kre button, .st-key-cat_quiz button,
.st-key-cat_new button,
[class*="st-key-kurs_"] button {
    background: #FAF9F5 !important;
    border: 1px solid #E3E0D5 !important;
    border-radius: 14px !important;
    padding: 16px 16px !important;
    min-height: 86px !important; height: auto !important;
    text-align: left !important;
    align-items: flex-start !important;
    transition: border-color .16s ease, background .16s ease, transform .16s ease;
}
.st-key-cat_app button:hover, .st-key-cat_doc button:hover,
.st-key-cat_game button:hover, .st-key-cat_prod button:hover,
.st-key-cat_kre button:hover, .st-key-cat_quiz button:hover,
.st-key-cat_new button:hover,
[class*="st-key-kurs_"] button:hover {
    border-color: #C9A99A !important;
    background: #FFFDF8 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(61,57,41,0.07) !important;
}
[class*="st-key-cat_"] button [data-testid="stMarkdownContainer"],
[class*="st-key-kurs_"] button [data-testid="stMarkdownContainer"] {
    width: 100%; text-align: left;
}
[class*="st-key-cat_"] button p, [class*="st-key-kurs_"] button p {
    white-space: normal !important; line-height: 1.35;
}

/* --- kartu kosong --- */
.empty-card {
    background: #FAF9F5; border: 1px dashed #D5D1C3;
    border-radius: 14px; padding: 18px;
    color: #73726C; font-size: 0.9rem; line-height: 1.55;
    margin: 2px 0 16px;
}

/* --- hero halaman --- */
.trinity-hero {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 18px;
    padding: 22px; display: flex; gap: 18px; align-items: center;
    margin-bottom: 16px;
}
.trinity-hero > div:first-child { flex-shrink: 0; }
.trinity-hero .logo-greeting { width: 54px; height: 54px; }
.trinity-hero .hero-text h1 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.8rem; font-weight: 600; color: #1a1915;
    margin: 0 0 6px; letter-spacing: -0.01em;
}
.trinity-hero .hero-text p {
    margin: 0; color: #73726C; font-size: 0.92rem; line-height: 1.55;
}

/* --- judul bagian di dalam halaman --- */
.set-section {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.06rem; font-weight: 600; color: #3D3929;
    margin: 22px 0 10px;
}

/* --- kartu kemampuan --- */
.cap-card {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 14px;
    padding: 6px 14px; margin: 4px 0 8px;
}
.cap-row {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 0; border-bottom: 1px solid #EFECDF;
    font-size: 0.9rem;
}
.cap-row:last-child { border-bottom: none; }
.cap-row .cap-icon { color: #C15F3C; display: grid; place-items: center; width: 22px; }
.cap-row .cap-name { flex: 1; color: #3D3929; }
.cap-row .cap-state {
    display: inline-flex; align-items: center; gap: 6px;
    color: #A8A69E; font-size: 0.82rem;
}

/* --- baris fitur / status kecil --- */
.feat-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 9px 2px; font-size: 0.88rem; color: #3D3929;
    border-bottom: 1px solid #EFECDF;
}
.feat-row:last-child { border-bottom: none; }
.chip-on, .chip-off {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.76rem; font-weight: 600;
    padding: 2px 8px; border-radius: 99px; white-space: nowrap;
}
.chip-on { background: #EAF1E4; color: #4C7A3C; }
.chip-off { background: #EFEDE4; color: #8A877E; }

/* --- kartu paket (Trinity Pro) --- */
.plan-card {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 16px;
    padding: 20px; height: 100%; box-sizing: border-box;
}
.plan-card.is-pro {
    border-color: #DA7756; background: #FFF9F5;
    box-shadow: 0 6px 22px rgba(218,119,86,0.14);
}
.plan-name {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.2rem; font-weight: 600; color: #1a1915;
}
.plan-price {
    font-size: 1.75rem; font-weight: 700; color: #C15F3C;
    margin: 6px 0 2px; letter-spacing: -0.02em;
}
.plan-note { font-size: 0.8rem; color: #A8A69E; margin-bottom: 12px; }
.feat-list { margin-top: 4px; }

/* --- memori --- */
.mem-item {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #3D3929; margin-bottom: 6px;
}

/* --- daftar bahasa --- */
.lang-card {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 14px;
    padding: 4px 14px;
}
.lang-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid #EFECDF; font-size: 0.9rem;
}
.lang-row:last-child { border-bottom: none; }
.lang-row .flag { font-size: 1.15rem; line-height: 1; }
.lang-row .lang-name {
    flex: 1; color: #3D3929; font-weight: 500;
    display: flex; flex-direction: column;
}
.lang-row .lang-native { font-size: 0.76rem; color: #A8A69E; font-weight: 400; }
.lang-row .lang-level { display: inline-flex; align-items: center; gap: 6px; }

/* --- langkah bantuan & tips --- */
.help-step {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; font-size: 0.9rem; color: #3D3929; line-height: 1.5;
}
.help-step .step-no {
    width: 24px; height: 24px; flex-shrink: 0;
    border-radius: 50%; background: #E8E5D8; color: #57544A;
    display: grid; place-items: center;
    font-size: 0.74rem; font-weight: 700;
}
.help-step .step-icon { color: #C15F3C; padding-top: 2px; }
.tip-row {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 0; font-size: 0.89rem; color: #3D3929; line-height: 1.5;
}
.tip-row .tip-no {
    width: 22px; height: 22px; flex-shrink: 0; border-radius: 50%;
    background: #F1E5DC; color: #C15F3C;
    display: grid; place-items: center; font-size: 0.72rem; font-weight: 700;
}

/* --- mini card (tentang aplikasi) --- */
.mini-card {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 14px;
    padding: 16px; height: 100%; box-sizing: border-box;
}
.mini-card .mini-icon { color: #C15F3C; margin-bottom: 8px; }
.mini-card .mini-title { font-weight: 600; color: #3D3929; margin-bottom: 4px; }
.mini-card .mini-desc { font-size: 0.84rem; color: #73726C; line-height: 1.5; }

/* --- kartu ponsel (halaman Dapatkan aplikasi) --- */
.phone-card {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 22px;
    padding: 30px 20px; text-align: center;
}
.phone-card .logo-greeting { width: 68px; height: 68px; margin: 0 auto 12px; }
.phone-card .phone-name { font-weight: 600; color: #3D3929; }
.phone-card .phone-tag { font-size: 0.78rem; color: #A8A69E; margin-top: 2px; }

/* --- baris modul kursus --- */
.mod-row {
    background: #FAF9F5; border: 1px solid #E3E0D5; border-radius: 10px;
    padding: 9px 12px; font-size: 0.88rem; color: #3D3929; margin-bottom: 6px;
}

/* --- tab Pengaturan: rapikan --- */
[data-baseweb="tab-list"] { gap: 4px !important; border-bottom: 1px solid #E3E0D5 !important; }
[data-baseweb="tab"] {
    font-size: 0.86rem !important; padding: 8px 10px !important;
    color: #73726C !important; background: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] { color: #3D3929 !important; font-weight: 600 !important; }
[data-baseweb="tab-highlight"] { background-color: #DA7756 !important; }
.st-key-chat_controls [class*="st-key-plus_menu"] [data-testid="stPopover"] button { … }
[data-testid="stPopoverBody"] [class*="st-key-plus_menu"] div.stButton > button,
[class*="st-key-plus_menu"] [data-testid="stPopoverBody"] div.stButton > button { … }
[class*="st-key-plus_upload_file"], [class*="st-key-plus_upload_image"] { … }
[class*="st-key-pending_strip"] { … }

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
        return "Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "Server terlalu lama merespons. Coba lagi."
    return "Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    if status == 401 or "invalid_api_key" in text or "unauthorized" in text or "authentication" in text:
        return "Layanan chat sedang tidak tersedia (konfigurasi). Coba lagi nanti."
    if status == 404 or "model_not_found" in text or "decommissioned" in text or "does not exist" in text:
        return "Model chat tidak tersedia lagi di provider. Coba pilih model lain."
    if status == 429 or "rate_limit" in text or "rate limit" in text or "quota" in text:
        return "Kuota chat sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "Respons terlalu lama. Coba lagi."
    return "Gagal membalas. Coba kirim ulang atau mulai obrolan baru."


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
def get_settings() -> dict:
    """Pengaturan user (halaman Pengaturan) — nilai yang belum diset
    otomatis diisi dari DEFAULT_SETTINGS, jadi aman walau state lama."""
    base = dict(DEFAULT_SETTINGS)
    base.update(st.session_state.get("settings") or {})
    return base


def build_system_prompt() -> str:
    """Gabungkan persona dasar Yuki + preferensi dari halaman "Sesuaikan",
    Pengaturan (kepribadian, bahasa, memori, refleksi), dan konteks mode."""
    s = get_settings()
    parts = [YUKI_SYSTEM_PROMPT]

    # Kepribadian & bahasa dari Pengaturan → Umum / Bahasa
    persona_map = {
        "Santai & kocak": "Pertahankan gaya santai, kocak, dan penuh candaan receh.",
        "Serius & ringkas": (
            "Kurangi candaan. Jawab ringkas, langsung ke inti, "
            "pakai poin-poin bila perlu."
        ),
        "Mentor sabar": (
            "Bersikaplah seperti mentor yang sabar: jelaskan langkah demi "
            "langkah, beri contoh, dan cek pemahaman User."
        ),
        "Profesional formal": (
            "Gunakan bahasa Indonesia formal dan profesional, "
            "tanpa emoji berlebihan."
        ),
    }
    if s.get("personality") in persona_map:
        parts.append(persona_map[s["personality"]])

    lang = LANG_BY_CODE.get(s.get("yuki_lang") or DEFAULT_LANG_CODE)
    if lang and lang["code"] != "id":
        parts.append(f"Selalu jawab dalam bahasa {lang['name']}.")

    nickname = (st.session_state.get("custom_nickname") or "").strip()
    if nickname:
        parts.append(f"Panggil User dengan sebutan: {nickname}.")

    display_name = (s.get("display_name") or "").strip()
    if display_name and display_name.lower() != "user":
        parts.append(f"Nama User adalah {display_name}.")

    # Memori jangka panjang (Pengaturan → Memori)
    if s.get("memory_on"):
        facts = [str(f).strip() for f in (s.get("memories") or []) if str(f).strip()]
        if facts:
            parts.append(
                "MEMORI JANGKA PANJANG tentang User (pakai seperlunya, "
                "jangan disebut satu per satu):\n- " + "\n- ".join(facts)
            )

    # Refleksi: target & kebiasaan yang sedang diperjuangkan User
    goal = (s.get("reflection_goal") or "").strip()
    habit = (s.get("reflection_habit") or "").strip()
    if goal or habit:
        refl = []
        if goal:
            refl.append(f"Target: {goal}")
        if habit:
            refl.append(f"Kebiasaan yang dilatih: {habit}")
        parts.append(
            "REFLEKSI USER — dukung dia mencapai ini, sesekali tanyakan "
            "kemajuannya:\n" + "\n".join(refl)
        )

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
               # Suhu bisa diatur user di Pengaturan → Trinity Code (0,3 = kaku,
        # 1,2 = liar). Dibaca tiap request supaya perubahan langsung terasa.
        temperature=float(get_settings().get("temperature", 0.7)),
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
# IKON SVG GARIS TIPIS ALA CLAUDE (stroke mengikuti warna teks)
# ============================================================================
def _svg(paths: str) -> str:
    return (
        '<svg class="icon-svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


ICON_COPY = _svg('<rect x="9" y="9" width="11" height="11" rx="2"/>'
                 '<path d="M5 15V5a2 2 0 0 1 2-2h10"/>')
ICON_MIC = _svg('<rect x="9" y="3" width="6" height="11" rx="3"/>'
                '<path d="M6 11a6 6 0 0 0 12 0"/><path d="M12 17v4"/>')
ICON_IMAGE = _svg('<rect x="3" y="5" width="18" height="14" rx="2"/>'
                  '<circle cx="9" cy="10" r="1.6"/>'
                  '<path d="M5.5 18.5l5-5 3.5 3.5 2.5-2.5 2 2"/>')
ICON_SEARCH = _svg('<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>')
ICON_CHEVRON = _svg('<path d="M6 9l6 6 6-6"/>')


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "",
                images_html: str = "", meta_note: str = "",
                icon_html: str = "") -> str:
    body = html.escape(content or "")
    css = "user" if role == "user" else "ai"
    if role == "user":
        # User: bubble krem membulat di kanan (gaya Claude)
        meta = ""
    else:
        # AI: teks polos + label kecil "Yuki" dengan titik terracotta (gaya Claude)
        meta = f'<div class="ai-label">{logo_img_html("logo-label")} Yuki</div>'
    # meta_note & icon_html diisi oleh kode ini sendiri (aman, bukan input user)
    note = f'<div class="bubble-meta">{meta_note}</div>' if meta_note else ""
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{icon_html}{body}{images_html}</div>'
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
            bubble_html("assistant", f"Hasil gambar untuk: {msg.get('prompt', '')}",
                        msg.get("time", ""), icon_html=ICON_IMAGE),
            unsafe_allow_html=True,
        )
        st.image(msg["image_bytes"], use_container_width=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label=":material/download:  Unduh PNG",
            data=msg["image_bytes"],
            file_name=f"trinity_{ts}.png",
            mime="image/png",
            key=f"dl_{msg.get('id', id(msg))}",
        )
    else:
        note = f"{ICON_MIC} via suara" if msg.get("via_voice") else ""
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
        f'title="Salin jawaban">{ICON_COPY}</button>'
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
            if st.button(":material/thumb_up:", key=f"fb_up_{mid}",
                         help="Jawaban membantu",
                         type="primary" if up_active else "secondary"):
                msg["feedback"] = None if up_active else "up"
                st.rerun()
        with cols[2]:
            down_active = feedback == "down"
            if st.button(":material/thumb_down:", key=f"fb_down_{mid}",
                         help="Jawaban kurang membantu",
                         type="primary" if down_active else "secondary"):
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

# Delay antar potongan kalimat saat jawaban muncul bertahap
SENTENCE_STREAM_DELAY = 0.15


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


def _sentence_chunks(text: str) -> list[str]:
    """Pecah teks jadi potongan per kalimat / per baris. Whitespace asli
    ikut di dalam potongan, sehingga gabungannya persis sama dengan teks
    awal (tidak ada spasi atau baris baru yang hilang/bertambah)."""
    raw = re.split(r"((?:[.!?]+|\n)\s*)", text or "")
    chunks: list[str] = []
    it = iter(raw)
    for body in it:
        delim = next(it, "")
        chunk = body + delim
        if chunk:
            chunks.append(chunk)
    return chunks


def stream_sentences(answer_slot, full_text: str) -> None:
    """Tampilkan jawaban bertahap per kalimat — animasi muncul yang beda
    dari sebelumnya (bukan kata per kata): lebih cepat, tetap terasa hidup,
    plus caret berkedip di ujung selama proses berlangsung."""
    chunks = _sentence_chunks(full_text)
    if not chunks:
        chunks = [full_text or "…"]
    acc = ""
    for i, chunk in enumerate(chunks):
        acc += chunk
        is_last = i == len(chunks) - 1
        caret = "" if is_last else '<span class="type-caret"></span>'
        html_bubble = bubble_html("assistant", acc)
        if caret:
            # sisipkan caret sebelum penutup bubble
            html_bubble = html_bubble.replace("</div></div></div>", f"{caret}</div></div></div>")
        answer_slot.markdown(html_bubble, unsafe_allow_html=True)
        if not is_last:
            time.sleep(SENTENCE_STREAM_DELAY)


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
    for m in active_thread():
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
# --- Thread pesan -----------------------------------------------------------
# Chat utama, halaman Artefak, dan halaman Trinity Kursus punya riwayat
# sendiri-sendiri supaya jawaban Yuki tidak tercampur antar halaman.
def main_thread() -> list[dict]:
    return st.session_state.messages


def artifact_thread(art_id: int) -> list[dict]:
    key = f"artifact_msgs_{art_id}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def course_thread(cid: str) -> list[dict]:
    key = f"course_msgs_{cid}"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def active_thread() -> list[dict]:
    """Riwayat pesan milik halaman yang sedang dibuka."""
    page = st.session_state.get("page", "chat")
    if page == "artefak":
        aid = st.session_state.get("artifact_active_id")
        if aid is not None:
            return artifact_thread(aid)
        return []
    if page == "kursus":
        cid = st.session_state.get("course_active_key")
        if cid:
            return course_thread(cid)
        return []
    return st.session_state.messages
      # Halaman aktif (routing internal): chat / artefak / pengaturan / bahasa /
    # bantuan / tingkatkan / aplikasi / kursus / pelajari
    if "page" not in st.session_state:
        st.session_state.page = "chat"
    # Pengaturan lengkap (halaman Pengaturan, 9 tab)
    if "settings" not in st.session_state:
        st.session_state.settings = dict(DEFAULT_SETTINGS)
    # Artefak yang sedang dikerjakan (halaman Artefak) + thread kursusnya
    if "artifact_active_id" not in st.session_state:
        st.session_state.artifact_active_id = None
    if "artifact_counter" not in st.session_state:
        st.session_state.artifact_counter = 0
    if "course_active_key" not in st.session_state:
        st.session_state.course_active_key = None
    if "logged_out" not in st.session_state:
        st.session_state.logged_out = False

def reset_conversation() -> None:
    """Chat baru: arsipkan obrolan utama, lalu kosongkan thread utama."""
    _archive_current_conversation()
    st.session_state.active_conv_id = None
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()
    st.session_state.page = "chat"


def open_conversation(conv_id: int) -> None:
    """Buka kembali percakapan lama dari riwayat sidebar."""
    _archive_current_conversation()
    for c in st.session_state.conversations:
        if c["id"] == conv_id:
            st.session_state.messages = c["messages"]
            st.session_state.page = "chat"
            st.session_state.active_conv_id = conv_id
            st.session_state.msg_counter = max(
                (m.get("id", 0) for m in c["messages"]), default=1
            )
            return

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
def go(page: str, **extra) -> None:
    """Pindah halaman internal (chat / artefak / pengaturan / …)."""
    for k, v in extra.items():
        st.session_state[k] = v
    st.session_state.page = page
    st.rerun()

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
            label = f":material/folder:  {p['name']}" + ("  :material/check:" if active else "")
            if st.button(label, key=f"proj_pick_{p['id']}", use_container_width=True):
                st.session_state.active_project_id = None if active else p["id"]
                st.rerun()

    st.divider()
    new_name = st.text_input("Nama proyek baru", key="proj_new_name",
                              placeholder="Nama proyek baru…", label_visibility="collapsed")
    if st.button(":material/add:  Mulai proyek baru", use_container_width=True):
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
        with st.expander(f":material/extension:  {art['title']}  ·  {art.get('time', '')}"):
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
            art_label = ":material/data_object: &nbsp;Artefak" + (f"  ({n_art})" if n_art else "")
            if st.button(art_label, use_container_width=True):
                # buka HALAMAN Artefak (bukan popup lagi)
                go("artefak")
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
            f"""
        # ---- Baris akun di dasar sidebar ala Claude ----
        # (U) Nama · Paket   [⋮ menu akun]
        s = get_settings()
        name = (s.get("display_name") or "User").strip() or "User"
        plan = s.get("plan") or "Free"
        initial = name[0].upper()
        with st.container(key="sb_account"):
            acc_col, menu_col = st.columns([5, 1.05], gap="small")
            with acc_col:
                st.markdown(
                    f"""
<div class="sb-account">
  <div class="ava">{html.escape(initial)}</div>
  <div class="name">{html.escape(name)} <span class="plan">· {html.escape(plan)}</span></div>
</div>
""",
                    unsafe_allow_html=True,
                )
            with menu_col:
                with st.container(key="acct_menu"):
                    with st.popover(":material/more_horiz:", use_container_width=False,
                                    help="Menu akun"):
                        if st.button(":material/settings:  Pengaturan", key="acct_pengaturan",
                                     use_container_width=True):
                            go("pengaturan")
                        if st.button(":material/translate:  Bahasa", key="acct_bahasa",
                                     use_container_width=True):
                            go("bahasa")
                        if st.button(":material/help:  Dapatkan bantuan", key="acct_bantuan",
                                     use_container_width=True):
                            go("bantuan")
                        if st.button(":material/workspace_premium:  Tingkatkan paket",
                                     key="acct_pro", use_container_width=True):
                            go("tingkatkan")
                        if st.button(":material/phone_iphone:  Dapatkan aplikasi",
                                     key="acct_app", use_container_width=True):
                            go("aplikasi")
                        if st.button(":material/school:  Trinity kursus", key="acct_kursus",
                                     use_container_width=True):
                            go("kursus")
                        if st.button(":material/menu_book:  Pelajari lebih lanjut",
                                     key="acct_pelajari", use_container_width=True):
                            go("pelajari")
                        st.divider()
                        if st.button(":material/logout:  Keluar", key="acct_keluar",
                                     use_container_width=True):
                            st.session_state.logged_out = True
                            go("chat")


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:thread = active_thread()
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
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
        if not msg.startswith(("Layanan", "Kuota", "Server terlalu",
                               "Gagal membuat", "Respons terlalu")):
            msg = public_error_image(None, msg, e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": msg, "time": datetime.now().strftime("%H:%M"),
        })


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback.
    Jawaban masuk ke THREAD AKTIF (chat utama, artefak, atau kursus)."""
    thread = active_thread()
    if not CHAT_READY:
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    s = get_settings()
    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )
    # Pesan bergambar WAJIB lewat model vision (model teks tidak bisa lihat gambar)
    last_user = next(
        (m for m in reversed(thread) if m.get("role") == "user"),
        None,
    )
    has_images = bool(last_user and last_user.get("images"))
    if has_images:
        model_id = VISION_MODEL_ID
    elif st.session_state.get("web_search_on") and s.get("cap_web_search", True):
        # Toggle "Pencarian web" ala Claude → pakai model Compound
        # (satu-satunya model Groq di katalog ini yang bisa browsing).
        model_id = AVAILABLE_MODELS["compound"]

    # Thinking ala Claude — frasa berganti-ganti selama beberapa detik
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()
    # Durasi "berpikir" minimum bisa diatur di Pengaturan → Umum
    min_think = float(s.get("min_think_seconds", THINKING_MIN_SECONDS))

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, thread, vision=has_images
            )
        )

        # Tahan sampai proses berpikir genap minimal beberapa detik
        elapsed = time.time() - t0
        if elapsed < min_think:
            time.sleep(min_think - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul bertahap per kalimat (bukan kata per kata)
        stream_sentences(answer_slot, full)

        reply = {
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        }
        thread.append(reply)
        _capture_artifacts_from_reply(full)
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================

def render_input_controls(page_key: str = "chat", show_mode: bool = True) -> None:
    """Isi dok bawah: [⋯ menu lampiran] [Gambar] ... [Nama Model].
    Dipanggil DI DALAM st.bottom / st._bottom oleh halaman pemanggilnya."""
    kp = "" if page_key == "chat" else f"{page_key}_"

    # ---- Strip lampiran yang menunggu dikirim (dari menu ⋯) ----
    pending = st.session_state.get("pending_images", [])
    if pending:
        with st.container(key=f"{kp}pending_strip"):
            pcols = st.columns([0.1] * len(pending) + [1.0])
            for i, im in enumerate(pending):
                with pcols[i]:
                    st.image(im["data"], width=54)
                    if st.button(":material/close:", key=f"{kp}pending_rm_{i}",
                                 use_container_width=True):
                        st.session_state.pending_images.pop(i)
                        st.rerun()
            with pcols[-1]:
                st.markdown(
                    '<div class="plus-menu-hint">Siap dikirim…</div>',
                    unsafe_allow_html=True,
                )

    # [menu] [Gambar] ....spacer.... [Nama Model]
    ctrl_plus, ctrl_mode, _sp, ctrl_model = st.columns([0.08, 0.22, 1.22, 0.28])

    # ---- Menu lampiran ala Claude: MINIMALIST (ikon + teks saja) ----
    with ctrl_plus:
        with st.container(key=f"{kp}plus_menu"):
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

                with st.container(key=f"{kp}plus_upload_file"):
                    picked_file = st.file_uploader(
                        ":material/attach_file:  Upload file", type=IMAGE_INPUT_TYPES,
                        accept_multiple_files=True,
                        label_visibility="visible",
                        key=f"{kp}plus_uploader_file_{gen}",
                    )
                with st.container(key=f"{kp}plus_upload_image"):
                    picked_image = st.file_uploader(
                        ":material/photo_camera:  Upload gambar atau foto",
                        type=IMAGE_INPUT_TYPES,
                        accept_multiple_files=True,
                        label_visibility="visible",
                        key=f"{kp}plus_uploader_image_{gen}",
                    )
                added_file = _stage_uploaded(picked_file)
                added_image = _stage_uploaded(picked_image)
                if added_file or added_image:
                    # tutup popover & langsung tampilkan thumbnail lampiran
                    st.rerun()

                st.markdown('<div class="plus-menu-divider"></div>',
                            unsafe_allow_html=True)

                # Browser murni tidak bisa memicu screen-capture dari
                # Streamlit → diarahkan ke cara tercepat: screenshot OS
                # lalu tempel (Ctrl+V) di kotak chat.
                if st.button(":material/screenshot:  Ambil tangkapan layar",
                             key=f"{kp}pm_screenshot", use_container_width=True):
                    st.toast("Ambil screenshot dengan tombol OS kamu, lalu "
                             "tempel (Ctrl+V) di kotak chat.",
                             icon=":material/screenshot:")

                # Pencarian web → otomatis pindah ke model Compound (browsing)
                web_check = " :orange[✓]" if st.session_state.get("web_search_on") else ""
                if st.button(f":material/public:  Pencarian web{web_check}",
                             key=f"{kp}pm_web", use_container_width=True):
                    st.session_state.web_search_on = not st.session_state.get("web_search_on", False)
                    st.rerun()

    with ctrl_mode:
        if show_mode:
            st.session_state.image_mode = st.toggle(
                "Gambar",
                value=st.session_state.image_mode,
                key=f"{kp}toggle_gambar",
                help="Nyalakan untuk membuat gambar dari teks. "
                     "Matikan untuk chat biasa dengan Yuki.",
            )

    with _sp:
        if st.session_state.messages or st.session_state.get("page") != "chat":
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
            # Daftar model ala Claude, terurut dari tingkat termudah → tertinggi
            for m in MODEL_CATALOG:
                is_active = m["key"] == st.session_state.selected_model_key
                check = " :orange[✓]" if is_active else ""
                label = f"{m['name']}{check}  \n:small[:gray[{m['desc']}]]"
                row_key = f"{kp}model_row_{m['key']}" + ("_premium" if m.get("premium") else "")
                with st.container(key=row_key):
                    if st.button(label, key=f"{kp}model_{m['key']}", use_container_width=True):
                        st.session_state.selected_model_key = m["key"]
                        st.rerun()


def process_user_input(user_input, answer_slot, is_fresh: bool = False) -> bool:
    """Simpan kiriman user ke thread aktif, render bubble-nya, lalu panggil
    Yuki. Return True bila halaman perlu di-rerun.
    Dipanggil dari HALAMAN (bukan dari dalam dok bawah)."""
    if user_input is None:
        return False

    # Bongkar nilai chat input: teks + lampiran + rekaman (bila didukung)
    if isinstance(user_input, str):
        raw_text, send_files, send_audio = user_input, [], None
    else:
        raw_text = getattr(user_input, "text", "") or ""
        send_files = list(getattr(user_input, "files", None) or [])
        send_audio = getattr(user_input, "audio", None)

    text = (raw_text or "").strip()
    via_voice = False
    thread = active_thread()

    # Kiriman suara tanpa teks → transkrip dulu dengan Groq Whisper
    if send_audio is not None and not text:
        if CHAT_READY:
            try:
                with st.spinner(":material/mic:  Mentranskrip suara…"):
                    text = transcribe_audio(build_chat_client(), send_audio.getvalue())
                via_voice = bool(text)
            except Exception:
                text = ""
        if not text:
            thread.append({
                "id": next_msg_id(), "role": "assistant", "type": "text",
                "content": "Hmm, suaranya belum kebaca nih. Coba rekam lagi "
                           "lebih dekat ke mikrofon, atau ketik saja ya!",
                "time": datetime.now().strftime("%H:%M"),
            })
            return True

    images = collect_images(send_files)
    # Gabungkan lampiran yang di-stage lewat menu ⋯ (hindari duplikat)
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

    if not (text or images):
        return False

    now = datetime.now().strftime("%H:%M")

    # Begitu KIRIM ditekan: kotak input langsung turun ke bawah dan scroll
    # diaktifkan lagi (menimpa CSS halaman awal).
    if is_fresh:
        st.markdown(_BOTTOM_RESET_CSS, unsafe_allow_html=True)

    # simpan & tampilkan pesan user (+ thumbnail lampiran)
    user_msg = {
        "id": next_msg_id(), "role": "user", "type": "text",
        "content": text, "time": now,
    }
    if images:
        user_msg["images"] = images
    if via_voice:
        user_msg["via_voice"] = True
    thread.append(user_msg)
    note = f"{ICON_MIC} via suara" if via_voice else ""
    st.markdown(
        bubble_html("user", text, now, images_bubble_html(images), note),
        unsafe_allow_html=True,
    )

    # Ada lampiran gambar → selalu chat vision (Yuki melihat gambarnya),
    # walau toggle "Gambar" sedang aktif sekalipun.
    if st.session_state.image_mode and not images:
        handle_image_request(text)
    else:
        handle_chat_request(answer_slot)

    return True


# Dua potong CSS pengatur posisi dok input (halaman awal vs sudah ada chat)
_FRESH_BOTTOM_CSS = """
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
"""

_BOTTOM_RESET_CSS = """
<style>
[data-testid="stBottom"] { transform: translateY(0) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
html, body { overflow: auto !important; }
</style>
"""


def _page_footer(in_chat: bool = False) -> None:
    foot_class = "trinity-foot" if not in_chat else "trinity-foot in-chat"
    st.markdown(
        f'<p class="{foot_class}">{logo_img_html("logo-foot")} '
        "Ampera Trinity AI · by Ampera Official · 2026</p>",
        unsafe_allow_html=True,
    )


# ============================================================================
# HALAMAN: CHAT UTAMA
# ============================================================================
def render_chat_page() -> None:
    is_fresh = len(main_thread()) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        # Sapaan besar serif di tengah + input diangkat ke tengah layar (CSS)
        st.markdown(_FRESH_BOTTOM_CSS, unsafe_allow_html=True)
        st.markdown(
            '<div class="trinity-greeting" style="margin-top:18vh;">'
            f'{logo_img_html("logo-greeting")} Semangat lagi!'
            "</div>",
            unsafe_allow_html=True,
        )

    # ---------- Riwayat chat ----------
    for msg in main_thread():
        render_message(msg)

    # Prompt tertunda (mis. dari tombol "Minta refleksi sekarang")
    pending_prompt = (st.session_state.pop("pending_prompt", "") or "").strip()

    # ---------- Chat input ----------
    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"
    # Mic & lampiran native Streamlit (kirim gambar, paste, drag-drop);
    # otomatis nonaktif bila versi Streamlit belum mendukung.
    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True
    user_input = st.chat_input(placeholder_text, **chat_kwargs)

    # ---------- Kontrol DI DALAM kotak chat input ----------
    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="chat_controls"):
            render_input_controls("chat", show_mode=True)

    # ---------- Proses kiriman ----------
    if pending_prompt and user_input is None:
        user_input = pending_prompt
    if process_user_input(user_input, st.empty(), is_fresh=is_fresh):
        st.rerun()

    _page_footer(in_chat=not is_fresh)
# ============================================================================
# HALAMAN: ARTEFAK (kotak kategori ala Claude + ruang kerja Yuki)
# ============================================================================
def start_artifact_thread(key: str) -> None:
    """Buka artefak baru dari kategori terpilih → Yuki langsung menjawab
    DI HALAMAN INI (bukan di chat utama)."""
    cat = ARTIFACT_BY_KEY.get(key) or ARTIFACT_CATEGORIES[-1]
    st.session_state.artifact_counter += 1
    aid = st.session_state.artifact_counter
    now = datetime.now().strftime("%H:%M")
    thread = artifact_thread(aid)
    thread.append({
        "id": next_msg_id(), "role": "user", "type": "text",
        "content": cat["brief"], "time": now, "meta": cat["title"],
        # tanda: Yuki harus langsung menjawab brief ini di halaman artefak
        "awaiting_reply": True,
    })
    st.session_state.artifact_active_id = aid
    go("artefak")


def _artifact_grid(prefix: str) -> None:
    """Grid 2 kolom berisi kotak-kotak kategori ala Claude."""
    cats = ARTIFACT_CATEGORIES
    for i in range(0, len(cats), 2):
        cols = st.columns(2)
        for j, cat in enumerate(cats[i:i + 2]):
            with cols[j]:
                label = (f"{cat['icon']}  **{cat['title']}**"
                         f"  \n:small[:gray[{cat['desc']}]]")
                if st.button(label, key=f"{prefix}_{cat['key']}",
                             use_container_width=True):
                    start_artifact_thread(cat["key"])


def _artifact_workspace(aid: int) -> None:
    thread = artifact_thread(aid)
    meta = ""
    for m in thread:
        if m.get("role") == "user":
            meta = m.get("meta") or ""
            break

    back, _sp, new_btn = st.columns([0.18, 1.0, 0.22])
    with back:
        if st.button(":material/arrow_back:", key="art_back",
                     use_container_width=True, help="Kembali ke pilihan artefak"):
            go("artefak", artifact_active_id=None)
    with new_btn:
        if st.button(":material/add: &nbsp;Baru", key="art_new",
                     use_container_width=True):
            go("artefak", artifact_active_id=None)

    st.markdown(
        f'<div class="page-head"><div class="page-head-icon">'
        f":material/data_object:</div>"
        f'<div><h2 class="page-title">{html.escape(meta or "Artefak")}</h2>'
        '<p class="page-sub">Yuki mengerjakan artefak ini di halaman ini — '
        "chat utamamu tetap bersih.</p></div></div>",
        unsafe_allow_html=True,
    )

    # Kalau pesan terakhir adalah brief kategori (belum dijawab), Yuki
    # langsung menjawabnya DI HALAMAN INI sebelum input dirender.
    if thread and thread[-1].get("awaiting_reply"):
        thread[-1].pop("awaiting_reply", None)
        handle_chat_request(st.empty())
        st.rerun()

    for msg in thread:
        render_message(msg)

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True
    user_input = st.chat_input("Jelaskan apa yang mau dibuat…", **chat_kwargs)

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="chat_controls"):
            render_input_controls("artefak", show_mode=False)

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=True)


def page_artefak() -> None:
    aid = st.session_state.get("artifact_active_id")
    if aid is not None:
        _artifact_workspace(aid)
        return

    artifacts = st.session_state.get("artifacts", [])
    st.markdown(
        '<div class="page-head"><div class="page-head-icon">'
        ":material/data_object:</div>"
        '<div><h2 class="page-title">Artefak</h2>'
        "<p class=\"page-sub\">Pilih salah satu kotak di bawah. Yuki langsung "
        "menjawab di halaman ini — bukan di chat utama.</p></div></div>",
        unsafe_allow_html=True,
    )

    if not artifacts:
        st.markdown(
            '<div class="empty-card">Belum ada artefak. Kode panjang dari '
            "jawaban Yuki otomatis tersimpan dan muncul di bagian bawah "
            "halaman ini.</div>",
            unsafe_allow_html=True,
        )
# ============================================================================
# HALAMAN: PENGATURAN (Umum · Akun · Privasi · Penagihan · Kemampuan ·
#                      Memori · Refleksi · Waktu dan fokus · Trinity Code)
# ============================================================================
THEME_OPTIONS = ["Krem (Claude)", "Gelap", "Ikut sistem"]
FONT_OPTIONS = ["Kecil", "Normal", "Besar"]
SPEED_OPTIONS = ["Lambat", "Sedang", "Cepat"]
PERSONA_OPTIONS = ["Santai & kocak", "Serius & ringkas", "Mentor sabar",
                   "Profesional formal"]
REFL_FREQ_OPTIONS = ["Setiap hari", "Setiap minggu", "Saat aku minta", "Nonaktif"]
REFL_TONE_OPTIONS = ["Mendorong", "Lembut", "Tegas", "Netral"]
TZ_OPTIONS = ["Asia/Jakarta (WIB)", "Asia/Makassar (WITA)", "Asia/Jayapura (WIT)",
              "Asia/Singapore (SGT)", "UTC"]

CAPABILITY_ROWS = [
    ("Chat AI (Yuki)",              ":material/chat_bubble:",    "selalu"),
    ("Generate gambar (FLUX)",      ":material/image:",          "cap_image"),
    ("Transkrip suara (Whisper)",   ":material/mic:",            "cap_voice"),
    ("Analisis gambar (Vision)",    ":material/visibility:",     "cap_vision"),
    ("Pencarian web (Compound)",    ":material/public:",         "cap_web_search"),
    ("Artefak otomatis",            ":material/data_object:",    "cap_artifacts"),
]


def _save_settings(patch: dict, label: str = "Perubahan disimpan.") -> None:
    merged = dict(st.session_state.get("settings") or {})
    merged.update(patch)
    st.session_state.settings = merged
    st.toast(label, icon=":material/check:")


def _capability_state(setting_key: str) -> str:
    """Status kemampuan: aktif / siap (butuh kredensial) / nonaktif."""
    if setting_key == "selalu":
        return "aktif" if CHAT_READY else "butuh GROQ_API_KEY"
    s = get_settings()
    if not s.get(setting_key, True):
        return "nonaktif"
    if setting_key == "cap_image":
        return "aktif" if IMAGE_READY else "butuh Cloudflare"
    if setting_key in ("cap_voice", "cap_vision"):
        return "aktif" if CHAT_READY else "butuh GROQ_API_KEY"
    return "aktif"


def _cap_rows_html() -> str:
    rows = []
    for label, icon, key in CAPABILITY_ROWS:
        state = _capability_state(key)
        ok = state == "aktif"
        mark = ":material/check_circle:" if ok else ":material/error_outline:"
        chip = "chip-on" if ok else "chip-off"
        rows.append(
            f'<div class="cap-row">'
            f'<span class="cap-icon">{icon}</span>'
            f'<span class="cap-name">{label}</span>'
            f'<span class="cap-state">{mark} '
            f'<span class="{chip}">{html.escape(state)}</span></span>'
            "</div>"
        )
    return f'<div class="cap-card">{"".join(rows)}</div>'


def _set_umum() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Tampilan</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        theme = st.selectbox("Tema", THEME_OPTIONS, index=THEME_OPTIONS.index(s["theme"]),
                             key="set_theme", help="Tema krem adalah tampilan bawaan Trinity.")
    with c2:
        font = st.selectbox("Ukuran teks", FONT_OPTIONS, index=FONT_OPTIONS.index(s["font_size"]),
                            key="set_font")
    c3, c4 = st.columns(2)
    with c3:
        compact = st.toggle("Mode ringkas", value=s["compact_mode"], key="set_compact",
                            help="Jarak antar pesan dipersempit supaya lebih banyak terlihat.")
    with c4:
        speed = st.selectbox("Kecepatan aliran jawaban", SPEED_OPTIONS,
                             index=SPEED_OPTIONS.index(s["stream_speed"]), key="set_speed",
                             help="Seberapa cepat kalimat Yuki muncul satu per satu.")

    st.markdown('<div class="set-section">Perilaku Yuki</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        persona = st.selectbox("Kepribadian", PERSONA_OPTIONS,
                               index=PERSONA_OPTIONS.index(s["personality"]), key="set_persona")
    with c6:
        min_think = st.slider("Durasi \"berpikir\" minimum (detik)", 0.0, 20.0,
                              float(s["min_think_seconds"]), 0.5, key="set_think",
                              help="Animasi berpikir ditahan minimal selama ini "
                                   "sebelum jawaban ditampilkan.")
    mode = st.radio("Mode bawaan saat membuka aplikasi", ["Chat", "Gambar"],
                    index=["Chat", "Gambar"].index(s["default_mode"]),
                    key="set_mode", horizontal=True)

    if st.button(":material/save:  Simpan perubahan", key="save_umum", type="primary"):
        _save_settings({
            "theme": theme, "font_size": font, "compact_mode": compact,
            "stream_speed": speed, "personality": persona,
            "min_think_seconds": float(min_think), "default_mode": mode,
        }, "Pengaturan umum disimpan.")
        st.rerun()


def _set_akun() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Profil</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Nama tampilan", value=s["display_name"], key="set_name",
                             help="Nama ini muncul di baris akun sidebar.")
        uname = st.text_input("Nama pengguna", value=s["username"], key="set_uname")
    with c2:
        email = st.text_input("Email", value=s["email"], key="set_email",
                              placeholder="nama@email.com")
        st.selectbox("Wilayah", ["Indonesia", "Malaysia", "Singapura", "Lainnya"],
                     key="set_region")
    bio = st.text_area("Tentang kamu (dibaca Yuki)", value=s["bio"], key="set_bio",
                       height=90, placeholder="mis. Aku pemilik UMKM kopi di Lampung…")

    st.markdown('<div class="set-section">Paket</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="feat-row"><span>Paket aktif</span>'
        f'<span class="chip-off">{html.escape(s["plan"])}</span></div>',
        unsafe_allow_html=True,
    )
    c3, c4 = st.columns(2)
    with c3:
        if st.button(":material/workspace_premium:  Tingkatkan ke Trinity Pro",
                     key="akun_pro", use_container_width=True):
            go("tingkatkan")
    with c4:
        if st.button(":material/lock:  Ubah kata sandi", key="akun_pw",
                     use_container_width=True):
            st.toast("Tautan ubah kata sandi akan dikirim ke email kamu.",
                     icon=":material/mail:")

    if st.button(":material/save:  Simpan profil", key="save_akun", type="primary"):
        _save_settings({"display_name": name.strip() or "User", "username": uname.strip(),
                        "email": email.strip(), "bio": bio.strip()}, "Profil disimpan.")
        st.rerun()


def _set_privasi() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Data &amp; percakapan</div>',
                unsafe_allow_html=True)
    st.toggle("Simpan riwayat percakapan di perangkat ini", value=s["save_history"],
              key="set_hist")
    st.toggle("Simpan rekaman suara setelah ditranskrip", value=s["keep_voice"],
              key="set_voice")
    st.toggle("Izinkan Yuki memakai pencarian web", value=s["allow_web_search"],
              key="set_web")
    st.toggle("Cadangkan data ke cloud", value=s["cloud_sync"], key="set_sync")

    st.markdown('<div class="set-section">Personalisasi</div>', unsafe_allow_html=True)
    st.toggle("Kirim data pemakaian anonim untuk perbaikan aplikasi",
              value=s["analytics"], key="set_analytics")
    st.toggle("Gunakan memoriku untuk jawaban yang lebih personal",
              value=s["personalization"], key="set_personal")

    st.markdown('<div class="set-section">Hapus data</div>', unsafe_allow_html=True)
    st.caption("Menghapus seluruh data akan mengosongkan percakapan, artefak, "
               "memori, dan pengaturan. Tindakan ini tidak bisa dibatalkan.")
    if st.button(":material/delete_forever:  Hapus seluruh data saya",
                 key="wipe_data", type="primary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.page = "chat"
        st.rerun()

    if st.button(":material/save:  Simpan pengaturan privasi", key="save_privasi",
                 type="primary"):
        _save_settings({
            "save_history": st.session_state.set_hist,
            "keep_voice": st.session_state.set_voice,
            "allow_web_search": st.session_state.set_web,
            "cloud_sync": st.session_state.set_sync,
            "analytics": st.session_state.set_analytics,
            "personalization": st.session_state.set_personal,
        }, "Pengaturan privasi disimpan.")
        st.rerun()


PRO_FEATURES = [
    ("Model Extreme & premium tanpa batas", True, False),
    ("Generate gambar resolusi tinggi", True, False),
    ("Memori jangka panjang tak terbatas", True, False),
    ("Artefak & Trinity Code penuh", True, True),
    ("Trinity kursus lengkap + mentor Yuki", True, False),
    ("Refleksi harian otomatis", True, False),
    ("Akses lebih awal fitur baru", True, False),
    ("Dukungan prioritas", True, False),
]


def _plan_col(title: str, price: str, note: str, is_pro: bool, key: str) -> None:
    rows = []
    for label, _pro, free in PRO_FEATURES:
        if is_pro:
            mark, cls = ":material/check_circle:", "chip-on"
        else:
            mark, cls = (":material/check_circle:", "chip-on") if free else (
                ":material/remove_circle_outline:", "chip-off")
        rows.append(f'<div class="feat-row"><span>{label}</span>'
                    f'<span class="{cls}">{mark}</span></div>')
    st.markdown(
        f'<div class="plan-card{" is-pro" if is_pro else ""}">'
        f'<div class="plan-name">{title}</div>'
        f'<div class="plan-price">{price}</div>'
        f'<div class="plan-note">{note}</div>'
        f'<div class="feat-list">{"".join(rows)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    label = ":material/workspace_premium:  Pilih Trinity Pro" if is_pro else "Paket aktif"
    if st.button(label, key=key, use_container_width=True,
                 type="primary" if is_pro else "secondary", disabled=not is_pro):
        if is_pro:
            _save_settings({"plan": "Trinity Pro"}, "Paket diperbarui ke Trinity Pro.")
            st.rerun()


def _set_penagihan() -> None:
    s = get_settings()
    cycle = st.radio("Siklus penagihan", ["Bulanan", "Tahunan (hemat 20%)"],
                     index=["Bulanan", "Tahunan (hemat 20%)"].index(s["billing_cycle"]),
                     key="set_cycle", horizontal=True)
    if st.button(":material/credit_card:  Atur metode pembayaran", key="bayar_metode"):
        st.toast("Metode pembayaran akan dibuka setelah gerbang pembayaran aktif.",
                 icon=":material/credit_card:")

    st.markdown('<div class="set-section">Pemakaian bulan ini</div>', unsafe_allow_html=True)
    st.markdown(
        "| Kemampuan | Terpakai | Sisa |\n|---|---|---|\n"
        "| Pesan chat | 0 | Tak terbatas |\n"
        "| Gambar dibuat | 0 | 10 |\n"
        "| Artefak | "
        f"{len(st.session_state.get('artifacts', []))} | 20 |\n"
        "| Kursus diikuti | 0 | 1 |",
    )
    st.markdown('<div class="set-section">Riwayat tagihan</div>', unsafe_allow_html=True)
    st.caption("Belum ada tagihan. Tagihan muncul di sini setelah kamu "
               "berlangganan Trinity Pro.")
    st.markdown(
        '<div class="feat-row"><span>Metode pembayaran</span>'
        f'<span class="chip-off">{html.escape(s["payment_method"])}</span></div>',
        unsafe_allow_html=True,
    )


def _set_kemampuan() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Status kemampuan</div>', unsafe_allow_html=True)
    st.markdown(_cap_rows_html(), unsafe_allow_html=True)
    st.caption("Kemampuan bertanda \"butuh …\" hanya menunggu kredensial diisi "
               "pemilik aplikasi di tab Trinity Code.")

    st.markdown('<div class="set-section">Nyalakan / matikan</div>', unsafe_allow_html=True)
    st.toggle("Pencarian web", value=s["cap_web_search"], key="cap_web",
              help="Bila mati, toggle pencarian web di kotak chat diabaikan.")
    st.toggle("Transkrip suara", value=s["cap_voice"], key="cap_voice_t")
    st.toggle("Analisis gambar (Vision)", value=s["cap_vision"], key="cap_vision_t")
    st.toggle("Generate gambar", value=s["cap_image"], key="cap_image_t")
    st.toggle("Tangkap artefak otomatis", value=s["cap_artifacts"], key="cap_art_t")

    if st.button(":material/save:  Simpan kemampuan", key="save_kemampuan", type="primary"):
        _save_settings({
            "cap_web_search": st.session_state.cap_web,
            "cap_voice": st.session_state.cap_voice_t,
            "cap_vision": st.session_state.cap_vision_t,
            "cap_image": st.session_state.cap_image_t,
            "cap_artifacts": st.session_state.cap_art_t,
        }, "Kemampuan disimpan.")
        st.rerun()


def _set_memori() -> None:
    s = get_settings()
    st.toggle("Gunakan memori jangka panjang", value=s["memory_on"], key="mem_on",
              help="Bila mati, daftar di bawah tidak dikirim ke Yuki.")
    st.toggle("Biarkan Yuki menambah memori otomatis", value=s["memory_auto"],
              key="mem_auto")

    st.markdown('<div class="set-section">Yang Yuki ingat tentang kamu</div>',
                unsafe_allow_html=True)
    facts = list(s.get("memories") or [])
    if not facts:
        st.caption("Belum ada memori. Tambahkan fakta singkat, misalnya "
                   "\"Usahaku: kopi bubuk, jual lewat WhatsApp\".")
    for i, f in enumerate(facts):
        row = st.columns([6, 1])
        with row[0]:
            st.markdown(f'<div class="mem-item">{i + 1}. {html.escape(str(f))}</div>',
                        unsafe_allow_html=True)
        with row[1]:
            if st.button(":material/delete:", key=f"mem_del_{i}",
                         use_container_width=True, help="Hapus memori ini"):
                new = dict(st.session_state.get("settings") or {})
                new["memories"] = [x for j, x in enumerate(facts) if j != i]
                st.session_state.settings = new
                st.rerun()

    new_fact = st.text_input("Tambah memori baru", key="mem_new",
                             placeholder="mis. Aku lebih suka jawaban singkat & pakai tabel")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(":material/add:  Tambah memori", key="mem_add",
                     use_container_width=True, type="primary"):
            if new_fact.strip():
                merged = dict(st.session_state.get("settings") or {})
                merged["memories"] = facts + [new_fact.strip()]
                st.session_state.settings = merged
                st.toast("Memori ditambahkan.", icon=":material/check:")
                st.rerun()
    with c2:
        if st.button(":material/save:  Simpan toggle memori", key="mem_save",
                     use_container_width=True):
            _save_settings({"memory_on": st.session_state.mem_on,
                            "memory_auto": st.session_state.mem_auto},
                           "Pengaturan memori disimpan.")
            st.rerun()


def _set_refleksi() -> None:
    s = get_settings()
    goal = st.text_area("Target yang sedang kamu kejar", value=s["reflection_goal"],
                        key="refl_goal", height=90,
                        placeholder="mis. Menambah 20 pelanggan baru bulan ini")
    habit = st.text_area("Kebiasaan yang ingin dibangun", value=s["reflection_habit"],
                         key="refl_habit", height=90,
                         placeholder="mis. Menulis konten setiap pagi 15 menit")
    c1, c2 = st.columns(2)
    with c1:
        freq = st.selectbox("Yuki menanyakan progres", REFL_FREQ_OPTIONS,
                            index=REFL_FREQ_OPTIONS.index(s["reflection_freq"]),
                            key="refl_freq")
    with c2:
        tone = st.selectbox("Gaya dorongan", REFL_TONE_OPTIONS,
                            index=REFL_TONE_OPTIONS.index(s["reflection_tone"]),
                            key="refl_tone")

    c3, c4 = st.columns(2)
    with c3:
        if st.button(":material/save:  Simpan refleksi", key="save_refl",
                     type="primary", use_container_width=True):
            _save_settings({"reflection_goal": goal.strip(),
                            "reflection_habit": habit.strip(),
                            "reflection_freq": freq, "reflection_tone": tone},
                           "Refleksi disimpan.")
            st.rerun()
    with c4:
        if st.button(":material/self_improvement:  Minta refleksi sekarang",
                     key="refl_now", use_container_width=True):
            go("chat")
            st.session_state.pending_prompt = (
                "Ajak aku refleksi singkat: tanyakan progres targetku, "
                "hambatan hari ini, dan satu langkah kecil untuk besok."
            )


def _set_waktu_fokus() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Sesi fokus</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        focus = st.number_input("Durasi fokus (menit)", 5, 180, int(s["focus_minutes"]),
                                5, key="set_focus")
    with c2:
        brk = st.number_input("Durasi jeda (menit)", 1, 60, int(s["break_minutes"]),
                              1, key="set_break")
    with c3:
        st.selectbox("Zona waktu", TZ_OPTIONS,
                     index=TZ_OPTIONS.index(s["tz_label"]) if s["tz_label"] in TZ_OPTIONS else 0,
                     key="set_tz")

    st.markdown('<div class="set-section">Jam kerja</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        start = st.text_input("Mulai", value=s["work_start"], key="set_start")
    with c5:
        end = st.text_input("Selesai", value=s["work_end"], key="set_end")
    with c6:
        st.text_input("Waktu lokal sekarang", value=datetime.now().strftime("%H:%M"),
                      key="set_now", disabled=True)

    remind = st.toggle("Ingatkan aku saat jam fokus selesai", value=s["focus_reminder"],
                       key="set_remind")

    if st.button(":material/save:  Simpan waktu & fokus", key="save_fokus", type="primary"):
        _save_settings({"focus_minutes": int(focus), "break_minutes": int(brk),
                        "work_start": start, "work_end": end,
                        "tz_label": st.session_state.set_tz,
                        "focus_reminder": remind},
                       "Waktu & fokus disimpan.")
        st.rerun()


def _set_trinity_code() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Kredensial layanan</div>', unsafe_allow_html=True)
    st.caption("Kosongkan bila pemilik aplikasi sudah mengisinya lewat "
               "Streamlit Secrets / environment variable.")
    gk = st.text_input("GROQ_API_KEY", type="password", value=s["groq_key"], key="set_gk",
                       help="Dipakai untuk chat, transkrip suara, dan vision.")
    ca = st.text_input("CF_ACCOUNT_ID", value=s["cf_account_id"], key="set_ca")
    ct = st.text_input("CF_API_TOKEN", type="password", value=s["cf_token"], key="set_ct")
    st.markdown(
        f'<div class="feat-row"><span>Status chat</span>'
        f'<span class="chip-{"on" if CHAT_READY else "off"}">'
        f'{":material/check_circle: aktif" if CHAT_READY else ":material/error_outline: butuh GROQ_API_KEY"}'
        "</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="feat-row"><span>Status generate gambar</span>'
        f'<span class="chip-{"on" if IMAGE_READY else "off"}">'
        f'{":material/check_circle: aktif" if IMAGE_READY else ":material/error_outline: butuh Cloudflare"}'
        "</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="set-section">Model &amp; perilaku</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        temp = st.slider("Suhu jawaban (kreativitas)", 0.0, 1.5,
                         float(s["temperature"]), 0.1, key="set_temp",
                         help="Rendah = kaku & presisi. Tinggi = liar & kreatif.")
    with c2:
        st.selectbox("Model bawaan", [m["name"] for m in MODEL_CATALOG],
                     index=max(0, next((i for i, m in enumerate(MODEL_CATALOG)
                                        if m["key"] == st.session_state.selected_model_key), 0)),
                     key="set_model")
    adv = st.toggle("Tampilkan error teknis apa adanya (mode pengembang)",
                    value=s["advanced_errors"], key="set_adv")

    c3, c4 = st.columns(2)
    with c3:
        if st.button(":material/save:  Simpan Trinity Code", key="save_code",
                     type="primary", use_container_width=True):
            patch = {"groq_key": gk.strip(), "cf_account_id": ca.strip(),
                     "cf_token": ct.strip(), "temperature": float(temp),
                     "advanced_errors": adv}
            _save_settings(patch, "Trinity Code disimpan.")
            st.rerun()
    with c4:
        if st.button(":material/terminal:  Uji koneksi", key="test_conn",
                     use_container_width=True):
            if not (CHAT_READY or gk.strip()):
                st.toast("Belum ada GROQ_API_KEY untuk diuji.", icon=":material/warning:")
            else:
                try:
                    client = OpenAI(api_key=(gk.strip() or GROQ_API_KEY), base_url=GROQ_BASE_URL)
                    r = client.chat.completions.create(
                        model=AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=5,
                    )
                    st.toast("Koneksi bagus: " + (r.choices[0].message.content or "pong"),
                             icon=":material/check_circle:")
                except Exception as e:
                    st.toast(f"Gagal terhubung: {str(e)[:120]}", icon=":material/error:")


def page_pengaturan() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="set_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    st.markdown(
        '<div class="page-head"><div class="page-head-icon">:material/settings:</div>'
        '<div><h2 class="page-title">Pengaturan</h2>'
        "<p class=\"page-sub\">Sembilan bagian pengaturan Trinity. Perubahan "
        "disimpan per bagian lewat tombol simpan.</p></div></div>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        ":material/tune:  Umum",
        ":material/person:  Akun",
        ":material/shield:  Privasi",
        ":material/receipt_long:  Penagihan",
        ":material/bolt:  Kemampuan",
        ":material/history_edu:  Memori",
        ":material/self_improvement:  Refleksi",
        ":material/schedule:  Waktu dan fokus",
        ":material/terminal:  Trinity Code",
    ])
    with tabs[0]:
        _set_umum()
    with tabs[1]:
        _set_akun()
    with tabs[2]:
        _set_privasi()
    with tabs[3]:
        _set_penagihan()
    with tabs[4]:
        _set_kemampuan()
    with tabs[5]:
        _set_memori()
    with tabs[6]:
        _set_refleksi()
    with tabs[7]:
        _set_waktu_fokus()
    with tabs[8]:
        _set_trinity_code()

    _page_footer()
    # ============================================================================
# HALAMAN: BAHASA
# ============================================================================
def page_bahasa() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="lang_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    s = get_settings()
    ui_code = s.get("ui_lang", DEFAULT_LANG_CODE)
    yuki_code = s.get("yuki_lang", DEFAULT_LANG_CODE)

    st.markdown(
        '<div class="page-head"><div class="page-head-icon">:material/translate:</div>'
        '<div><h2 class="page-title">Bahasa</h2>'
        "<p class=\"page-sub\">Bahasa antarmuka Trinity dan bahasa yang dipakai "
        "Yuki saat menjawab.</p></div></div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        ui_name = st.selectbox(
            "Bahasa antarmuka",
            [l["name"] for l in SUPPORTED_LANGUAGES],
            index=next((i for i, l in enumerate(SUPPORTED_LANGUAGES)
                        if l["code"] == ui_code), 0),
            key="lang_ui",
        )
    with c2:
        yuki_name = st.selectbox(
            "Yuki menjawab dengan bahasa",
            [l["name"] for l in SUPPORTED_LANGUAGES],
            index=next((i for i, l in enumerate(SUPPORTED_LANGUAGES)
                        if l["code"] == yuki_code), 0),
            key="lang_yuki",
        )

    if st.button(":material/save:  Simpan bahasa", key="lang_save", type="primary"):
        ui_sel = next(l for l in SUPPORTED_LANGUAGES if l["name"] == ui_name)
        yuki_sel = next(l for l in SUPPORTED_LANGUAGES if l["name"] == yuki_name)
        _save_settings({"ui_lang": ui_sel["code"], "yuki_lang": yuki_sel["code"]},
                       f"Bahasa disimpan — Yuki akan menjawab dalam {yuki_sel['name']}.")
        st.rerun()

    st.markdown('<div class="set-section">Daftar bahasa yang tersedia</div>',
                unsafe_allow_html=True)
    rows = []
    for l in SUPPORTED_LANGUAGES:
        active_ui = l["code"] == ui_code
        active_yuki = l["code"] == yuki_code
        badge = ""
        if active_ui and active_yuki:
            badge = '<span class="chip-on">Antarmuka + Yuki</span>'
        elif active_ui:
            badge = '<span class="chip-on">Antarmuka</span>'
        elif active_yuki:
            badge = '<span class="chip-on">Yuki</span>'
        level_cls = "chip-on" if l["level"] == "Penuh" else "chip-off"
        rows.append(
            f'<div class="lang-row">'
            f'<span class="flag">{l["flag"]}</span>'
            f'<span class="lang-name">{html.escape(l["name"])}'
            f'<span class="lang-native">{html.escape(l["native"])}</span></span>'
            f'<span class="lang-level"><span class="{level_cls}">{l["level"]}</span>'
            f"{badge}</span>"
            "</div>"
        )
    st.markdown(f'<div class="lang-card">{"".join(rows)}</div>', unsafe_allow_html=True)

    st.caption("Level \"Beta\" berarti terjemahan masih disempurnakan. Bahasa "
               "yang dipilih untuk Yuki langsung dipakai pada jawaban "
               "berikutnya.")
    _page_footer()
    # ============================================================================
# HALAMAN: DAPATKAN BANTUAN (petunjuk detail pemakaian aplikasi)
# ============================================================================
HELP_STEPS = [
    (":material/edit_note:", "Tulis pesan",
     "Ketik di kotak paling bawah lalu tekan Enter. Jawaban Yuki muncul "
     "per kalimat, ada animasi berpikir lebih dulu."),
    (":material/photo_camera:", "Kirim gambar",
     "Klik ikon ⋯ di kiri kotak chat → Upload gambar atau foto. Bisa juga "
     "tempel (Ctrl+V) atau seret file ke kotak chat. Yuki menganalisisnya "
     "dengan model vision."),
    (":material/mic:", "Bicara lewat suara",
     "Klik ikon mikrofon di kotak chat, bicara, lalu hentikan. Rekaman "
     "diubah jadi teks otomatis dan ditandai \"via suara\"."),
    (":material/public:", "Nyalakan pencarian web",
     "Ikon ⋯ → Pencarian web. Trinity otomatis pindah ke model Compound "
     "yang bisa membuka internet."),
    (":material/memory:", "Ganti model AI",
     "Klik nama model di kanan kotak chat, pilih tingkat yang kamu mau "
     "(Easy sampai Extreme)."),
    (":material/image:", "Membuat gambar",
     "Nyalakan toggle Gambar, lalu tulis deskripsi gambar yang kamu mau."),
    (":material/data_object:", "Membuat artefak",
     "Sidebar → Artefak → pilih salah satu kotak (aplikasi, permainan, "
     "kuis, dll). Yuki menjawab di halaman itu, chat utama tidak terganggu."),
    (":material/school:", "Belajar lewat kursus",
     "Menu akun (⋯) → Trinity kursus → pilih topik. Yuki jadi mentor dan "
     "menyusun modul belajar."),
    (":material/content_copy:", "Salin jawaban",
     "Di bawah tiap jawaban Yuki ada ikon salin, jempol atas, dan jempol "
     "bawah untuk memberi umpan balik."),
    (":material/download:", "Unduh riwayat chat",
     "Sidebar → Unduh Chat. Riwayat tersimpan sebagai file .md."),
]

HELP_FAQ = [
    ("Kenapa Yuki tidak menjawab?",
     "Periksa koneksi internet, lalu buka Pengaturan → Trinity Code dan "
     "lakukan \"Uji koneksi\". Bila statusnya \"butuh GROQ_API_KEY\", "
     "kredensial belum diisi pemilik aplikasi."),
    ("Kenapa generate gambar gagal?",
     "Generate gambar butuh CF_ACCOUNT_ID dan CF_API_TOKEN (Cloudflare). "
     "Statusnya terlihat di Pengaturan → Kemampuan."),
    ("Apakah percakapanku tersimpan di server?",
     "Tidak. Riwayat hidup di sesi browser kamu dan hilang saat sesi "
     "berakhir, kecuali kamu mengunduhnya lewat \"Unduh Chat\"."),
    ("Bagaimana cara menghapus semua data?",
     "Pengaturan → Privasi → \"Hapus seluruh data saya\"."),
    ("Apa itu Memori dan Refleksi?",
     "Memori = fakta tentang kamu yang selalu diingat Yuki. Refleksi = "
     "target & kebiasaan yang Yuki bantu pantau. Keduanya ada di "
     "Pengaturan."),
    ("Bisakah Yuki menjawab dalam bahasa lain?",
     "Bisa. Buka menu akun (⋯) → Bahasa, lalu pilih bahasa untuk Yuki."),
]


def page_bantuan() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="help_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    st.markdown(
        '<div class="page-head"><div class="page-head-icon">:material/help:</div>'
        '<div><h2 class="page-title">Dapatkan bantuan</h2>'
        "<p class=\"page-sub\">Petunjuk lengkap memakai Ampera Trinity AI, "
        "dari kirim pesan sampai membuat artefak.</p></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="set-section">Mulai cepat</div>', unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate(HELP_STEPS):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{icon}</span>'
            f'<span class="step-text"><b>{title}</b><br>{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="set-section">Pertanyaan yang sering muncul</div>',
                unsafe_allow_html=True)
    for fi, (q, a) in enumerate(HELP_FAQ):
        with st.container(key=f"faq_{fi}"):
            with st.expander(f":material/help_outline:  {q}"):
                st.write(a)

    st.markdown('<div class="set-section">Butuh bantuan manusia?</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(":material/mail:  Email dukungan", key="help_mail",
                     use_container_width=True):
            st.toast("Kirim email ke dukungan@amperaofficial.id", icon=":material/mail:")
    with c2:
        if st.button(":material/forum:  Grup komunitas", key="help_group",
                     use_container_width=True):
            st.toast("Tautan grup komunitas akan segera dibuka.", icon=":material/forum:")
    with c3:
        if st.button(":material/menu_book:  Pelajari lebih lanjut", key="help_more",
                     use_container_width=True):
            go("pelajari")
    _page_footer()
    # ============================================================================
# HALAMAN: PELAJARI LEBIH LANJUT (tentang aplikasi + cara memakainya)
# ============================================================================
ABOUT_CARDS = [
    (":material/chat_bubble:", "Multi AI",
     "Pilih tingkat model Groq dari Easy sampai Extreme lewat nama model di "
     "kotak chat, lengkap dengan fallback otomatis bila satu model sedang "
     "tidak tersedia."),
    (":material/image:", "Generate Foto",
     "Nyalakan toggle Gambar lalu tulis deskripsi. Gambar dibuat dengan "
     "model FLUX di Cloudflare, ada progress bar bergaya Claude."),
    (":material/record_voice_over:", "Suara &amp; Gambar Masuk",
     "Rekam suara (ditranskrip Whisper) atau kirim foto untuk dianalisis "
     "model vision Llama-4 Scout."),
    (":material/data_object:", "Artefak",
     "Kode panjang dari jawaban Yuki otomatis ditangkap, plus halaman "
     "khusus untuk membangun aplikasi, game, kuis, dan dokumen."),
    (":material/school:", "Trinity kursus",
     "Sepuluh topik belajar dengan Yuki sebagai mentor: pemasaran, "
     "penjualan, desain, copywriting, dan lainnya."),
    (":material/tune:", "Pengaturan dalam",
     "Sembilan bagian: Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, "
     "Refleksi, Waktu dan fokus, Trinity Code."),
]

TIPS_LIST = [
    "Beri konteks di awal: siapa kamu, untuk apa, dan batasannya. Jawaban "
    "Yuki langsung lebih tepat sasaran.",
    "Isi Memori dengan fakta penting (usaha, gaya jawaban favorit) supaya "
    "tidak perlu mengulang-ulang.",
    "Pakai halaman Artefak untuk pekerjaan besar supaya chat utama tetap "
    "rapi.",
    "Turunkan suhu (Pengaturan → Trinity Code) bila butuh jawaban presisi "
    "seperti kode atau hitungan.",
    "Nyalakan Pencarian web hanya saat benar-benar butuh data terbaru.",
    "Unduh Chat secara berkala sebagai arsip pekerjaanmu.",
]


def page_pelajari() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="pel_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    st.markdown(
        f'<div class="trinity-hero">{logo_img_html("logo-greeting")}'
        '<div class="hero-text"><h1>Ampera Trinity AI</h1>'
        "<p>Tiga mesin AI dalam satu tempat: mengobrol dengan Yuki, membuat "
        "gambar, dan menganalisis gambar atau suara yang kamu kirim. "
        "Dibuat oleh Ampera Official.</p></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="set-section">Apa saja di dalamnya</div>', unsafe_allow_html=True)
    for i in range(0, len(ABOUT_CARDS), 3):
        cols = st.columns(3)
        for j, (icon, title, desc) in enumerate(ABOUT_CARDS[i:i + 3]):
            with cols[j]:
                st.markdown(
                    f'<div class="mini-card"><div class="mini-icon">{icon}</div>'
                    f'<div class="mini-title">{title}</div>'
                    f'<div class="mini-desc">{desc}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="set-section">Cara memakainya</div>', unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate(HELP_STEPS[:6]):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{icon}</span>'
            f'<span class="step-text"><b>{title}</b><br>{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="set-section">Enam tips dari Yuki</div>', unsafe_allow_html=True)
    for i, tip in enumerate(TIPS_LIST):
        st.markdown(
            f'<div class="tip-row"><span class="tip-no">{i + 1}</span>'
            f"<span>{tip}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="set-section">Lanjutkan ke</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(":material/help:  Petunjuk lengkap", key="pel_bantuan",
                     use_container_width=True):
            go("bantuan")
    with c2:
        if st.button(":material/school:  Trinity kursus", key="pel_kursus",
                     use_container_width=True):
            go("kursus")
    with c3:
        if st.button(":material/data_object:  Artefak", key="pel_artefak",
                     use_container_width=True):
            go("artefak")
    with c4:
        if st.button(":material/workspace_premium:  Trinity Pro", key="pel_pro",
                     use_container_width=True):
            go("tingkatkan")
    _page_footer()
    # ============================================================================
# HALAMAN: TINGKATKAN PAKET (promosi Trinity Pro)
# ============================================================================
def page_tingkatkan() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="pro_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    s = get_settings()
    st.markdown(
        '<div class="trinity-hero"><div class="hero-text">'
        '<h1>Trinity Pro</h1>'
        "<p>Semua kemampuan Trinity dibuka penuh: model tertinggi tanpa batas, "
        "gambar resolusi tinggi, memori tak terbatas, artefak & Trinity Code, "
        "serta seluruh Trinity kursus dengan Yuki sebagai mentor pribadi.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        _plan_col("Free", "Rp 0", "Selamanya gratis · untuk mencoba", False, "plan_free")
    with c2:
        _plan_col("Trinity Pro", "Rp …", "Harga menyusul · batal kapan saja", True, "plan_pro")

    st.markdown('<div class="set-section">Cara berlangganan</div>', unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate([
        (":material/tap_and_play:", "Pilih paket",
         "Tentukan siklus bulanan atau tahunan di tab Pengaturan → Penagihan."),
        (":material/credit_card:", "Atur pembayaran",
         "Kartu, transfer bank, atau e-wallet. Gerbang pembayaran akan "
         "diaktifkan pemilik aplikasi."),
        (":material/bolt:", "Langsung aktif",
         "Paket berubah menjadi Trinity Pro dan semua kemampuan terbuka "
         "saat itu juga."),
    ]):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{icon}</span>'
            f'<span class="step-text"><b>{title}</b><br>{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.caption("Harga resmi Trinity Pro belum ditetapkan — akan diumumkan "
               "pemilik aplikasi. Status paket kamu saat ini: "
               f"{s.get('plan', 'Free')}.")
    _page_footer()


# ============================================================================
# HALAMAN: DAPATKAN APLIKASI
# ============================================================================
def page_aplikasi() -> None:
    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="app_back", use_container_width=True,
                     help="Kembali ke chat"):
            go("chat")
    st.markdown(
        f'<div class="trinity-hero">{logo_img_html("logo-greeting")}'
        '<div class="hero-text"><h1>Trinity di genggaman</h1>'
        "<p>Ampera Trinity AI sedang disiapkan menjadi aplikasi Android & iOS. "
        "Semua fitur yang ada di sini — Yuki, gambar, suara, artefak, dan "
        "kursus — ikut terbawa.</p></div></div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1.35])
    with c1:
        st.markdown(
            f'<div class="phone-card">{logo_img_html("logo-greeting")}'
            '<div class="phone-name">Ampera Trinity AI</div>'
            '<div class="phone-tag">pratinjau aplikasi</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="set-section">Unduh</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button(":material/android:  Android", key="app_android",
                         use_container_width=True):
                st.toast("Versi Android belum dirilis. Daftar beta di bawah ya!",
                         icon=":material/android:")
        with b2:
            if st.button(":material/apple:  iOS", key="app_ios", use_container_width=True):
                st.toast("Versi iOS belum dirilis. Daftar beta di bawah ya!",
                         icon=":material/apple:")
        st.markdown('<div class="set-section">Rencana rilis</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="feat-row"><span>Android (APK & Play Store)</span>'
            '<span class="chip-off">Tahap 1</span></div>'
            '<div class="feat-row"><span>iOS (App Store)</span>'
            '<span class="chip-off">Tahap 2</span></div>'
            '<div class="feat-row"><span>Desktop (Windows & macOS)</span>'
            '<span class="chip-off">Tahap 3</span></div>'
            '<div class="feat-row"><span>Sinkronisasi antar perangkat</span>'
            '<span class="chip-off">Menyusul</span></div>',
            unsafe_allow_html=True,
        )
        email = st.text_input("Email untuk kabar rilis", key="app_email",
                              placeholder="nama@email.com")
        if st.button(":material/notifications_active:  Kabari saya saat rilis",
                     key="app_notify", type="primary", use_container_width=True):
            if email.strip():
                st.toast("Terima kasih! Kami kabari begitu aplikasi siap.",
                         icon=":material/check_circle:")
            else:
                st.toast("Isi dulu email kamu ya.", icon=":material/warning:")
    _page_footer()


# ============================================================================
# HALAMAN: TRINITY KURSUS (fokus belajar: pemasaran, penjualan, desain, dll)
# ============================================================================
def _course_grid(prefix: str) -> None:
    for i in range(0, len(COURSE_CATALOG), 2):
        cols = st.columns(2)
        for j, c in enumerate(COURSE_CATALOG[i:i + 2]):
            with cols[j]:
                label = (f"{c['icon']}  **{c['title']}**"
                         f"  \n:small[:gray[{c['desc']} · {c['level']}]]")
                if st.button(label, key=f"{prefix}_{c['key']}", use_container_width=True):
                    st.session_state.course_active_key = c["key"]
                    go("kursus")


def _course_workspace(key: str) -> None:
    course = COURSE_BY_KEY.get(key) or COURSE_CATALOG[0]
    thread = course_thread(key)

    back, _sp = st.columns([0.12, 1.0])
    with back:
        if st.button(":material/arrow_back:", key="course_back", use_container_width=True,
                     help="Kembali ke daftar kursus"):
            go("kursus", course_active_key=None)

    st.markdown(
        f'<div class="page-head"><div class="page-head-icon">{course["icon"]}</div>'
        f'<div><h2 class="page-title">Trinity kursus · {html.escape(course["title"])}</h2>'
        f'<p class="page-sub">{html.escape(course["desc"])} — '
        f'{html.escape(course["level"])}</p></div></div>',
        unsafe_allow_html=True,
    )

    with st.container(key="course_modules"):
        with st.expander(f":material/menu_book:  Kurikulum {course['title']} (4 modul)"):
            for mod in course_curriculum(course):
                st.markdown(
                    f'<div class="mod-row">{mod}</div>', unsafe_allow_html=True
                )

    if not thread:
        st.markdown(
            '<div class="empty-card">Mulai belajar: tulis tujuanmu di bawah, '
            "misalnya \"Aku ingin bisa jualan kopi lewat WhatsApp\". Yuki "
            "menyusun jalur belajar di halaman ini.</div>",
            unsafe_allow_html=True,
        )

    for msg in thread:
        render_message(msg)

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True
    user_input = st.chat_input(f"Tanya apa saja tentang {course['title']}…", **chat_kwargs)

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="chat_controls"):
            render_input_controls(f"kursus_{key}", show_mode=False)

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=True)


def page_kursus() -> None:
    key = st.session_state.get("course_active_key")
    if key:
        _course_workspace(key)
        return

    st.markdown(
        '<div class="page-head"><div class="page-head-icon">:material/school:</div>'
        '<div><h2 class="page-title">Trinity kursus</h2>'
        "<p class=\"page-sub\">Pilih fokus belajar. Yuki jadi mentor dan "
        "menjawab langsung di halaman kursus ini.</p></div></div>",
        unsafe_allow_html=True,
    )
    _course_grid("kurs")
    _page_footer()
    _artifact_grid("cat")

    if artifacts:
        st.markdown('<div class="sb-group" style="margin-top:14px;">Artefak tersimpan</div>',
                    unsafe_allow_html=True)
        for art in artifacts[:20]:
            with st.container(key=f"art_saved_{art['id']}"):
                with st.expander(f":material/extension:  {art['title']}  ·  {art.get('time', '')}"):
                    st.code(art["content"], language=art.get("lang") or None)

    _page_footer()
    # ============================================================================
# MAIN — pengalih halaman
# ============================================================================
def main() -> None:
    init_state()
    inject_css()

    # "Keluar" dari menu akun: bersihkan sesi lalu kembali ke halaman awal
    if st.session_state.get("logged_out"):
        st.session_state.logged_out = False
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    render_sidebar()

    page = st.session_state.get("page", "chat")
    if page == "artefak":
        page_artefak()
    elif page == "pengaturan":
        page_pengaturan()
    elif page == "bahasa":
        page_bahasa()
    elif page == "bantuan":
        page_bantuan()
    elif page == "tingkatkan":
        page_tingkatkan()
    elif page == "aplikasi":
        page_aplikasi()
    elif page == "kursus":
        page_kursus()
    elif page == "pelajari":
        page_pelajari()
    else:
        render_chat_page()


if __name__ == "__main__":
    main()
