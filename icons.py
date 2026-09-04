# -*- coding: utf-8 -*-
"""
Ikon SVG garis tipis ala Claude (stroke mengikuti warna teks) + helper
untuk menyisipkan ikon Material Symbols di dalam string HTML mentah
(dipakai saat Streamlit tidak bisa menerjemahkan sintaks ":material_x:"
karena berada di dalam tag HTML, mis. di dalam st.markdown(..., html)).
"""


def _svg(paths: str) -> str:
    return (
        '<svg class="icon-svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
    )


ICON_COPY = _svg('<rect x="9" y="9" width="11" height="11" rx="2"/>'
                 '<path d="M5 15V5a2 2 0 0 1 2-2h10"/>')
ICON_MIC = _svg('<rect x="9" y="3" width="6" height="11" rx="3"/>'
                '<path d="M6 11a6 6 0 0 0 12 0"/><path d="M12 17v4"/>')
ICON_IMAGE = _svg('<rect x="3" y="5" width="18" height="14" rx="2"/>'
                  '<circle cx="9" cy="10" r="1.6"/>'
                  '<path d="M5.5 18.5l5-5 3.5 3.5 2.5-2.5 2 2"/>')
ICON_SEARCH = _svg('<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>')
ICON_CHEVRON = _svg('<path d="M6 9l6 6 6-6"/>')


def mi(name: str) -> str:
    """Ikon Material untuk dipakai DI DALAM string HTML (st.markdown).

    Streamlit hanya menerjemahkan sintaks ikon material pada TEKS markdown biasa.
    Begitu string itu berada di dalam tag HTML, penggantinya tidak jalan dan
    yang tampil justru teks mentah ':material_nama:' di layar. Karena itu
    setiap ikon yang masuk ke HTML dibuat manual sebagai <span> dengan font
    ikon yang sama persis seperti yang dipakai Streamlit sendiri
    ("Material Symbols Rounded"), lengkap dengan ligature nama ikonnya.
    """
    glyph = name.split("/")[-1].rstrip(":")
    return (
        '<span class="mi" aria-hidden="true" translate="no" '
        "style=\"font-family:'Material Symbols Rounded';font-weight:normal;"
        "font-style:normal;display:inline-block;line-height:1;"
        "text-transform:none;letter-spacing:normal;word-wrap:normal;"
        "white-space:nowrap;direction:ltr;vertical-align:bottom;"
        '-webkit-font-smoothing:antialiased;user-select:none;">'
        f"{glyph}</span>"
    )
