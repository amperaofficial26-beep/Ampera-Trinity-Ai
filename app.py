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
  - pengaturan  → 8 tab: Umum · Akun · Privasi · Penagihan · Kemampuan ·
                  Memori · Refleksi · Waktu dan fokus
  - bahasa      → 14 bahasa (antarmuka + bahasa jawaban Yuki)
  - bantuan     → petunjuk detail pemakaian aplikasi + FAQ + kontak
  - tingkatkan  → promosi paket "Trinity Pro"
  - aplikasi    → rencana rilis aplikasi Android/iOS
  - kursus      → Trinity kursus (Yuki jadi mentor, thread sendiri)
  - pelajari    → tentang aplikasi + cara pakai + tips
"""

from __future__ import annotations

import base64
import html
import io
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

def now_wib() -> str:
    return datetime.now(WIB).strftime("%H:%M")

def _waktu_lokal(zona: str) -> str:
    """Jam saat ini menurut zona waktu terpilih (fallback: WIB)."""
    try:
        return datetime.now(ZoneInfo(zona)).strftime("%H:%M")
    except Exception:
        return now_wib()

import streamlit as st

from config import (
    CHAT_INPUT_SUPPORTS_AUDIO, CHAT_INPUT_SUPPORTS_FILE,
    CHAT_READY, COURSE_BY_KEY, COURSE_CATALOG,
    IMAGE_INPUT_TYPES, IMAGE_READY,
    MODEL_CATALOG,ARTIFACT_BY_KEY, ARTIFACT_CATEGORIES, DEFAULT_LANG_CODE, LANG_BY_CODE,
    SUPPORTED_LANGUAGES, course_curriculum, CLARIFY_OPTIONS,
    AMPERA_BRAND, AMPERA_EMAIL, AMPERA_LOKASI, AMPERA_PRODUK_LAIN, PRO_HARGA,
)

from icons import mi
from logo import LOGO_B64
from state import (
    active_thread, artifact_thread, course_thread, get_settings, init_state,
    main_thread, next_msg_id, open_conversation, reset_conversation,
)
from sidebar import go, go_cb, render_sidebar
from ui_helpers import (
    _BOTTOM_RESET_CSS, _FRESH_BOTTOM_CSS, _page_footer, get_greeting,
    logo_img_html, render_message,
)
from anim import inject_anim_css, inject_page_anim
from toast_anim import inject_toast_anim
from panel_file import render_file_dock          # ← BARIS BARU
from page_desain import page_desain
from page_jadwal import page_jadwal
from page_multi_agent import page_multi_agent
from styles import inject_css
from riwayat import dialog_bersihkan, tampilkan_toast_tertunda
from tampilan import (
    PALET_NAMES, WALLPAPER_NAMES, SUDUT_NAMES, DEFAULT_PALET,
    inject_tampilan, kartu_pratinjau, siapkan_wallpaper_unggahan,
    palet_aktif, _valid_hex,
)
from chat_handlers import (
    process_user_input, render_input_controls, render_pending_preview,
    maybe_run_yuki, fragmen_jawaban_yuki, chat_input_atau_hentikan,
    render_loader_yuki,
)

# Room chat Ampera = app Streamlit terpisah (repo ampera-official-group).
# Tombol "ke Room Chat Ampera" di halaman Tingkatkan mengarah ke sini;
# pesan user di room itu diteruskan ke inbox amperaofficialgroup@gmail.com.
ROOM_CHAT_URL = "https://room-chat-ampera-group.streamlit.app/"


def render_multi_agent_launcher() -> None:
    """Tombol Agent + kartu informasi animasi di samping sidebar."""

    # Di dalam room dan halaman chat utama, launcher disembunyikan agar
    # tidak menabrak topbar dashboard baru. Akses Multi AI tetap tersedia
    # dari sidebar dan panel fitur kanan.
    if st.session_state.get("page") in ("multi_agent", "chat"):
        return

    # _TAB_ICON sudah dipotong rapat dari margin transparan PNG.
    # Logo akan benar-benar berada di tengah tombol.
    logo_agent = _TAB_ICON
    st.markdown(
        """
        <style>
        :root {
          /*
           * Posisi saat sidebar terbuka dan tertutup.
           */
          --agent-launcher-open: 250px;
          --agent-launcher-closed: 58px;
        }


        /*
         * Mencegah position:fixed dihitung dari area tengah konten
         * ketika animasi halaman sedang berjalan.
         */
        [data-testid="stMainBlockContainer"]:has(
          .st-key-multi_agent_launcher
        ) {
          animation: none !important;
          transform: none !important;
        }


        /*
         * Pembungkus tombol dan kartu informasi.
         */
        .st-key-multi_agent_launcher {
          position: fixed !important;

          top: 14px !important;

          left:
            var(--agent-launcher-open) !important;

          width: 340px !important;

          margin: 0 !important;

          z-index: 1000000 !important;

          transition:
            left .24s
            cubic-bezier(.2, .8, .2, 1) !important;
        }


        /*
         * Posisi ketika sidebar ditutup.
         */
        .stApp:has(
          section[data-testid="stSidebar"][aria-expanded="false"]
        )
        .st-key-multi_agent_launcher {
          left:
            var(--agent-launcher-closed) !important;
        }


        /*
         * Susunan horizontal:
         *
         * [Tombol] [Informasi]
         */
        .st-key-multi_agent_launcher
        [data-testid="stHorizontalBlock"] {
          align-items: center !important;

          gap: 10px !important;

          flex-wrap: nowrap !important;
        }


        /*
         * Kolom tombol.
         */
        .st-key-multi_agent_launcher
        [data-testid="stColumn"]:first-child {
          width: 46px !important;
          min-width: 46px !important;

          flex:
            0
            0
            46px !important;
        }


        /*
         * Kolom informasi.
         */
        .st-key-multi_agent_launcher
        [data-testid="stColumn"]:last-child {
          min-width: 0 !important;

          flex:
            1
            1
            auto !important;
        }


        /*
         * Tombol Multi Trinity Agent.
         */
        .st-key-multi_agent_launcher button {
          position: relative !important;
        
          width: 46px !important;
          height: 46px !important;
          min-height: 46px !important;
        
          padding: 0 !important;
        
          overflow: hidden !important;
        
          border-radius: 50% !important;
        
          color: #2d2115 !important;
        
          background:
            linear-gradient(
              145deg,
              #f3d47d,
              #bd8125
            ) !important;
        
          border:
            1px solid
            rgba(255, 226, 151, .8) !important;
        
          box-shadow:
            0 7px 18px rgba(66, 43, 16, .25),
            0 0 18px rgba(218, 166, 55, .38) !important;
        
          /*
           * Menyembunyikan teks ✦.
           * Logo akan dibuat melalui ::before.
           */
          font-size: 0 !important;
        }
        /*
         * Sembunyikan label ✦ bawaan st.button.
         * Logo Trinity dari button::before tetap ditampilkan.
         */
        .st-key-multi_agent_launcher button p,
        .st-key-multi_agent_launcher
        button [data-testid="stMarkdownContainer"] {
          display: none !important;
        }
        
        /* Logo Trinity asli. */
        .st-key-multi_agent_launcher button::before {
          content: "";
        
          position: absolute;
        
          /*
           * Logo mengisi tombol dengan jarak 5px pada setiap sisi.
           * Karena menggunakan position:absolute, posisinya tidak
           * dipengaruhi label tombol yang disembunyikan.
           */
          inset: 5px;
        
          display: block;
        
          z-index: 1;
        
          background:
            url("__AGENT_LOGO__")
            center
            /
            contain
            no-repeat;
        
          filter:
            drop-shadow(
              0
              0
              6px
              rgba(218, 166, 55, .58)
            );
        }
        
        /* Cahaya yang menyapu logo dari kanan ke kiri. */
        .st-key-multi_agent_launcher button::after {
          content: "";
        
          position: absolute;
        
          inset:
            -30%
            -45%;
        
          background:
            linear-gradient(
              90deg,
              transparent,
              rgba(255, 248, 206, .78),
              transparent
            );
        
          transform:
            translateX(100%)
            rotate(-18deg);
        
          animation:
            agentLogoSweep
            2.8s
            ease-in-out
            infinite;
        }
        
        
        /* Arah sapuan: kanan ke kiri. */
        @keyframes agentLogoSweep {
          0%,
          35% {
            transform:
              translateX(100%)
              rotate(-18deg);
          }
        
          72%,
          100% {
            transform:
              translateX(-100%)
              rotate(-18deg);
          }
        }
        
        
        .st-key-multi_agent_launcher button:hover {
          transform:
            translateY(-2px)
            scale(1.04);
        }

        /*
         * Kartu informasi.
         */
        .agent-launch-info {
          position: relative;

          box-sizing: border-box;

          height: 46px;

          padding:
            7px
            14px
            6px
            34px;

          overflow: hidden;

          border:
            1px solid
            color-mix(
              in srgb,
              var(--tr-accent) 25%,
              var(--tr-border)
            );

          border-radius: 14px;

          background:
            color-mix(
              in srgb,
              var(--tr-surface) 94%,
              white 6%
            );

          box-shadow:
            0 6px 18px
            rgba(44, 31, 51, .09);

          color:
            var(--tr-text);
        }


        /*
         * Bintang kecil pada kartu informasi.
         */
        .agent-launch-info::before {
          content: "✦";

          position: absolute;

          left: 12px;
          top: 13px;

          color: #bd8125;

          animation:
            agentInfoStar
            1.8s
            ease-in-out
            infinite;
        }


        /*
         * Setiap informasi ditumpuk di posisi yang sama.
         * CSS animation menentukan informasi mana yang terlihat.
         */
        .agent-info-line {
          position: absolute;

          left: 34px;
          right: 10px;
          top: 6px;

          opacity: 0;

          transform:
            translateY(8px);

          animation:
            agentInfoRotate
            12s
            ease-in-out
            infinite;
        }


        /*
         * Informasi kedua muncul setelah tiga detik.
         */
        .agent-info-line:nth-child(2) {
          animation-delay: 3s;
        }


        /*
         * Informasi ketiga muncul setelah enam detik.
         */
        .agent-info-line:nth-child(3) {
          animation-delay: 6s;
        }


        /*
         * Informasi keempat muncul setelah sembilan detik.
         */
        .agent-info-line:nth-child(4) {
          animation-delay: 9s;
        }


        /*
         * Judul informasi.
         */
        .agent-info-line b {
          display: block;

          color:
            var(--tr-text);

          font-size: 11.5px;
          line-height: 1.25;
        }


        /*
         * Keterangan informasi.
         */
        .agent-info-line small {
          display: block;

          color:
            var(--tr-text2);

          font-size: 9.5px;
          line-height: 1.3;

          white-space: nowrap;

          overflow: hidden;

          text-overflow: ellipsis;
        }


        /*
         * Informasi masuk dari bawah, diam, lalu keluar ke atas.
         */
        @keyframes agentInfoRotate {
          0% {
            opacity: 0;

            transform:
              translateY(8px);
          }

          5%,
          20% {
            opacity: 1;

            transform:
              translateY(0);
          }

          25%,
          100% {
            opacity: 0;

            transform:
              translateY(-7px);
          }
        }


        /*
         * Bintang kecil berputar dan menyala.
         */
        @keyframes agentInfoStar {
          50% {
            transform:
              rotate(180deg)
              scale(1.2);

            filter:
              drop-shadow(
                0
                0
                5px
                #d9a637
              );
          }
        }


        /*
         * Di layar HP hanya tampilkan tombol.
         * Kartu informasi disembunyikan supaya tidak menutupi layar.
         */
        @media (max-width: 760px) {
          .st-key-multi_agent_launcher {
            left: auto !important;
            right: 66px !important;
            top: 10px !important;

            width: 46px !important;
          }

          .st-key-multi_agent_launcher
          [data-testid="stColumn"]:last-child {
            display: none !important;
          }
        }
        </style>
        """.replace(
            "__AGENT_LOGO__",
            logo_agent,
        ),
        unsafe_allow_html=True,
    )

    with st.container(
        key="multi_agent_launcher"
    ):
        tombol, info = st.columns(
            [46, 284],
            gap="small",
        )

        with tombol:
            buka = st.button(
                "✦",
                key="open_multi_agent",
                help="Multi Trinity Agent · Pro",
            )

        with info:
            st.markdown(
                '<div class="agent-launch-info">'

                '<div class="agent-info-line">'
                '<b>Multi Trinity Agent</b>'
                '<small>'
                'Semua model, satu jawaban profesional'
                '</small>'
                '</div>'

                '<div class="agent-info-line">'
                '<b>Analisis berlapis</b>'
                '<small>'
                'Jawaban diperiksa dari banyak sudut'
                '</small>'
                '</div>'

                '<div class="agent-info-line">'
                '<b>Khusus Trinity Pro</b>'
                '<small>'
                'Panel AI premium bekerja bersama'
                '</small>'
                '</div>'

                '<div class="agent-info-line">'
                '<b>Lebih teliti</b>'
                '<small>'
                'Menilai solusi, risiko, dan saran lanjutan'
                '</small>'
                '</div>'

                '</div>',
                unsafe_allow_html=True,
            )

        if buka:
            from chat_handlers import (
                _boleh_premium,
                _dialog_premium,
            )

            if _boleh_premium():
                go("multi_agent")
            else:
                _dialog_premium()
# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
# Ikon tab (favicon) = logo_thinking_small.png yang otomatis di-CROP saat
# aplikasi jalan: margin transparannya dibuang supaya ikon tampil sebesar
# mungkin di tab browser. Kalau Pillow / file logonya tidak ada, kembali ke
# logo biasa (LOGO_B64) lalu emoji — aplikasi tetap jalan.
try:
    from PIL import Image as _PILImage
except ImportError:                        # Pillow ada di requirements.txt,
    _PILImage = None                       # ini cuma jaga-jaga.


@st.cache_data
def _buat_ikon_tab() -> str | None:
    """Ikon tab versi persegi rapat (tanpa margin transparan)."""
    if _PILImage is None:
        return None
    try:
        img = _PILImage.open("assets/logo_thinking_small.png").convert("RGBA")
        bbox = img.getchannel("A").getbbox()
        if not bbox:
            return None
        potong = img.crop(bbox)                  # buang margin transparan
        sisi = max(potong.size)
        bantalan = round(sisi * 0.03)            # tepi tipis biar tidak nempel
        kanvas = sisi + 2 * bantalan
        persegi = _PILImage.new("RGBA", (kanvas, kanvas), (0, 0, 0, 0))
        persegi.paste(potong, ((kanvas - potong.width) // 2,
                               (kanvas - potong.height) // 2), potong)
        buf = io.BytesIO()
        persegi.resize((256, 256),
                       _PILImage.Resampling.LANCZOS).save(buf, "PNG", optimize=True)
        return ("data:image/png;base64,"
                + base64.b64encode(buf.getvalue()).decode("ascii"))
    except Exception:
        return None


_TAB_ICON = _buat_ikon_tab() or (
    f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else "🔱")

st.set_page_config(
    page_title="Ampera Trinity AI",
    page_icon=_TAB_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

def _clip_text(value: str, limit: int = 46) -> str:
    """Potong teks untuk panel ringkas tanpa memecah layout."""
    value = (value or "").strip()
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "…"


def _render_chat_chrome(is_fresh: bool) -> None:
    """Topbar dashboard chat seperti referensi, tetap memakai tema app.

    Elemen ini sengaja tidak memakai gambar baru: avatar aplikasi dibuat dari
    huruf "T" berbasis CSS, dan seluruh warna mengambil variabel tema
    (var(--tr-*)).
    """
    s = get_settings()
    display_name = (s.get("display_name") or "User").strip() or "User"
    plan = (s.get("plan") or "Free").strip() or "Free"
    initial = html.escape(display_name[:1].upper() or "U")

    mode_title = "Generate Gambar" if st.session_state.get("image_mode") else "AI Assistant"
    mode_hint = (
        "Deskripsikan gambar yang ingin dibuat…"
        if st.session_state.get("image_mode")
        else "Tanyakan apa saja, kami siap membantumu…"
    )
    marker_class = "tr-chat-layout tr-fresh-home" if is_fresh else "tr-chat-layout"

    st.markdown(
        f"""
        <div class="{marker_class}"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="chat_topbar"):
        brand_col, status_col, user_col, out_col = st.columns(
            [1.15, 2.85, 1.05, 0.82],
            gap="small",
        )

        with brand_col:
            st.markdown(
                """
                <div class="tr-brand-profile">
                  <div class="tr-brand-avatar">T</div>
                  <div class="tr-brand-copy">
                    <div class="tr-brand-name">Trinity</div>
                    <div class="tr-brand-sub">Room Chat AI</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with status_col:
            st.markdown(
                (
                    '<div class="tr-assistant-pill">'
                    f'<div class="tr-pill-icon">{mi(":material/support_agent:")}</div>'
                    '<div class="tr-pill-copy">'
                    f'<div class="tr-pill-title">{html.escape(mode_title)}</div>'
                    f'<div class="tr-pill-sub">{html.escape(mode_hint)}</div>'
                    '</div></div>'
                ),
                unsafe_allow_html=True,
            )

        with user_col:
            st.markdown(
                (
                    '<div class="tr-user-pill">'
                    f'<span class="tr-user-avatar">{initial}</span>'
                    '<span class="tr-user-copy">'
                    f'<b>{html.escape(_clip_text(display_name, 18))}</b>'
                    f'<small>{html.escape(plan)}</small>'
                    '</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        with out_col:
            if st.button(
                ":material/logout:  Keluar",
                key="top_logout",
                use_container_width=True,
            ):
                st.session_state.logged_out = True
                go("chat")


def _render_chat_right_rail() -> None:
    """Panel fitur kanan untuk chat utama.

    Semua kontrol tetap memakai fitur yang sudah ada, tanpa gambar baru.
    """
    with st.container(key="chat_right_rail"):
        st.markdown(
            '<div class="tr-rail-title-row"><span>Fitur Cepat</span></div>',
            unsafe_allow_html=True,
        )

        q1, q2 = st.columns(2, gap="small")

        with q1:
            with st.container(key="rail_quick_chat"):
                if st.button(
                    ":material/chat_bubble:  \n**Chat AI**  \n:gray[Tanya apa saja]",
                    key="rail_btn_chat",
                    use_container_width=True,
                ):
                    st.session_state.image_mode = False
                    go("chat")

            with st.container(key="rail_quick_image"):
                if st.button(
                    ":material/image:  \n**Generate Gambar**  \n:gray[Buat visual cepat]",
                    key="rail_btn_image",
                    use_container_width=True,
                ):
                    st.session_state.image_mode = True
                    go("chat")

        with q2:
            with st.container(key="rail_quick_multi"):
                if st.button(
                    ":material/groups:  \n**Multi AI**  \n:gray[Room agent]",
                    key="rail_btn_multi",
                    use_container_width=True,
                ):
                    go("multi_agent")

            with st.container(key="rail_quick_upload"):
                if st.button(
                    ":material/upload_file:  \n**Upload File**  \n:gray[Pakai tombol +]",
                    key="rail_btn_upload",
                    use_container_width=True,
                ):
                    st.toast(
                        "Upload file tersedia lewat tombol + di kotak chat.",
                        icon=":material/attach_file:",
                    )

        st.markdown(
            '<div class="tr-rail-title-row with-link"><span>Model AI Populer</span>'
            '<small>Pilih</small></div>',
            unsafe_allow_html=True,
        )

        popular_models = [
            m for m in MODEL_CATALOG
            if m.get("chat_selectable", True) and not m.get("premium")
        ][:4]

        for m in popular_models:
            row_key = f"rail_model_{m['key']}"
            active = m.get("key") == st.session_state.get("selected_model_key")

            with st.container(key=row_key):
                if st.button(
                    f"**{m['name']}**  \n:gray[{_clip_text(m.get('desc', ''), 36)}]",
                    key=f"rail_btn_model_{m['key']}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    st.session_state.selected_model_key = m["key"]
                    st.toast(f"Model dipilih: {m['name']}", icon=":material/check_circle:")
                    st.rerun()

        st.markdown(
            '<div class="tr-rail-title-row with-link"><span>Chat Terbaru</span>'
            '<small>Riwayat</small></div>',
            unsafe_allow_html=True,
        )

        convs = st.session_state.get("conversations", [])[:3]

        if not convs:
            st.markdown(
                '<div class="tr-rail-empty">Belum ada chat terbaru.</div>',
                unsafe_allow_html=True,
            )

        for c in convs:
            title = _clip_text(c.get("title") or "Chat baru", 30)
            meta = c.get("time") or c.get("updated") or "Terbaru"
            cid = c.get("id")

            with st.container(key=f"rail_recent_{cid}"):
                if st.button(
                    f":material/forum:  **{title}**  \n:gray[{_clip_text(str(meta), 28)}]",
                    key=f"rail_btn_recent_{cid}",
                    use_container_width=True,
                ):
                    open_conversation(cid)
                    st.rerun()


# ============================================================================
# HALAMAN: CHAT UTAMA
# ============================================================================
def render_chat_page() -> None:
    is_fresh = len(main_thread()) == 0

    _render_chat_chrome(is_fresh)
    _render_chat_right_rail()

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
        user_input = chat_input_atau_hentikan(placeholder_text, **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("chat", show_mode=True)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    # Jawaban yang sedang mengalir + animasi berpikir + tombol Hentikan.
    fragmen_jawaban_yuki()
    render_loader_yuki()

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

    # Jawaban yang sedang mengalir + animasi berpikir + tombol Hentikan.
    fragmen_jawaban_yuki()
    render_loader_yuki()

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
        user_input = chat_input_atau_hentikan("Jelaskan apa yang mau dibuat…", **chat_kwargs)
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

    # Import lokal menjaga fungsi selalu tersedia saat callback dijalankan,
    # termasuk setelah hot-reload Streamlit memakai modul app versi lama.
    from toast_anim import toast_sukses
    toast_sukses(label)


def _baris_aksi_simpan(label: str, key: str, patch: dict, toast: str,
                       sekunder: tuple[str, str, object] | None = None) -> None:
    """Baris aksi seragam di dasar setiap tab Pengaturan & halaman Bahasa:
    tombol utama "Simpan" rata kanan, plus satu tombol sekunder opsional
    (mis. "Uji koneksi") persis di sampingnya — jadi semua tab seragam."""
    _, kiri, kanan = st.columns([2, 1, 1])
    if sekunder:
        label2, key2, fn2 = sekunder
        with kiri:
            if st.button(label2, key=key2, use_container_width=True):
                fn2()
    with kanan:
        if st.button(f":material/save:  {label}", key=key, type="primary",
                     use_container_width=True):
            _save_settings(patch, toast)
            st.rerun()


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
    # Catatan: pemilih "Tema" yang dulu ada di sini sudah dipindah ke tab
    # "Tampilan" (tampilan.py) yang benar-benar mengubah warna aplikasi.
    # Selectbox lama hanya menyimpan nilai tanpa efek apa pun.
    st.markdown('<div class="set-section">Tampilan</div>', unsafe_allow_html=True)
    st.caption(
        "Wallpaper dan warna aplikasi diatur di tab **Tampilan**."
    )
    c2, c3 = st.columns(2)
    with c2:
        font = st.selectbox("Ukuran teks", FONT_OPTIONS, index=_opt_index(FONT_OPTIONS, s["font_size"]),
                            key="set_font")
    with c3:
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
    mode = st.radio("Mode bawaan saat membuka aplikasi", ["Chat", "Gambar"],
                    index=_opt_index(["Chat", "Gambar"], s["default_mode"]),
                    key="set_mode", horizontal=True)

    _baris_aksi_simpan(
        "Simpan perubahan", "save_umum",
        {
            "font_size": font,
            "stream_speed": speed, "personality": persona,
            "clarify_mode": clarify,
            "default_mode": mode,
        },
        "Pengaturan umum disimpan.",
    )

def _set_tampilan() -> None:
    """Tab Pengaturan > Tampilan: wallpaper & warna pilihan User.

    Pratinjau diperbarui LANGSUNG saat pilihan diubah (tanpa menekan
    Simpan) karena widget-nya dibaca dari nilai balik, bukan dari
    settings. Yang tersimpan permanen tetap lewat tombol Simpan.
    """
    s = get_settings()

    st.markdown('<div class="set-section">Warna</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        palet = st.selectbox(
            "Tema warna", PALET_NAMES,
            index=_opt_index(PALET_NAMES, s.get("ui_palet", DEFAULT_PALET)),
            key="set_ui_palet",
            help="Mengubah warna latar, kartu, sidebar, dan teks di seluruh aplikasi.",
        )
    with c2:
        sudut = st.selectbox(
            "Kelengkungan sudut", SUDUT_NAMES,
            index=_opt_index(SUDUT_NAMES, s.get("ui_sudut", "Sedang")),
            key="set_ui_sudut",
            help="Seberapa bulat sudut kartu, gelembung pesan, dan tombol.",
        )

    pakai_aksen = st.checkbox(
        "Pakai warna aksen sendiri", value=bool(s.get("ui_accent_custom")),
        key="set_ui_aksen_on",
        help="Warna tombol utama, tautan, dan tab aktif.",
    )
    if pakai_aksen:
        aksen = st.color_picker(
            "Warna aksen",
            value=(s.get("ui_accent_custom") or palet_aktif(s)["accent"]),
            key="set_ui_aksen",
        )
    else:
        aksen = ""

    st.markdown('<div class="set-section">Wallpaper</div>', unsafe_allow_html=True)
    wp = st.selectbox(
        "Pola latar belakang", WALLPAPER_NAMES,
        index=_opt_index(WALLPAPER_NAMES, s.get("ui_wallpaper", "Polos")),
        key="set_ui_wp",
        help="Pola dibuat dari CSS, jadi ringan dan tidak menambah waktu muat.",
    )

    berkas = st.file_uploader(
        "Atau unggah gambar sendiri (JPG/PNG)",
        type=["jpg", "jpeg", "png", "webp"], key="set_ui_wp_file",
        help="Gambar unggahan menimpa pilihan pola di atas. "
             "Otomatis dikecilkan maks 1920px agar aplikasi tetap ringan.",
    )

    wp_custom = s.get("ui_wallpaper_custom") or ""
    if berkas is not None:
        try:
            wp_custom = siapkan_wallpaper_unggahan(berkas.getvalue())
        except Exception:
            st.warning("Gambar tidak bisa dibaca. Coba berkas lain.")

    if wp_custom:
        k1, k2 = st.columns([3, 1])
        with k1:
            st.caption("Gambar wallpaper sedang dipakai.")
        with k2:
            if st.button("Hapus gambar", key="set_ui_wp_hapus",
                         use_container_width=True):
                _save_settings({"ui_wallpaper_custom": ""}, "Wallpaper gambar dihapus.")
                st.rerun()

    c3, c4 = st.columns(2)
    with c3:
        opac = st.slider(
            "Kepekatan wallpaper", 0, 100,
            value=int(s.get("ui_wallpaper_opacity", 100)), step=5,
            key="set_ui_wp_opac",
            help="Turunkan kalau wallpaper membuat teks susah dibaca.",
        )
    with c4:
        blur = st.slider(
            "Buram", 0, 20, value=int(s.get("ui_wallpaper_blur", 0)),
            key="set_ui_wp_blur",
            help="Berguna untuk foto unggahan supaya teks tetap jelas terbaca.",
        )

    # Pratinjau memakai pilihan SAAT INI, bukan yang tersimpan.
    pratinjau = dict(s)
    pratinjau.update({
        "ui_palet": palet, "ui_sudut": sudut,
        "ui_accent_custom": aksen if (pakai_aksen and _valid_hex(aksen)) else "",
        "ui_wallpaper": wp, "ui_wallpaper_custom": wp_custom,
        "ui_wallpaper_opacity": opac, "ui_wallpaper_blur": blur,
    })
    st.markdown('<div class="set-section">Pratinjau</div>', unsafe_allow_html=True)
    st.markdown(kartu_pratinjau(pratinjau), unsafe_allow_html=True)
    st.caption("Tekan Simpan untuk menerapkan ke seluruh aplikasi.")

    def _reset() -> None:
        _save_settings({
            "ui_palet": DEFAULT_PALET, "ui_sudut": "Sedang",
            "ui_accent_custom": "", "ui_wallpaper": "Polos",
            "ui_wallpaper_custom": "", "ui_wallpaper_opacity": 100,
            "ui_wallpaper_blur": 0,
        }, "Tampilan dikembalikan ke bawaan.")
        st.rerun()

    _baris_aksi_simpan(
        "Simpan perubahan", "save_tampilan",
        {
            "ui_palet": palet, "ui_sudut": sudut,
            "ui_accent_custom": aksen if (pakai_aksen and _valid_hex(aksen)) else "",
            "ui_wallpaper": wp, "ui_wallpaper_custom": wp_custom,
            "ui_wallpaper_opacity": opac, "ui_wallpaper_blur": blur,
        },
        "Tampilan disimpan.",
        sekunder=("Kembalikan ke bawaan", "reset_tampilan", _reset),
    )


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
        pilihan_wilayah = ["Indonesia", "Malaysia", "Singapura", "Lainnya"]
        region = st.selectbox(
            "Wilayah", pilihan_wilayah,
            index=pilihan_wilayah.index(s.get("region")) if s.get("region") in pilihan_wilayah else 0,
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

    _baris_aksi_simpan(
        "Simpan profil", "save_akun",
        {"display_name": name.strip() or "User", "username": uname.strip(),
         "email": email.strip(), "bio": bio.strip(), "region": region},
        "Profil disimpan.",
    )


def _set_privasi() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Data &amp; percakapan</div>',
                unsafe_allow_html=True)
    st.toggle("Simpan riwayat percakapan di perangkat ini", value=s["save_history"],
              key="set_hist")
    st.toggle("Simpan rekaman suara setelah ditranskrip", value=s["keep_voice"],
              key="set_voice")

    st.markdown('<div class="set-section">Personalisasi</div>', unsafe_allow_html=True)
    st.toggle("Kirim data pemakaian anonim untuk perbaikan aplikasi",
              value=s["analytics"], key="set_analytics")
    st.toggle("Gunakan memoriku untuk jawaban yang lebih personal",
              value=s["personalization"], key="set_personal")

    _baris_aksi_simpan(
        "Simpan privasi", "save_privasi",
        {
            "save_history": st.session_state.set_hist,
            "keep_voice": st.session_state.set_voice,
            "analytics": st.session_state.set_analytics,
            "personalization": st.session_state.set_personal,
        },
        "Pengaturan privasi disimpan.",
    )

    st.markdown('<div class="set-section">Riwayat obrolan</div>',
                unsafe_allow_html=True)
    st.caption(
        "Menghapus riwayat hanya mengosongkan percakapan. Pengaturan, "
        "memori, dan tampilan tetap tersimpan."
    )
    dialog_bersihkan("set")

    st.markdown('<div class="set-section danger">Hapus data</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="danger-box">Menghapus seluruh data akan mengosongkan '
        "percakapan, artefak, memori, dan pengaturan. Tindakan ini tidak bisa "
        "dibatalkan.</div>",
        unsafe_allow_html=True,
    )
    # Konfirmasi dua langkah: tombol ini menghapus SEMUANYA (termasuk
    # pengaturan & tampilan), jadi tidak boleh jalan hanya karena satu
    # klik tak sengaja.
    if not st.session_state.get("_wipe_tahap"):
        _, kolom_hapus = st.columns([3, 1])
        with kolom_hapus:
            if st.button(":material/delete_forever:  Hapus seluruh data saya",
                         key="wipe_data", use_container_width=True):
                st.session_state["_wipe_tahap"] = True
                st.rerun()
    else:
        st.error(
            "Seluruh data akan dihapus: percakapan, artefak, memori, "
            "pengaturan, dan tampilan kembali ke bawaan.",
            icon=":material/warning:",
        )
        w1, w2 = st.columns(2)
        with w1:
            if st.button("Batal", key="wipe_batal", use_container_width=True):
                st.session_state.pop("_wipe_tahap", None)
                st.rerun()
        with w2:
            if st.button(":material/delete_forever:  Ya, hapus semua",
                         key="wipe_ya", type="primary",
                         use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.session_state.page = "chat"
                st.session_state["_toast_riwayat"] = "Seluruh data dihapus."
                st.rerun()


PRO_FEATURES = [
    ("Model premium tertinggi tanpa batas", True, False),
    ("Generate gambar resolusi tinggi", True, False),
    ("Memori jangka panjang tak terbatas", True, False),
    ("Artefak penuh tanpa batas", True, False),
    ("Trinity kursus lengkap + mentor Yuki", True, False),
    ("Refleksi harian otomatis", True, False),
    ("Akses lebih awal fitur baru", True, False),
    ("Dukungan prioritas", True, False),
]


def _harga_col(paket: dict, key: str) -> None:
    st.markdown(
        f'<div class="plan-card{" is-pro" if paket.get("unggul") else ""}">'
        f'<div class="plan-name">{html.escape(paket["nama"])}</div>'
        f'<div class="plan-price">{html.escape(paket["harga"])}</div>'
        f'<div class="plan-note">{html.escape(paket["satuan"])} · '
        f'{html.escape(paket["catatan"])}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button(":material/workspace_premium:  Pilih paket ini", key=key,
                 use_container_width=True,
                 type="primary" if paket.get("unggul") else "secondary"):
        st.toast(
            "Untuk berlangganan, tekan tombol ke Room Chat Ampera "
            "di bagian bawah halaman ini 👇",
            icon=":material/forum:",
        )


def _set_penagihan() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Siklus &amp; pembayaran</div>',
                unsafe_allow_html=True)
    opsi_siklus = [f"{p['nama']} — {p['harga']}" for p in PRO_HARGA]
    st.radio("Siklus penagihan", opsi_siklus,
             index=_opt_index(opsi_siklus, s.get("billing_cycle")),
             key="set_cycle", horizontal=True)
    _, kolom_bayar = st.columns([3, 1])
    with kolom_bayar:
        if st.button(":material/credit_card:  Atur pembayaran", key="bayar_metode",
                     use_container_width=True):
            st.toast(
                f"Untuk berlangganan Trinity Pro, hubungi Ampera Official "
                f"lewat email: {AMPERA_EMAIL}",
                icon=":material/mail:",
            )
    st.markdown(
        f'<div class="feat-row"><span>Info berlangganan</span>'
        f'<span class="chip-off">{html.escape(AMPERA_EMAIL)}</span></div>',
        unsafe_allow_html=True,
    )

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

    _baris_aksi_simpan(
        "Simpan penagihan", "save_tagih",
        {"billing_cycle": st.session_state.set_cycle},
        "Penagihan disimpan.",
    )


def _set_kemampuan() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Status kemampuan</div>', unsafe_allow_html=True)
    st.markdown(_cap_rows_html(), unsafe_allow_html=True)
    st.caption("Kemampuan bertanda \"butuh …\" hanya menunggu kredensial diisi "
               "pemilik aplikasi lewat Streamlit Secrets / environment variable.")

    st.markdown('<div class="set-section">Nyalakan / matikan</div>', unsafe_allow_html=True)
    st.toggle("Pencarian web", value=s["cap_web_search"], key="cap_web",
              help="Bila mati, toggle pencarian web di kotak chat diabaikan.")
    st.toggle("Transkrip suara", value=s["cap_voice"], key="cap_voice_t")
    st.toggle("Analisis gambar (Vision)", value=s["cap_vision"], key="cap_vision_t")
    st.toggle("Generate gambar", value=s["cap_image"], key="cap_image_t")
    st.toggle("Tangkap artefak otomatis", value=s["cap_artifacts"], key="cap_art_t")

    _baris_aksi_simpan(
        "Simpan kemampuan", "save_kemampuan",
        {
            "cap_web_search": st.session_state.cap_web,
            "cap_voice": st.session_state.cap_voice_t,
            "cap_vision": st.session_state.cap_vision_t,
            "cap_image": st.session_state.cap_image_t,
            "cap_artifacts": st.session_state.cap_art_t,
        },
        "Kemampuan disimpan.",
    )


def _set_memori() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Kemampuan memori</div>', unsafe_allow_html=True)
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

    st.text_input("Tambah memori baru", key="mem_new",
                  placeholder="mis. Aku lebih suka jawaban singkat & pakai tabel")

    def _tambah_memori() -> None:
        baru = (st.session_state.get("mem_new") or "").strip()
        if baru:
            merged = dict(st.session_state.get("settings") or {})
            merged["memories"] = facts + [baru]
            st.session_state.settings = merged
            toast_sukses("Memori ditambahkan.")
            st.rerun()

    _baris_aksi_simpan(
        "Simpan memori", "mem_save",
        {"memory_on": st.session_state.mem_on,
         "memory_auto": st.session_state.mem_auto},
        "Pengaturan memori disimpan.",
        sekunder=(":material/add:  Tambah memori", "mem_add", _tambah_memori),
    )


def _set_refleksi() -> None:
    s = get_settings()
    st.markdown('<div class="set-section">Target &amp; kebiasaan</div>',
                unsafe_allow_html=True)
    goal = st.text_area("Target yang sedang kamu kejar", value=s["reflection_goal"],
                        key="refl_goal", height=90,
                        placeholder="mis. Menambah 20 pelanggan baru bulan ini")
    habit = st.text_area("Kebiasaan yang ingin dibangun", value=s["reflection_habit"],
                         key="refl_habit", height=90,
                         placeholder="mis. Menulis konten setiap pagi 15 menit")
    st.markdown('<div class="set-section">Gaya refleksi</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        freq = st.selectbox("Yuki menanyakan progres", REFL_FREQ_OPTIONS,
                            index=_opt_index(REFL_FREQ_OPTIONS, s["reflection_freq"]),
                            key="refl_freq")
    with c2:
        tone = st.selectbox("Gaya dorongan", REFL_TONE_OPTIONS,
                            index=_opt_index(REFL_TONE_OPTIONS, s["reflection_tone"]),
                            key="refl_tone")

    def _minta_refleksi() -> None:
        go("chat")
        st.session_state.pending_prompt = (
            "Ajak aku refleksi singkat: tanyakan progres targetku, "
            "hambatan hari ini, dan satu langkah kecil untuk besok."
        )

    _baris_aksi_simpan(
        "Simpan refleksi", "save_refl",
        {"reflection_goal": goal.strip(),
         "reflection_habit": habit.strip(),
         "reflection_freq": freq, "reflection_tone": tone},
        "Refleksi disimpan.",
        sekunder=(":material/self_improvement:  Minta refleksi sekarang",
                  "refl_now", _minta_refleksi),
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
    c4, c5 = st.columns(2)
    with c4:
        start = st.text_input("Mulai", value=s["work_start"], key="set_start")
    with c5:
        end = st.text_input("Selesai", value=s["work_end"], key="set_end")
    zona = (st.session_state.get("set_tz") or s["tz_label"]).split(" (")[0]
    st.caption(f"⏰ Waktu lokal sekarang: **{_waktu_lokal(zona)}** ({zona}). "
               "Zona waktu bisa diganti di bagian Sesi fokus di atas.")

    remind = st.toggle("Ingatkan aku saat jam fokus selesai", value=s["focus_reminder"],
                       key="set_remind")

    _baris_aksi_simpan(
        "Simpan waktu & fokus", "save_fokus",
        {"focus_minutes": int(focus), "break_minutes": int(brk),
         "work_start": start, "work_end": end,
         "tz_label": st.session_state.set_tz,
         "focus_reminder": remind},
        "Waktu & fokus disimpan.",
    )


def page_pengaturan() -> None:
    
    st.markdown(
        f'<div class="page-head"><div class="page-head-icon">{mi(":material/settings:")}</div>'
        '<div><h2 class="page-title">Pengaturan</h2>'
        "<p class=\"page-sub\">Delapan bagian pengaturan Trinity. Perubahan "
        "disimpan per bagian lewat tombol simpan.</p></div></div>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        ":material/tune:  Umum",
        ":material/palette:  Tampilan",
        ":material/person:  Akun",
        ":material/shield:  Privasi",
        ":material/receipt_long:  Penagihan",
        ":material/bolt:  Kemampuan",
        ":material/history_edu:  Memori",
        ":material/self_improvement:  Refleksi",
        ":material/schedule:  Waktu dan fokus",
    ])
    with tabs[0]:
        _set_umum()
    with tabs[1]:
        _set_tampilan()
    with tabs[2]:
        _set_akun()
    with tabs[3]:
        _set_privasi()
    with tabs[4]:
        _set_penagihan()
    with tabs[5]:
        _set_kemampuan()
    with tabs[6]:
        _set_memori()
    with tabs[7]:
        _set_refleksi()
    with tabs[8]:
        _set_waktu_fokus()

    _page_footer()
  # ============================================================================
# HALAMAN: BAHASA
# ============================================================================
def page_bahasa() -> None:
    
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

    st.markdown('<div class="set-section">Pilih bahasa</div>', unsafe_allow_html=True)
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

    ui_sel = next(l for l in SUPPORTED_LANGUAGES if l["name"] == ui_name)
    yuki_sel = next(l for l in SUPPORTED_LANGUAGES if l["name"] == yuki_name)
    _baris_aksi_simpan(
        "Simpan bahasa", "lang_save",
        {"ui_lang": ui_sel["code"], "yuki_lang": yuki_sel["code"]},
        f"Bahasa disimpan — Yuki akan menjawab dalam {yuki_sel['name']}.",
    )

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
    (":material/swap_horiz:", "Ganti model AI",
     "Klik nama model di kanan kotak chat, pilih tingkat yang kamu mau "
     "(Trinity Seed sampai Trinity Sovereign)."),
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
     "Periksa koneksi internet, lalu kirim ulang pesannya. Bila masih gagal, "
     "cek status \"Chat AI (Yuki)\" di Pengaturan → Kemampuan — bila tertulis "
     "\"butuh GROQ_API_KEY\", kredensial belum diisi pemilik aplikasi."),
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
            st.toast(f"Kirim email ke {AMPERA_EMAIL}", icon=":material/mail:")
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
     "Pilih tingkat model dari Trinity Seed sampai Trinity Sovereign lewat "
     "nama model di kotak chat, lengkap dengan fallback otomatis bila satu "
     "model sedang tidak tersedia."),
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
     "Delapan bagian: Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, "
     "Refleksi, Waktu dan fokus."),
]
TIPS_LIST = [
    "Beri konteks di awal: siapa kamu, untuk apa, dan batasannya. Jawaban "
    "Yuki langsung lebih tepat sasaran.",
    "Isi Memori dengan fakta penting (usaha, gaya jawaban favorit) supaya "
    "tidak perlu mengulang-ulang.",
    "Pakai halaman Artefak untuk pekerjaan besar supaya chat utama tetap "
    "rapi.",
    "Pilih kepribadian \"Serius & ringkas\" di Pengaturan → Umum bila butuh "
    "jawaban presisi seperti kode atau hitungan.",
    "Nyalakan Pencarian web hanya saat benar-benar butuh data terbaru.",
    "Unduh Chat secara berkala sebagai arsip pekerjaanmu.",
]

def page_pelajari() -> None:
    
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

    s = get_settings()
    st.markdown(
        '<div class="trinity-hero"><div class="hero-text">'
        f'<h1>{html.escape(AMPERA_BRAND)}</h1>'
        f"<p>Trinity Pro kini bergabung ke keluarga {html.escape(AMPERA_BRAND)} — "
        f"{html.escape(AMPERA_LOKASI)}. Semua kemampuan dibuka penuh: model "
        "tertinggi tanpa batas, gambar resolusi tinggi, memori tak terbatas, "
        "artefak penuh, serta seluruh Trinity kursus dengan Yuki sebagai "
        "mentor pribadi.</p>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="set-section">Pilih paket Trinity Pro</div>',
                unsafe_allow_html=True)
    kolom_harga = st.columns(3)
    for i, paket in enumerate(PRO_HARGA):
        with kolom_harga[i]:
            _harga_col(paket, f"plan_pro_{i}")

    st.markdown('<div class="set-section">Semua paket Pro mendapat</div>',
                unsafe_allow_html=True)
    for label, _pro, _free in PRO_FEATURES:
        st.markdown(
            f'<div class="feat-row"><span>{label}</span>'
            f'<span class="chip-on">{mi(":material/check_circle:")}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="set-section">Keluarga produk Ampera</div>',
                unsafe_allow_html=True)
    for produk in AMPERA_PRODUK_LAIN:
        st.markdown(
            f'<div class="help-step"><span class="step-icon">'
            f'{mi(":material/auto_awesome:")}</span>'
            f'<span class="step-text"><b>{html.escape(produk["nama"])}</b><br>'
            f'{html.escape(produk["desc"])}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="set-section">Cara berlangganan</div>',
                unsafe_allow_html=True)
    for i, (icon, title, desc) in enumerate([
        (":material/tap_and_play:", "Pilih paket",
         "Bulanan, tahunan (paling hemat), atau sekali bayar untuk selamanya."),
        (":material/forum:", "Chat di Room Ampera",
         'Tekan tombol "ke Room Chat Ampera" di bawah — kamu langsung '
         "diarahkan ke room chat resmi Ampera Official. Tulis pesanmu "
         "(sebutkan paket pilihanmu) dan pesan itu langsung sampai "
         "ke admin."),
        (":material/bolt:", "Langsung aktif",
         "Setelah pembayaran dikonfirmasi, paket berubah menjadi Trinity Pro "
         "dan semua kemampuan terbuka saat itu juga."),
    ]):
        st.markdown(
            f'<div class="help-step"><span class="step-no">{i + 1}</span>'
            f'<span class="step-icon">{mi(icon)}</span>'
            f'<span class="step-text"><b>{title}</b><br>{desc}</span></div>',
            unsafe_allow_html=True,
        )

    st.link_button("💬 ke Room Chat Ampera", ROOM_CHAT_URL,
                   use_container_width=True, type="primary")
    st.caption(
        f"Pesanmu di room chat langsung masuk ke admin {AMPERA_BRAND} — "
        f"{AMPERA_LOKASI}. Status paket kamu saat ini: {s.get('plan', 'Free')}."
    )
    _page_footer()
# ============================================================================
# HALAMAN: DAPATKAN APLIKASI
# ============================================================================
def page_aplikasi() -> None:
    
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

    # Jawaban yang sedang mengalir + animasi berpikir + tombol Hentikan.
    fragmen_jawaban_yuki()
    render_loader_yuki()

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
        user_input = chat_input_atau_hentikan(f"Tanya apa saja tentang {course['title']}…", **chat_kwargs)
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
    inject_toast_anim()
    inject_anim_css()
    # Lapisan tampilan pilihan User (wallpaper & warna) — HARUS sesudah
    # inject_css() supaya menimpa tema bawaan, bukan tertimpa.
    inject_tampilan()
    # Toast hasil "bersihkan riwayat" (dititipkan sebelum rerun).
    tampilkan_toast_tertunda()

    if st.session_state.get("logged_out"):
        st.session_state.logged_out = False
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    # ===== GERBANG PEMBUKA (welcome_gate.py): splash animasi Trinity +
    # halaman login Google. Sekali per sesi; setelah masuk, gerbang ini
    # tidak melakukan apa-apa lagi. =====
    from welcome_gate import tampilkan_gerbang
    if tampilkan_gerbang():
        st.stop()
      
    render_multi_agent_launcher()
    render_sidebar()

    page = st.session_state.get("page", "chat")
    # Dok file kecil (panel_file.py): ikon folder melayang + daftar file
    # buatan Yuki. Tidak buka otomatis — hanya gelembung penanda.
    render_file_dock()

    # Animasi ala iOS untuk perpindahan halaman.

    # ================================================================
    # ANIMASI PERPINDAHAN HALAMAN
    # ================================================================
    #
    # JANGAN jalankan animasi pada first load.
    # First load harus langsung stabil supaya topbar, panel kanan,
    # sidebar, dan elemen position:fixed tidak terpengaruh transform
    # dari animasi halaman.
    #
    # Animasi hanya dijalankan kalau user BENAR-BENAR berpindah
    # dari satu halaman ke halaman lain.
    
    _last_page = st.session_state.get("_last_page")
    
    if _last_page is None:
    
        # First load:
        # simpan halaman sekarang, TANPA animasi.
        st.session_state["_last_page"] = page
    
    elif _last_page != page:
    
        # Benar-benar pindah halaman.
        st.session_state["_last_page"] = page
    
        inject_page_anim()
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
    elif page == "desain":
        page_desain()
    elif page == "jadwal":
        page_jadwal()
    elif page == "multi_agent":
        page_multi_agent()
    else:
        render_chat_page()


if __name__ == "__main__":
    main()
