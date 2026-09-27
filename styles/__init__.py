# -*- coding: utf-8 -*-
"""CSS — TEMA TRINITY (beige + ungu).

Seluruh gaya visual aplikasi tinggal di paket ini; app.py cukup memanggil
inject_css(). File asli styles.py (satu file, ~8800 baris) dipecah jadi
beberapa modul di dalam folder ini supaya lebih gampang dicari & diedit,
tanpa mengubah satu baris CSS pun dan tanpa mengubah perilaku inject_css().

Urutan penggabungan HARUS sama seperti urutan asli di styles.py karena ada
aturan CSS yang saling override berdasarkan urutan (cascade).
"""
import streamlit as st

from .part01_base_sidebar import CSS as _P01
from .part02_chat_input import CSS as _P02
from .part03_loading_thinking import CSS as _P03
from .part04_cards_files import CSS as _P04
from .part05_pages_new import CSS as _P05
from .part06_animations import CSS as _P06
from .part07_dashboard_layout import CSS as _P07
from .part08_controls_icons import CSS as _P08
from .part09_design_system import CSS as _P09
from .part10_multiai_layout import CSS as _P10
from .part11_settings_page import CSS as _P11
from .part12_ai_image import CSS as _P12

# Setiap modul part*.py menulis kontennya sebagai CSS = r"""\n...\n"""
# sehingga selalu ada tepat satu newline pembungkus di awal & akhir yang
# perlu dibuang (bukan strip("\n") biasa, supaya baris kosong ASLI di
# dalam CSS -- yang juga berupa newline -- tidak ikut terpotong).
_ALL_CSS = "\n".join(
    part[1:-1]
    for part in (
        _P01, _P02, _P03, _P04, _P05,
        _P06, _P07, _P08, _P09, _P10, _P11, _P12,
    )
)


def inject_css() -> None:
    st.markdown(
        f"""
<style>
{_ALL_CSS}
</style>
""",
        unsafe_allow_html=True,
    )
