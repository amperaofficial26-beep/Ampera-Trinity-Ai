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
import streamlit.components.v1 as components
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
    """Potong blok kode dari jawaban Yuki -> simpan sebagai file, 
    sekaligus merapikan teks dan menyisipkan kartu artefak di chat."""
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
    
    # Rapikan spasi atau baris kosong berlebih yang tertinggal
    bersih = re.sub(r"\n{3,}", "\n\n", "".join(potongan)).strip()

    # Jika ada file/artefak baru yang berhasil dibuat, 
    # sematkan kartu ringkasnya di akhir teks pesan chat
    if baru:
        bersih += "\n\n" + kartu_file_html(baru)

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
    st.session_state["artifact_panel_wide"] = not bool(
        st.session_state.get("artifact_panel_wide", False)
    )

    # Menekan perluas tidak boleh menutup panel.
    st.session_state["artifact_panel_open"] = True


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
  
def render_tombol_salin(teks: str) -> None:
    """Tombol salin yang benar-benar menyalin isi file ke clipboard."""
    data = base64.b64encode((teks or "").encode("utf-8")).decode("ascii")

    components.html(
        f"""
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                overflow: hidden;
            }}

            #copy-code {{
                width: 100%;
                height: 46px;
                border: 1px solid #DCCFBE;
                border-radius: 8px;
                background: #FFFFFF;
                color: #382843;
                font-size: 14px;
                font-weight: 650;
                cursor: pointer;
                transition: background .18s ease, color .18s ease;
            }}

            #copy-code:hover {{
                background: #F7F0E5;
            }}

            #copy-code.copied {{
                background: #382843;
                color: #FFFFFF;
                animation: copy-in .18s ease-out, copy-out .18s ease-in 1.15s;
            }}

            @keyframes copy-in {{
                from {{ transform: scale(.82) rotate(-8deg); opacity: .4; }}
                to {{ transform: scale(1) rotate(0deg); opacity: 1; }}
            }}

            @keyframes copy-out {{
                from {{ transform: scale(1) rotate(0deg); opacity: 1; }}
                to {{ transform: scale(.82) rotate(8deg); opacity: .4; }}
            }}
        </style>

        <button id="copy-code" type="button">Salin</button>

        <script>
            const button = document.getElementById("copy-code");
            const encoded = "{data}";

            async function copyText() {{
                const bytes = Uint8Array.from(atob(encoded), c => c.charCodeAt(0));
                const text = new TextDecoder().decode(bytes);

                try {{
                    await navigator.clipboard.writeText(text);
                }} catch (_) {{
                    const area = document.createElement("textarea");
                    area.value = text;
                    document.body.appendChild(area);
                    area.select();
                    document.execCommand("copy");
                    area.remove();
                }}

                button.classList.add("copied");
                button.textContent = "✓";

                setTimeout(() => {{
                    button.classList.remove("copied");
                    button.textContent = "Salin";
                }}, 1350);
            }}

            button.addEventListener("click", copyText);
        </script>
        """,
        height=48,
        scrolling=False,
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
    geser = str(w + 12) if terbuka else "16"

    return (
        "<style>"
        ".st-key-art_panel{"
        "position:fixed!important;top:0!important;right:0!important;"
        "bottom:0!important;width:" + str(w) + "px!important;"
        "padding:24px 20px 32px!important;overflow-y:auto!important;"
        "background:#FFFCF7!important;border-left:1px solid #E8E0D4!important;"
        "box-shadow:-12px 0 36px rgba(44,31,51,.10)!important;"
        "z-index:999990!important;"
        "}"
        "[class*='st-key-af_card_']{"
        "padding:12px!important;margin:0 0 10px!important;"
        "background:#FFFFFF!important;border:1px solid #E8E0D4!important;"
        "border-radius:12px!important;"
        "}"
        ".af-panel-title{font-size:20px;font-weight:700;color:#2C1F33;margin:0;}"
        ".af-panel-sub{font-size:13px;color:#8A7B8F;margin:4px 0 18px;}"
        ".af-file-name{font-size:15px;font-weight:650;color:#2C1F33;}"
        ".af-file-meta{font-size:12px;color:#8A7B8F;margin-top:3px;}"
        ".af-preview-head{font-size:18px;font-weight:700;color:#2C1F33;margin:0;}"
        ".af-preview-meta{font-size:12px;color:#8A7B8F;margin-top:4px;}"
        ".af-empty{padding:28px 12px;color:#75697A;text-align:center;line-height:1.55;}"
        ".af-codebox{margin-top:18px!important;border:1px solid #E8E0D4!important;"
        "border-radius:12px!important;background:#FFFDF9!important;padding:14px 0!important;}"
        ".af-ln{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;"
        "font-size:13px!important;line-height:1.75!important;}"
        ".af-num{color:#B3A6B8!important;min-width:38px!important;}"
        ".af-code{color:#34283A!important;}"
        ".k-key{color:#7D3FB2!important;font-weight:700;}"
        ".k-str{color:#13795B!important;}"
        ".k-com{color:#8A7B8F!important;}"
        ".k-num{color:#B45309!important;}"
        ".af-copy{width:100%;padding:10px 14px;border:1px solid #DCCEBB;"
        "border-radius:9px;background:#FFFFFF;color:#2C1F33;font-weight:650;"
        "cursor:pointer;font-size:14px;}"
        ".af-copy:hover{background:#F7F0E5;}"
        "body [class*='st-key-af_toggle']{"
        "position:fixed!important;"
        "top:18px!important;"
        "right:18px!important;"
        "left:auto!important;"
        "bottom:auto!important;"
        "width:48px!important;"
        "margin:0!important;"
        "z-index:999999!important;"
        "}"
        "body [class*='st-key-af_toggle'] button{"
        "width:48px!important;"
        "height:48px!important;"
        "min-width:48px!important;"
        "padding:0!important;"
        "border-radius:10px!important;"
        "background:#FFFFFF!important;"
        "border:1px solid #DCCFBE!important;"
        "color:#382843!important;"
        "box-shadow:0 4px 14px rgba(44,31,51,.12)!important;"
        "}"
        "body .st-key-af_toggle button{border-radius:50px!important;"
        "background:#FFFFFF!important;border:1px solid #DCCEBB!important;"
        "color:#4A3559!important;box-shadow:0 4px 14px rgba(44,31,51,.10)!important;}"
        "body [class*='st-key-af_preview_'] button,"
        "body [class*='st-key-af_download_'] button,"
        "body .st-key-af_back button,body .st-key-af_close button,"
        "body .st-key-af_wide button{border-radius:50px!important;"
        "border:1px solid #DCCEBB!important;background:#FFFFFF!important;"
        "color:#4A3559!important;font-weight:600!important;}"
        "@media(max-width:850px){"
        ".st-key-art_panel{width:100%!important;padding:20px 16px 28px!important;}"
        "body [class*='st-key-af_toggle']{"
        "top:14px!important;"
        "right:14px!important;"
        "left:auto!important;"
        "bottom:auto!important;"
        "}"
        "body .st-key-af_back_wrap button,"
        "body [class*='st-key-af_download_current_wrap_'] button,"
        "body .st-key-af_expand_wrap button{"
        "height:46px!important;"
        "min-height:46px!important;"
        "border:1px solid #DCCFBE!important;"
        "border-radius:8px!important;"
        "background:#FFFFFF!important;"
        "color:#382843!important;"
        "font-weight:650!important;"
        "box-shadow:none!important;"
        "}"
        "</style>"
    )


def _render_daftar(daftar: list[dict]) -> None:
    jumlah = len(daftar)
    st.markdown(
        '<div class="af-panel-title">File</div>'
        f'<div class="af-panel-sub">{jumlah} file tersimpan di percakapan ini</div>',
        unsafe_allow_html=True,
    )

    if not daftar:
        st.markdown(
            '<div class="af-empty">Belum ada file.<br>'
            'Minta Yuki membuat kode atau dokumen untuk melihat preview di sini.</div>',
            unsafe_allow_html=True,
        )
        return

    with st.container(key="af_download_all"):
        st.download_button(
            ":material/folder_zip:  Unduh semua",
            data=_zip_semua(daftar),
            file_name="artefak-trinity.zip",
            mime="application/zip",
            key="af_zip",
            use_container_width=True,
        )

    st.divider()

    for a in daftar[:20]:
        ext = (
            a["title"].rsplit(".", 1)[-1].upper()
            if "." in a["title"]
            else a["lang"].upper()
        )

        with st.container(key=f"af_card_{a['id']}"):
            info, aksi = st.columns([1.75, 1])

            with info:
                st.markdown(
                    '<div class="af-file-name">' + html.escape(a["title"]) + "</div>"
                    '<div class="af-file-meta">' + html.escape(ext)
                    + " · " + str(len(a["content"].splitlines()))
                    + " baris · " + html.escape(a.get("time", "")) + "</div>",
                    unsafe_allow_html=True,
                )

            with aksi:
                left, right = st.columns(2)

                with left:
                    with st.container(key=f"af_preview_{a['id']}"):
                        if st.button(
                            "Preview",
                            key=f"af_open_{a['id']}",
                            use_container_width=True,
                        ):
                            pilih_file(a["id"])

                with right:
                    with st.container(key=f"af_download_{a['id']}"):
                        st.download_button(
                            ":material/download:",
                            data=a["content"],
                            file_name=a["title"],
                            mime="text/plain",
                            key=f"af_dl_{a['id']}",
                            use_container_width=True,
                        )


def _render_isi(aktif: dict, lebar: bool) -> None:
    ext = (
        aktif["title"].rsplit(".", 1)[-1].upper()
        if "." in aktif["title"]
        else aktif["lang"].upper()
    )

    st.markdown(
        '<div class="af-head-title">' + html.escape(aktif["title"]) + "</div>"
        '<div class="af-head-sub">' + html.escape(ext)
        + " · " + str(len(aktif["content"].splitlines()))
        + " baris</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # Semua tombol berukuran dan sejajar sama.
    kembali, salin, unduh, perluas = st.columns(4, gap="small")

    with kembali:
        with st.container(key="af_back_wrap"):
            if st.button(
                "← File",
                key="af_back_btn",
                use_container_width=True,
            ):
                kembali_ke_daftar()

    with salin:
        render_tombol_salin(aktif["content"])

    with unduh:
        with st.container(key=f"af_download_current_wrap_{aktif['id']}"):
            st.download_button(
                "Unduh",
                data=aktif["content"],
                file_name=aktif["title"],
                mime="text/plain",
                key=f"af_download_current_{aktif['id']}",
                use_container_width=True,
            )

    with perluas:
        with st.container(key="af_expand_wrap"):
            if st.button(
                ":material/close_fullscreen:" if lebar
                else ":material/open_in_full:",
                key="af_expand_btn",
                help="Perlebar atau kecilkan panel",
                use_container_width=True,
            ):
                toggle_lebar()

    st.markdown(_kode_html(aktif["content"]), unsafe_allow_html=True)
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
