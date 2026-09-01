#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
File utama: hanya menyatukan modul-modul lain lalu mengatur navigasi
antar halaman. Semua konstanta/katalog ada di config.py, semua state di
state.py, sidebar di sidebar.py, handler kirim pesan di chat_handlers.py,
komponen render kecil di ui_helpers.py, ikon di icons.py, logo di logo.py,
dan CSS di styles.py.

HALAMAN (routing internal lewat st.session_state.page):
  - chat        → halaman utama (default)
  - artefak     → kotak kategori ala Claude, Yuki menjawab di halaman itu
  - pengaturan  → 9 tab: Umum · Akun · Privasi · Penagihan · Kemampuan ·
                  Memori · Refleksi · Waktu dan fokus · Trinity Code
  - bahasa      → 14 bahasa (antarmuka + bahasa jawaban Yuki)
  - bantuan     → petunjuk detail pemakaian aplikasi + FAQ + kontak
  - tingkatkan  → promosi paket "Trinity Pro"
  - aplikasi    → rencana rilis aplikasi Android/iOS
  - kursus      → Trinity kursus (Yuki jadi mentor, thread sendiri)
  - pelajari    → tentang aplikasi + cara pakai + tips
"""

from __future__ import annotations

import html
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

def now_wib() -> str:
    return datetime.now(WIB).strftime("%H:%M")

import streamlit as st
from openai import OpenAI

from config import (
    AVAILABLE_MODELS, CHAT_INPUT_SUPPORTS_AUDIO, CHAT_INPUT_SUPPORTS_FILE,
    CHAT_READY, COURSE_BY_KEY, COURSE_CATALOG, DEFAULT_MODEL_KEY,
    GROQ_API_KEY, GROQ_BASE_URL, IMAGE_INPUT_TYPES, IMAGE_READY,
    ARTIFACT_BY_KEY, ARTIFACT_CATEGORIES, DEFAULT_LANG_CODE, LANG_BY_CODE,
    SUPPORTED_LANGUAGES, course_curriculum, CLARIFY_OPTIONS,
)
from icons import mi
from logo import LOGO_B64
from state import (
    active_thread, artifact_thread, course_thread, get_settings, init_state,
    main_thread, next_msg_id, open_conversation, reset_conversation,
)
from sidebar import go, render_sidebar
from ui_helpers import (
    _BOTTOM_RESET_CSS, _FRESH_BOTTOM_CSS, _page_footer, get_greeting,
    logo_img_html, render_message,
)
from styles import inject_css
from chat_handlers import (
    process_user_input, render_input_controls, render_pending_preview,
    maybe_run_yuki,
)

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="Ampera Trinity AI",
    page_icon=(f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else "🔱"),
    layout="centered",
    initial_sidebar_state="expanded",
)


# ============================================================================
# HALAMAN: CHAT UTAMA
# ============================================================================
def render_chat_page() -> None:
    is_fresh = len(main_thread()) == 0

    if is_fresh:
        # ---------- HALAMAN AWAL ala Claude ----------
        st.markdown(_FRESH_BOTTOM_CSS, unsafe_allow_html=True)
        st.markdown(
            '<div class="trinity-greeting" style="margin-top:18vh;">'
            f'{logo_img_html("logo-greeting")} {get_greeting()}'
            "</div>",
            unsafe_allow_html=True,
        )

    for msg in main_thread():
        render_message(msg)

    pending_prompt = (st.session_state.pop("pending_prompt", "") or "").strip()

    if st.session_state.image_mode:
        placeholder_text = "Deskripsikan gambar yang ingin dibuat…"
    elif is_fresh:
        placeholder_text = "Apa yang bisa Yuki bantu hari ini?"
    else:
        placeholder_text = "Tulis pesan…"

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    # ====== URUTAN AREA INPUT ala Claude: preview lampiran di atas, lalu
    # kotak teks, lalu baris "+" & pilihan model di paling bawah. Urutan ini
    # ditentukan MURNI oleh urutan pemanggilan widget di sini (bukan CSS) —
    # st.chat_input() SENGAJA dipanggil di antara pending_preview dan
    # chat_controls, bukan sesudahnya. ======
    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="pending_preview"):
            render_pending_preview("chat")
        user_input = st.chat_input(placeholder_text, **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("chat", show_mode=True)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    if pending_prompt and user_input is None:
        user_input = pending_prompt
    if process_user_input(user_input, st.empty(), is_fresh=is_fresh):
        st.rerun()

    _page_footer(in_chat=not is_fresh)


# ============================================================================
# HALAMAN: ARTEFAK
# ============================================================================
def start_artifact_thread(key: str) -> None:
    cat = ARTIFACT_BY_KEY.get(key) or ARTIFACT_CATEGORIES[-1]
    st.session_state.artifact_counter += 1
    aid = st.session_state.artifact_counter
    now = now_wib()
    thread = artifact_thread(aid)
    thread.append({
        "id": next_msg_id(), "role": "user", "type": "text",
        "content": cat["brief"], "time": now, "meta": cat["title"],
        "awaiting_reply": True,
    })
    st.session_state.artifact_active_id = aid
    go("artefak")


def _artifact_grid(prefix: str) -> None:
    cats = ARTIFACT_CATEGORIES
    for i in range(0, len(cats), 3):
        cols = st.columns(3)
        for j, cat in enumerate(cats[i:i + 3]):
            with cols[j]:
                label = (f"{cat['icon']}  \n"
                         f"**{cat['title']}**  \n"
                         f":gray[{cat['desc']}]")
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
        f'{mi(":material/data_object:")}</div>'
        f'<div><h2 class="page-title">{html.escape(meta or "Artefak")}</h2>'
        '<p class="page-sub">Yuki mengerjakan artefak ini di halaman ini — '
        "chat utamamu tetap bersih.</p></div></div>",
        unsafe_allow_html=True,
    )

    if thread and thread[-1].get("awaiting_reply"):
        thread[-1].pop("awaiting_reply", None)
        from chat_handlers import handle_chat_request
        handle_chat_request(st.empty())
        st.rerun()

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    # ====== URUTAN AREA INPUT ala Claude (lihat catatan di render_chat_page)
    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="pending_preview"):
            render_pending_preview("artefak")
        user_input = st.chat_input("Jelaskan apa yang mau dibuat…", **chat_kwargs)
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
        f'{mi(":material/data_object:")}</div>'
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
# HALAMAN: PENGATURAN
# ============================================================================
def _opt_index(options: list, value) -> int:
    return options.index(value) if value in options else 0


THEME_OPTIONS = ["Beige hangat", "Gelap", "Ikut sistem"]
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
        mark = mi(":material/check_circle:") if ok else mi(":material/error_outline:")
        chip = "chip-on" if ok else "chip-off"
        rows.append(
            f'<div class="cap-row">'
            f'<span class="cap-icon">{mi(icon)}</span>'
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
        theme = st.selectbox("Tema", THEME_OPTIONS, index=_opt_index(THEME_OPTIONS, s["theme"]),
                             key="set_theme", help="Tema beige hangat adalah tampilan bawaan Trinity.")
    with c2:
        font = st.selectbox("Ukuran teks", FONT_OPTIONS, index=_opt_index(FONT_OPTIONS, s["font_size"]),
                            key="set_font")
    c3, c4 = st.columns(2)
    with c3:
        compact = st.toggle("Mode ringkas", value=s["compact_mode"], key="set_compact",
                            help="Jarak antar pesan dipersempit supaya lebih banyak terlihat.")
    with c4:
        speed = st.selectbox("Kecepatan aliran jawaban", SPEED_OPTIONS,
                             index=_opt_index(SPEED_OPTIONS, s["stream_speed"]), key="set_speed",
                             help="Seberapa cepat kalimat Yuki muncul satu per satu.")

        st.markdown('<div class="set-section">Perilaku Yuki</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        persona = st.selectbox("Kepribadian", PERSONA_OPTIONS,
                               index=_opt_index(PERSONA_OPTIONS, s["personality"]), key="set_persona")
        clarify = st.selectbox(
            "Bertanya balik saat permintaan kurang jelas", CLARIFY_OPTIONS,
            index=_opt_index(CLARIFY_OPTIONS, s.get("clarify_mode", "Seperlunya")),
            key="set_clarify",
            help="Mati: Yuki langsung mengerjakan dengan asumsi sendiri. "
                 "Seperlunya: bertanya hanya kalau permintaan benar-benar kabur. "
                 "Teliti: lebih sering memastikan detail penting dulu.",
        )
    with c6:
        min_think = st.slider("Durasi \"berpikir\" minimum (detik)", 0.0, 20.0,
                              float(s["min_think_seconds"]), 0.5, key="set_think",
                              help="Animasi berpikir ditahan minimal selama ini "
                                   "sebelum jawaban ditampilkan.")
    mode = st.radio("Mode bawaan saat membuka aplikasi", ["Chat", "Gambar"],
                    index=_opt_index(["Chat", "Gambar"], s["default_mode"]),
                    key="set_mode", horizontal=True)

    if st.button(":material/save:  Simpan perubahan", key="save_umum", type="primary"):
        _save_settings({
            "theme": theme, "font_size": font, "compact_mode": compact,
            "stream_speed": speed, "personality": persona,
            "clarify_mode": clarify,
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
            mark, cls = mi(":material/check_circle:"), "chip-on"
        else:
            mark, cls = (mi(":material/check_circle:"), "chip-on") if free else (
                mi(":material/remove_circle_outline:"), "chip-off")
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
    st.radio("Siklus penagihan", ["Bulanan", "Tahunan (hemat 20%)"],
             index=_opt_index(["Bulanan", "Tahunan (hemat 20%)"], s["billing_cycle"]),
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
                            index=_opt_index(REFL_FREQ_OPTIONS, s["reflection_freq"]),
                            key="refl_freq")
    with c2:
        tone = st.selectbox("Gaya dorongan", REFL_TONE_OPTIONS,
                            index=_opt_index(REFL_TONE_OPTIONS, s["reflection_tone"]),
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
        st.text_input("Waktu lokal sekarang", value=now_wib(),
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
    from config import MODEL_CATALOG
    s = get_settings()
    st.markdown('<div class="set-section">Kredensial layanan</div>', unsafe_allow_html=True)
    st.caption("Kosongkan bila pemilik aplikasi sudah mengisinya lewat "
               "Streamlit Secrets / environment variable.")
    gk = st.text_input("GROQ_API_KEY", type="password", value=s["groq_key"], key="set_gk",
                       help="Dipakai untuk chat, transkrip suara, dan vision.")
    ca = st.text_input("CF_ACCOUNT_ID", value=s["cf_account_id"], key="set_ca")
    ct = st.text_input("CF_API_TOKEN", type="password", value=s["cf_token"], key="set_ct")
    chat_state = (
        mi(":material/check_circle:") + " aktif" if CHAT_READY
        else mi(":material/error_outline:") + " butuh GROQ_API_KEY"
    )
    st.markdown(
        f'<div class="feat-row"><span>Status chat</span>'
        f'<span class="chip-{"on" if CHAT_READY else "off"}">'
        f"{chat_state}"
        "</span></div>",
        unsafe_allow_html=True,
    )
    img_state = (
        mi(":material/check_circle:") + " aktif" if IMAGE_READY
        else mi(":material/error_outline:") + " butuh Cloudflare"
    )
    st.markdown(
        f'<div class="feat-row"><span>Status generate gambar</span>'
        f'<span class="chip-{"on" if IMAGE_READY else "off"}">'
        f"{img_state}"
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
        f'<div class="page-head"><div class="page-head-icon">{mi(":material/settings:")}</div>'
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
        f'<div class="page-head"><div class="page-head-icon">{mi(":material/translate:")}</div>'
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
# HALAMAN: DAPATKAN BANTUAN
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
        f'<div class="page-head"><div class="page-head-icon">{mi(":material/help:")}</div>'
        '<div><h2 class="page-title">Dapatkan bantuan</h2>'
        "<p class=\"page-sub\">Petunjuk lengkap memakai Ampera Trinity AI, "
        "dari kirim pesan sampai membuat artefak.</p></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="set-section">Mulai cepat</div>', unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate(HELP_STEPS):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{mi(icon)}</span>'
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
# HALAMAN: PELAJARI LEBIH LANJUT
# ============================================================================
ABOUT_CARDS = [
    (":material/chat_bubble:", "Multi AI",
     "Pilih tingkat model Groq dari Easy sampai Extreme lewat nama model di "
     "kotak chat, lengkap dengan fallback otomatis bila satu model sedang "
     "tidak tersedia."),
    (":material/image:", "Generate Foto",
     "Nyalakan toggle Gambar lalu tulis deskripsi. Gambar dibuat dengan "
     "model FLUX di Cloudflare, ada progress bar bergaya Trinity."),
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
                    f'<div class="mini-card"><div class="mini-icon">{mi(icon)}</div>'
                    f'<div class="mini-title">{title}</div>'
                    f'<div class="mini-desc">{desc}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="set-section">Cara memakainya</div>', unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate(HELP_STEPS[:6]):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{mi(icon)}</span>'
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
# HALAMAN: TINGKATKAN PAKET
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
            f'<span class="step-icon">{mi(icon)}</span>'
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
            if st.button(":material/smartphone:  iOS", key="app_ios", use_container_width=True):
                st.toast("Versi iOS belum dirilis. Daftar beta di bawah ya!",
                         icon=":material/smartphone:")
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
# HALAMAN: TRINITY KURSUS
# ============================================================================
def _course_grid(prefix: str) -> None:
    for i in range(0, len(COURSE_CATALOG), 3):
        cols = st.columns(3)
        for j, c in enumerate(COURSE_CATALOG[i:i + 3]):
            with cols[j]:
                label = (f"{c['icon']}  \n"
                         f"**{c['title']}**  \n"
                         f":gray[{c['desc']} · {c['level']}]")
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
        f'<div class="page-head"><div class="page-head-icon">{mi(course["icon"])}</div>'
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

    if maybe_run_yuki(st.empty()):
        st.rerun()

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    # ====== URUTAN AREA INPUT ala Claude (lihat catatan di render_chat_page)
    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="pending_preview"):
            render_pending_preview(f"kursus_{key}")
        user_input = st.chat_input(f"Tanya apa saja tentang {course['title']}…", **chat_kwargs)
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
        f'<div class="page-head"><div class="page-head-icon">{mi(":material/school:")}</div>'
        '<div><h2 class="page-title">Trinity kursus</h2>'
        "<p class=\"page-sub\">Pilih fokus belajar. Yuki jadi mentor dan "
        "menjawab langsung di halaman kursus ini.</p></div></div>",
        unsafe_allow_html=True,
    )
    _course_grid("kurs")
    _page_footer()


# ============================================================================
# MAIN — pengalih halaman
# ============================================================================
def main() -> None:
    init_state()
    inject_css()

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
