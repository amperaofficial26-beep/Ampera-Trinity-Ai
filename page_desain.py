# -*- coding: utf-8 -*-
"""
HALAMAN: AI DESAIN (CREATIVE STUDIO)

Mode chat khusus dengan persona art director (DESAIN_PROMPT di config.py),
tombol mulai cepat bergaya bento, dan kartu palet warna (cards.py).
"""

from __future__ import annotations

import streamlit as st

from config import CHAT_INPUT_SUPPORTS_AUDIO, CHAT_INPUT_SUPPORTS_FILE, IMAGE_INPUT_TYPES
from icons import mi
from state import mode_thread
from ui_helpers import _page_footer, render_message

TOMBOL_CEPAT = [
    ("🎨  Palet Warna", "Rekomendasi palet warna & kode HEX harmonis",
     "Buatkan satu palet warna yang enak dipandang untuk aplikasi ini, lengkap dengan peran tiap warna dan kode HEX-nya."),
    ("🔤  Pasangan Font", "Kombinasi font judul & isi yang serasi",
     "Sarankan 2 pasangan font (judul + isi) yang cocok untuk aplikasi AI bernuansa hangat dan elegan, beserta alasannya."),
    ("🔍  Kritik Tampilan / UI", "Evaluasi hierarki, spasi, dan kontras",
     "Aku akan mengirimkan rancangan desainku. Tolong evaluasi hierarki visual, spasi, warna, tipografi, dan konsistensinya."),
    ("🖼️  Moodboard Visual", "Eksplorasi konsep atmosfer & estetika",
     "Buatkan konsep moodboard bernuansa hangat minimalis dan mewah untuk produk digital."),
]


def _kirim(teks: str) -> None:
    """Kirim prompt tombol cepat seolah User mengetiknya."""
    st.session_state["pending_prompt_mode"] = teks


def page_desain() -> None:
    from chat_handlers import (
        maybe_run_yuki, process_user_input, render_input_controls,
        render_pending_preview,
    )

    thread = mode_thread("desain")

    st.markdown(
        f'<div class="page-head"><div class="page-head-icon">{mi("palette")}</div>'
        '<div><h2 class="page-title">AI Desain · Creative Studio</h2>'
        '<p class="page-sub">Art director pribadimu: palet warna, tipografi, '
        'evaluasi antarmuka, sampai konsep moodboard visual.</p></div></div>',
        unsafe_allow_html=True,
    )

    # ---- Mulai cepat: hanya tampil saat percakapan masih kosong ----
    if not thread:
        st.markdown('<div class="set-section">Inspirasi &amp; Mulai Cepat</div>', unsafe_allow_html=True)
        with st.container(key="desain_quick"):
            for i in range(0, len(TOMBOL_CEPAT), 2):
                pasangan = TOMBOL_CEPAT[i:i + 2]
                cols = st.columns(len(pasangan))
                for j, (title, desc, prompt) in enumerate(pasangan):
                    with cols[j]:
                        with st.container(key=f"desain_card_{i+j}"):
                            if st.button(f"**{title}**  \n:gray[{desc}]",
                                         key=f"desain_q_{i + j}",
                                         use_container_width=True,
                                         on_click=_kirim, args=(prompt,)):
                                pass

        st.markdown(
            '<div class="empty-card">💡 Ceritakan apa yang sedang kamu rancang, '
            "atau unggah tangkapan layar desainmu lewat tombol <b>+</b> di bawah. "
            "Yuki akan menilainya dengan ketajaman seorang art director profesional.</div>",
            unsafe_allow_html=True,
        )

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()

    st.markdown('<div class="dock-spacer"></div>', unsafe_allow_html=True)

    chat_kwargs: dict = {}
    if CHAT_INPUT_SUPPORTS_FILE:
        chat_kwargs["accept_file"] = True
        chat_kwargs["file_type"] = IMAGE_INPUT_TYPES
    if CHAT_INPUT_SUPPORTS_AUDIO:
        chat_kwargs["accept_audio"] = True

    bottom_dock = getattr(st, "bottom", None) or st._bottom
    with bottom_dock:
        with st.container(key="pending_preview"):
            render_pending_preview("desain")
        user_input = st.chat_input("Konsultasikan konsep desainmu dengan Yuki…", **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("desain", show_mode=False)

    antre = (st.session_state.pop("pending_prompt_mode", "") or "").strip()
    if antre and user_input is None:
        user_input = antre

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=bool(thread))
