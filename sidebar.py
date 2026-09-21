# -*- coding: utf-8 -*-
"""
SIDEBAR ALA CLAUDE
  Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah

Berisi juga navigasi antar-halaman (go()) dan tiga dialog kecil (Proyek,
Artefak lama, Sesuaikan) yang dipicu dari menu sidebar.
"""

from __future__ import annotations

import html

import streamlit as st

from state import open_conversation, reset_conversation
from ui_helpers import get_chat_export_text, logo_img_html

HAS_DIALOG = hasattr(st, "dialog")

# ============================================================================
# >>> ATUR POSISI TOMBOL TITIK TIGA (menu akun) DI SINI <<<
#   Ditulis langsung sebagai <style> di dekat tombolnya, jadi PASTI menang
#   melawan aturan lain. Perbesar Y = tombol naik.
# ----------------------------------------------------------------------------
ACCT_MENU_X_PX = 190   # jarak dari tepi KIRI layar
ACCT_MENU_Y_PX = 4    # jarak dari DASAR layar

# Warna tombol ⋯ . Pakai "transparent" agar menyatu dengan latar sidebar,
# atau tulis kode warna (mis. "#EDE2D1" = warna sidebar, "#E8DCC8" = warna
# kanvas aplikasi).
ACCT_MENU_BG = "transparent"        # latar tombol saat diam
ACCT_MENU_BG_HOVER = "#E0D2BB"      # latar saat disentuh kursor
ACCT_MENU_FG = "#6B6172"            # warna ikon titik tiga
ACCT_MENU_BORDER = "transparent"    # garis tepi; "transparent" = tanpa garis
# ============================================================================


# ============================================================================
# >>> ATUR POSISI TULISAN DI PANEL PROYEK DI SINI <<<
#   Mengatur 3 tulisan: kotak "Cari proyek", teks "Belum ada proyek.",
#   dan tombol "Mulai proyek baru".
#   Nilai perataan: "left" | "center" | "right"
# ----------------------------------------------------------------------------
PROYEK_LEBAR_PX = 300         # lebar panel popover Proyek
PROYEK_PADDING_PX = 14        # jarak isi dari tepi panel
PROYEK_JARAK_PX = 10          # jarak antar elemen (kotak cari, teks, tombol)

PROYEK_CARI_ALIGN = "left"    # perataan teks di dalam kotak "Cari proyek"
PROYEK_KOSONG_ALIGN = "center"  # perataan teks "Belum ada proyek."
PROYEK_KOSONG_PADDING_PX = 10   # jarak atas-bawah teks "Belum ada proyek."
PROYEK_TOMBOL_ALIGN = "left"  # perataan label tombol "Mulai proyek baru"
# ============================================================================

# Gaya agar tombol pemicu popover di sidebar tampak identik dengan tombol
# menu biasa (rata kiri, tanpa kotak), dan panel popovernya cukup lebar.
_GAYA_MENU_POPOVER = (
    "<style>"
    ".st-key-sb_menu_proyek [data-testid='stPopover'] button,"
    ".st-key-sb_menu_proyek button[data-testid='stPopoverButton']{"
    "background:transparent !important;"
    "border:none !important;"
    "box-shadow:none !important;"
    "color:#2C1F33 !important;"
    "text-align:left !important;"
    "justify-content:flex-start !important;"
    "padding:0.45rem 0.6rem !important;"
    "width:100% !important;"
    "}"
    ".st-key-sb_menu_proyek button:hover{"
    "background:#E0D2BB !important;"
    "border-radius:9px !important;"
    "}"
    ".st-key-sb_menu_proyek [data-testid='stPopover'] button p{"
    "text-align:left !important;font-size:1.06rem !important;"
    "line-height:1.25 !important;color:#2C1F33 !important;margin:0 !important;"
    "}"
    ".st-key-sb_menu_proyek [data-testid='stIconMaterial']{"
    "font-size:1.35rem !important;width:1.35rem !important;height:1.35rem !important;"
    "}"
    # ---- panel popover Proyek ----
    "[data-testid='stPopoverBody']:has([class*='st-key-proj_']){"
    "min-width:" + str(PROYEK_LEBAR_PX) + "px !important;"
    "max-width:" + str(PROYEK_LEBAR_PX + 40) + "px !important;"
    "padding:" + str(PROYEK_PADDING_PX) + "px !important;"
    "}"
    # jarak antar elemen di dalam panel
    "[data-testid='stPopoverBody']:has([class*='st-key-proj_']) "
    "[data-testid='stVerticalBlock']{"
    "gap:" + str(PROYEK_JARAK_PX) + "px !important;"
    "}"
    # 1) kotak "Cari proyek"
    ".st-key-proj_search input,.st-key-proj_new_name input{"
    "text-align:" + PROYEK_CARI_ALIGN + " !important;"
    "font-size:0.9rem !important;"
    "}"
    # 2) teks "Belum ada proyek."
    "[data-testid='stPopoverBody'] [data-testid='stCaptionContainer'],"
    "[data-testid='stPopoverBody'] [data-testid='stCaptionContainer'] p{"
    "text-align:" + PROYEK_KOSONG_ALIGN + " !important;"
    "width:100% !important;"
    "padding:" + str(PROYEK_KOSONG_PADDING_PX) + "px 0 !important;"
    "margin:0 !important;"
    "font-size:0.85rem !important;"
    "color:#8E8398 !important;"
    "}"
    # 3) tombol "Mulai proyek baru" + tombol pilih proyek
    "[data-testid='stPopoverBody'] div.stButton > button{"
    "justify-content:" + ("flex-start" if PROYEK_TOMBOL_ALIGN == "left"
                          else "center" if PROYEK_TOMBOL_ALIGN == "center"
                          else "flex-end") + " !important;"
    "text-align:" + PROYEK_TOMBOL_ALIGN + " !important;"
    "}"
    "[data-testid='stPopoverBody'] div.stButton > button p{"
    "text-align:" + PROYEK_TOMBOL_ALIGN + " !important;"
    "width:100% !important;"
    "}"
    "</style>"
)
      
def go(page: str, **extra) -> None:
    """Pindah halaman internal (chat / artefak / pengaturan / …)."""
    for k, v in extra.items():
        st.session_state[k] = v
    st.session_state.page = page
    st.rerun()

def go_cb(page: str, **extra) -> None:
    """Versi go() untuk dipakai sebagai on_click=... pada st.button.

    Bedanya: TIDAK memanggil st.rerun(). Streamlit sudah otomatis
    menjalankan ulang halaman setelah callback selesai. Cara ini lebih
    andal daripada pola "if st.button(): go(...)" — pada halaman yang
    juga memanggil st.rerun() di tempat lain (mis. maybe_run_yuki atau
    process_user_input), klik tombol bisa "hilang" sebelum sempat
    diproses."""
    for k, v in extra.items():
        st.session_state[k] = v
    st.session_state.page = page
  
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
        # Catatan tata letak baru: brand "Trinity" yang tadinya di sini
        # sudah pindah ke TOPBAR di atas (layout.py). Sidebar kini langsung
        # diawali tombol "+ Baru" lalu menu navigasi utama.

        # Di room Multi Trinity Agent, sidebar sengaja dibersihkan.
        # Hanya navigasi kembali dan riwayat room yang ditampilkan.
        if st.session_state.get("page") == "multi_agent":
            if st.button(
                ":material/arrow_back: &nbsp;Kembali ke Chat",
                key="agent_back_chat",
                use_container_width=True,
            ):
                go("chat")
        
            agent_messages = st.session_state.get(
                "mode_msgs_multi_agent",
                [],
            )
        
            questions = [
                message
                for message in agent_messages
                if message.get("role") == "user"
            ]
        
            st.markdown(
                '<div class="sb-divider"></div>',
                unsafe_allow_html=True,
            )
        
            st.markdown(
                '<div class="sb-group">'
                'Riwayat Multi Agent'
                '</div>',
                unsafe_allow_html=True,
            )
        
            if not questions:
                st.caption(
                    "Belum ada percakapan."
                )
        
            else:
                # Ambil maksimal 15 pertanyaan terbaru.
                for message in reversed(questions[-15:]):
                    title = " ".join(
                        str(
                            message.get("content") or ""
                        ).split()
                    )
        
                    title = (
                        title[:42]
                        + ("…" if len(title) > 42 else "")
                    )
        
                    st.markdown(
                        '<div class="mem-item" '
                        'style="margin-bottom:6px">'
                        + html.escape(title)
                        + '</div>',
                        unsafe_allow_html=True,
                    )
        
            if st.button(
                ":material/add: &nbsp;Room baru",
                key="agent_new_room",
                use_container_width=True,
            ):
                st.session_state[
                    "mode_msgs_multi_agent"
                ] = []
        
                st.rerun()
        
            # Menghentikan render menu sidebar biasa.
            return

        # + Baru (latar krem menonjol seperti Claude)
        with st.container(key="sb_new"):
            if st.button(":material/add: &nbsp;Baru", use_container_width=True):
                reset_conversation()
                st.rerun()

        # ---- Navigasi utama (tata letak baru: Chat AI · Multi AI ·
        #      Generate Gambar · Riwayat · Pengaturan) ----
        with st.container(key="sb_menu_chat"):
            if st.button(":material/chat_bubble: &nbsp;Chat AI",
                         use_container_width=True):
                st.session_state.image_mode = False
                st.rerun()
        with st.container(key="sb_menu_multi"):
            if st.button(":material/groups: &nbsp;Multi AI",
                         use_container_width=True):
                go("multi_agent")
        with st.container(key="sb_menu_img"):
            if st.button(":material/image: &nbsp;Generate Gambar",
                         use_container_width=True):
                st.session_state.image_mode = True
                st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # ---- Riwayat Chat (navigasi percakapan lama) ----
        convs = st.session_state.get("conversations", [])
        st.markdown('<div class="sb-group">Riwayat Chat</div>',
                    unsafe_allow_html=True)
        if convs:
            for c in convs[:15]:
                key = f"sb_hist_{c['id']}"
                with st.container(key=key):
                    if st.button(c["title"], key=f"btn_{key}",
                                 use_container_width=True):
                        open_conversation(c["id"])
                        st.rerun()

            # Bersihkan riwayat — konfirmasi dua langkah ditampilkan
            # langsung di sidebar (konteks "sb" supaya kunci widgetnya
            # tidak bentrok dengan yang di halaman Pengaturan).
            from riwayat import dialog_bersihkan
            with st.container(key="sb_bersih_riwayat"):
                dialog_bersihkan("sb")
        else:
            st.caption("Belum ada percakapan.")

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # ---- Pengaturan ----
        with st.container(key="sb_menu_pengaturan"):
            if st.button(":material/settings: &nbsp;Pengaturan",
                         use_container_width=True):
                go("pengaturan")

        # ---- Lainnya: fitur yang sudah ada, dikelompokkan agar menu
        #      utama di atas tetap ringkas ----
        st.markdown('<div class="sb-group">Lainnya</div>',
                    unsafe_allow_html=True)
        with st.container(key="sb_menu_proyek"):
            # Proyek tampil sebagai POPOVER (muncul di samping tombolnya),
            # bukan dialog yang melayang di tengah halaman. Gaya tombolnya
            # disamakan dengan menu sidebar lain lewat <style> di bawah.
            st.markdown(_GAYA_MENU_POPOVER, unsafe_allow_html=True)
            with st.popover(":material/deployed_code: &nbsp;Proyek",
                            use_container_width=True):
                _proyek_dialog_body()
        with st.container(key="sb_menu_artefak"):
            n_art = len(st.session_state.get("artifacts", []))
            art_label = ":material/data_object: &nbsp;Artefak" + (f"  ({n_art})" if n_art else "")
            if st.button(art_label, use_container_width=True):
                # buka HALAMAN Artefak (bukan popup lagi)
                go("artefak")
        with st.container(key="sb_menu_sesuaikan"):
            if st.button(":material/tune: &nbsp;Sesuaikan", use_container_width=True):
                show_sesuaikan_dialog()

        # ---- Kelompok AI khusus ----
        with st.container(key="sb_menu_desain"):
            if st.button(":material/palette: &nbsp;AI Desain", use_container_width=True):
                go("desain")
        with st.container(key="sb_menu_jadwal"):
            n_tugas = len([t for t in st.session_state.get("tasks", [])
                           if not t.get("selesai")])
            label_jd = (":material/calendar_month: &nbsp;AI Penjadwal"
                        + (f"  ({n_tugas})" if n_tugas else ""))
            if st.button(label_jd, use_container_width=True):
                go("jadwal")

        with st.container(key="sb_download"):
            st.download_button(
                label=":material/download: &nbsp;Unduh Chat",
                data=get_chat_export_text(),
                file_name=f"trinity-chat-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        # ---- Branding + maskot di dasar sidebar (tata letak baru).
        #      Menu akun yang tadinya di sini sudah pindah ke popover
        #      "Profil" di topbar (layout.py). ----
        st.markdown(
            '<div class="sb-footbrand">'
            + logo_img_html("logo-footbrand")
            + '<div class="t">Trinity</div>'
            + '<div class="s">by Ampera Official</div>'
            + '</div>',
            unsafe_allow_html=True,
        )
