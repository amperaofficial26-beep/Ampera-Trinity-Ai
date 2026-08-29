# -* coding: utf-8 -*-
"""
Konfigurasi, konstanta, dan katalog data Ampera Trinity AI.

Semua "data statis" aplikasi tinggal di sini: daftar model AI, bahasa yang
didukung, kategori artefak, katalog kursus, nilai bawaan pengaturan, dan
pembacaan kredensial (Streamlit Secrets / environment variable).
Ubah data di sini tanpa perlu menyentuh logika UI atau engine AI.
"""

from __future__ import annotations

import inspect
import os

import streamlit as st

# ============================================================================
# IDENTITAS APLIKASI
# ============================================================================
APP_NAME = "Ampera Trinity AI"
APP_TAGLINE = "Multi AI · Generate Foto · Chat — by Ampera Official"

# ============================================================================
# MULTI AI (Groq)
# ============================================================================
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

# Fallback jika model terpilih sudah tidak tersedia di provider
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier
MAX_HISTORY_MESSAGES = 40

# ============================================================================
# PERSONA YUKI
# ============================================================================
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, menganalisis gambar yang dikirim User, sampai ide kreatif.
"""

# ============================================================================
# GENERATE GAMBAR (Cloudflare FLUX)
# ============================================================================
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4

# ============================================================================
# SUARA & GAMBAR MASUK (Groq — pakai GROQ_API_KEY yang sama)
# ============================================================================
STT_MODEL = "whisper-large-v3-turbo"          # transkrip suara → teks
MAX_IMAGES_PER_MESSAGE = 5                    # batas model vision (Llama-4)
IMAGE_INPUT_TYPES = ["png", "jpg", "jpeg", "webp", "gif"]
VISION_RECENT_MESSAGES = 4  # pesan terakhir yang gambarnya ikut ke API

# ============================================================================
# BAHASA (halaman "Bahasa")
# ============================================================================
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

# ============================================================================
# KOTAK KATEGORI HALAMAN ARTEFAK (ala Claude)
# ============================================================================
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

# ============================================================================
# KATALOG KURSUS TRINITY (halaman "Trinity kursus")
# ============================================================================
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


# ============================================================================
# NILAI BAWAAN SELURUH PENGATURAN (9 tab)
# ============================================================================
DEFAULT_SETTINGS: dict = {
    # Umum
    "ui_lang": DEFAULT_LANG_CODE,
    "yuki_lang": DEFAULT_LANG_CODE,
    "theme": "Beige hangat",
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
