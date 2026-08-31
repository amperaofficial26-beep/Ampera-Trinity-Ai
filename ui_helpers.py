# -*- coding: utf-8 -*-
"""
Komponen UI kecil yang dipakai berulang: render bubble chat, indikator
"berpikir" ala Claude, progress bar generate gambar, animasi jawaban
bertahap per kalimat, ekspor riwayat chat ke Markdown, dan footer halaman.
"""

from __future__ import annotations

import base64
import html
import random
import re
import time
from datetime import datetime

import streamlit as st

from icons import ICON_COPY, ICON_MIC, ICON_IMAGE
from logo import LOGO_B64
from state import active_thread

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

# ----------------------------------------------------------------------
# UKURAN LOGO PER TEMPAT PAKAI (FIX: logo greeting kegedean)
#   Ditulis sebagai inline style (bukan cuma class CSS) supaya PASTI
#   menang walau ada aturan lain di stylesheet (styles.py) yang
#   mengira logo harus tampil besar. Ubah angkanya di sini kalau masih
#   kurang pas.
# ----------------------------------------------------------------------
_LOGO_SIZES = {
    "logo-greeting": "70px",   # logo di sebelah "Selamat pagi" — SEBELUMNYA kegedean
    "logo-label":    "20px",   # logo kecil di label "Yuki" pada bubble jawaban
    "logo-progress": "18px",   # logo di progress bar generate gambar
    "logo-foot":     "18px",   # logo di footer halaman
    "logo-inline":   "18px",   # default umum
    "logo-shimmer":  "25px",   # logo di indikator "berpikir"
}


def logo_img_html(css_class: str = "logo-inline") -> str:
    """Logo brand (PNG base64) — identik dengan logo tab/thinking.

    Ukurannya dipatok inline per css_class (lihat _LOGO_SIZES) supaya
    selalu tampil proporsional, tidak lagi bisa "kebobolan" jadi besar
    sekali seperti sebelumnya.
    """
    size = _LOGO_SIZES.get(css_class, "18px")
    return (
        f'<span class="{css_class}" role="img" aria-label="logo Trinity" '
        f'style="display:inline-block;width:{size};height:{size};'
        f'vertical-align:middle;line-height:0;">'
        f'<img src="data:image/png;base64,{LOGO_B64}" alt="" '
        f'style="width:100%;height:100%;object-fit:contain;display:block;"/>'
        f'</span>'
    )


# Kumpulan sapaan per waktu; dipilih acak tiap sesi agar halaman utama
# tidak monoton saat aplikasi dibuka berulang kali.
SAPAAN = {
    "pagi":  ["Selamat pagi", "Pagi! Siap berkarya?", "Halo, selamat pagi"],
    "siang": ["Selamat siang", "Halo! Ada yang bisa kubantu?", "Selamat datang kembali"],
    "sore":  ["Selamat sore", "Sore! Lanjut berkarya?", "Halo, selamat sore"],
    "malam": ["Selamat malam", "Malam! Masih semangat?", "Halo, selamat malam"],
}


def get_greeting() -> str:
    """Sapaan halaman utama; acak per sesi, sesuai waktu, tidak monoton."""
    if "sapaan" not in st.session_state:
        h = datetime.now().hour
        periode = ("pagi" if 4 <= h < 11 else "siang" if 11 <= h < 15
                   else "sore" if 15 <= h < 19 else "malam")
        st.session_state["sapaan"] = random.choice(SAPAAN[periode])
    return st.session_state["sapaan"]


def thinking_html(phrases: list[str]) -> str:
    spans = "".join(
        f'<span class="phrase">{html.escape(p)}…</span>' for p in phrases
    )
    # Logo brand dengan pita cahaya berjalan (shimmer).
    icon = logo_img_html("logo-shimmer")
    return (
        '<div class="claude-think">'
        f"{icon}"
        f'<span class="phrases">{spans}</span>'
        "</div>"
    )


IMAGE_STAGE_PHRASES = [
    "Membayangkan gambarnya",
    "Menyiapkan kanvas",
    "Melukis perlahan",
    "Menajamkan detail",
]


def image_progress_html(labels: list[str] | None = None,
                        done: bool = False) -> str:
    """Kotak loading pembuatan gambar ala ChatGPT.

    PENTING: HTML ini dirender SEKALI saja, lalu seluruh gerakannya
    (shimmer tepi yang berputar, sapuan kanvas, pergantian teks, bar
    progres) dijalankan murni oleh CSS di browser. Kalau blok ini
    di-`markdown()` berulang kali, Streamlit mengganti node DOM-nya
    setiap kali sehingga semua animasi CSS ter-reset dari awal dan
    terlihat diam / berkedip.
    """
    phrases = list(labels or IMAGE_STAGE_PHRASES)[:4]
    if done:
        phrases = ["Selesai"]

    spans = "".join(
        f'<span class="img-gen-phrase">{html.escape(p)}…</span>' for p in phrases
    )
    meta = f'<div class="ai-label">{logo_img_html("logo-label")} Yuki</div>'
    state_cls = " is-done" if done else ""
    return (
        f'<div class="bubble-row ai">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="img-gen-box-wrapper{state_cls}">'
        '<div class="img-gen-box-inner">'
        '<div class="img-gen-canvas-shimmer"></div>'
        '<div class="img-gen-center-icon">'
        '<svg class="img-gen-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect width="18" height="18" x="3" y="3" rx="4"/>'
        '<circle cx="8.5" cy="8.5" r="1.5"/>'
        '<path d="m21 15-5-5L5 21"/>'
        '</svg>'
        '</div>'
        '<div class="img-gen-status-wrap">'
        f'<div class="img-gen-phrases">{spans}</div>'
        '<div class="img-gen-mini-bar">'
        '<div class="img-gen-mini-fill"></div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div></div>'
    )
    # ============================================================================
# BUBBLE CHAT
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
# EXPORT CHAT (.md)
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
# CSS posisi dok input (halaman awal vs sudah ada chat)
#   FIX: sebelumnya halaman awal MENGUNCI overflow (overflow:hidden) di
#   html/body/section.main. Itulah penyebab "nggak bisa discroll" — di
#   banyak browser (terutama mobile Safari), reset overflow:auto yang
#   dikirim belakangan tidak selalu menang balik, jadi kadang halaman
#   tetap terkunci. Solusinya: JANGAN sentuh overflow sama sekali. Cukup
#   geser posisi kotak input (transform) tanpa mengunci scroll.
# ============================================================================
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
</style>
"""

_BOTTOM_RESET_CSS = """
<style>
[data-testid="stBottom"] { transform: translateY(0) !important; }
</style>
"""


def _page_footer(in_chat: bool = False) -> None:
    foot_class = "trinity-foot" if not in_chat else "trinity-foot in-chat"
    st.markdown(
        f'<p class="{foot_class}">© 2026 Ampera Trinity AI · by Ampera Official</p>',
        unsafe_allow_html=True,
    )
