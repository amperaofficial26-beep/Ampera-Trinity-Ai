# -*- coding: utf-8 -*-
"""
TAMPILAN — wallpaper & warna yang bisa diatur sendiri oleh User.

Cara kerjanya:
  styles.py tetap jadi tema dasar (beige + ungu) dan TIDAK diubah.
  Modul ini menyuntikkan satu lapis CSS TAMBAHAN sesudahnya, jadi
  pilihan User menimpa warna bawaan tanpa merusak apa pun. Kalau User
  memilih tema "Beige hangat" + wallpaper "Polos", lapisan ini hampir
  tidak mengeluarkan CSS sama sekali — persis tampilan aslinya.

Isi:
  - PALET      : kumpulan tema warna siap pakai
  - WALLPAPER  : latar belakang (gradien/pola CSS murni, tanpa file luar)
  - build_css(): rakit CSS override dari pengaturan User

Dipakai app.py:  from tampilan import inject_tampilan  ->  inject_tampilan()
"""

from __future__ import annotations

import base64
import io

import streamlit as st

# ============================================================================
# PALET WARNA
# ============================================================================
# Kunci warna tiap palet:
#   bg      : latar halaman
#   surface : kartu / permukaan
#   sidebar : latar sidebar
#   border  : garis pemisah
#   text    : teks utama
#   text2   : teks sekunder
#   accent  : warna aksen (tombol utama, highlight)
#   bubble  : gelembung pesan User
#   dark    : True kalau palet gelap (dipakai untuk menyetel skema form)
PALET: dict[str, dict] = {
    "Beige hangat": {
        "bg": "#E8DCC8", "surface": "#F2E8D6", "sidebar": "#EDE2D1",
        "border": "#DBCEB9", "text": "#2C1F33", "text2": "#6B6172",
        "accent": "#4A3559", "bubble": "#E0D2BB", "dark": False,
    },
    "Malam ungu": {
        "bg": "#1A1520", "surface": "#251E2E", "sidebar": "#201A28",
        "border": "#3A3145", "text": "#EDE7F2", "text2": "#A89CB5",
        "accent": "#B794D4", "bubble": "#2F2739", "dark": True,
    },
    "Gelap netral": {
        "bg": "#17171A", "surface": "#212125", "sidebar": "#1C1C20",
        "border": "#33333A", "text": "#E9E9EC", "text2": "#9E9EA8",
        "accent": "#8AB4F8", "bubble": "#2A2A30", "dark": True,
    },
    "Kertas putih": {
        "bg": "#FBFBF9", "surface": "#FFFFFF", "sidebar": "#F4F4F1",
        "border": "#E2E2DC", "text": "#1F1F23", "text2": "#6E6E78",
        "accent": "#3B5BA5", "bubble": "#EFEFEA", "dark": False,
    },
    "Hijau sejuk": {
        "bg": "#E4EDE4", "surface": "#F1F7F0", "sidebar": "#E9F1E8",
        "border": "#CBDBC9", "text": "#1E2B1F", "text2": "#5C6B5C",
        "accent": "#2F6B45", "bubble": "#DCE8DA", "dark": False,
    },
    "Biru laut": {
        "bg": "#E3EAF2", "surface": "#F0F5FA", "sidebar": "#E8EEF5",
        "border": "#C7D5E4", "text": "#17242F", "text2": "#566878",
        "accent": "#1F5C8B", "bubble": "#D9E4EF", "dark": False,
    },
    "Senja mawar": {
        "bg": "#F2E4E4", "surface": "#FAF0F0", "sidebar": "#F5E9E9",
        "border": "#E2CCCC", "text": "#2E1F22", "text2": "#776266",
        "accent": "#A24457", "bubble": "#EBDADA", "dark": False,
    },
    "Kopi gelap": {
        "bg": "#1E1A16", "surface": "#2A2420", "sidebar": "#241F1B",
        "border": "#3D352E", "text": "#EFE7DD", "text2": "#AE9F90",
        "accent": "#C89A63", "bubble": "#332C26", "dark": True,
    },
}

PALET_NAMES = list(PALET.keys())
DEFAULT_PALET = "Beige hangat"


# ============================================================================
# WALLPAPER
# ============================================================================
# Nilai = potongan CSS untuk properti `background` pada lapisan wallpaper.
# "__ACCENT__" dan "__BG__" diganti warna palet aktif supaya wallpaper
# selalu serasi dengan tema, bukan tabrakan.
WALLPAPER: dict[str, str] = {
    "Polos": "",

    "Gradien lembut":
        "radial-gradient(1200px 700px at 12% -10%, __ACCENT__22 0%, transparent 60%),"
        "radial-gradient(900px 600px at 100% 0%, __ACCENT__1A 0%, transparent 55%)",

    "Cahaya atas":
        "radial-gradient(1400px 520px at 50% -18%, __ACCENT__2E 0%, transparent 70%)",

    "Aurora":
        "radial-gradient(760px 520px at 8% 8%, __ACCENT__2A 0%, transparent 60%),"
        "radial-gradient(680px 480px at 92% 18%, __ACCENT__1F 0%, transparent 62%),"
        "radial-gradient(900px 620px at 50% 105%, __ACCENT__24 0%, transparent 65%)",

    "Titik halus":
        "radial-gradient(__ACCENT__33 1px, transparent 1px)",

    "Garis miring":
        "repeating-linear-gradient(45deg, __ACCENT__14 0 2px, transparent 2px 11px)",

    "Kotak-kotak":
        "linear-gradient(__ACCENT__16 1px, transparent 1px),"
        "linear-gradient(90deg, __ACCENT__16 1px, transparent 1px)",

    "Sorot bawah":
        "radial-gradient(1100px 480px at 50% 118%, __ACCENT__30 0%, transparent 68%)",
}

# Ukuran ubin untuk wallpaper berpola (yang lain: default/auto).
_WALLPAPER_SIZE = {
    "Titik halus": "22px 22px",
    "Kotak-kotak": "34px 34px",
}

WALLPAPER_NAMES = list(WALLPAPER.keys())
DEFAULT_WALLPAPER = "Polos"


# ============================================================================
# PENGATURAN BAWAAN (digabung ke DEFAULT_SETTINGS di config.py)
# ============================================================================
TAMPILAN_DEFAULTS: dict = {
    "ui_palet": DEFAULT_PALET,
    "ui_wallpaper": DEFAULT_WALLPAPER,
    "ui_wallpaper_custom": "",      # data URL gambar unggahan User
    "ui_wallpaper_opacity": 100,    # 0-100, kepekatan wallpaper
    "ui_wallpaper_blur": 0,         # 0-20 px, buram (untuk foto unggahan)
    "ui_accent_custom": "",         # "#RRGGBB" — menimpa accent palet
    "ui_sudut": "Sedang",           # kelengkungan sudut kartu
}

SUDUT_PX = {"Tajam": "4px", "Sedang": "12px", "Bulat": "20px"}
SUDUT_NAMES = list(SUDUT_PX.keys())


# ============================================================================
# UTILITAS
# ============================================================================
def _valid_hex(v: str) -> bool:
    v = (v or "").strip()
    return (
        len(v) == 7
        and v.startswith("#")
        and all(c in "0123456789abcdefABCDEF" for c in v[1:])
    )


def _luminansi(hex_color: str) -> float:
    """Terang-gelapnya sebuah warna (0 = hitam, 1 = putih).

    Pakai bobot mata manusia (hijau paling berpengaruh) supaya
    keputusan teks hitam/putih di atasnya benar-benar terbaca.
    """
    h = (hex_color or "#000000").lstrip("#")
    if len(h) != 6:
        return 0.0
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def warna_di_atas(hex_color: str) -> str:
    """Warna teks yang kontras di atas `hex_color`."""
    return "#1A1A1A" if _luminansi(hex_color) > 0.6 else "#FFFFFF"


def palet_aktif(s: dict) -> dict:
    """Palet yang sedang dipakai, sudah termasuk aksen kustom User."""
    p = dict(PALET.get(s.get("ui_palet") or DEFAULT_PALET, PALET[DEFAULT_PALET]))
    custom = s.get("ui_accent_custom") or ""
    if _valid_hex(custom):
        p["accent"] = custom
    # Teks di atas warna aksen dihitung, bukan dipatok putih: kalau User
    # memilih aksen terang (kuning, cyan), teks putih jadi tak terbaca.
    p["on_accent"] = warna_di_atas(p["accent"])
    return p


def siapkan_wallpaper_unggahan(data: bytes, maks_px: int = 1920) -> str:
    """Ubah gambar unggahan jadi data URL yang ringan.

    Foto asli dari HP bisa 5-10 MB — kalau ditanam mentah ke CSS,
    setiap rerun Streamlit ikut mengirim ulang dan aplikasi jadi berat.
    Di sini gambar dikecilkan (maks 1920px) dan dikompres ke JPEG.
    """
    from PIL import Image

    im = Image.open(io.BytesIO(data))
    im.load()
    w, h = im.size
    if max(w, h) > maks_px:
        skala = maks_px / max(w, h)
        im = im.resize((max(1, int(w * skala)), max(1, int(h * skala))),
                       Image.LANCZOS)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="JPEG", quality=82, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


# ============================================================================
# PERAKIT CSS
# ============================================================================
def build_css(s: dict) -> str:
    """Rakit CSS override dari pengaturan tampilan User."""
    p = palet_aktif(s)
    nama_wp = s.get("ui_wallpaper") or DEFAULT_WALLPAPER
    custom_wp = s.get("ui_wallpaper_custom") or ""
    opacity = max(0, min(100, int(s.get("ui_wallpaper_opacity", 100)))) / 100
    blur = max(0, min(20, int(s.get("ui_wallpaper_blur", 0))))
    radius = SUDUT_PX.get(s.get("ui_sudut") or "Sedang", "12px")
    gelap = bool(p.get("dark"))

    bagian: list[str] = []

    # ---- variabel + warna dasar -------------------------------------
    # color-scheme penting: tanpa ini widget bawaan Streamlit (dropdown,
    # date picker, scrollbar) tetap putih di tema gelap.
    bagian.append(f"""
:root {{
  --tr-bg: {p['bg']};
  --tr-surface: {p['surface']};
  --tr-sidebar: {p['sidebar']};
  --tr-border: {p['border']};
  --tr-text: {p['text']};
  --tr-text2: {p['text2']};
  --tr-accent: {p['accent']};
  --tr-on-accent: {p['on_accent']};
  --tr-bubble: {p['bubble']};
  --tr-radius: {radius};
  color-scheme: {"dark" if gelap else "light"};
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--tr-bg) !important;
  color: var(--tr-text) !important;
}}
[data-testid="stAppViewContainer"] {{ background: transparent !important; }}

section[data-testid="stSidebar"] {{
  background: var(--tr-sidebar) !important;
  border-right: 1px solid var(--tr-border) !important;
}}
""")

    # ---- lapisan wallpaper -------------------------------------------
    # Ditaruh di ::before milik .stApp dengan z-index 0 supaya berada DI
    # BAWAH seluruh konten, dan tidak ikut ter-scroll (fixed).
    lapisan = ""
    if custom_wp:
        lapisan = f"url('{custom_wp}') center center / cover no-repeat"
    elif nama_wp != "Polos" and WALLPAPER.get(nama_wp):
        lapisan = (
            WALLPAPER[nama_wp]
            .replace("__ACCENT__", p["accent"])
            .replace("__BG__", p["bg"])
        )

    if lapisan:
        size = _WALLPAPER_SIZE.get(nama_wp, "")
        baris_size = f"background-size: {size};" if size and not custom_wp else ""
        baris_blur = f"filter: blur({blur}px);" if blur else ""
        bagian.append(f"""
.stApp::before {{
  content: "";
  position: fixed;
  inset: {-blur * 3}px;           /* lebihkan tepi supaya blur tidak bocor */
  z-index: 0;
  pointer-events: none;
  background: {lapisan};
  {baris_size}
  {baris_blur}
  opacity: {opacity:.2f};
}}
/* Konten harus di ATAS wallpaper */
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebar"],
[data-testid="stBottom"] {{
  position: relative;
  z-index: 1;
}}
""")

    # ---- permukaan, teks, border -------------------------------------
    bagian.append("""
[data-testid="stMainBlockContainer"] { background: transparent !important; }

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--tr-text) !important;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
small, .stCaption { color: var(--tr-text2) !important; }

/* gelembung pesan
   PENTING: hanya .bubble.user yang diwarnai. Selektor lama
   [class*="bubble"][class*="user"] juga kena .bubble-row.user dan
   .bubble-wrap — dua-duanya elemen FLEX selebar penuh, jadi warnanya
   ikut melebar satu bar penuh, bukan mengikuti lebar teks. */
.bubble.user {
  background: var(--tr-bubble) !important;
  color: var(--tr-text) !important;
  border-radius: var(--tr-radius) !important;
}
/* wadahnya wajib tetap transparan */
.bubble-row, .bubble-row.user, .bubble-wrap {
  background: transparent !important;
}
.bubble.ai { background: transparent !important; color: var(--tr-text) !important; }
.bubble-meta, .msg-action-time { color: var(--tr-text2) !important; }

/* kartu & panel */
.cap-card, .set-card, .art-card, .course-card, .price-card,
[data-testid="stExpander"], [data-testid="stForm"] {
  background: var(--tr-surface) !important;
  border-color: var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
}

/* kotak input chat */
[data-testid="stChatInput"], [data-testid="stBottomBlockContainer"] > div {
  background: var(--tr-surface) !important;
  border-color: var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--tr-text) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--tr-text2) !important; }

/* widget form */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
  background: var(--tr-surface) !important;
  color: var(--tr-text) !important;
  border-color: var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
  background: var(--tr-surface) !important;
  color: var(--tr-text) !important;
}
[role="option"] { color: var(--tr-text) !important; }

/* tombol utama pakai warna aksen */
.stButton button[kind="primary"],
.stFormSubmitButton button[kind="primary"] {
  background: var(--tr-accent) !important;
  border-color: var(--tr-accent) !important;
  color: var(--tr-on-accent) !important;
  border-radius: var(--tr-radius) !important;
}
.stButton button[kind="primary"]:hover,
.stFormSubmitButton button[kind="primary"]:hover {
  filter: brightness(1.08);
}
.stButton button[kind="primary"] p,
.stButton button[kind="primary"] [data-testid="stIconMaterial"] {
  color: var(--tr-on-accent) !important;
}
.stButton button[kind="secondary"] {
  background: var(--tr-surface) !important;
  color: var(--tr-text) !important;
  border-color: var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
}

/* BARIS AKSI DI BAWAH JAWABAN YUKI (salin, 👍, 👎)
   Tombol ini harus tampak seperti ikon telanjang — tanpa kotak, tanpa
   latar — baik saat aktif maupun tidak. styles.py sudah membuat yang
   varian primary transparan; di sini disamakan untuk SEMUA keadaan
   supaya pilihan tema tidak memunculkan kembali kotak latarnya. */
[class*="st-key-msg_actions_"] div.stButton > button,
[class*="st-key-msg_actions_"] div.stButton > button[kind="primary"],
[class*="st-key-msg_actions_"] div.stButton > button[kind="secondary"],
[class*="st-key-msg_actions_"] [data-testid="stBaseButton-primary"],
[class*="st-key-msg_actions_"] [data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--tr-text2) !important;
  padding: 2px 4px !important;
  min-height: 0 !important;
}
[class*="st-key-msg_actions_"] div.stButton > button:hover,
[class*="st-key-msg_actions_"] div.stButton > button:hover
  [data-testid="stIconMaterial"] {
  color: var(--tr-accent) !important;
  background: transparent !important;
}
/* keadaan TERPILIH (sudah diberi 👍/👎): ikon berwarna aksen, tetap
   tanpa latar, jadi user tahu pilihannya tersimpan. */
[class*="st-key-msg_actions_"] div.stButton > button[kind="primary"],
[class*="st-key-msg_actions_"] div.stButton > button[kind="primary"]
  [data-testid="stIconMaterial"] {
  color: var(--tr-accent) !important;
}

/* POPUP MENU (menu pengguna & menu +) — ikut warna tema */
[data-testid="stPopoverBody"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] [role="dialog"] {
  background: var(--tr-surface) !important;
  border-color: var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
}
[data-testid="stPopoverBody"] div.stButton > button {
  background: transparent !important;
  color: var(--tr-text) !important;
  border: none !important;
}
[data-testid="stPopoverBody"] div.stButton > button:hover {
  background: var(--tr-bubble) !important;
}
[data-testid="stPopoverBody"] p,
[data-testid="stPopoverBody"] [data-testid="stIconMaterial"] {
  color: var(--tr-text) !important;
}

/* DOK INPUT CHAT bawah
   Struktur aslinya di styles.py:
     stBottom                 -> batang dok
       stBottomBlockContainer -> "kartu gabungan" (#F2E8D6 + border + shadow)
         stChatInput          -> kotak teks
         st-key-chat_controls -> baris +/model

   styles.py mewarnai KARTU LUAR, sehingga area di belakang baris
   "+ ... Trinity Seed" tampak sebagai strip krem terang yang menutupi
   wallpaper. Di sini kartu luar dibuat BENAR-BENAR transparan (termasuk
   border & bayangannya), lalu warnanya dipindah ke kotak teks saja —
   jadi yang terlihat melayang di atas wallpaper cuma satu kolom input,
   sementara + dan nama model duduk langsung di atas wallpaper. */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stBottomBlockContainer"]:focus-within {
  border: none !important;
  box-shadow: none !important;
}

/* baris +/model: tanpa latar, duduk di atas wallpaper */
.st-key-chat_controls,
.st-key-chat_controls > div,
.st-key-chat_controls [data-testid="stHorizontalBlock"],
.st-key-chat_controls [data-testid="stColumn"],
[class*="st-key-pending_strip"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* kotak teks = satu-satunya permukaan berwarna di dok */
[data-testid="stChatInput"] {
  background: var(--tr-surface) !important;
  border: 1px solid var(--tr-border) !important;
  border-radius: var(--tr-radius) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,.06) !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--tr-accent) !important;
}
/* lapisan di DALAM kotak teks tetap transparan supaya tidak bertumpuk */
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.chat-disclaimer, .chat-note, .input-disclaimer,
.st-key-chat_controls p {
  color: var(--tr-text2) !important;
}
.st-key-chat_controls [data-testid="stPopover"] button,
.st-key-chat_controls button[data-testid="stPopoverButton"] {
  background: transparent !important;
  color: var(--tr-text2) !important;
  border-color: var(--tr-border) !important;
}
/* TOMBOL KIRIM (panah) & mikrofon di dalam kotak teks.
   styles.py menargetkan '[data-testid="stChatInput"] button' — bukan
   stChatInputSubmitButton — jadi selektor itu harus ditiru persis,
   kalau tidak warnanya kalah spesifisitas dan panahnya tetap ungu. */
[data-testid="stChatInput"] button {
  background: var(--tr-accent) !important;
  color: var(--tr-on-accent) !important;
  border-radius: var(--tr-radius) !important;
}
[data-testid="stChatInput"] button svg {
  fill: var(--tr-on-accent) !important;
  color: var(--tr-on-accent) !important;
}
[data-testid="stChatInput"] button:hover { filter: brightness(1.12); }
[data-testid="stChatInput"] button:disabled {
  background: var(--tr-bubble) !important;
}
[data-testid="stChatInput"] button:disabled svg {
  fill: var(--tr-text2) !important;
  color: var(--tr-text2) !important;
}
/* mikrofon: ikon telanjang, bukan tombol berwarna */
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"] {
  background: transparent !important;
}
[data-testid="stChatInput"] [data-testid="stChatInputMicButton"] svg {
  fill: var(--tr-text2) !important;
  color: var(--tr-text2) !important;
}

/* tab & pemisah */
.stTabs [data-baseweb="tab-list"] { border-bottom-color: var(--tr-border) !important; }
.stTabs [data-baseweb="tab"] { color: var(--tr-text2) !important; }
.stTabs [aria-selected="true"] { color: var(--tr-accent) !important; }
hr, [data-testid="stDivider"] { border-color: var(--tr-border) !important; }

a { color: var(--tr-accent) !important; }
""")

    # ---- sapu bersih warna beige harfiah -----------------------------
    # styles.py menulis warna beige langsung (bukan variabel) di puluhan
    # tempat. Selama warnanya tidak disapu, tema apa pun akan menyisakan
    # kartu/menu/dok yang masih krem — persis keluhan "warna tampilan
    # nggak sesuai". Berlaku untuk SEMUA tema, bukan cuma yang gelap.
    if (s.get("ui_palet") or DEFAULT_PALET) != DEFAULT_PALET or _valid_hex(
        s.get("ui_accent_custom") or ""
    ):
        bagian.append("""
/* permukaan krem bawaan -> permukaan tema */
[style*="#F2E8D6"], [style*="#EDE2D1"], [style*="#FBF6EC"],
[style*="#F5EFE6"], [style*="#FFFBF2"], [style*="#F7F1E6"],
[style*="#E5D8C3"], [style*="#E0D2BB"] {
  background-color: var(--tr-surface) !important;
  border-color: var(--tr-border) !important;
}
/* sisa permukaan krem yang ditulis lewat class di styles.py */
.cap-card, .set-card, .price-card, .art-card, .course-card,
.rc-card, .plus-menu, .dna-card {
  background-color: var(--tr-surface) !important;
  border-color: var(--tr-border) !important;
}
/* latar halaman krem -> latar tema */
[style*="#E8DCC8"] { background-color: var(--tr-bg) !important; }
/* garis tepi krem -> garis tema */
[style*="#DBCEB9"] { border-color: var(--tr-border) !important; }
/* teks ungu gelap bawaan -> teks tema */
[style*="color: #2C1F33"], [style*="color:#2C1F33"],
[style*="color: #4A3559"], [style*="color:#4A3559"] {
  color: var(--tr-text) !important;
}
[style*="color: #6B6172"], [style*="color:#6B6172"],
[style*="color: #7E7387"], [style*="color:#7E7387"],
[style*="color: #827788"], [style*="color:#827788"] {
  color: var(--tr-text2) !important;
}
""")

    # ---- penyesuaian khusus tema gelap -------------------------------
    if gelap:
        bagian.append("""
code, pre, [data-testid="stCodeBlock"] {
  background: rgba(255,255,255,.06) !important;
  color: var(--tr-text) !important;
}
[data-testid="stSidebarNav"], [data-testid="stSidebarUserContent"] {
  color: var(--tr-text) !important;
}
img[src*="logo"] { filter: brightness(1.35) !important; }
""")

    return "\n".join(bagian)


def inject_tampilan() -> None:
    """Suntikkan CSS tampilan User. Panggil SESUDAH inject_css()."""
    from state import get_settings

    try:
        css = build_css(get_settings())
    except Exception:
        return  # tampilan kustom gagal -> tema bawaan tetap jalan
    if css.strip():
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def kartu_pratinjau(s: dict) -> str:
    """HTML kartu pratinjau kecil untuk tab Pengaturan > Tampilan."""
    p = palet_aktif(s)
    nama_wp = s.get("ui_wallpaper") or DEFAULT_WALLPAPER
    custom_wp = s.get("ui_wallpaper_custom") or ""
    opacity = max(0, min(100, int(s.get("ui_wallpaper_opacity", 100)))) / 100
    radius = SUDUT_PX.get(s.get("ui_sudut") or "Sedang", "12px")

    if custom_wp:
        lapis = f"url('{custom_wp}') center center / cover no-repeat"
    else:
        lapis = (
            WALLPAPER.get(nama_wp, "")
            .replace("__ACCENT__", p["accent"])
            .replace("__BG__", p["bg"])
        )
    size = _WALLPAPER_SIZE.get(nama_wp, "")
    size_css = f"background-size: {size};" if size and not custom_wp else ""

    return f"""
<div style="position:relative; overflow:hidden; border:1px solid {p['border']};
            border-radius:{radius}; background:{p['bg']}; padding:14px 16px;
            min-height:132px;">
  <div style="position:absolute; inset:0; background:{lapis or 'none'};
              {size_css} opacity:{opacity:.2f};"></div>
  <div style="position:relative;">
    <div style="font-size:12px; letter-spacing:.14em; text-transform:uppercase;
                color:{p['text2']}; margin-bottom:9px;">Pratinjau</div>
    <div style="display:inline-block; background:{p['bubble']}; color:{p['text']};
                padding:7px 12px; border-radius:{radius}; font-size:13px;
                margin-bottom:7px;">Halo Yuki, apa kabar?</div><br>
    <div style="display:inline-block; background:{p['surface']}; color:{p['text']};
                padding:7px 12px; border-radius:{radius}; font-size:13px;
                border:1px solid {p['border']};">Baik! Ada yang bisa dibantu?</div>
    <div style="margin-top:11px;">
      <span style="display:inline-block; background:{p['accent']}; color:#fff;
                   padding:5px 14px; border-radius:{radius}; font-size:12px;">
        Tombol utama</span>
    </div>
  </div>
</div>
"""
