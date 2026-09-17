# -*- coding: utf-8 -*-
"""
Sinkronisasi riwayat chat utama ke database cloud (Supabase).

Fitur "riwayat chat tersimpan": setiap pesan baru di halaman Chat dikirim
ke tabel `chat_messages` di Supabase. Saat user login dengan akun Google,
SEMUA percakapan lamanya dimuat ke menu "Riwayat" di sidebar, dan user
selalu mulai dengan PERCAKAPAN BARU yang bersih. Riwayat tidak hilang
walau aplikasi di-refresh, tab ditutup, atau dibuka dari HP/laptop lain.

CARA MENGAKTIFKAN:
Pasang SUPABASE_URL dan SUPABASE_ANON_KEY di Streamlit Secrets (atau
environment variable). Tanpa kedua kunci itu, semua fungsi di file ini
diam saja — aplikasi jalan normal seperti sebelumnya (riwayat per-sesi).

CATATAN V1:
- Hanya chat utama. Riwayat halaman Artefak / Trinity Kursus / mode
  khusus (desain, jadwal) tetap per-sesi dan tidak disimpan.
- Pesan gambar disimpan TANPA file gambarnya (byte gambar terlalu besar
  untuk database gratis). Saat dimuat, pesan itu tampil sebagai teks
  keterangan berisi prompt-nya.
- Semua kegagalan jaringan ditelan diam-diam supaya pengalaman chat
  tidak pernah terganggu oleh masalah database.
"""

from __future__ import annotations

import json
import threading
import urllib.parse
import uuid

import requests
import streamlit as st

_TIMEOUT_KIRIM = 10  # detik — pengiriman lewat thread kecil
_TIMEOUT_MUAT = 12   # detik — hanya sekali saat login


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
# SIMPAN — dipanggil dari render_message() untuk setiap pesan chat utama
# ---------------------------------------------------------------------------
def kirim_pesan_baru(msg: dict) -> None:
    """Kirim SATU pesan chat utama ke database.

    Aman dipanggil berulang kali (setiap halaman digambar ulang): pesan
    yang sudah pernah dikirim tidak dikirim dua kali. Pengiriman HTTP
    dikerjakan thread kecil supaya UI tidak pernah menunggu database.
    """
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

        email = (st.session_state.get("_user_google") or {}).get("email", "")
        bersih = dict(msg)
        # Byte gambar tidak disimpan (terlalu besar): hasil gambar Yuki
        # dan lampiran gambar user cukup catatan kecilnya saja.
        if bersih.get("type") == "image":
            bersih["image_bytes"] = None
        if bersih.get("images"):
            bersih["images"] = [
                {"name": im.get("name", "gambar"), "mime": im.get("mime", "")}
                for im in bersih["images"] if isinstance(im, dict)
            ]
        # Serialisasi di thread utama (default=str menangani tipe aneh),
        # lalu dikirim sebagai JSON murni dari thread kecil.
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
        requests.post(
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
    except Exception:
        pass


# ---------------------------------------------------------------------------
# MUAT — dipanggil sekali oleh welcome_gate setelah login Google sukses
# ---------------------------------------------------------------------------
def muat_riwayat_setelah_login() -> None:
    """Isi ulang semua percakapan user dari database.

    Dipanggil tepat setelah login Google sukses, saat session state masih
    kosong. Bila Supabase tidak terpasang / koneksi gagal / data kosong,
    fungsi ini diam saja dan aplikasi mulai dengan chat bersih.
    """
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

        # Kelompokkan baris per percakapan (conv_key); urutan grup =
        # urutan kemunculan pertamanya (kronologis).
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

        # Bangun ulang daftar percakapan ala state.py: {id, title,
        # messages, conv_key}. Nomor id pesan diberi ulang berurutan
        # supaya unik satu sesi.
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

        # Setelah login, user selalu mulai dengan PERCAKAPAN BARU yang
        # bersih (bukan lanjut di percakapan terakhir). Semua percakapan
        # lama dari database masuk ke menu "Riwayat" di sidebar —
        # urutannya yang terbaru di atas. Klik salah satunya untuk
        # membukanya kembali.
        st.session_state.messages = []
        st.session_state.active_conv_id = None
        st.session_state.conv_key = uuid.uuid4().hex
        st.session_state.conversations = list(reversed(convs))
        st.session_state.conv_counter = len(convs)
        st.session_state.msg_counter = nomor_id
        # Tandai semua pesan yang dimuat sebagai "sudah tersimpan" supaya
        # tidak dikirim ulang ke database.
        st.session_state["_db_synced"] = {
            (c["conv_key"], m["id"]) for c in convs for m in c["messages"]
        }
    except Exception:
        pass


def _pesan_dari_data(d: dict) -> dict:
    """Ubah satu baris database menjadi pesan siap-render.

    Pesan gambar (byte tidak disimpan) menjadi teks keterangan. Lampiran
    gambar user tidak dipulihkan (thumbnail-nya butuh byte asli).
    """
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


# ---------------------------------------------------------------------------
# HAPUS — alat bantu bila suatu saat ingin mengosongkan riwayat seorang user
# ---------------------------------------------------------------------------
def hapus_riwayat(email: str = "") -> bool:
    """Hapus seluruh riwayat seorang user dari database.

    Return True HANYA bila server benar-benar mengonfirmasi baris
    terhapus. Dipakai riwayat.py saat user menekan "Bersihkan riwayat
    obrolan" — kalau ini gagal diam-diam, riwayat akan dimuat ulang oleh
    muat_riwayat_setelah_login() pada login berikutnya dan user mengira
    penghapusannya tidak berfungsi.
    """
    try:
        email = (email or (st.session_state.get("_user_google") or {})
                 .get("email", "")).strip()
        if not email or not siap():
            return False
        # Prefer: return=representation membuat Supabase mengirim balik
        # baris yang dihapus. Tanpa ini DELETE menjawab 200/204 walaupun
        # TIDAK ADA baris yang cocok (mis. kebijakan RLS memblokirnya),
        # sehingga kegagalan terbaca sebagai sukses.
        headers = dict(_headers())
        headers["Prefer"] = "return=representation"
        r = requests.delete(
            _url("/rest/v1/chat_messages?user_email=eq."
                 + urllib.parse.quote(email, safe="")),
            headers=headers,
            timeout=_TIMEOUT_MUAT,
        )
        if r.status_code not in (200, 204):
            return False

        # Pastikan lewat pembacaan ulang: kalau masih ada baris tersisa,
        # penghapusan dianggap GAGAL walau status HTTP-nya sukses.
        cek = requests.get(
            _url("/rest/v1/chat_messages?select=id&limit=1&user_email=eq."
                 + urllib.parse.quote(email, safe="")),
            headers=_headers(),
            timeout=_TIMEOUT_MUAT,
        )
        if cek.status_code == 200 and (cek.json() or []):
            return False
        return True
    except Exception:
        return False
