# -*- coding: utf-8 -*-
"""
Sinkronisasi riwayat chat utama ke database cloud (Supabase).

>>> VERSI DIAGNOSA SEMENTARA <<<
Versi ini sama dengan versi normal, tetapi menampilkan popup "DB-..."
supaya masalah koneksi bisa terlihat jelas. Setelah semuanya beres,
akan diganti kembali dengan versi bersih.
"""

from __future__ import annotations

import json
import threading
import urllib.parse

import requests
import streamlit as st

_TIMEOUT_KIRIM = 10  # detik — pengiriman lewat thread kecil
_TIMEOUT_MUAT = 12   # detik — hanya sekali saat login

# DEBUG: hasil POST terakhir dari thread kecil (kode HTTP / nama galat)
_HASIL_KIRIM: dict = {"kode": None}


# ---------------------------------------------------------------------------
# KUNCI & KONEKSI
# ---------------------------------------------------------------------------
def _secret(nama: str) -> str:
    """Baca kunci dari st.secrets; kalau tidak ada, coba environment var."""
    try:
        nilai = st.secrets.get(nama)
        if nilai:
            return str(nilai).strip()
    except Exception:
        pass
    try:
        import os
        return (os.environ.get(nama) or "").strip()
    except Exception:
        return ""


def siap() -> bool:
    """True bila sinkronisasi database aktif (kunci terpasang + user login)."""
    try:
        user = st.session_state.get("_user_google") or {}
        return bool(user.get("email")
                    and _secret("SUPABASE_URL")
                    and _secret("SUPABASE_ANON_KEY"))
    except Exception:
        return False


def _headers() -> dict:
    key = _secret("SUPABASE_ANON_KEY")
    return {
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    return _secret("SUPABASE_URL").rstrip("/") + path


# ---------------------------------------------------------------------------
# DEBUG SEMENTARA — popup pemeriksaan (dihapus setelah masalah selesai)
# ---------------------------------------------------------------------------
def _debug_pesan(teks: str) -> None:
    try:
        st.toast(teks, icon="🔧")
    except Exception:
        pass


def _debug_periksa() -> None:
    """Sekali per sesi: periksa kunci + koneksi, toast hasil berkode DB-x."""
    if st.session_state.get("_db_debug_jalan"):
        return
    st.session_state["_db_debug_jalan"] = True
    try:
        user = st.session_state.get("_user_google") or {}
        if not user.get("email"):
            _debug_pesan("DB-A: belum login Google")
            return
        u = _secret("SUPABASE_URL")
        k = _secret("SUPABASE_ANON_KEY")
        if not u and not k:
            _debug_pesan("DB-B: SUPABASE_URL dan KEY dua-duanya kosong")
            return
        if not u:
            _debug_pesan("DB-C: SUPABASE_URL kosong (KEY ada)")
            return
        if not k:
            _debug_pesan("DB-D: SUPABASE_ANON_KEY kosong (URL ada)")
            return
        if not u.startswith("https://") or "[" in u or "]" in u or "(" in u:
            _debug_pesan("DB-E: SUPABASE_URL rusak isinya: " + u[:50])
            return
        try:
            r = requests.get(
                _url("/rest/v1/chat_messages?select=id&limit=1"),
                headers=_headers(), timeout=10,
            )
            if r.status_code == 200:
                _debug_pesan("DB-F: kunci terbaca + koneksi Supabase OK")
            else:
                _debug_pesan("DB-G: terhubung tapi server jawab kode "
                             + str(r.status_code))
        except Exception as e:
            _debug_pesan("DB-H: tidak bisa terhubung (" + type(e).__name__ + ")")
    except Exception as e:
        _debug_pesan("DB-Z: error pemeriksaan " + repr(e)[:60])


def _debug_lapor_kirim() -> None:
    """Laporkan (sekali) hasil POST pesan sebelumnya dari thread kecil."""
    try:
        if _HASIL_KIRIM["kode"] is None:
            return
        if st.session_state.get("_db_lapor_kirim"):
            return
        st.session_state["_db_lapor_kirim"] = True
        kode = _HASIL_KIRIM["kode"]
        if isinstance(kode, int) and kode in (200, 201, 204):
            _debug_pesan("DB-K: pesan BERHASIL tersimpan ke database")
        else:
            _debug_pesan("DB-J: gagal kirim ke database, kode " + str(kode))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# SIMPAN — dipanggil dari render_message() untuk setiap pesan chat utama
# ---------------------------------------------------------------------------
def kirim_pesan_baru(msg: dict) -> None:
    """Kirim SATU pesan chat utama ke database."""
    _debug_periksa()
    if not siap():
        return
    try:
        mid = msg.get("id")
        conv_key = st.session_state.get("conv_key")
        if mid is None or not conv_key:
            return
        tag = (conv_key, mid)
        sudah = st.session_state.get("_db_synced")
        if sudah is None:
            sudah = set()
            st.session_state["_db_synced"] = sudah
        if tag in sudah:
            return
        sudah.add(tag)
        _debug_lapor_kirim()

        email = (st.session_state.get("_user_google") or {}).get("email", "")
        bersih = dict(msg)
        if bersih.get("type") == "image":
            bersih["image_bytes"] = None
        if bersih.get("images"):
            bersih["images"] = [
                {"name": im.get("name", "gambar"), "mime": im.get("mime", "")}
                for im in bersih["images"] if isinstance(im, dict)
            ]
        payload = json.loads(json.dumps(bersih, ensure_ascii=False, default=str))
        threading.Thread(
            target=_kirim_baris,
            args=(email, conv_key, str(mid), payload),
            daemon=True,
        ).start()
    except Exception:
        pass


def _kirim_baris(email: str, conv_key: str, msg_id: str, data: dict) -> None:
    """POST satu baris ke tabel chat_messages (jalan di thread kecil)."""
    try:
        r = requests.post(
            _url("/rest/v1/chat_messages"),
            headers={**_headers(), "Prefer": "return=minimal"},
            json={
                "user_email": email,
                "conv_key": conv_key,
                "msg_id": msg_id,
                "data": data,
            },
            timeout=_TIMEOUT_KIRIM,
        )
        _HASIL_KIRIM["kode"] = r.status_code
    except Exception as e:
        _HASIL_KIRIM["kode"] = type(e).__name__


# ---------------------------------------------------------------------------
# MUAT — dipanggil sekali oleh welcome_gate setelah login Google sukses
# ---------------------------------------------------------------------------
def muat_riwayat_setelah_login() -> None:
    """Isi ulang semua percakapan user dari database."""
    try:
        if not siap():
            return
        if st.session_state.get("messages"):
            return  # sesi sudah punya isi; jangan ditimpa
        email = (st.session_state.get("_user_google") or {}).get("email", "")
        r = requests.get(
            _url("/rest/v1/chat_messages?select=conv_key,data&user_email=eq."
                 + urllib.parse.quote(email, safe="") + "&order=id.asc"),
            headers=_headers(),
            timeout=_TIMEOUT_MUAT,
        )
        if r.status_code != 200:
            return
        baris = r.json() or []
        if not isinstance(baris, list) or not baris:
            return

        grup: dict = {}
        for b in baris:
            if not isinstance(b, dict):
                continue
            data = b.get("data")
            if not isinstance(data, dict):
                continue
            key = str(b.get("conv_key") or "umum")
            grup.setdefault(key, []).append(data)
        if not grup:
            return

        convs = []
        nomor_id = 0
        for key, daftar in grup.items():
            msgs = []
            for d in daftar:
                nomor_id += 1
                m = _pesan_dari_data(d)
                m["id"] = nomor_id
                msgs.append(m)
            convs.append({
                "id": len(convs) + 1,
                "title": _judul(msgs),
                "messages": msgs,
                "conv_key": key,
            })

        aktif = convs[-1]
        arsip = convs[:-1]
        st.session_state.messages = aktif["messages"]
        st.session_state.active_conv_id = aktif["id"]
        st.session_state.conv_key = aktif["conv_key"]
        st.session_state.conversations = list(reversed(arsip))
        st.session_state.conv_counter = len(convs)
        st.session_state.msg_counter = nomor_id
        st.session_state["_db_synced"] = {
            (c["conv_key"], m["id"]) for c in convs for m in c["messages"]
        }
        _debug_pesan("DB-I: riwayat dimuat (" + str(len(baris)) + " pesan)")
    except Exception:
        pass


def _pesan_dari_data(d: dict) -> dict:
    """Ubah satu baris database menjadi pesan siap-render."""
    m = {
        "role": d.get("role") or "assistant",
        "type": "text",
        "content": str(d.get("content") or ""),
        "time": d.get("time") or "",
    }
    if d.get("type") == "image":
        m["content"] = (
            "🖼️ Hasil gambar untuk: " + str(d.get("prompt") or "")
            + "  \n_(file gambarnya tidak tersimpan di riwayat — silakan "
            "minta Yuki membuat ulang bila perlu)_"
        )
    for k in ("via_voice", "cards", "quick_replies",
              "error_detail", "catatan_prompt"):
        if d.get(k) is not None:
            m[k] = d[k]
    return m


def _judul(messages: list) -> str:
    """Judul percakapan = potongan pesan user pertama (sama ala Claude)."""
    for m in messages:
        if m.get("role") == "user" and m.get("content"):
            t = " ".join(str(m["content"]).split())
            return t[:48] + ("…" if len(t) > 48 else "")
    return "Percakapan baru"


def hapus_riwayat(email: str = "") -> bool:
    """Hapus seluruh riwayat seorang user dari database."""
    try:
        email = (email or (st.session_state.get("_user_google") or {})
                 .get("email", "")).strip()
        if not email or not siap():
            return False
        r = requests.delete(
            _url("/rest/v1/chat_messages?user_email=eq."
                 + urllib.parse.quote(email, safe="")),
            headers=_headers(),
            timeout=_TIMEOUT_MUAT,
        )
        return r.status_code in (200, 204)
    except Exception:
        return False
