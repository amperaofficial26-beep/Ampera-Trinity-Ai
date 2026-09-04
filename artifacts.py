# -*- coding: utf-8 -*-
"""
PANEL ARTEFAK (sidebar kanan) — ala Claude Artifacts.

Dua tampilan:
  DAFTAR : bagian "Artefak" (kartu file + unduh semua) dan "Konten"
           (petak gambar hasil buatan Yuki)
  ISI    : kode dengan nomor baris + pewarnaan sintaks, tombol Salin,
           perlebar, dan tutup

Alur: Yuki menulis blok kode ```...``` -> ambil_artefak() memotongnya dari
teks chat, menyimpannya sebagai file, lalu panel ini terbuka otomatis.

>>> ATUR LEBAR & PERILAKU PANEL DI BAGIAN "PENGATURAN" DI BAWAH <<<
"""

from __future__ import annotations

import base64
import html
import io
import re
import zipfile
from datetime import datetime

import streamlit as st

# ============================================================================
# PENGATURAN
# ============================================================================
PANEL_LEBAR_PX = 470        # lebar panel kanan
PANEL_LEBAR_LEBAR_PX = 860  # lebar saat tombol "perlebar" ditekan
BUKA_OTOMATIS = True        # panel langsung terbuka saat file baru dibuat
MIN_BARIS_JADI_FILE = 3     # blok kode lebih pendek dari ini tetap di chat
MIN_KARAKTER_JADI_FILE = 40
BARIS_LANGSUNG_FILE = 5     # sebanyak ini baris ke atas: selalu jadi file

# --- TOMBOL BUKA/TUTUP PANEL: warna, ukuran, posisi ------------------------
# Catatan: styles.py punya aturan global "div.stButton > button" yang juga
# memakai !important. Karena itu CSS di bawah ditulis dengan awalan "body"
# agar spesifisitasnya lebih tinggi dan pasti menang.
TOMBOL_BG = "#F2E8D6"          # latar tombol saat diam
TOMBOL_BG_HOVER = "#40304A"    # latar saat disentuh kursor
TOMBOL_IKON = "#4A3559"        # warna ikon
TOMBOL_GARIS = "#2C1F33"       # garis tepi ("transparent" = tanpa garis)
TOMBOL_UKURAN_PX =   38        # lebar = tinggi
TOMBOL_RADIUS_PX = 50          # kelengkungan sudut
TOMBOL_POSISI = "atas"       # "tengah" | "atas" | "bawah"
TOMBOL_OFFSET_PX = 53         # jarak dari atas/bawah bila posisi bukan tengah
TOMBOL_JARAK_TEPI_PX = 15      # jarak dari tepi layar saat panel TERTUTUP
TOMBOL_JARAK_PANEL_PX = 5     # jarak dari tepi panel saat panel TERBUKA
TOMBOL_BAYANGAN = "0 4px 14px rgba(44,31,51,0.18)"   # "none" = tanpa bayangan
# ============================================================================
_EKSTENSI = {
    "python": "py", "py": "py", "javascript": "js", "js": "js",
    "typescript": "ts", "ts": "ts", "html": "html", "css": "css",
    "json": "json", "yaml": "yml", "yml": "yml", "sql": "sql",
    "bash": "sh", "sh": "sh", "shell": "sh", "java": "java",
    "kotlin": "kt", "swift": "swift", "php": "php", "dart": "dart",
    "go": "go", "rust": "rs", "c": "c", "cpp": "cpp", "csharp": "cs",
    "markdown": "md", "md": "md", "xml": "xml", "toml": "toml",
}

_KODE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.S)
_NAMA_RE = re.compile(r"([\w./-]+\.[A-Za-z0-9]{1,5})\s*:?\s*$")

_KATA_KUNCI = {
    "def", "class", "return", "import", "from", "as", "if", "elif", "else",
    "for", "while", "in", "not", "and", "or", "is", "None", "True", "False",
    "try", "except", "finally", "raise", "with", "lambda", "yield", "pass",
    "break", "continue", "global", "nonlocal", "assert", "del", "async", "await",
    "function", "const", "let", "var", "new", "this", "export", "default",
    "public", "private", "static", "void", "int", "str", "bool", "float",
}


# ============================================================================
# PENYIMPANAN
# ============================================================================
def daftar_artefak() -> list[dict]:
    if "artifacts" not in st.session_state:
        st.session_state.artifacts = []
    return st.session_state.artifacts


def _tebak_nama(lang: str, kode: str, sebelum: str) -> str:
    m = _NAMA_RE.search((sebelum or "").strip().splitlines()[-1]
                        if (sebelum or "").strip() else "")
    if m:
        return m.group(1)
    baris1 = (kode.splitlines() or [""])[0].strip()
    m2 = re.search(r"([\w./-]+\.[A-Za-z0-9]{1,5})", baris1)
    if m2 and baris1.startswith(("#", "//", "/*", "<!--")):
        return m2.group(1)
    ext = _EKSTENSI.get((lang or "").lower(), "txt")
    return f"file_{len(daftar_artefak()) + 1}.{ext}"


def ambil_artefak(teks: str) -> tuple[str, list[int]]:
    """Potong blok kode dari jawaban Yuki -> simpan sebagai file."""
    raw = teks or ""
    if "```" not in raw:
        return raw, []

    baru: list[int] = []
    potongan: list[str] = []
    posisi = 0

    for m in _KODE_RE.finditer(raw):
        lang = (m.group(1) or "").lower()
        kode = m.group(2).strip("\n")
        potongan.append(raw[posisi:m.start()])
        sebelum = raw[posisi:m.start()]
        posisi = m.end()

        n_baris = len(kode.splitlines())
        layak = (n_baris >= BARIS_LANGSUNG_FILE
                 or (n_baris >= MIN_BARIS_JADI_FILE
                     and len(kode) >= MIN_KARAKTER_JADI_FILE))
        if not layak:
            potongan.append(m.group(0))
            continue

        st.session_state["artifact_counter"] = (
            st.session_state.get("artifact_counter", 0) + 1
        )
        aid = st.session_state["artifact_counter"]
        daftar_artefak().insert(0, {
            "id": aid,
            "title": _tebak_nama(lang, kode, sebelum),
            "content": kode,
            "lang": lang or "text",
            "time": datetime.now().strftime("%H:%M"),
        })
        baru.append(aid)

    potongan.append(raw[posisi:])
    bersih = re.sub(r"\n{3,}", "\n\n", "".join(potongan)).strip()

    if baru and BUKA_OTOMATIS:
        st.session_state["artifact_panel_open"] = True
        st.session_state["artifact_panel_id"] = baru[0]

    return bersih, baru


def kartu_file_html(ids: list[int]) -> str:
    """Kartu ringkas pengganti kode di dalam chat."""
    kartu = ""
    for aid in ids:
        art = next((a for a in daftar_artefak() if a["id"] == aid), None)
        if not art:
            continue
        kartu += (
            '<div class="af-chip"><span class="af-chip-ic">&lt;/&gt;</span>'
            f'<span class="af-chip-name">{html.escape(art["title"])}</span>'
            f'<span class="af-chip-meta">{html.escape(art["lang"])} · '
            f'{len(art["content"].splitlines())} baris</span></div>'
        )
    return kartu


# ============================================================================
# AKSI PANEL
# ============================================================================
def buka_panel(aid: int) -> None:
    st.session_state["artifact_panel_open"] = True
    st.session_state["artifact_panel_id"] = aid


def tutup_panel() -> None:
    st.session_state["artifact_panel_open"] = False


def toggle_panel() -> None:
    st.session_state["artifact_panel_open"] = not st.session_state.get(
        "artifact_panel_open", False
    )


def pilih_file(aid: int) -> None:
    st.session_state["artifact_panel_id"] = aid


def kembali_ke_daftar() -> None:
    st.session_state["artifact_panel_id"] = None


def toggle_lebar() -> None:
    st.session_state["artifact_panel_wide"] = not st.session_state.get(
        "artifact_panel_wide", False
    )


# ============================================================================
# TAMPILAN KODE: nomor baris + pewarnaan sintaks sederhana
# ============================================================================
def _warnai(baris: str) -> str:
    """Pewarnaan sintaks ringan tanpa pustaka luar (Pygments tidak ada di
    lingkungan Streamlit Cloud kita). Urutannya penting: komentar dan teks
    dikunci lebih dulu agar isinya tidak ikut diwarnai sebagai kata kunci."""
    hasil: list[str] = []
    pola = re.compile(
        r'(?P<komentar>#[^\n]*|//[^\n]*)'
        r'|(?P<teks>"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')'
        r'|(?P<angka>\b\d+(?:\.\d+)?\b)'
        r'|(?P<kata>\b[A-Za-z_][A-Za-z_0-9]*\b)'
    )
    posisi = 0
    for m in pola.finditer(baris):
        hasil.append(html.escape(baris[posisi:m.start()]))
        posisi = m.end()
        isi = html.escape(m.group(0))
        if m.lastgroup == "komentar":
            hasil.append(f'<span class="k-com">{isi}</span>')
        elif m.lastgroup == "teks":
            hasil.append(f'<span class="k-str">{isi}</span>')
        elif m.lastgroup == "angka":
            hasil.append(f'<span class="k-num">{isi}</span>')
        elif m.group(0) in _KATA_KUNCI:
            hasil.append(f'<span class="k-key">{isi}</span>')
        else:
            hasil.append(isi)
    hasil.append(html.escape(baris[posisi:]))
    return "".join(hasil) or "&nbsp;"


def _kode_html(kode: str) -> str:
    """Kode dengan nomor baris, siap ditempel sebagai HTML."""
    baris_html = ""
    for i, b in enumerate(kode.splitlines() or [""], start=1):
        baris_html += (
            '<div class="af-ln"><span class="af-num">' + str(i) + "</span>"
            '<span class="af-code">' + _warnai(b) + "</span></div>"
        )
    return '<div class="af-codebox">' + baris_html + "</div>"


def _tombol_salin_html(teks: str, label: str = "Salin") -> str:
    b64 = base64.b64encode((teks or "").encode("utf-8")).decode("ascii")
    return (
        '<button class="af-copy" data-b64="' + b64 + '" '
        'onclick="const t=atob(this.dataset.b64);'
        "navigator.clipboard.writeText(decodeURIComponent(escape(t)));"
        "const o=this.innerHTML;this.innerHTML='Tersalin';"
        'setTimeout(()=>{this.innerHTML=o;},1300);" '
        'title="Salin seluruh isi">' + html.escape(label) + "</button>"
    )


def _zip_semua(daftar: list[dict]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        dipakai: set[str] = set()
        for a in daftar:
            nama = a["title"]
            n = 1
            while nama in dipakai:
                n += 1
                nama = f"{n}_{a['title']}"
            dipakai.add(nama)
            z.writestr(nama, a["content"])
    return buf.getvalue()


def _gambar_sesi() -> list[dict]:
    """Kumpulkan gambar hasil buatan Yuki dari semua thread (bagian Konten)."""
    keluar: list[dict] = []
    for kunci, nilai in st.session_state.items():
        if not isinstance(nilai, list):
            continue
        if not (kunci == "messages" or str(kunci).endswith("_msgs")
                or str(kunci).startswith(("mode_msgs", "course_msgs",
                                          "artifact_msgs"))):
            continue
        for m in nilai:
            if isinstance(m, dict) and m.get("type") == "image" and m.get("image_bytes"):
                keluar.append(m)
    return keluar[-8:]


# ============================================================================
# CSS PANEL
# ============================================================================
def _css_panel(terbuka: bool, lebar: bool) -> str:
    w = PANEL_LEBAR_LEBAR_PX if lebar else PANEL_LEBAR_PX
    geser = (str(w + TOMBOL_JARAK_PANEL_PX) if terbuka
             else str(TOMBOL_JARAK_TEPI_PX))

    if TOMBOL_POSISI == "atas":
        posisi_css = ("top:" + str(TOMBOL_OFFSET_PX) + "px !important;"
                      "bottom:auto !important;transform:none !important;")
    elif TOMBOL_POSISI == "bawah":
        posisi_css = ("bottom:" + str(TOMBOL_OFFSET_PX) + "px !important;"
                      "top:auto !important;transform:none !important;")
    else:
        posisi_css = "top:50% !important;transform:translateY(-50%) !important;"
    return (
        "<style>"
        ".st-key-art_panel{"
        "position:fixed !important;top:3.2rem !important;right:0 !important;"
        "bottom:0 !important;width:" + str(w) + "px !important;"
        "background:#FBF7F0 !important;border-left:1px solid #E4D9C6 !important;"
        "padding:18px 18px 90px !important;overflow-y:auto !important;"
        "z-index:999990 !important;"
        "box-shadow:-10px 0 30px rgba(44,31,51,0.07) !important;"
        "transition:width .3s cubic-bezier(.32,.72,0,1) !important;"
        "animation:afSlideIn .34s cubic-bezier(.32,.72,0,1) both;}"
        "@keyframes afSlideIn{from{opacity:0;transform:translateX(30px);}"
        "to{opacity:1;transform:translateX(0);}}"
        ".st-key-art_panel [data-testid='stVerticalBlock']{gap:.5rem !important;}"

        # --- tombol mengambang buka/tutup ---
        # Awalan "body" menaikkan spesifisitas agar menang melawan aturan
        # global div.stButton > button di styles.py.
        "body .st-key-af_toggle{position:fixed !important;"
        + posisi_css +
        "right:" + geser + "px !important;"
        "width:" + str(TOMBOL_UKURAN_PX) + "px !important;margin:0 !important;"
        "z-index:999995 !important;"
        "transition:right .3s cubic-bezier(.32,.72,0,1) !important;}"
        "body .st-key-af_toggle div.stButton > button,"
        "body .st-key-af_toggle button[kind='secondary'],"
        "body .st-key-af_toggle [data-testid='stBaseButton-secondary']{"
        "background:" + TOMBOL_BG + " !important;"
        "background-color:" + TOMBOL_BG + " !important;"
        "border:1px solid " + TOMBOL_GARIS + " !important;"
        "color:" + TOMBOL_IKON + " !important;"
        "width:" + str(TOMBOL_UKURAN_PX) + "px !important;"
        "min-width:" + str(TOMBOL_UKURAN_PX) + "px !important;"
        "height:" + str(TOMBOL_UKURAN_PX) + "px !important;"
        "min-height:" + str(TOMBOL_UKURAN_PX) + "px !important;"
        "padding:0 !important;"
        "border-radius:" + str(TOMBOL_RADIUS_PX) + "px !important;"
        "box-shadow:" + TOMBOL_BAYANGAN + " !important;"
        "transition:transform .15s ease, background .15s ease !important;}"
        "body .st-key-af_toggle div.stButton > button:hover{"
        "background:" + TOMBOL_BG_HOVER + " !important;"
        "background-color:" + TOMBOL_BG_HOVER + " !important;"
        "transform:scale(1.06) !important;}"
        "body .st-key-af_toggle div.stButton > button:active{"
        "transform:scale(.94) !important;}"
        "body .st-key-af_toggle [data-testid='stIconMaterial']{"
        "font-size:1.35rem !important;width:1.35rem !important;"
        "height:1.35rem !important;color:" + TOMBOL_IKON + " !important;}"

        "[data-testid='stMainBlockContainer']{padding-right:"
        + (str(w + 40) + "px" if terbuka else "1rem")
        + " !important;transition:padding-right .3s cubic-bezier(.32,.72,0,1);}"

        "@media (max-width:1100px){"
        ".st-key-art_panel{width:100% !important;top:0 !important;}"
        "[data-testid='stMainBlockContainer']{padding-right:1rem !important;}"
        "body .st-key-af_toggle{right:14px !important;top:auto !important;"
        "bottom:96px !important;transform:none !important;}}"
        "</style>"
    )
# ============================================================================
# TAMPILAN 1: DAFTAR (Artefak + Konten)
# ============================================================================
def _render_daftar(daftar: list[dict]) -> None:
    st.markdown('<div class="af-sec">Artefak</div>', unsafe_allow_html=True)

    if not daftar:
        st.markdown(
            '<div class="af-empty">Minta Yuki membuat kode atau file, '
            "misalnya <b>\"buatkan kalkulator python\"</b>. Hasilnya otomatis "
            "muncul di panel ini, bukan memenuhi ruang chat.</div>",
            unsafe_allow_html=True,
        )
    else:
        with st.container(key="af_dlall"):
            st.download_button(
                ":material/download:  Unduh semua",
                data=_zip_semua(daftar),
                file_name="artefak-trinity.zip",
                mime="application/zip",
                key="af_zip",
                use_container_width=True,
            )

        for a in daftar[:20]:
            nama = a["title"].rsplit(".", 1)[0]
            ext = (a["title"].rsplit(".", 1)[-1] if "." in a["title"]
                   else a["lang"]).upper()
            with st.container(key=f"af_card_{a['id']}"):
                ikon, isi, unduh = st.columns([0.22, 1.0, 0.2])
                with ikon:
                    st.markdown('<div class="af-file-ic">&lt;/&gt;</div>',
                                unsafe_allow_html=True)
                with isi:
                    st.markdown(
                        '<div class="af-file-name">' + html.escape(nama) + "</div>"
                        '<div class="af-file-ext">' + html.escape(ext) + "</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("Buka", key=f"af_open_{a['id']}",
                                 use_container_width=True):
                        pilih_file(a["id"])
                with unduh:
                    st.download_button(
                        ":material/download:",
                        data=a["content"],
                        file_name=a["title"],
                        mime="text/plain",
                        key=f"af_dl1_{a['id']}",
                    )

    # ---- bagian Konten: gambar hasil buatan Yuki ----
    gambar = _gambar_sesi()
    if gambar:
        st.markdown('<div class="af-sec af-sec-2">Konten</div>',
                    unsafe_allow_html=True)
        with st.container(key="af_konten"):
            for i in range(0, len(gambar), 2):
                pasangan = gambar[i:i + 2]
                cols = st.columns(len(pasangan))
                for j, m in enumerate(pasangan):
                    with cols[j]:
                        st.image(m["image_bytes"], use_container_width=True)


# ============================================================================
# TAMPILAN 2: ISI FILE
# ============================================================================
def _render_isi(aktif: dict, lebar: bool) -> None:
    ext = (aktif["title"].rsplit(".", 1)[-1] if "." in aktif["title"]
           else aktif["lang"]).upper()
    nama = aktif["title"].rsplit(".", 1)[0]

    judul, aksi = st.columns([1.0, 0.72])
    with judul:
        st.markdown(
            '<div class="af-title-row"><span class="af-title">'
            + html.escape(nama) + '</span><span class="af-title-ext"> · '
            + html.escape(ext) + "</span></div>",
            unsafe_allow_html=True,
        )
    with aksi:
        with st.container(key="af_actbar"):
            c1, c2, c3 = st.columns([1.0, 0.34, 0.34])
            with c1:
                st.markdown(_tombol_salin_html(aktif["content"]),
                            unsafe_allow_html=True)
            with c2:
                if st.button(":material/close_fullscreen:" if lebar
                             else ":material/open_in_full:",
                             key="af_wide", help="Perlebar / kecilkan panel"):
                    toggle_lebar()
            with c3:
                if st.button(":material/close:", key="af_close",
                             help="Tutup panel"):
                    tutup_panel()

    if st.button(":material/arrow_back:  Semua file", key="af_back"):
        kembali_ke_daftar()

    st.markdown(_kode_html(aktif["content"]), unsafe_allow_html=True)

    with st.container(key="af_actions"):
        st.download_button(
            ":material/download:  Unduh " + aktif["title"],
            data=aktif["content"],
            file_name=aktif["title"],
            mime="text/plain",
            key=f"af_dl_{aktif['id']}",
            use_container_width=True,
        )
# ============================================================================
# PINTU MASUK
# ============================================================================
def render_panel() -> None:
    """Panel kanan + tombol mengambang buka/tutup.

    Streamlit tidak punya sidebar kanan bawaan, jadi panel ini container
    biasa yang DIPOSISIKAN ke kanan lewat CSS.
    """
    daftar = daftar_artefak()
    terbuka = bool(st.session_state.get("artifact_panel_open"))
    lebar = bool(st.session_state.get("artifact_panel_wide"))
    st.markdown(_css_panel(terbuka, lebar), unsafe_allow_html=True)

    # tombol mengambang: SELALU tampil
    with st.container(key="af_toggle"):
        if st.button(
            ":material/right_panel_close:" if terbuka
            else ":material/right_panel_open:",
            key="af_toggle_btn",
            help=("Tutup panel file" if terbuka
                  else (f"Buka panel file ({len(daftar)})" if daftar
                        else "Panel file (masih kosong)")),
        ):
            toggle_panel()

    if not terbuka:
        return

    aktif_id = st.session_state.get("artifact_panel_id")
    aktif = next((a for a in daftar if a["id"] == aktif_id), None)

    with st.container(key="art_panel"):
        if aktif is None:
            _render_daftar(daftar)
        else:
            _render_isi(aktif, lebar)
