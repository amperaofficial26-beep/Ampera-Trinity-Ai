# -*- coding: utf-8 -*-
"""
ROUTER NIAT — Yuki menebak sendiri apa yang diminta User.

Tujuannya: User tidak perlu bergonta-ganti mode. Cukup mengetik, lalu
aplikasi memutuskan sendiri:

    "buatkan gambar kucing"        -> BUAT GAMBAR  (FLUX)
    (lampirkan foto) "ini apa?"    -> ANALISIS     (model vision)
    "makasih ya"                   -> CHAT BIASA

Prinsip yang dipegang:

1. NAMA MODEL TIDAK BERUBAH. Yang dipilih otomatis hanyalah model yang
   DIPAKAI di balik layar. Label di UI (Trinity Seed, dst.) tetap
   seperti pilihan User — persis permintaan "tanpa mengubah nama model".

2. BUKTI MENANG ATAS KATA-KATA. Kalau ada gambar dilampirkan, itu
   analisis — titik. Tidak peduli kalimatnya berbunyi apa.

3. SEKALI JALAN, BUKAN MENEMPEL. Selesai membuat gambar, kalimat
   berikutnya yang tidak mengandung perintah apa pun kembali dianggap
   chat biasa. Mode tidak "lengket".

4. MURAH DULU, BARU MAHAL. Penebakan memakai pencocokan kata (nol biaya,
   nol latensi). Model AI hanya dipanggil untuk kalimat yang benar-benar
   ambigu, itu pun dibatasi 5 token.

Dipakai chat_handlers.py:
    from niat import tebak_niat
    niat = tebak_niat(teks, punya_gambar=bool(images))
"""

from __future__ import annotations

import re

import streamlit as st

# Tiga kemungkinan hasil.
CHAT = "chat"
GAMBAR = "gambar"      # buat gambar baru (FLUX)
ANALISIS = "analisis"  # lihat/analisis gambar yang dilampirkan


# ============================================================================
# KATA KUNCI
# ============================================================================
# Kata kerja yang berarti "hasilkan gambar baru".
_KERJA_BUAT = (
    r"buat(?:kan|in)?|bikin(?:kan|in)?|gambar(?:kan|in)?|lukis(?:kan)?|"
    r"desain(?:kan|in)?|rancang(?:kan)?|render|generate|gen|create|draw|"
    r"paint|design|sketsa|ilustrasi(?:kan)?|visualisasi(?:kan)?"
)

# Kata benda yang menandakan objeknya memang gambar.
_BENDA_GAMBAR = (
    r"gambar|foto|poster|logo|ilustrasi|sketsa|lukisan|wallpaper|banner|"
    r"thumbnail|avatar|ikon|icon|desain|design|image|picture|art|artwork|"
    r"mockup|komik|karikatur|potret"
)

# "buatkan gambar ...", "bikin poster ...", "generate image of ..."
_POLA_BUAT_GAMBAR = re.compile(
    rf"\b(?:{_KERJA_BUAT})\b[^.!?\n]{{0,40}}?\b(?:{_BENDA_GAMBAR})\b",
    re.I,
)

# Bentuk terbalik: "gambar seekor naga", "foto pemandangan gunung"
# Dibatasi: harus diikuti kata benda, bukan tanda tanya (itu pertanyaan).
_POLA_GAMBAR_DULU = re.compile(
    rf"^\s*(?:tolong\s+|coba\s+|minta\s+)?(?:{_BENDA_GAMBAR})\s+"
    r"(?:seekor|sebuah|seorang|sebatang|tentang|dari|of|a|an)\b",
    re.I,
)

# Kata kerja yang SUDAH berarti "menghasilkan gambar" tanpa perlu kata
# benda: "gambarkan naga", "lukiskan pemandangan", "sketsakan wajah".
# Dipisah dari _POLA_BUAT_GAMBAR karena di sana objeknya wajib berupa
# kata benda gambar — padahal di sini kata kerjanya sendiri sudah cukup.
_POLA_KERJA_VISUAL = re.compile(
    r"^\s*(?:tolong\s+|coba\s+|minta\s+|please\s+)?"
    r"(?:gambar(?:kan|in)|lukis(?:kan)?|sketsa(?:kan)?|"
    r"ilustrasikan|visualisasikan|draw|paint|sketch)\b\s+\S",
    re.I,
)

# Kata kerja "lihat/analisis" untuk gambar yang SUDAH ada.
_POLA_ANALISIS = re.compile(
    r"\b(?:analisa|analisis|analyze|periksa|cek|check|baca|read|"
    r"jelas(?:kan)?|terangkan|describe|deskripsi(?:kan)?|"
    r"apa\s+(?:ini|itu|isi|yang)|tulisan\s+(?:apa|di)|"
    r"ada\s+apa|siapa\s+(?:ini|itu|di)|"
    r"terjemah(?:kan)?|translate|ocr|"
    r"menurutmu|bagaimana\s+(?:menurut|pendapat))\b",
    re.I,
)

# Penyangkal: kalimat TENTANG gambar, tapi bukan minta dibuatkan.
# "cara membuat gambar di photoshop", "apa itu AI gambar?"
_POLA_BUKAN_PERINTAH = re.compile(
    r"\b(?:cara|bagaimana|gimana|how\s+to|tutorial|tips|belajar|"
    r"apa\s+itu|apa\s+bedanya|jelaskan\s+tentang|kenapa|mengapa|"
    r"rekomendasi|aplikasi\s+apa|software|situs|website)\b",
    re.I,
)

# Lanjutan pada gambar yang baru dibuat: "lagi", "versi malam", "ubah warnanya"
_POLA_LANJUTAN_GAMBAR = re.compile(
    r"^\s*(?:lagi|sekali\s+lagi|ulangi|coba\s+lagi|satu\s+lagi|"
    r"versi\s+\w+|ubah\s+|ganti\s+|tambah(?:kan)?\s+|"
    r"bikin\s+lagi|buat\s+lagi|yang\s+\w+\s+dong|lebih\s+\w+)",
    re.I,
)


# ============================================================================
# PENEBAK
# ============================================================================
def _bersih(teks: str) -> str:
    return " ".join((teks or "").split()).strip()


def tebak_cepat(teks: str, punya_gambar: bool = False,
                baru_buat_gambar: bool = False) -> tuple[str, float]:
    """Tebak niat dari pola kata. Return (niat, keyakinan 0..1).

    Keyakinan < 0.6 berarti ambigu — pemanggil boleh minta bantuan AI.
    """
    t = _bersih(teks)

    # --- 1. BUKTI: ada gambar dilampirkan -> pasti analisis ----------
    # Ini menang atas apa pun. User melampirkan foto = mau dibahas.
    if punya_gambar:
        return ANALISIS, 1.0

    if not t:
        return CHAT, 1.0

    # --- 2. Penyangkal: kalimat bertanya TENTANG gambar --------------
    # "cara membuat gambar di canva" bukan permintaan bikin gambar.
    if _POLA_BUKAN_PERINTAH.search(t):
        return CHAT, 0.85

    # --- 3. Pola perintah buat gambar --------------------------------
    if _POLA_BUAT_GAMBAR.search(t):
        return GAMBAR, 0.95
    if _POLA_KERJA_VISUAL.search(t):
        return GAMBAR, 0.9
    if _POLA_GAMBAR_DULU.search(t):
        return GAMBAR, 0.8

    # --- 4. Lanjutan sesudah gambar dibuat ---------------------------
    # "lagi dong", "versi malam" — hanya berlaku kalau pesan SEBELUMNYA
    # memang gambar. Tanpa syarat ini, kata "lagi" di obrolan biasa akan
    # salah dianggap minta gambar.
    if baru_buat_gambar and _POLA_LANJUTAN_GAMBAR.search(t) and len(t) < 60:
        return GAMBAR, 0.75

    # --- 5. Minta analisis tapi tidak melampirkan gambar -------------
    # Biarkan jadi CHAT: Yuki sendiri yang akan bilang "fotonya mana?".
    if _POLA_ANALISIS.search(t) and re.search(
        rf"\b(?:{_BENDA_GAMBAR})\b", t, re.I
    ):
        return CHAT, 0.7

    return CHAT, 0.65


_PROMPT_NIAT = (
    "Klasifikasikan permintaan user ke SATU kata saja:\n"
    "gambar = minta DIBUATKAN gambar/foto/poster/logo baru\n"
    "chat   = selain itu (tanya, ngobrol, minta teks/kode/saran)\n\n"
    "Jawab HANYA satu kata: gambar atau chat.\n\n"
    "Permintaan: "
)


def _tanya_ai(teks: str) -> str | None:
    """Minta model kecil memutuskan. Return niat, atau None kalau gagal.

    Dibatasi 5 token & timeout 8 detik supaya tidak menambah latensi
    yang terasa. Kegagalan apa pun -> None (pemanggil pakai tebakan pola).
    """
    try:
        from config import AVAILABLE_MODELS, DEFAULT_MODEL_KEY
        from engines.groq_engine import build_chat_client

        client = build_chat_client()
        resp = client.chat.completions.create(
            model=AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
            messages=[{"role": "user", "content": _PROMPT_NIAT + teks[:300]}],
            temperature=0,
            max_tokens=5,
            stream=False,
            timeout=8,
        )
        jawab = (resp.choices[0].message.content or "").strip().lower()
        if "gambar" in jawab or "image" in jawab:
            return GAMBAR
        if "chat" in jawab:
            return CHAT
    except Exception:
        pass
    return None


def tebak_niat(teks: str, punya_gambar: bool = False,
               pakai_ai: bool = True) -> str:
    """Tentukan niat User: CHAT, GAMBAR, atau ANALISIS.

    punya_gambar : True kalau pesan ini membawa lampiran gambar.
    pakai_ai     : boleh memanggil model kecil untuk kasus ambigu.
    """
    baru = bool(st.session_state.get("_niat_terakhir") == GAMBAR)
    niat, yakin = tebak_cepat(teks, punya_gambar, baru_buat_gambar=baru)

    # Hanya kasus benar-benar ambigu yang dilempar ke AI, dan hanya
    # kalau kalimatnya cukup panjang untuk bermakna.
    if pakai_ai and yakin < 0.7 and len(_bersih(teks)) > 12:
        try:
            if st.session_state.get("_niat_ai_gagal", 0) < 3:
                hasil = _tanya_ai(teks)
                if hasil:
                    niat = hasil
                else:
                    st.session_state["_niat_ai_gagal"] = (
                        st.session_state.get("_niat_ai_gagal", 0) + 1
                    )
        except Exception:
            pass

    st.session_state["_niat_terakhir"] = niat
    return niat


def label_mode(niat: str) -> str:
    """Keterangan singkat untuk ditampilkan di UI."""
    return {
        GAMBAR: "Mode gambar otomatis",
        ANALISIS: "Menganalisis gambar",
    }.get(niat, "")
