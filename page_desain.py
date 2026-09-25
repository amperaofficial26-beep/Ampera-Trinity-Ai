# -*- coding: utf-8 -*-
"""
HALAMAN: AI DESAIN

Mode chat khusus dengan persona art director (DESAIN_PROMPT di config.py),
tombol mulai cepat, dan kartu palet warna (cards.py).

Tata letak sengaja SATU LAJUR penuh, sama seperti halaman chat lain, supaya
gelembung jawaban dan kartu palet punya ruang yang cukup.
"""

from __future__ import annotations

import streamlit as st

from config import CHAT_INPUT_SUPPORTS_AUDIO, CHAT_INPUT_SUPPORTS_FILE, IMAGE_INPUT_TYPES
from icons import mi
from state import mode_thread
from ui_helpers import _page_footer, render_message

# ============================================================================
# >>> ATUR TOMBOL MULAI CEPAT DI SINI <<<
#   (label tombol, kalimat yang dikirim ke Yuki)
#   Disusun 2 kolom; tambah/kurangi bebas, tata letaknya menyesuaikan.
# ============================================================================
TOMBOL_CEPAT = [
    ("Buat palet warna",
     "Buatkan satu palet warna yang enak dipandang untuk aplikasi ini, "
     "lengkap dengan peran tiap warna."),
    ("Saran pasangan font",
     "Sarankan 2 pasangan font (judul + isi) yang cocok untuk aplikasi AI "
     "bernuansa hangat, beserta alasannya."),
    ("Kritik desain saya",
     "Aku akan kirim tangkapan layar desainku. Tolong kritik: hierarki, "
     "spasi, warna, tipografi, dan konsistensinya."),
    ("Buat moodboard",
     "Buatkan gambar moodboard suasana hangat minimalis untuk aplikasi ini."),
]


def _kirim(teks: str) -> None:
    """Kirim prompt tombol cepat seolah User mengetiknya."""
    st.session_state["pending_prompt_mode"] = teks


def page_desain() -> None:
    from chat_handlers import (
        maybe_run_yuki, process_user_input, render_input_controls,
        render_pending_preview, fragmen_jawaban_yuki, chat_input_atau_hentikan,
        render_loader_yuki,
    )

    thread = mode_thread("desain")
    st.markdown('<div class="design-page-shell"></div>', unsafe_allow_html=True)

    st.markdown(
        f'''
        <div class="design-topbar">
          <div class="design-heading">
            <div class="design-heading-icon">{mi(":material/palette:")}</div>
            <div>
              <h1>AI Desain</h1>
              <p>Art director pribadimu: palet warna, tipografi, kritik tampilan,
              sampai moodboard.</p>
            </div>
          </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # ---- Mulai cepat: hanya tampil saat percakapan masih kosong ----
    if not thread:
        card_meta = {
            "Buat palet warna": (
                ":material/palette:",
                "Dapatkan palet warna yang cocok untuk desain kamu.",
                "palette",
            ),
            "Saran pasangan font": (
                "Aa",
                "Temukan kombinasi font yang harmonis dan profesional.",
                "font",
            ),
            "Kritik desain saya": (
                ":material/chat_bubble_outline:",
                "Dapatkan masukan objektif untuk meningkatkan desainmu.",
                "critique",
            ),
            "Buat moodboard": (
                ":material/image:",
                "Kumpulkan inspirasi visual untuk proyek desainmu.",
                "moodboard",
            ),
        }

        st.markdown(
            '<div class="design-section-title">'
            f'<span class="design-section-icon">{mi(":material/bolt:")}</span>'
            '<span>Mulai cepat</span><i></i></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="desain_quick"):
            for i in range(0, len(TOMBOL_CEPAT), 2):
                pasangan = TOMBOL_CEPAT[i:i + 2]
                cols = st.columns(len(pasangan), gap="medium")
                for j, (label, prompt) in enumerate(pasangan):
                    with cols[j]:
                        icon, desc, visual = card_meta[label]
                        with st.container(key=f"desain_quick_card_{i + j}"):
                            st.markdown(
                                f'''
                                <div class="design-quick-visual design-visual-{visual}">
                                  <div class="design-quick-icon">{mi(icon) if icon.startswith(":") else icon}</div>
                                  <div class="design-quick-art"></div>
                                </div>
                                ''',
                                unsafe_allow_html=True,
                            )
                            st.button(
                                f"**{label}**  \n:gray[{desc}]  \n→",
                                key=f"desain_q_{i + j}",
                                use_container_width=True,
                                on_click=_kirim,
                                args=(prompt,),
                            )

        st.markdown(
            f'''
            <div class="design-prompt-card">
              <div class="design-prompt-art" aria-hidden="true">
                <div class="design-prompt-paper">Aa<div></div><span></span></div>
                <div class="design-prompt-swatch swatch-a"></div>
                <div class="design-prompt-swatch swatch-b"></div>
                <div class="design-prompt-swatch swatch-c"></div>
                <div class="design-prompt-spark">{mi(":material/auto_awesome:")}</div>
              </div>
              <div class="design-prompt-copy">
                <h2>{mi(":material/auto_awesome:")} Apa yang ingin kamu desain?</h2>
                <p>Ceritakan kebutuhan desainmu, misalnya: buatkan palet warna untuk aplikasi,
                beri kritik pada desain yang ada, atau upload gambar untuk dianalisis.</p>
              </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    for msg in thread:
        render_message(msg)

    if maybe_run_yuki(st.empty()):
        st.rerun()
    fragmen_jawaban_yuki()
    render_loader_yuki()

    # ruang kosong supaya isi terakhir tidak tertutup kotak input
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
        user_input = chat_input_atau_hentikan("Tanya soal desain…", **chat_kwargs)
        with st.container(key="chat_controls"):
            render_input_controls("desain", show_mode=False)

    antre = (st.session_state.pop("pending_prompt_mode", "") or "").strip()
    if antre and user_input is None:
        user_input = antre

    if process_user_input(user_input, st.empty()):
        st.rerun()

    _page_footer(in_chat=bool(thread))
