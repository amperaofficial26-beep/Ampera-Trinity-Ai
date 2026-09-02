# -*- coding: utf-8 -*-
"""
Kartu kaya (rich cards) untuk jawaban Yuki.

Yuki menulis blok khusus di dalam jawabannya, lalu blok itu diubah menjadi
kartu visual — bukan ditampilkan sebagai teks mentah:

    [[KARTU:perbandingan]]
    judul: Laptop A | Laptop B
    Harga: Rp 8.000.000 | Rp 10.000.000
    RAM: 8GB | 16GB
    [[/KARTU]]

Jenis yang sudah didukung: perbandingan, langkah, link.
Menambah jenis baru cukup: tulis satu fungsi _render_<jenis>(kartu, kunci)
lalu daftarkan di RENDERER.
"""

from __future__ import annotations

import html
import re

import streamlit as st

# Penanda blok sengaja longgar: model kadang menebalkan, memakai kurung
# tunggal, atau membungkusnya dalam pagar kode.
_OPEN = r"[`*_]*\[{1,2}\s*KARTU\s*:\s*([a-zA-Z_]+)\s*\]{1,2}[`*_]*"
_CLOSE = r"[`*_]*\[{1,2}\s*/\s*KARTU\s*\]{1,2}[`*_]*"
_CARD_RE = re.compile(_OPEN + r"(.*?)" + _CLOSE, re.S | re.I)

# nama lain yang mungkin dipakai model -> nama baku kita
_ALIAS = {
    "banding": "perbandingan", "bandingkan": "perbandingan",
    "compare": "perbandingan", "comparison": "perbandingan",
    "langkah_langkah": "langkah", "steps": "langkah", "step": "langkah",
    "panduan": "langkah", "tutorial": "langkah",
    "tautan": "link", "referensi": "link", "sumber": "link", "links": "link",
}


def _baris_bersih(isi: str) -> list[str]:
    out = []
    for b in (isi or "").splitlines():
        b = b.strip().strip("`")
        if b:
            out.append(b)
    return out


def parse_cards(text: str) -> tuple[str, list[dict]]:
    """Pisahkan semua blok [[KARTU:...]] dari teks jawaban.

    SELALU mengembalikan (teks_bersih, daftar_kartu) — tidak pernah None.
    """
    raw = text or ""
    try:
        if "KARTU" not in raw.upper():
            return raw, []

        # Buka pagar kode yang isinya memang blok kartu.
        def _buka(m):
            return m.group(1) if re.search(_OPEN, m.group(0), re.I) else m.group(0)

        kerja = re.sub(r"```[a-zA-Z]*\n(.*?)```", _buka, raw, flags=re.S)

        kartu_list: list[dict] = []

        def _ambil(m):
            jenis = (m.group(1) or "").lower()
            jenis = _ALIAS.get(jenis, jenis)
            baris = _baris_bersih(m.group(2))
            if baris:
                kartu_list.append({"type": jenis, "lines": baris})
            return ""

        bersih = _CARD_RE.sub(_ambil, kerja).strip()
        # rapikan baris kosong berlebih bekas blok yang diangkat
        bersih = re.sub(r"\n{3,}", "\n\n", bersih)
        return bersih, kartu_list
    except Exception:
        return raw, []


# ============================================================================
# RENDERER PER JENIS KARTU
# ============================================================================
def _esc(s: str) -> str:
    return html.escape((s or "").strip())


def _render_perbandingan(kartu: dict, kunci: str) -> None:
    """Dua kolom sejajar + baris spesifikasi bergaris pemisah."""
    baris = kartu["lines"]
    judul: list[str] = []
    spek: list[tuple[str, list[str]]] = []

    for b in baris:
        if ":" not in b:
            continue
        label, nilai = b.split(":", 1)
        kolom = [k.strip() for k in nilai.split("|")]
        if label.strip().lower() in ("judul", "nama", "title"):
            judul = kolom
        else:
            spek.append((label.strip(), kolom))

    if not judul:
        judul = [f"Opsi {i + 1}" for i in range(max((len(k) for _, k in spek), default=2))]
    n = len(judul)

    head = "".join(f'<div class="rc-cmp-head">{_esc(j)}</div>' for j in judul)
    rows = ""
    for label, kolom in spek:
        kolom = (kolom + [""] * n)[:n]
        sel = "".join(
            f'<div class="rc-cmp-cell">'
            f'<div class="rc-cmp-label">{_esc(label)}</div>'
            f'<div class="rc-cmp-value">{_esc(v)}</div></div>'
            for v in kolom
        )
        rows += f'<div class="rc-cmp-row">{sel}</div>'

    st.markdown(
        f'<div class="rc-card rc-cmp" style="--rc-cols:{n}">'
        f'<div class="rc-cmp-row rc-cmp-toprow">{head}</div>{rows}</div>',
        unsafe_allow_html=True,
    )


def _render_langkah(kartu: dict, kunci: str) -> None:
    """Satu langkah tampil per waktu + indikator bulat + tombol navigasi."""
    langkah: list[tuple[str, str]] = []
    for b in kartu["lines"]:
        b = re.sub(r"^(\d+[.)]|[-*•])\s*", "", b).strip()
        if not b:
            continue
        if "|" in b:
            j, d = b.split("|", 1)
        elif ":" in b:
            j, d = b.split(":", 1)
        else:
            j, d = b, ""
        langkah.append((j.strip(), d.strip()))

    if not langkah:
        return

    sk = f"_rc_step_{kunci}"
    idx = int(st.session_state.get(sk, 0))
    idx = max(0, min(idx, len(langkah) - 1))
    judul, desc = langkah[idx]

    dots = "".join(
        f'<span class="rc-dot{" on" if i == idx else ""}">{i + 1}</span>'
        for i in range(len(langkah))
    )
    st.markdown(
        f'<div class="rc-card rc-step">'
        f'<div class="rc-step-title">{_esc(judul)}</div>'
        f'<div class="rc-step-desc">{_esc(desc)}</div>'
        f'<div class="rc-step-dots">{dots}'
        f'<span class="rc-step-count">Langkah {idx + 1} dari {len(langkah)}</span>'
        f"</div></div>",
        unsafe_allow_html=True,
    )

    def _geser(d: int) -> None:
        st.session_state[sk] = max(0, min(idx + d, len(langkah) - 1))

    with st.container(key=f"rc_nav_{kunci}"):
        c1, c2 = st.columns(2)
        with c1:
            st.button("Sebelumnya", key=f"rc_prev_{kunci}", disabled=idx == 0,
                      use_container_width=True, on_click=_geser, args=(-1,))
        with c2:
            st.button("Berikutnya", key=f"rc_next_{kunci}",
                      disabled=idx >= len(langkah) - 1, type="primary",
                      use_container_width=True, on_click=_geser, args=(1,))


def _render_link(kartu: dict, kunci: str) -> None:
    """Daftar rujukan: judul bergaris bawah + ringkasan + nama sumber."""
    kartu_html = ""
    for b in kartu["lines"]:
        b = re.sub(r"^(\d+[.)]|[-*•])\s*", "", b).strip()
        bagian = [x.strip() for x in b.split("|")]
        if not bagian or not bagian[0]:
            continue
        judul = bagian[0]
        url = bagian[1] if len(bagian) > 1 else ""
        ket = bagian[2] if len(bagian) > 2 else ""
        sumber = ""
        if url:
            m = re.search(r"https?://([^/]+)", url)
            sumber = (m.group(1).replace("www.", "") if m else url)[:40]
        tautan = (f'<a class="rc-link-title" href="{_esc(url)}" target="_blank" '
                  f'rel="noopener">{_esc(judul)}</a>') if url else \
                 f'<span class="rc-link-title">{_esc(judul)}</span>'
        kartu_html += (
            f'<div class="rc-card rc-link">{tautan}'
            + (f'<div class="rc-link-desc">{_esc(ket)}</div>' if ket else "")
            + (f'<div class="rc-link-src">{_esc(sumber)}</div>' if sumber else "")
            + "</div>"
        )
    if kartu_html:
        st.markdown(kartu_html, unsafe_allow_html=True)


RENDERER = {
    "perbandingan": _render_perbandingan,
    "langkah": _render_langkah,
    "link": _render_link,
}


def render_cards(msg: dict) -> None:
    """Tampilkan semua kartu milik satu pesan Yuki."""
    daftar = msg.get("cards") or []
    if not daftar:
        return
    mid = msg.get("id", id(msg))
    for i, kartu in enumerate(daftar):
        fn = RENDERER.get((kartu.get("type") or "").lower())
        if not fn:
            continue
        try:
            fn(kartu, f"{mid}_{i}")
        except Exception:
            # Satu kartu bermasalah tidak boleh menjatuhkan seluruh halaman.
            continue
