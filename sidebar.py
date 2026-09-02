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
ACCT_MENU_Y_PX = 10    # jarak dari DASAR layar
# ============================================================================

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
            if st.button(":material/deployed_code: &nbsp;Proyek", use_container_width=True):
                show_proyek_dialog()
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
                # Style disuntik TEPAT di sini (setelah CSS utama), jadi
                # pasti menang dan tombol tidak ikut hanyut mengikuti
                # daftar menu sidebar.
                st.markdown(
                    "<style>.st-key-acct_menu{"
                    "position:fixed !important;"
                    f"left:{ACCT_MENU_X_PX}px !important;"
                    f"bottom:{ACCT_MENU_Y_PX}px !important;"
                    "top:auto !important;right:auto !important;"
                    "width:32px !important;margin:0 !important;"
                    "z-index:999996 !important;}</style>",
                    unsafe_allow_html=True,
                )
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
