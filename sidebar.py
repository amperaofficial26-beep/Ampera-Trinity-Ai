# -*- coding: utf-8 -*-
"""
SIDEBAR ALA CLAUDE
  Brand serif · + Baru · menu · riwayat "Hari ini" · akun di bawah

Setiap item riwayat kini punya menu ⋯ di ujung kanan (persis Claude) untuk:
sematkan, tandai dibaca/belum dibaca, ganti nama, tambah ke proyek, dan hapus.

Berisi juga navigasi antar-halaman (go()) dan tiga dialog kecil (Proyek,
Artefak lama, Sesuaikan) yang dipicu dari menu sidebar.
"""

from __future__ import annotations

import html

import streamlit as st

from state import (
    assign_conversation_project, delete_conversation, get_settings,
    open_conversation, rename_conversation, reset_conversation,
    set_conversation_unread, sync_current_conversation,
    toggle_pin_conversation,
)
from ui_helpers import get_chat_export_text

HAS_DIALOG = hasattr(st, "dialog")


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


def _tambah_ke_proyek_dialog_body() -> None:
    """Dialog pilih proyek untuk satu percakapan (dipicu dari menu ⋮)."""
    conv_id = st.session_state.get("pick_project_conv_id")
    conv = next((c for c in st.session_state.get("conversations", [])
                 if c["id"] == conv_id), None)
    if conv is None:
        st.caption("Pilih percakapan dulu.")
        return
    st.caption(html.escape(conv["title"]))
    projects = st.session_state.get("projects", [])
    if not projects:
        st.info("Belum ada proyek. Buat dulu lewat menu Proyek di sidebar.")
        return
    for p in projects:
        assigned = conv.get("project_id") == p["id"]
        label = f":material/folder:  {p['name']}" + ("  :material/check:" if assigned else "")
        if st.button(label, key=f"conv_proj_{conv_id}_{p['id']}",
                     use_container_width=True):
            assign_conversation_project(conv_id, p["id"])
            st.rerun()
    if conv.get("project_id") is not None:
        st.divider()
        if st.button(":material/link_off:  Lepas dari proyek",
                     key=f"conv_proj_clear_{conv_id}", use_container_width=True):
            assign_conversation_project(conv_id, None)
            st.rerun()


show_project_picker_dialog = _register_dialog(
    "Tambah ke proyek", _tambah_ke_proyek_dialog_body)


def _render_rename_row(c: dict) -> None:
    """Baris ganti judul inline (di tempat item riwayat, ala Claude)."""
    with st.form(key=f"rename_form_{c['id']}", clear_on_submit=False):
        new_title = st.text_input(
            "Judul", value=st.session_state.get("rename_draft", c["title"]),
            key=f"rtitle_{c['id']}", label_visibility="collapsed",
            placeholder="Judul percakapan…",
        )
        save_col, cancel_col = st.columns([1, 1], gap="small")
        with save_col:
            submitted = st.form_submit_button(
                ":material/check:  Simpan", use_container_width=True,
            )
        with cancel_col:
            cancelled = st.form_submit_button(
                ":material/close:  Batal", use_container_width=True,
            )
    if submitted:
        rename_conversation(c["id"], new_title)
        st.session_state.rename_conv_id = None
        st.session_state.pop("rename_draft", None)
        st.rerun()
    if cancelled:
        st.session_state.rename_conv_id = None
        st.session_state.pop("rename_draft", None)
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        # ---- Bagian atas: TETAP di atas (sticky), tidak ikut scroll ----
        with st.container(key="sb_top"):
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

        # ---- Bagian tengah: daftar riwayat — INI SATU-SATUNYA yang scroll ----
        with st.container(key="sb_history"):
            # Riwayat percakapan (grup "Hari ini" seperti Claude). Obrolan yang
            # sedang berjalan langsung ikut tampil (seperti Claude), lalu yang
            # disematkan tampil paling atas. Tiap baris punya menu ⋯ di kanan
            # untuk: sematkan, tandai dibaca/belum dibaca, ganti nama,
            # tambah ke proyek, dan hapus.
            sync_current_conversation()
            convs = st.session_state.get("conversations", [])
            if convs:
                st.markdown('<div class="sb-group">Hari ini</div>', unsafe_allow_html=True)
                # urutkan: tersemat dulu (urutan tetap), baru yang lain
                convs_sorted = sorted(convs, key=lambda c: 0 if c.get("pinned") else 1)
                for c in convs_sorted[:15]:
                    key = f"sb_hist_{c['id']}"
                    pinned = bool(c.get("pinned"))
                    unread = bool(c.get("unread"))
                    active = st.session_state.get("active_conv_id") == c["id"]
                    with st.container(key=key):
                        if st.session_state.get("rename_conv_id") == c["id"]:
                            _render_rename_row(c)
                        else:
                            title_label = (
                                ":material/push_pin:  " + c["title"]
                                if pinned else c["title"]
                            )
                            btn, more = st.columns([0.82, 0.18], gap="small",
                                                   vertical_alignment="center")
                            with btn:
                                if st.button(title_label, key=f"btn_{key}",
                                             use_container_width=True):
                                    open_conversation(c["id"])
                                    st.rerun()
                            with more:
                                with st.popover(":material/more_horiz:",
                                                use_container_width=True,
                                                help="Aksi untuk percakapan ini"):
                                    st.caption(html.escape(c["title"]))
                                    if c.get("project_name"):
                                        st.caption("Proyek: "
                                                   + html.escape(c["project_name"]))
                                    if st.button(
                                        (":material/push_pin:  Lepas sematan"
                                         if pinned else ":material/push_pin:  Sematkan"),
                                        key=f"pin_{c['id']}",
                                        use_container_width=True,
                                    ):
                                        toggle_pin_conversation(c["id"])
                                        st.rerun()
                                    if st.button(
                                        (":material/mark_email_read:  Tandai sebagai dibaca"
                                         if unread
                                         else ":material/mark_email_unread:  Tandai sebagai belum dibaca"),
                                        key=f"read_{c['id']}",
                                        use_container_width=True,
                                    ):
                                        set_conversation_unread(c["id"], not unread)
                                        st.rerun()
                                    if st.button(
                                        ":material/edit:  Ganti nama",
                                        key=f"ren_{c['id']}",
                                        use_container_width=True,
                                    ):
                                        st.session_state.rename_conv_id = c["id"]
                                        st.session_state.rename_draft = c["title"]
                                        st.rerun()
                                    if st.button(
                                        ":material/create_new_folder:  Tambah ke proyek",
                                        key=f"proj_{c['id']}",
                                        use_container_width=True,
                                    ):
                                        st.session_state.pick_project_conv_id = c["id"]
                                        show_project_picker_dialog()
                                    if st.button(
                                        ":material/delete:  Hapus",
                                        key=f"del_{c['id']}",
                                        use_container_width=True,
                                    ):
                                        delete_conversation(c["id"])
                                        st.rerun()
                            # penanda untuk highlight CSS (pin/unread/aktif)
                            markers = []
                            if pinned:
                                markers.append("sb-pinned-marker")
                            if unread:
                                markers.append("sb-unread-marker")
                            if active:
                                markers.append("sb-active-marker")
                            if markers:
                                st.markdown(
                                    "".join(f'<div class="{m}"></div>' for m in markers),
                                    unsafe_allow_html=True,
                                )

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
