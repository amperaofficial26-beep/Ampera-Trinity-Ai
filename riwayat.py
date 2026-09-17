# -*- coding: utf-8 -*-
"""
BERSIHKAN RIWAYAT OBROLAN.

Semua logika penghapusan riwayat dikumpulkan di sini supaya tombol di
sidebar dan di Pengaturan > Privasi memakai jalur yang sama persis —
tidak ada satu tempat yang lupa membersihkan sesuatu.

Aturan penting yang dipegang modul ini:

1. HAPUS ITU PERMANEN -> selalu minta konfirmasi dua langkah.
   Tidak ada penghapusan yang terjadi hanya karena satu klik.

2. Bersihkan JUGA turunannya. Sekadar mengosongkan `conversations`
   menyisakan obrolan yang sedang terbuka di layar, penghitung pesan,
   dan lampiran yang menunggu dikirim — user merasa "riwayatnya balik
   lagi" padahal itu sisa state.

3. Ikut menghapus di database (db_sync) kalau user memakai cloud sync.
   Fungsi db_sync.hapus_riwayat() sudah lama ada tapi belum pernah
   dipanggil UI mana pun.

Isi:
  - ringkasan_riwayat()   : hitung berapa obrolan & pesan yang tersimpan
  - bersihkan_riwayat()   : hapus riwayat (arsip + obrolan aktif)
  - dialog_bersihkan()    : UI konfirmasi dua langkah (dipakai 2 tempat)
"""

from __future__ import annotations

import uuid

import streamlit as st

# Kunci session_state yang ikut dibersihkan bersama riwayat.
# Dipisah jadi konstanta supaya kalau nanti ada state baru yang
# berhubungan dengan obrolan, cukup ditambahkan di sini sekali.
_KUNCI_OBROLAN = (
    "messages",          # obrolan yang sedang terbuka
    "conversations",     # daftar arsip di sidebar
    "active_conv_id",    # penanda arsip yang sedang dibuka
    "msg_counter",       # penomoran pesan
    "conv_counter",      # penomoran percakapan
    "pending_images",    # lampiran yang belum terkirim
    "_yuki_dihentikan",  # catatan "anda menghentikan respon yuki"
    "_db_synced",        # penanda pesan yang sudah dikirim ke database
)

# Thread milik halaman lain (Desain, Jadwal, Artefak, Kursus) disimpan
# dengan awalan kunci berikut. Ikut dihapus HANYA kalau user memilih
# "termasuk mode lain".
_AWALAN_THREAD_LAIN = ("mode_thread_", "artifact_thread_", "course_thread_")


def ringkasan_riwayat() -> dict:
    """Hitung isi riwayat: berapa obrolan tersimpan & total pesannya."""
    convs = st.session_state.get("conversations") or []
    aktif = st.session_state.get("messages") or []

    pesan_arsip = sum(len(c.get("messages") or []) for c in convs)
    punya_aktif = any(m.get("role") == "user" for m in aktif)

    return {
        "obrolan": len(convs) + (1 if punya_aktif else 0),
        "pesan": pesan_arsip + (len(aktif) if punya_aktif else 0),
        "kosong": not convs and not punya_aktif,
    }


def _hapus_thread_lain() -> int:
    """Hapus thread halaman Desain/Jadwal/Artefak/Kursus. Return jumlahnya."""
    kunci = [
        k for k in list(st.session_state.keys())
        if isinstance(k, str) and k.startswith(_AWALAN_THREAD_LAIN)
    ]
    for k in kunci:
        st.session_state.pop(k, None)
    return len(kunci)


def bersihkan_riwayat(termasuk_mode_lain: bool = False,
                      hapus_di_cloud: bool = True) -> dict:
    """Hapus riwayat obrolan. Return ringkasan apa saja yang terhapus.

    termasuk_mode_lain : ikut hapus thread Desain, Jadwal, Artefak, Kursus.
    hapus_di_cloud     : ikut hapus di database kalau cloud sync menyala.
    """
    sebelum = ringkasan_riwayat()

    # --- database ----------------------------------------------------
    # Dicoba SEBELUM state lokal dikosongkan, karena butuh email user
    # yang tersimpan di session_state.
    #
    # Syaratnya sama persis dengan penyimpanan (ui_helpers.py memanggil
    # db_sync.kirim_pesan_baru() yang cuma memeriksa siap()): kalau
    # pesannya bisa masuk database, penghapusannya juga harus jalan.
    cloud = None
    if hapus_di_cloud:
        try:
            import db_sync
            if db_sync.siap():
                cloud = db_sync.hapus_riwayat()
        except Exception:
            cloud = False

    # --- state lokal --------------------------------------------------
    for k in _KUNCI_OBROLAN:
        st.session_state.pop(k, None)

    jml_lain = _hapus_thread_lain() if termasuk_mode_lain else 0

    # Kunci percakapan baru: pesan setelah ini masuk kelompok baru di
    # database, tidak menyambung ke riwayat yang barusan dihapus.
    st.session_state["conv_key"] = uuid.uuid4().hex

    # Nilai bawaan dipasang ulang lewat init_state() supaya tidak ada
    # kunci yang hilang dan menyebabkan KeyError di halaman lain.
    from state import init_state
    init_state()

    return {
        "obrolan": sebelum["obrolan"],
        "pesan": sebelum["pesan"],
        "mode_lain": jml_lain,
        "cloud": cloud,   # True/False = dicoba, None = tidak dipakai
    }


def dialog_bersihkan(konteks: str = "set") -> bool:
    """UI konfirmasi dua langkah. Return True kalau riwayat baru dihapus.

    konteks : awalan kunci widget — WAJIB berbeda antara pemanggil
              (sidebar vs Pengaturan), kalau sama Streamlit melempar
              DuplicateWidgetID saat keduanya tampil bersamaan.
    """
    info = ringkasan_riwayat()
    kunci_tahap = f"_bersih_riwayat_tahap_{konteks}"

    if info["kosong"]:
        st.caption("Belum ada riwayat obrolan yang tersimpan.")
        return False

    # ---- tahap 1: tombol pembuka ------------------------------------
    if not st.session_state.get(kunci_tahap):
        st.caption(
            f"Tersimpan **{info['obrolan']} obrolan** "
            f"({info['pesan']} pesan)."
        )
        if st.button(":material/delete_sweep:  Bersihkan riwayat obrolan",
                     key=f"{konteks}_bersih_mulai", use_container_width=True):
            st.session_state[kunci_tahap] = True
            st.rerun()
        return False

    # ---- tahap 2: konfirmasi ----------------------------------------
    st.warning(
        f"**{info['obrolan']} obrolan** ({info['pesan']} pesan) akan dihapus "
        "permanen. Tindakan ini tidak bisa dibatalkan.",
        icon=":material/warning:",
    )
    ikut_lain = st.checkbox(
        "Ikut hapus thread Desain, Jadwal, Artefak, dan Kursus",
        key=f"{konteks}_bersih_lain",
    )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Batal", key=f"{konteks}_bersih_batal",
                     use_container_width=True):
            st.session_state.pop(kunci_tahap, None)
            st.rerun()
    with b2:
        if st.button(":material/delete_forever:  Ya, hapus",
                     key=f"{konteks}_bersih_ya", type="primary",
                     use_container_width=True):
            hasil = bersihkan_riwayat(termasuk_mode_lain=ikut_lain)
            st.session_state.pop(kunci_tahap, None)

            pesan = f"{hasil['obrolan']} obrolan dihapus."
            if hasil["mode_lain"]:
                pesan += f" {hasil['mode_lain']} thread mode lain ikut dihapus."
            if hasil["cloud"] is False:
                # Jujur bahwa salinan di server masih ada — kalau tidak,
                # user mengira sudah bersih lalu terkejut riwayatnya
                # kembali saat login berikutnya.
                pesan += (
                    " Tapi salinan di server GAGAL dihapus — riwayat bisa "
                    "muncul lagi saat login berikutnya. Coba ulangi nanti."
                )
            st.session_state["_toast_riwayat"] = pesan

            st.session_state.page = "chat"
            st.rerun()
    return False


def tampilkan_toast_tertunda() -> None:
    """Tampilkan toast hasil penghapusan sesudah rerun.

    st.toast() yang dipanggil tepat sebelum st.rerun() ikut hilang,
    jadi pesannya dititipkan di session_state lalu ditampilkan di
    awal siklus berikutnya.
    """
    pesan = st.session_state.pop("_toast_riwayat", None)
    if pesan:
        st.toast(pesan, icon=":material/check:")
