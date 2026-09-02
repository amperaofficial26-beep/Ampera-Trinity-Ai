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

from state import get_settings, open_conversation, reset_conversation
from ui_helpers import get_chat_export_text

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

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        with st.container(key="sb_download"):
            st.download_button(
                label=":material/download: &nbsp;Unduh Chat",
                data=get_chat_export_text(),
                file_name=f"trinity-chat-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M')}.md",
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

        # ---- Baris akun di dasar sidebar ala Claude ----
        # (U) Nama · Paket   [⋮ menu akun]
        s = get_settings()
        name = (s.get("display_name") or "User").strip() or "User"
        plan = s.get("plan") or "Free"
        initial = name[0].upper()
        with st.container(key="sb_account"):
            acc_col, menu_col = st.columns([5, 1.05], gap="small")
            with acc_col:
                # Baris akun. Disusun dari potongan string biasa (bukan
                # f-string tiga kutip) supaya aman saat kode ini di-copy
                # paste ke editor lain, dan bebas karakter non-ASCII di
                # luar string.
                acc_html = (
                    '<div class="sb-account">'
                    '<div class="ava">' + html.escape(initial) + '</div>'
                    '<div class="name">' + html.escape(name)
                    + ' <span class="plan">&middot; ' + html.escape(plan)
                    + '</span></div>'
                    '</div>'
                )
                st.markdown(acc_html, unsafe_allow_html=True)
            with menu_col:
                # Gaya tombol titik tiga disusun sebagai string biasa
                # (bukan f-string) supaya kurung kurawal CSS tidak bentrok
                # dengan sintaks f-string Python.
                gaya_acct = (
                    "<style>"
                    ".st-key-acct_menu{"
                    "position:fixed !important;"
                    "left:" + str(ACCT_MENU_X_PX) + "px !important;"
                    "bottom:" + str(ACCT_MENU_Y_PX) + "px !important;"
                    "top:auto !important;right:auto !important;"
                    "width:32px !important;margin:0 !important;"
                    "background:transparent !important;"
                    "box-shadow:none !important;"
                    "z-index:999996 !important;"
                    "}"
                    ".st-key-acct_menu [data-testid='stPopover'],"
                    ".st-key-acct_menu [data-testid='stPopover'] > div,"
                    ".st-key-acct_menu button,"
                    ".st-key-acct_menu button[data-testid='stPopoverButton'],"
                    ".st-key-acct_menu [data-testid='stBaseButton-secondary']{"
                    "background:" + ACCT_MENU_BG + " !important;"
                    "background-color:" + ACCT_MENU_BG + " !important;"
                    "border:1px solid " + ACCT_MENU_BORDER + " !important;"
                    "color:" + ACCT_MENU_FG + " !important;"
                    "box-shadow:none !important;"
                    "border-radius:8px !important;"
                    "}"
                    ".st-key-acct_menu button:hover{"
                    "background:" + ACCT_MENU_BG_HOVER + " !important;"
                    "background-color:" + ACCT_MENU_BG_HOVER + " !important;"
                    "color:#2C1F33 !important;"
                    "}"
                    ".st-key-acct_menu button svg{"
                    "fill:" + ACCT_MENU_FG + " !important;"
                    "color:" + ACCT_MENU_FG + " !important;"
                    "}"
                    "</style>"
                )
                st.markdown(gaya_acct, unsafe_allow_html=True)
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
