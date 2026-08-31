#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pembangun situs GitHub Pages untuk Ampera Trinity AI.

Mengubah berkas Markdown yang sudah ada (docs/*.md, CONTRIBUTING.md,
CHANGELOG.md) menjadi situs statis HTML lengkap dengan sidebar, daftar isi,
pencarian, dan tema "Beige hangat" — tanpa Jekyll, tanpa Node.

Sumber kebenaran tetap berkas Markdown-nya, jadi dokumentasi di GitHub dan
di situs tidak pernah berbeda isi.

Pemakaian:
    python tools/build_site.py            # bangun ke _site/
    python tools/build_site.py --serve    # bangun lalu jalankan server lokal
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import unicodedata
from pathlib import Path

import markdown

# ============================================================================
# LOKASI & IDENTITAS
# ============================================================================
ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "tools" / "theme"
OUT = ROOT / "_site"

REPO_URL = "https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai"
EDIT_BASE = f"{REPO_URL}/edit/main"
SITE_NAME = "Ampera Trinity AI"
SITE_DESC = ("Aplikasi web AI berbasis Streamlit dengan asisten Yuki — "
             "chat multi-model, analisis & generate gambar, artefak, dan kursus.")

GH_ICON = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8'
           'c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37'
           '-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01'
           '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64'
           '-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21'
           '2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1'
           '.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73'
           '.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8'
           'c0-4.42-3.58-8-8-8Z"/></svg>')

SEARCH_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
               '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>')

MENU_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round"/></svg>')

# ============================================================================
# DAFTAR HALAMAN
#   src      : berkas Markdown sumber (relatif terhadap root repo)
#   out      : nama berkas HTML hasil
#   title    : judul di sidebar & <title>
#   icon     : emoji kecil di sidebar
#   group    : pengelompokan di sidebar
#   desc     : dipakai di kartu landing page & meta description
#   keywords : kata bantu untuk pencarian sidebar
# ============================================================================
PAGES = [
    {"src": "docs/README.md",            "out": "dokumentasi.html",
     "title": "Ikhtisar Dokumentasi",    "icon": "📚", "group": "Mulai",
     "desc": "Peta seluruh dokumen dan ringkasan 30 detik.",
     "keywords": "index peta ikhtisar overview daftar"},

    {"src": "docs/instalasi.md",         "out": "instalasi.html",
     "title": "Instalasi",               "icon": "🔧", "group": "Mulai",
     "desc": "Prasyarat, langkah pemasangan, dan penyelesaian masalah umum.",
     "keywords": "install setup pip venv python jalankan troubleshooting error"},

    {"src": "docs/konfigurasi.md",       "out": "konfigurasi.html",
     "title": "Konfigurasi",             "icon": "🔑", "group": "Mulai",
     "desc": "Cara mendapatkan API key, daftar model, dan semua opsi pengaturan.",
     "keywords": "api key groq cloudflare secrets env model bahasa pengaturan settings"},

    {"src": "docs/deploy.md",            "out": "deploy.html",
     "title": "Deploy",                  "icon": "🌍", "group": "Mulai",
     "desc": "Publikasikan lewat Streamlit Cloud, Hugging Face, Docker, atau VPS.",
     "keywords": "deploy hosting streamlit cloud docker vps nginx https publish link"},

    {"src": "docs/fitur.md",             "out": "fitur.html",
     "title": "Fitur",                   "icon": "✨", "group": "Memakai",
     "desc": "Rincian setiap kemampuan aplikasi, dari chat sampai animasi teks.",
     "keywords": "fitur chat vision gambar suara artefak kursus bahasa animasi"},

    {"src": "docs/panduan-pengguna.md",  "out": "panduan-pengguna.html",
     "title": "Panduan Pengguna",        "icon": "🧭", "group": "Memakai",
     "desc": "Langkah demi langkah memakai aplikasi, tanpa perlu paham kode.",
     "keywords": "panduan cara pakai tutorial pengguna prompt tips"},

    {"src": "docs/faq.md",               "out": "faq.html",
     "title": "FAQ",                     "icon": "❓", "group": "Memakai",
     "desc": "Sekitar 35 pertanyaan yang paling sering muncul.",
     "keywords": "faq tanya jawab pertanyaan masalah kenapa bagaimana"},

    {"src": "docs/arsitektur.md",        "out": "arsitektur.html",
     "title": "Arsitektur",              "icon": "🏗️", "group": "Mengembangkan",
     "desc": "Peta modul, alur data, dan cara menambah fitur baru.",
     "keywords": "arsitektur struktur kode modul state alur developer"},

    {"src": "docs/situs-dokumentasi.md", "out": "situs-dokumentasi.html",
     "title": "Situs Dokumentasi",   "icon": "🖥️", "group": "Mengembangkan",
     "desc": "Cara kerja situs GitHub Pages ini dan cara menambah halaman.",
     "keywords": "situs pages website build tema jekyll static deploy docs"},

    {"src": "CONTRIBUTING.md",           "out": "kontribusi.html",
     "title": "Kontribusi",              "icon": "🤝", "group": "Mengembangkan",
     "desc": "Alur pull request, gaya kode, dan daftar ide yang bisa dikerjakan.",
     "keywords": "kontribusi contributing pull request commit gaya kode"},

    {"src": "CHANGELOG.md",              "out": "changelog.html",
     "title": "Changelog",               "icon": "📝", "group": "Mengembangkan",
     "desc": "Riwayat perubahan tiap versi.",
     "keywords": "changelog riwayat versi rilis perubahan"},
]

GROUP_ORDER = ["Mulai", "Memakai", "Mengembangkan"]

# Pemetaan tautan Markdown -> berkas HTML hasil
LINK_MAP = {}
for _p in PAGES:
    _src = _p["src"]
    LINK_MAP[_src] = _p["out"]                       # docs/instalasi.md
    LINK_MAP[Path(_src).name] = _p["out"]            # instalasi.md
    LINK_MAP["../" + _src] = _p["out"]               # ../CONTRIBUTING.md
LINK_MAP.update({
    "docs/": "dokumentasi.html",
    "docs": "dokumentasi.html",
    "README.md": "dokumentasi.html",
    "../README.md": "index.html",
    "LICENSE": f"{REPO_URL}/blob/main/LICENSE",
    "../LICENSE": f"{REPO_URL}/blob/main/LICENSE",
    "assets/logo_thinking_small.png": "assets/logo.png",
})


# ============================================================================
# UTILITAS
# ============================================================================
def slugify(text: str) -> str:
    """Buat anchor id yang identik dengan milik GitHub.

    Meniru pustaka `github-slugger` yang dipakai GitHub saat merender Markdown:
    kecilkan huruf, buang tanda baca & emoji, lalu ubah spasi jadi tanda hubung.
    Penting: tanda hubung di awal TIDAK dibuang dan tanda hubung berurutan TIDAK
    digabung — persis seperti GitHub. Judul "## 🚀 1. Docker" menghasilkan
    "-1-docker", sehingga tautan #jangkar yang ditulis di berkas Markdown tetap
    berfungsi baik di GitHub maupun di situs ini.
    """
    text = re.sub(r"<[^>]+>", "", text)                  # buang tag HTML
    text = html.unescape(text).strip().lower()

    out = []
    for ch in text:
        if ch in " -_":
            out.append(ch)
            continue
        code = ord(ch)
        # Pengubah emoji: variation selector, zero-width joiner, keycap.
        # GitHub membuangnya, jadi kita ikut membuang supaya slug sama persis.
        if 0xFE00 <= code <= 0xFE0F or code in (0x200D, 0x20E3):
            continue
        # Huruf, angka, dan tanda gabung (untuk aksara Arab/Hindi dsb) tetap
        if unicodedata.category(ch)[0] in ("L", "N", "M"):
            out.append(ch)
        # sisanya (tanda baca, emoji, simbol) dibuang tanpa diganti apa pun

    return "".join(out).replace(" ", "-") or "bagian"


class GitHubSlugger:
    """Slug unik per halaman, meniru perilaku GitHub (duplikat diberi -1, -2)."""

    def __init__(self) -> None:
        self.seen: dict[str, int] = {}

    def __call__(self, text: str, sep: str = "-") -> str:
        base = slugify(text)
        if base in self.seen:
            self.seen[base] += 1
            return f"{base}-{self.seen[base]}"
        self.seen[base] = 0
        return base


def rewrite_links(html_text: str) -> str:
    """Ubah tautan .md antar dokumen menjadi tautan .html pada situs."""

    def repl(match: re.Match) -> str:
        quote, target = match.group(1), match.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#", "/")):
            return match.group(0)

        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
            anchor = "#" + anchor

        mapped = LINK_MAP.get(target)
        if mapped is None and target.endswith(".md"):
            mapped = Path(target).stem + ".html"
        if mapped is None:
            return match.group(0)
        return f'href={quote}{mapped}{anchor}{quote}'

    return re.sub(r'href=(["\'])([^"\']+)\1', repl, html_text)


def build_toc(toc_tokens: list) -> str:
    """Susun daftar isi kanan dari judul h2 & h3."""
    items = []
    for tok in toc_tokens:                        # h2
        items.append(
            f'<li class="lvl-2"><a href="#{tok["id"]}">'
            f'{html.escape(strip_emoji(tok["name"]))}</a></li>'
        )
        for sub in tok.get("children", []):       # h3
            items.append(
                f'<li class="lvl-3"><a href="#{sub["id"]}">'
                f'{html.escape(strip_emoji(sub["name"]))}</a></li>'
            )
    if not items:
        return ""
    return (
        '<nav class="toc" aria-label="Daftar isi halaman">'
        '<div class="toc-title">Di halaman ini</div>'
        f'<ul>{"".join(items)}</ul></nav>'
    )


def strip_emoji(text: str) -> str:
    """Buang emoji di awal judul supaya daftar isi rapi."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    out = []
    for ch in text:
        if unicodedata.category(ch) in ("So", "Sk", "Cf"):
            continue
        out.append(ch)
    return " ".join("".join(out).split())


def render_sidebar(current: str | None) -> str:
    """Sidebar navigasi, item halaman aktif ditandai."""
    parts = [
        '<div class="search-wrap">',
        SEARCH_ICON,
        '<input id="nav-search" type="search" placeholder="Cari halaman…  (tekan /)" '
        'autocomplete="off" aria-label="Cari halaman">',
        "</div>",
        '<a class="nav-home" hidden></a>',
    ]

    for group in GROUP_ORDER:
        pages = [p for p in PAGES if p["group"] == group]
        if not pages:
            continue
        parts.append('<div class="nav-group">')
        parts.append(f'<div class="nav-group-title">{html.escape(group)}</div><ul>')
        for p in pages:
            cls = ' class="active"' if p["out"] == current else ""
            aria = ' aria-current="page"' if p["out"] == current else ""
            parts.append(
                f'<li><a href="{p["out"]}"{cls}{aria} '
                f'data-keywords="{html.escape(p["keywords"])}">'
                f'<span class="nav-ico">{p["icon"]}</span>'
                f'<span>{html.escape(p["title"])}</span></a></li>'
            )
        parts.append("</ul></div>")

    parts.append('<div class="nav-empty">Tidak ada halaman yang cocok.</div>')
    return "".join(parts)


def page_nav(index: int) -> str:
    """Tautan halaman sebelumnya / berikutnya."""
    prev_p = PAGES[index - 1] if index > 0 else None
    next_p = PAGES[index + 1] if index < len(PAGES) - 1 else None
    if not prev_p and not next_p:
        return ""

    left = (
        f'<a class="prev" href="{prev_p["out"]}">'
        f'<span class="dir">← Sebelumnya</span>'
        f'<span class="ttl">{html.escape(prev_p["title"])}</span></a>'
        if prev_p else '<span class="spacer"></span>'
    )
    right = (
        f'<a class="next" href="{next_p["out"]}">'
        f'<span class="dir">Berikutnya →</span>'
        f'<span class="ttl">{html.escape(next_p["title"])}</span></a>'
        if next_p else '<span class="spacer"></span>'
    )
    return f'<nav class="page-nav">{left}{right}</nav>'


# ============================================================================
# KERANGKA HALAMAN
# ============================================================================
def shell(title: str, description: str, body: str,
          *, is_home: bool = False, extra_head: str = "") -> str:
    full_title = title if is_home else f"{title} · {SITE_NAME}"
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#f6f1e7">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="assets/logo.png">
<meta name="twitter:card" content="summary">
<link rel="icon" href="assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<link rel="stylesheet" href="assets/highlight.css">
{extra_head}
</head>
<body>
<a class="skip-link" href="#main">Lewati ke konten</a>

<header class="site-header">
  {'<button class="menu-btn" type="button" aria-label="Buka menu navigasi" aria-expanded="false">' + MENU_ICON + '</button>' if not is_home else ''}
  <a class="brand" href="index.html">
    <img src="assets/logo.png" alt="">
    <span>Ampera Trinity AI</span>
    <span class="brand-sub">Dokumentasi</span>
  </a>
  <div class="header-spacer"></div>
  <nav class="header-nav">
    <a href="dokumentasi.html">Dokumentasi</a>
    <a href="instalasi.html">Instalasi</a>
    <a href="deploy.html">Deploy</a>
    <a class="gh" href="{REPO_URL}" target="_blank" rel="noopener">{GH_ICON} GitHub</a>
  </nav>
</header>

{body}

<footer class="site-footer">
  <div class="footer-inner">
    <div>© Ampera Official · Dirilis di bawah lisensi MIT</div>
    <div class="footer-links">
      <a href="{REPO_URL}">Repositori</a>
      <a href="{REPO_URL}/issues">Lapor masalah</a>
      <a href="kontribusi.html">Kontribusi</a>
      <a href="changelog.html">Changelog</a>
    </div>
  </div>
</footer>

<script src="assets/script.js"></script>
</body>
</html>
"""


# ============================================================================
# LANDING PAGE
# ============================================================================
FEATURES = [
    ("💬", "Multi AI (Groq)",
     "Enam model dalam empat tingkat — Trinity Easy, Normal, Hard, sampai Extreme — "
     "lengkap dengan fallback otomatis saat model tidak tersedia."),
    ("👁️", "Analisis Gambar",
     "Kirim sampai lima gambar sekaligus dan minta Yuki membaca diagram, teks, "
     "atau mengkritik desain."),
    ("🎨", "Generate Gambar",
     "Cloudflare Workers AI dengan model FLUX.1 schnell, dilengkapi progres "
     "bertahap yang mulus."),
    ("🎙️", "Input Suara",
     "Bicara langsung ke aplikasi, ditranskripsi oleh Whisper Large v3 Turbo, "
     "lalu bisa diedit sebelum dikirim."),
    ("🗂️", "Artefak",
     "Tujuh kategori ala Claude dengan thread terpisah, plus penangkapan blok "
     "kode panjang secara otomatis."),
    ("🎓", "Trinity Kursus",
     "Sepuluh topik dengan kurikulum empat modul yang disusun otomatis, "
     "Yuki berperan sebagai mentor."),
    ("🌐", "14 Bahasa",
     "Bahasa antarmuka dan bahasa jawaban Yuki bisa diatur terpisah, "
     "dari Indonesia sampai 日本語 dan العربية."),
    ("⚙️", "Pengaturan Lengkap",
     "Sembilan tab pengaturan: dari kepribadian Yuki, memori, refleksi, "
     "sampai timer fokus dan kunci API pribadi."),
    ("✍️", "Animasi Teks",
     "Jawaban muncul bertahap per kalimat dengan caret berkedip, ditambah "
     "sekitar 20 keyframes animasi antarmuka."),
]

QUICKSTART = """git clone https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai.git
cd Ampera-Trinity-Ai

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# isi GROQ_API_KEY di berkas tersebut

streamlit run app.py"""

STATS = [
    ("6", "Model AI"),
    ("14", "Bahasa"),
    ("9", "Halaman aplikasi"),
    ("10", "Topik kursus"),
]


def build_home() -> str:
    md = markdown.Markdown(extensions=["fenced_code", "codehilite"],
                           extension_configs={"codehilite": {"guess_lang": False}})
    quick_html = md.convert(f"```bash\n{QUICKSTART}\n```")

    features = "".join(
        f'<article class="feature-card"><div class="ico">{ico}</div>'
        f"<h3>{html.escape(name)}</h3><p>{html.escape(desc)}</p></article>"
        for ico, name, desc in FEATURES
    )

    docs_cards = "".join(
        f'<a class="doc-card" href="{p["out"]}">'
        f'<span class="doc-ico">{p["icon"]}</span>'
        f'<span class="doc-ttl">{html.escape(p["title"])}</span>'
        f'<span class="doc-desc">{html.escape(p["desc"])}</span></a>'
        for p in PAGES
    )

    stats = "".join(
        f'<div class="stat"><span class="num">{n}</span>'
        f'<span class="lbl">{html.escape(l)}</span></div>'
        for n, l in STATS
    )

    body = f"""
<main id="main" class="landing">

  <section class="hero">
    <img class="hero-logo" src="assets/logo.png" alt="Logo Ampera Trinity AI">
    <h1>Ampera Trinity AI</h1>
    <p class="tagline">
      Multi AI · Generate Foto · Chat — aplikasi web berbasis Streamlit
      dengan asisten AI bernama <strong>Yuki</strong>.
    </p>
    <div class="badges">
      <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.11+">
      <img src="https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&amp;logoColor=white" alt="Streamlit">
      <img src="https://img.shields.io/badge/LLM-Groq-F55036" alt="Groq">
      <img src="https://img.shields.io/badge/Image-Cloudflare%20FLUX-F38020?logo=cloudflare&amp;logoColor=white" alt="Cloudflare FLUX">
      <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="Lisensi MIT">
    </div>
    <div class="cta-row">
      <a class="btn btn-primary" href="instalasi.html">Mulai sekarang</a>
      <a class="btn btn-ghost" href="dokumentasi.html">Baca dokumentasi</a>
      <a class="btn btn-ghost" href="{REPO_URL}" target="_blank" rel="noopener">{GH_ICON} Lihat di GitHub</a>
    </div>
  </section>

  <section class="section">
    <div class="stat-row">{stats}</div>
  </section>

  <section class="section">
    <div class="section-head">
      <h2>Semua dalam satu aplikasi</h2>
      <p>Chat, penglihatan, gambar, suara, artefak, dan kursus — tanpa berpindah alat.</p>
    </div>
    <div class="feature-grid">{features}</div>
  </section>

  <section class="section">
    <div class="section-head">
      <h2>Jalan dalam lima menit</h2>
      <p>Cukup Python 3.11 dan satu API key Groq gratis.</p>
    </div>
    <div class="quickstart">
      {quick_html}
      <p class="quickstart-note">
        Butuh langkah lebih rinci? Lihat <a href="instalasi.html">panduan instalasi</a>
        dan <a href="konfigurasi.html">cara mendapatkan API key</a>.
      </p>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <h2>Dokumentasi</h2>
      <p>Sepuluh dokumen untuk pengguna, pemilik aplikasi, dan pengembang.</p>
    </div>
    <div class="doc-grid">{docs_cards}</div>
  </section>

  <section class="cta-band">
    <h2>Siap dipublikasikan</h2>
    <p>
      Deploy gratis ke Streamlit Community Cloud dan dapatkan tautan yang bisa
      dibagikan hanya dalam beberapa menit.
    </p>
    <div class="cta-row">
      <a class="btn btn-primary" href="deploy.html">Panduan deploy</a>
      <a class="btn btn-ghost" href="kontribusi.html">Ikut berkontribusi</a>
    </div>
  </section>

</main>
"""
    return shell(f"{SITE_NAME} — Multi AI · Generate Foto · Chat",
                 SITE_DESC, body, is_home=True)


# ============================================================================
# HALAMAN DOKUMENTASI
# ============================================================================
def build_doc(page: dict, index: int) -> str:
    src = ROOT / page["src"]
    text = src.read_text(encoding="utf-8")

    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "codehilite", "attr_list", "md_in_html"],
        extension_configs={
            "toc": {"slugify": GitHubSlugger(), "permalink": "¶",
                    "permalink_class": "headerlink",
                    "permalink_title": "Tautan permanen ke bagian ini",
                    "toc_depth": "2-3"},
            "codehilite": {"guess_lang": False, "linenums": False},
        },
    )
    content = rewrite_links(md.convert(text))
    toc = build_toc(getattr(md, "toc_tokens", []))

    body = f"""
<div class="nav-overlay"></div>
<div class="docs-shell">
  <aside class="sidebar" aria-label="Navigasi dokumentasi">{render_sidebar(page["out"])}</aside>

  <main id="main" class="content">
    <div class="breadcrumb">
      <a href="index.html">Beranda</a><span class="sep">/</span>
      <a href="dokumentasi.html">Dokumentasi</a><span class="sep">/</span>
      <span>{html.escape(page["title"])}</span>
    </div>

    <article class="md">{content}</article>

    {page_nav(index)}

    <p class="edit-link">
      <a href="{EDIT_BASE}/{page["src"]}" target="_blank" rel="noopener">
        ✏️ Sunting halaman ini di GitHub</a>
    </p>
  </main>

  {toc}
</div>
"""
    return shell(page["title"], page["desc"], body)


# ============================================================================
# PROSES BUILD
# ============================================================================
def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    # Berkas tema
    for name in ("style.css", "highlight.css", "script.js"):
        shutil.copy2(THEME / "assets" / name, OUT / "assets" / name)

    # Logo
    logo = ROOT / "assets" / "logo_thinking_small.png"
    if logo.exists():
        shutil.copy2(logo, OUT / "assets" / "logo.png")

    # Nonaktifkan Jekyll di GitHub Pages (situs ini sudah HTML jadi)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Landing page
    (OUT / "index.html").write_text(build_home(), encoding="utf-8")
    written = ["index.html"]

    # Halaman dokumentasi
    for i, page in enumerate(PAGES):
        if not (ROOT / page["src"]).exists():
            print(f"  ! lewati (tidak ada): {page['src']}")
            continue
        (OUT / page["out"]).write_text(build_doc(page, i), encoding="utf-8")
        written.append(page["out"])

    # Halaman 404
    not_found = shell(
        "Halaman tidak ditemukan",
        "Halaman yang kamu cari tidak ada.",
        """
<main id="main" class="landing">
  <section class="hero">
    <h1>404</h1>
    <p class="tagline">Halaman yang kamu cari tidak ada atau sudah dipindahkan.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="index.html">Kembali ke beranda</a>
      <a class="btn btn-ghost" href="dokumentasi.html">Buka dokumentasi</a>
    </div>
  </section>
</main>
""",
        is_home=True,
    )
    (OUT / "404.html").write_text(not_found, encoding="utf-8")
    written.append("404.html")

    # Peta situs
    base = "https://amperaofficial26-beep.github.io/Ampera-Trinity-Ai/"
    urls = "".join(f"<url><loc>{base}{n}</loc></url>" for n in written if n != "404.html")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n", encoding="utf-8"
    )

    total_kb = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1024
    print(f"✓ Situs dibangun di {OUT.relative_to(ROOT)}/ "
          f"— {len(written)} halaman, {total_kb:.0f} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bangun situs dokumentasi.")
    parser.add_argument("--serve", action="store_true",
                        help="jalankan server lokal setelah membangun")
    parser.add_argument("--port", type=int, default=8000, help="port server lokal")
    args = parser.parse_args()

    build()

    if args.serve:
        import functools
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(OUT))
        print(f"→ Melayani di http://0.0.0.0:{args.port}")
        ThreadingHTTPServer(("0.0.0.0", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
