# -*- coding: utf-8 -*-
"""
Handler inti pengiriman pesan: mode gambar (Cloudflare FLUX), mode chat
(Groq + streaming + fallback), kontrol di dalam kotak chat input
(menu ➕, toggle Gambar, popover pilihan model), dan pemrosesan kiriman
user (teks/gambar/suara) yang dipakai bersama oleh semua halaman chat
(chat utama, Artefak, Trinity kursus).
"""

from __future__ import annotations

import threading
import time
import base64
import io
import re

from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from config import (
    AVAILABLE_MODELS, DEFAULT_MODEL_KEY, IMAGE_INPUT_TYPES, IMAGE_READY,
    CHAT_READY, MAX_IMAGES_PER_MESSAGE, MODEL_BY_KEY, MODEL_CATALOG,
    VISION_MODEL_ID,
)
from engines.groq_engine import (
    build_chat_client,
    build_system_prompt,
    collect_images,
    stream_chat_with_fallback,
    transcribe_audio,
)
from engines.compatible_engine import (
    build_compatible_client,
    stream_compatible_reply,
)
from artifacts import ambil_artefak
from loading_params import (
    detect_loading_mode,
    loading_subject,
    param_loading_html,
    special_loading_html,
)
from model_dna import DNA_CSS, dna_header_html, active_node_css
from cards import parse_cards
from engines.image_engine import generate_image
from errors import public_error_chat, public_error_image
from icons import ICON_MIC
from state import active_thread, get_settings, next_msg_id
from ui_helpers import (
    _BOTTOM_RESET_CSS, _capture_artifacts_from_reply,
    bubble_html, image_progress_html, images_bubble_html,
    parse_quick_replies, THINKING_MIN_SECONDS,
)
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

def now_wib() -> str:
    return datetime.now(WIB).strftime("%H:%M")


# Catatan kecil di bawah jawaban, tampil setelah pengguna menekan tombol
# "Hentikan" — teksnya persis seperti yang diminta pengguna.
_CATATAN_DIHENTIKAN_HTML = (
    '<div style="text-align:center;font-size:12.5px;font-style:italic;'
    'color:#98a0ab;padding:0 6px 10px 2px;">'
    "anda menghentikan respon yuki...</div>"
)

# CSS tombol "Hentikan" yang mungil: font, tinggi, dan padding
# dirampingkan (pola .st-key-* sama seperti tombol sidebar di styles.py).
_STOP_BTN_CSS = (
    "<style>"
    ".st-key-yuki_stop_dok button, button.st-key-yuki_stop_dok {"
    "font-size:13px !important;"
    "min-height:30px !important;"
    "height:30px !important;"
    "padding:0.05rem 0.95rem !important;"
    "border-radius:999px !important;"
    "gap:6px !important;"
    "}"
    "</style>"
)


# --- Durasi tampilan kotak loading pembuatan gambar (detik) ---------------
# IMAGE_MIN_SECONDS : kotak minimal tampil selama ini walau API sudah selesai,
#                     supaya animasi shimmer sempat terlihat.
# IMAGE_DONE_SECONDS: jeda singkat pada keadaan "Selesai" sebelum gambar muncul.
# IMAGE_MAX_SECONDS : batas aman menunggu API sebelum dianggap timeout.
# Siklus frasa desain tetap 15 detik di loading_params.py; angka ini hanya
# mencegah kedipan jika API gambar menjawab sangat cepat.
IMAGE_MIN_SECONDS = float(THINKING_MIN_SECONDS)
IMAGE_DONE_SECONDS = 0.7
IMAGE_MAX_SECONDS = 200.0


def maybe_run_yuki(answer_slot) -> bool:
    job = st.session_state.pop("_yuki_job", None)
    if not job:
        return False
    # Pesan pengguna sudah tersimpan dan halaman sudah masuk ke rerun baru.
    # Job harus dimulai pada run ini juga; gerbang dua-rerun sebelumnya dapat
    # meninggalkan job tertunda sampai pengguna membuka percakapan baru.
    st.session_state.pop("_yuki_ui_flushed", None)
    
    if job.get("image_mode"):
        # Beri tahu kalau perpindahan mode terjadi otomatis, supaya User
        # paham kenapa jawabannya berupa gambar — bukan mode yang
        # "berubah sendiri tanpa sebab".
        if job.get("auto"):
            st.toast("Beralih ke mode gambar otomatis.",
                     icon=":material/auto_awesome:")
        handle_image_request(job.get("text") or "")
    else:
        handle_chat_request(answer_slot, request_text=job.get("text") or "")
    return True
# Blok kode (``` ... ```), kode inline (` ... `), dan blok kode tak
# tertutup — isinya TIDAK boleh dirapatkan saat merapikan jawaban Yuki
# supaya indentasi dan spasi di dalam kode tetap utuh.
_TEKS_TERLINDUNG_RE = re.compile(r"```.*?```|```.*$|`[^`\n]*`", re.S)

# Baris item daftar: "- ", "* ", "+ ", "• ", atau "1. " / "1) " (boleh menjorok)
_BARIS_DAFTAR_RE = re.compile(r"^\s*(?:[-*+\u2022]\s|\d+[.)]\s)")


def rapihkan_teks_chat(teks: str) -> str:
    """Merapikan jarak spasi dan enter jawaban Yuki tanpa merusak Markdown."""
    if not teks:
        return ""

    # 1) Sisihkan dulu semua blok/inline kode ke tempat aman.
    laci: list[str] = []

    def _sisihkan(m: re.Match) -> str:
        laci.append(m.group(0))
        return f"\x00RAPIH{len(laci) - 1}\x00"

    teks = _TEKS_TERLINDUNG_RE.sub(_sisihkan, teks)

    # 2) Rapikan tiap baris: spasi menggantung di ujung kanan dibuang,
    #    spasi/tab ganda di tengah kalimat dirapatkan jadi satu spasi,
    #    sedangkan indentasi kiri (daftar, kutipan) dibiarkan apa adanya.
    baris_bersih: list[str] = []
    for baris in teks.splitlines():
        baris = baris.rstrip()
        if not baris.strip():
            baris_bersih.append("")
            continue
        indentasi = baris[: len(baris) - len(baris.lstrip())]
        isi = re.sub(r"[ \t]{2,}", " ", baris.lstrip())
        baris_bersih.append(indentasi + isi)
    teks = "\n".join(baris_bersih)

    # 3) Rapikan daftar: baris kosong di antara dua item daftar (-, *, •,
    #    1. dst.) dihapus supaya itemnya rapat, bukan berjauhan.
    baris_list = teks.splitlines()
    rapat: list[str] = []
    for i, b in enumerate(baris_list):
        if (
            not b.strip()
            and rapat
            and _BARIS_DAFTAR_RE.match(rapat[-1])
            and i + 1 < len(baris_list)
            and _BARIS_DAFTAR_RE.match(baris_list[i + 1])
        ):
            continue
        rapat.append(b)
    teks = "\n".join(rapat)

    # 4) Rapikan jarak enter: baris kosong berlebih (lebih dari satu)
    #    disusutkan jadi tepat satu baris kosong.
    teks = re.sub(r"\n{3,}", "\n\n", teks)

    # 5) Kembalikan blok kode yang tadi disisihkan.
    for i, terlindung in enumerate(laci):
        teks = teks.replace(f"\x00RAPIH{i}\x00", terlindung)

    return teks.strip()
    

def handle_image_request(prompt: str) -> None:
    thread = active_thread()
    if not IMAGE_READY:
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": now_wib(),
        })
        return

    progress_slot = st.empty()
    result: dict = {"data": None, "error": None, "catatan": ""}

    def _worker() -> None:
        try:
            # FLUX hanya mampu membaca ±256 token; prompt yang lebih panjang
            # ditolak Cloudflare (HTTP 400). Ringkas/potong dulu di sini
            # supaya animasi loading tetap tampil selama proses berjalan.
            from engines.image_engine import ringkas_prompt_panjang
            prompt_siap, catatan = ringkas_prompt_panjang(prompt)
            result["catatan"] = catatan
            result["data"] = generate_image(prompt_siap)
        except Exception as exc:
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Render kotak loading SEKALI saja. Semua gerakan (shimmer berputar di
    # tepi kotak, sapuan kanvas, pergantian teks, bar progres) dijalankan
    # oleh CSS di browser sehingga tetap mulus walau server sedang menunggu
    # API. Jangan me-render ulang di dalam loop: setiap markdown() baru akan
    # mengganti node DOM dan me-reset animasi CSS dari nol (itu penyebab
    # shimmer terlihat diam/berkedip sebelumnya).
    # `special_loading_html()` berisi CSS + elemen bertumpuk. Renderer
    # Markdown dapat menutup tag <span> lebih awal dan menampilkan sisanya
    # sebagai teks kode; components.html merendernya sebagai dokumen HTML utuh.
    with progress_slot:
        components.html(
            special_loading_html(
                "design",
                loading_subject(prompt),
            ),
            height=62,
            scrolling=False,
        )
        if st.session_state.pop("_yuki_scroll_pending", False):
            _scroll_to_yuki_work_once()

    # Tunggu hasilnya. Kotak tetap tampil MINIMAL IMAGE_MIN_SECONDS detik
    # supaya animasinya sempat terlihat utuh (FLUX-schnell sering selesai
    # dalam 2-3 detik). Polling pakai sleep pendek TANPA render ulang, jadi
    # animasi CSS di browser tidak ter-reset.
    t0 = time.time()
    while worker.is_alive() and (time.time() - t0) < IMAGE_MAX_SECONDS:
        time.sleep(0.1)
    while (time.time() - t0) < IMAGE_MIN_SECONDS:
        time.sleep(0.1)
    worker.join(timeout=1.0)

    if result["error"] is None and result["data"]:
        # Tampilkan sebentar keadaan "Selesai" (animasi berhenti), lalu
        # kotak diganti oleh gambar hasilnya.
        progress_slot.markdown(image_progress_html(done=True), unsafe_allow_html=True)
        time.sleep(IMAGE_DONE_SECONDS)
        progress_slot.empty()
        st.session_state.pop("_last_image_error", None)
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "image",
            "image_bytes": result["data"], "prompt": prompt,
            "catatan_prompt": result.get("catatan") or None,
            "time": now_wib(),
        })
        return

    progress_slot.empty()

    if result["error"] is None and worker.is_alive():
        e: Exception = RuntimeError("timeout")
    else:
        e = result["error"] or RuntimeError("no image")

    # Simpan detail teknisnya supaya bisa dilihat di UI (expander "Detail
    # teknis" di bawah pesan error) — sebelumnya kegagalan bisa terasa
    # seperti "tidak terjadi apa-apa".
    detail = f"{type(e).__name__}: {e}"
    st.session_state["_last_image_error"] = detail

    msg = str(e)
    if not msg.startswith(("Layanan", "Kuota", "Server terlalu",
                           "Gagal membuat", "Respons terlalu")):
        msg = public_error_image(None, msg, e)
    thread.append({
        "id": next_msg_id(), "role": "assistant", "type": "text",
        "content": msg, "time": now_wib(), "error_detail": detail,
    })


def _get_model_provider(model_key: str) -> str:
    """Mengambil provider dari model yang dipilih."""
    model = MODEL_BY_KEY.get(model_key, {})
    return model.get("provider", "groq")
    

def _susun_balasan_yuki(full: str, thread: list[dict]) -> None:
    """Pascaproses teks jawaban Yuki lalu simpan sebagai pesan assistant.

    Dipakai baik saat jawaban selesai normal maupun saat dihentikan
    lewat tombol "Hentikan respons" (teksnya berupa potongan parsial).
    """
    # Pisahkan blok [[PILIHAN]]
    hasil = parse_quick_replies(full)

    if isinstance(hasil, (tuple, list)) and len(hasil) == 2:
        full, kartu = hasil
        kartu = kartu if isinstance(kartu, dict) else {}
    else:
        kartu = {}

    if not full:
        full = kartu.get("question") or "…"

    # Blok [[TUGAS]] di halaman AI Penjadwal
    if st.session_state.get("page") == "jadwal":
        try:
            from page_jadwal import serap_blok_tugas

            full, jml = serap_blok_tugas(full)

            if jml:
                st.toast(
                    f"{jml} tugas ditambahkan ke daftar.",
                    icon=":material/task_alt:",
                )
        except Exception:
            pass

    # Blok [[KARTU:...]]
    hasil_kartu = parse_cards(full)

    if isinstance(hasil_kartu, (tuple, list)) and len(hasil_kartu) == 2:
        full, kartu_kaya = hasil_kartu
        kartu_kaya = (
            kartu_kaya
            if isinstance(kartu_kaya, list)
            else []
        )
    else:
        kartu_kaya = []

    if not full:
        full = "Ini hasilnya ya!"

    # Simulator HTML harus diambil sebelum parser artefak.
    from interactive_simulation import (
        extract_interactive_html,
        is_interactive_request,
    )
    full, interactive_html = extract_interactive_html(
        full,
        allow_raw=is_interactive_request(thread),
    )

    # Blok kode biasa tetap diproses menjadi artefak.
    full, file_ids = ambil_artefak(full)

    full = rapihkan_teks_chat(full)
    
    if not full:
        full = (
            "Selesai! Filenya sudah kubuat ya."
            if file_ids
            else "…"
        )

    reply = {
        "id": next_msg_id(),
        "role": "assistant",
        "type": "text",
        "content": full,
        "time": now_wib(),
    }

    if file_ids:
        reply["artifact_ids"] = file_ids

    if kartu:
        reply["quick_replies"] = kartu

    if kartu_kaya:
        reply["cards"] = kartu_kaya

    if interactive_html:
        reply["interactive_html"] = (
            interactive_html
        )

    thread.append(reply)


def _finalisasi_stream_yuki(
    stream_state: dict,
) -> None:
    """Ubah hasil stream selesai, dihentikan, atau error menjadi pesan."""
    thread = active_thread()
    err = stream_state.get("err")
    full = "".join(
        stream_state.get("buf")
        or []
    )

    if err is not None:
        # Provider kadang menutup stream karena timeout setelah dokumen
        # simulator selesai terkirim. Selamatkan dokumen HTML lengkap.
        from interactive_simulation import (
            extract_interactive_html,
            is_interactive_request,
        )

        _, recovered_html = extract_interactive_html(
            full,
            allow_raw=is_interactive_request(
                thread
            ),
        )

        if recovered_html:
            _susun_balasan_yuki(
                full,
                thread,
            )
            return

        thread.append({
            "id": next_msg_id(),
            "role": "assistant",
            "type": "text",
            "content": public_error_chat(
                err
            ),
            "time": now_wib(),
            "error_detail": (
                f"{type(err).__name__}: {err}"
            ),
        })
        return

    _susun_balasan_yuki(
        full,
        thread,
    )


def _hentikan_dan_finalisasi_stream_lama() -> None:
    """Hentikan stream lama (kalau ada) lalu finalisasi potongannya.

    Dipanggil saat pengguna mengirim pesan baru di tengah jawaban Yuki
    yang sedang mengalir: jawaban lama dihentikan, potongan yang sudah
    tampil di layar disimpan, lalu pekerjaan baru dimulai. Finalisasi
    untuk tombol "Hentikan" TIDAK lewat sini — dikerjakan langsung oleh
    fragmen_jawaban_yuki() supaya selalu lewat jalur yang terbukti aman.
    """
    lama = st.session_state.pop("_yuki_stream", None)
    stop = st.session_state.pop("_yuki_stop", None)
    st.session_state.pop("_yuki_thread", None)
    st.session_state.pop("_yuki_t0", None)
    st.session_state.pop("_yuki_loader_tampil", None)

    # Jangan hapus mode/subjek loader di sini. Fungsi ini juga dipanggil
    # sesudah job baru dibuat, sehingga penghapusan tersebut membuat semua
    # tugas baru jatuh kembali ke loader chat biasa.
    if stop:
        stop.set()

    if not lama:
        return

    potongan = "".join(
        lama.get("buf")
        or []
    )

    if potongan.strip():
        _finalisasi_stream_yuki({
            "buf": [
                potongan,
            ],
            "err": None,
        })

# 0,15 detik ≈ 7 pembaruan/detik: teks terasa MENGALIR, bukan muncul
# per blok tiap 0,4 detik. Masih cukup longgar supaya Streamlit tidak
# kebanjiran rerun (0,1 detik ke bawah mulai membebani server).
@st.fragment(run_every=0.15)
def fragmen_jawaban_yuki() -> None:
    """Teks jawaban Yuki yang mengalir (fase setelah animasi berpikir).

    Dipanggil di tiap halaman chat, setelah daftar pesan. Selama stream
    berjalan di thread belakang, fragmen ini menyegarkan dirinya sendiri
    tiap 0,4 detik.

    Pembagian tugas:
    - Fase ANIMASI BERPIKIR (minimal THINKING_MIN_SECONDS): fragmen ini
      TIDAK merender apa pun. Animasinya dirender SEKALI oleh script
      utama lewat render_loader_yuki() — kalau dirender di sini,
      iframe-nya dibuat ulang tiap 0,4 detik dan animasinya jadi
      patah-patah/acak.
    - Fase TEKS MENGALIR: setelah durasi animasi terpenuhi, fragmen
      memicu satu rerun penuh (untuk menghapus loader statis), lalu
      menampilkan teks jawaban yang terus diperbarui.
    - Tombol "Hentikan respons" ada di KOTAK INPUT (chat_input_atau_
      hentikan): tombol kirim berubah jadi tombol berhenti.
    """
    # Catatan "anda menghentikan respon yuki..." dirender DI DALAM fragmen
    # (bukan di script utama): fragmen menyegarkan dirinya sendiri tiap
    # 0,4 detik, jadi catatan pasti tampil walau rerun penuh terganggu.
    # Catatan terkunci ke thread & jumlah pesan saat stop — otomatis
    # hilang begitu ada pesan baru atau pindah halaman/percakapan,
    # jadi tidak "nyasar" muncul di waktu/tempat yang salah.
    info_dihentikan = st.session_state.get("_yuki_dihentikan")
    if isinstance(info_dihentikan, dict):
        thread_catatan = info_dihentikan.get("thread")
        if (
            thread_catatan is not None
            and thread_catatan is active_thread()
            and len(thread_catatan) == info_dihentikan.get("n")
        ):
            st.markdown(_CATATAN_DIHENTIKAN_HTML, unsafe_allow_html=True)

    stream_state = st.session_state.get("_yuki_stream")
    if not stream_state:
        return

    pekerja = st.session_state.get("_yuki_thread")
    hidup = bool(pekerja and pekerja.is_alive())
    teks = "".join(stream_state.get("buf") or [])
    minta_henti = bool(stream_state.get("hentikan"))

    if hidup and not minta_henti:
        # Jawaban tetap dikumpulkan di background, tetapi tidak lagi
        # ditampilkan karakter demi karakter. Loader berpikir tetap terlihat
        # sampai respons selesai; jawaban kemudian muncul sekaligus dengan
        # animasi fade-blur dari render_message().
        return

    # Thread sudah selesai ATAU pengguna menekan tombol "Hentikan":
    # susun balasannya jadi pesan biasa, lalu muat ulang halaman.
    # Penanda satu-kali ini membuat input yang kembali tampil menjalankan
    # animasi partikel dari tombol Hentikan menjadi kolom chat.
    st.session_state["_yuki_morph_return"] = True
    st.session_state.pop("_yuki_stream", None)
    st.session_state.pop("_yuki_stop", None)
    st.session_state.pop("_yuki_thread", None)
    st.session_state.pop("_yuki_t0", None)
    st.session_state.pop(
        "_yuki_loader_mode",
        None,
    )
    
    st.session_state.pop(
        "_yuki_loader_subject",
        None,
    )

    if minta_henti:
        # Dihentikan lewat tombol: simpan HANYA potongan teks yang sudah
        # tampil di layar. Kalau masih fase animasi berpikir (belum ada
        # teks yang tampil), jawabannya dibuang. Lalu pasang catatan
        # "anda menghentikan respon yuki..." yang terkunci ke kondisi
        # thread saat ini.
        # Tidak ada lagi animasi ketik, jadi simpan seluruh bagian respons
        # yang sudah diterima worker sampai tombol Hentikan ditekan.
        potongan = "".join(
            stream_state.get("buf")
            or []
        )
        if potongan.strip():
            _finalisasi_stream_yuki({"buf": [potongan], "err": None})
        thread = active_thread()
        st.session_state["_yuki_dihentikan"] = {
            "thread": thread,
            "n": len(thread),
        }
    else:
        _finalisasi_stream_yuki(stream_state)

    st.rerun()

def _scroll_to_yuki_work_once() -> None:
    """Scroll halus satu kali; sesudahnya posisi sepenuhnya milik pengguna."""
    components.html(
        """
<script>
(function () {
  const frame = window.frameElement;
  if (!frame) return;

  // Posisi "end" menaruh iframe tepat di balik bottom dock chat. Gunakan
  // center agar loader yang berada persis di atas marker tetap terlihat.
  const move = () => frame.scrollIntoView({
    behavior: "smooth",
    block: "center"
  });

  window.requestAnimationFrame(
    () => window.requestAnimationFrame(move)
  );
})();
</script>
        """,
        height=1,
        scrolling=False,
    )
    

def render_loader_yuki() -> None:
    """Animasi "Yuki sedang berpikir" — dirender oleh SCRIPT UTAMA.

    Harus dipanggil dari halaman (bukan dari dalam fragmen), tepat
    setelah fragmen_jawaban_yuki(). Dengan begitu iframe animasinya
    hanya dibuat SEKALI per jawaban dan berjalan halus sampai selesai —
    persis seperti sebelum ada fitur tombol Hentikan.
    """
    # (Catatan "anda menghentikan respon yuki..." tidak dirender di sini
    # lagi — sekarang dirender oleh fragmen_jawaban_yuki.)
    if not stream_yuki_aktif():
        return
    loader_mode = str(
        st.session_state.get(
            "_yuki_loader_mode"
        )
        or ""
    )

    subject = str(
        st.session_state.get(
            "_yuki_loader_subject",
        )
        or ""
    )

    loader_html = (
        special_loading_html(
            loader_mode,
            subject,
        )
        if loader_mode
        else param_loading_html()
    )

    st.session_state[
        "_yuki_loader_tampil"
    ] = True

    components.html(
        loader_html,
        height=62 if loader_mode else 90,
        scrolling=False,
    )
    # Hanya kiriman baru yang menggeser kamera. Rerun fragmen dan kemunculan
    # jawaban tidak mengulang scroll, sehingga pengguna bebas melihat ke atas.
    if st.session_state.pop("_yuki_scroll_pending", False):
        _scroll_to_yuki_work_once()


def stream_yuki_aktif() -> bool:
    """True bila Yuki sedang menulis jawaban (stream masih berjalan)."""
    if not st.session_state.get("_yuki_stream"):
        return False
    pekerja = st.session_state.get("_yuki_thread")
    return bool(pekerja and pekerja.is_alive())


def chat_input_atau_hentikan(placeholder: str, **kwargs):
    """Kotak kirim pesan yang BERUBAH jadi tombol "Hentikan respons".

    Selama Yuki sedang menjawab, tombol kirim di kotak input digantikan
    tombol "Hentikan respons" — menekannya menghentikan jawaban Yuki dan
    potongan teks yang sudah muncul tetap disimpan. Setelah selesai,
    kotak kirim kembali seperti biasa.
    """
    if stream_yuki_aktif():
        # Marker CSS mengganti seluruh dok input menjadi satu tombol. Saat
        # marker pertama muncul, kartu input seolah pecah menjadi partikel
        # lalu partikel menyatu menjadi tombol Hentikan.
        st.markdown(
            '<div class="yuki-input-morph yuki-input-morph--stop" '
            'aria-hidden="true"></div>' + _STOP_BTN_CSS,
            unsafe_allow_html=True,
        )
        
        _render_input_particle_morph("stop")
        
        _kiri, _tombol, _kanan = st.columns([1, 0.8, 1])
        with _tombol:
            if st.button(":material/stop_circle:  Hentikan",
                         key="yuki_stop_dok"):
                # Hanya KIRIM PERINTAH berhenti — TIDAK memanggil
                # st.rerun dan TIDAK membersihkan state di sini (dulu
                # rerun dari dalam kotak bawah ini bikin catatan
                # penghentian tidak muncul pas tombol ditekan).
                # Finalisasi — simpan potongan teks + tulis catatan
                # "anda menghentikan respon yuki..." + muat ulang —
                # dikerjakan fragmen_jawaban_yuki() yang dipanggil
                # halaman tepat setelah kotak input, di run yang sama
                # dengan kliknya.
                stop = st.session_state.get("_yuki_stop")
                if stop:
                    stop.set()
                stream_state = st.session_state.get("_yuki_stream")
                if stream_state is not None:
                    stream_state["hentikan"] = True
        return None

    # Setelah stream selesai, marker hanya hidup untuk satu render. Kolom
    # chat masuk kembali dengan arah animasi kebalikan: partikel menyatu
    # dari posisi tombol Hentikan menjadi kartu input utuh.
    _yuki_returning = st.session_state.pop(
        "_yuki_morph_return",
        False,
    )
    
    if _yuki_returning:
        st.markdown(
            '<div class="yuki-input-morph yuki-input-morph--return" '
            'aria-hidden="true"></div>' +
            _STOP_BTN_CSS,
            unsafe_allow_html=True,
        )
    
        _render_input_particle_morph("return")
    
        # Tombol visual sementara.
        # Selama 3 detik pertama tetap terlihat,
        # lalu menghilang ketika particle morph dimulai.
        _kiri, _tombol, _kanan = st.columns([1, 0.8, 1])
    
        with _tombol:
            st.button(
                ":material/stop_circle:  Hentikan",
                key="yuki_return_visual_stop",
                disabled=True,
            )
    
    return st.chat_input(placeholder, **kwargs)


def handle_chat_request(answer_slot, request_text: str = "") -> None:
    thread = active_thread()

    if not CHAT_READY:
        thread.append({
            "id": next_msg_id(),
            "role": "assistant",
            "type": "text",
            "content": (
                "Fitur chat belum dikonfigurasi pemilik "
                "(GROQ_API_KEY / PLUGSKY_API_KEY / AION_API_KEY / FINAL_ROUTER_API_KEY)."
            ),
            "time": now_wib(),
        })
        return

    s = get_settings()

    model_key = st.session_state.selected_model_key

    selected_config = MODEL_BY_KEY.get(
        model_key,
        {},
    )

    if not selected_config.get(
        "chat_selectable",
        True,
    ):
        model_key = DEFAULT_MODEL_KEY
        st.session_state.selected_model_key = (
            model_key
        )

    model_id = AVAILABLE_MODELS.get(
        model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )

    last_user = next(
        (m for m in reversed(thread) if m.get("role") == "user"),
        None,
    )

    has_images = bool(last_user and last_user.get("images"))

    web_search_active = bool(
        st.session_state.get(
            "web_search_on"
        )
        and s.get(
            "cap_web_search",
            True,
        )
        and not has_images
    )

    if has_images:
        model_id = VISION_MODEL_ID
        
    # Kalau masih ada jawaban yang mengalir (pengguna kirim pesan baru di
    # tengah jawaban sebelumnya), hentikan dulu yang lama lalu simpan
    # potongannya sebagai pesan.
    _hentikan_dan_finalisasi_stream_lama()

    t0 = time.time()
    # Durasi 8/10/12/15 detik pada loader khusus adalah durasi SATU SIKLUS
    # frasa, bukan waktu blokir respons. Respons boleh muncul segera setelah
    # provider selesai; jeda minimum tetap mengikuti loader chat biasa.
    loader_mode = str(st.session_state.get("_yuki_loader_mode") or "")
    # Loader khusus membutuhkan satu sapuan glow penuh agar tidak selesai di
    # antara dua rerun Streamlit sebelum sempat dilukis oleh browser.
    min_think = max(
        float(THINKING_MIN_SECONDS),
        2.4 if loader_mode else 0.0,
    )    
    # Dicatat supaya fragmen tahu sampai kapan animasi "berpikir" wajib
    # tampil sebelum teks jawaban boleh mengalir.
    st.session_state["_yuki_t0"] = t0
    try:
        # Semua pembacaan Streamlit/session state wajib selesai di thread utama.
        # Worker hanya boleh menjalankan I/O Tavily dan streaming provider.
        provider = _get_model_provider(model_key)
        use_compatible = (
            provider in ("plugsky", "aion", "final_router")
            and not has_images
        )
        if use_compatible:
            provider_client = build_compatible_client(provider)
            system_prompt = build_system_prompt(thread)
        else:
            provider_client = build_chat_client()
            system_prompt = ""

        def _lazy_reply_stream():
            """Mulai I/O pencarian/model di worker agar loader sudah terlihat."""
            request_thread = thread
            """Mulai pencarian/model di worker agar loader sudah terlihat."""
            request_thread = thread
            if web_search_active:
                from engines.web_search_engine import (
                    history_with_web_context,
                    search_web,
                )

                # Teks job adalah sumber utama. Fallback ke pesan terakhir
                # menjaga jalur lama (artefak/kursus) tetap kompatibel.
                query = str(
                    request_text
                    or (last_user or {}).get("content")
                    or ""
                ).strip()
                search_results = search_web(query)
                request_thread = history_with_web_context(
                    thread,
                    search_results,
                )

            # Vision tetap menggunakan Groq; Web Search memakai Tavily lalu
            # hasilnya dirangkum oleh model yang dipilih pengguna.
            if use_compatible:
                reply_stream = stream_compatible_reply(
                    provider_client,
                    request_thread,
                    model=model_id,
                    system_prompt=system_prompt,
                )
            else:
                reply_stream = stream_chat_with_fallback(
                    provider_client,
                    model_id,
                    request_thread,
                    vision=has_images,
                    web_search=False,
                )

            yield from reply_stream

        stream = _lazy_reply_stream()

        # Stream dijalankan di THREAD BELAKANG. Tampilannya — animasi
        # "berpikir", teks jawaban yang mengalir, dan tombol "Hentikan
        # respons" — ditangani fragmen_jawaban_yuki() yang menyegarkan
        # dirinya sendiri tiap 0,4 detik. Dengan begitu tombolnya bisa
        # diklik kapan saja tanpa menunggu jawaban selesai.
        stream_state = {"buf": [], "err": None, "done": False, "stopped": False}
        stop_event = threading.Event()

        def _kerja() -> None:
            try:
                for piece in stream:
                    if stop_event.is_set():
                        stream_state["stopped"] = True
                        break
                    stream_state["buf"].append(piece or "")
            except Exception as e:
                stream_state["err"] = e
            # Animasi "berpikir" minimal tampil selama min_think detik —
            # tapi tidurnya dipecah potongan 0,2 detik dan dicek tiap
            # potong. (Dulu: time.sleep(sisa) sekali jalan — walau tombol
            # Hentikan sudah ditekan, thread tetap tidur sampai 25 detik
            # penuh sehingga proses terasa "tidak mau berhenti".)
            batas = t0 + min_think
            while not stop_event.is_set():
                sisa = batas - time.time()
                if sisa <= 0:
                    break
                time.sleep(min(0.2, sisa))
            stream_state["done"] = True

        pekerja = threading.Thread(target=_kerja, daemon=True)
        st.session_state["_yuki_stream"] = stream_state
        st.session_state["_yuki_stop"] = stop_event
        st.session_state["_yuki_thread"] = pekerja
        pekerja.start()

    except Exception as e:
        thread.append({
            "id": next_msg_id(),
            "role": "assistant",
            "type": "text",
            "content": public_error_chat(e),
            "time": now_wib(),
            "error_detail": f"{type(e).__name__}: {e}",
        })


def _make_square_preview(data: bytes, size: int = 160) -> tuple[bytes, str]:
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        w, h = im.size
        side = min(w, h) or 1
        left, top = (w - side) // 2, (h - side) // 2
        im = im.crop((left, top, left + side, top + side))
        im = im.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        if im.mode in ("RGBA", "LA", "P"):
            im.convert("RGBA").save(buf, format="PNG", optimize=True)
            return buf.getvalue(), "image/png"
        im.convert("RGB").save(buf, format="JPEG", quality=82)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return b"", "image/jpeg"


def _pending_cards_html(pending: list) -> str:
    cards = []
    for im in pending:
        name = (im.get("name") or "gambar").replace("<", "").replace(">", "")[:32]
        preview = im.get("preview") or b""
        if im.get("status") == "loading" or not preview:
            cards.append(
                f'<div class="pending-card">'
                f'<div class="pending-square pending-loading" title="{name}"></div>'
                f'<div class="pending-name">{name}</div>'
                f"</div>"
            )
        else:
            b64 = base64.b64encode(preview).decode("ascii")
            mime = im.get("preview_mime") or "image/jpeg"
            cards.append(
                f'<div class="pending-card">'
                f'<div class="pending-square">'
                f'<img src="data:{mime};base64,{b64}" alt="{name}"/>'
                f"</div>"
                f'<div class="pending-name">{name}</div>'
                f"</div>"
            )
    return '<div class="pending-row">' + "".join(cards) + "</div>"

def _drop_pending(idx: int) -> None:
    imgs = list(st.session_state.get("pending_images") or [])
    if 0 <= idx < len(imgs):
        imgs.pop(idx)
        st.session_state.pending_images = imgs


def render_pending_preview(page_key: str = "chat") -> None:
    kp = "" if page_key == "chat" else f"{page_key}_"
    pending = st.session_state.get("pending_images", [])
    if not pending:
        return
    cols = st.columns(len(pending))
    for i, im in enumerate(pending):
        with cols[i]:
            with st.container(key=f"{kp}pending_card_{i}"):
                name = (im.get("name") or "gambar").replace("<", "")[:32]
                preview = im.get("preview") or b""
                if im.get("status") == "loading" or not preview:
                    inner = '<div class="pending-square pending-loading"></div>'
                else:
                    b64 = base64.b64encode(preview).decode("ascii")
                    mime = im.get("preview_mime") or "image/jpeg"
                    inner = (
                        f'<div class="pending-square">'
                        f'<img src="data:{mime};base64,{b64}" alt="{name}"/>'
                        f"</div>"
                    )
                st.markdown(
                    f'<div class="pending-card">{inner}'
                    f'<div class="pending-name">{name}</div></div>',
                    unsafe_allow_html=True,
                )
                st.button(
                    "×",
                    key=f"{kp}pending_rm_{i}",
                    help="Hapus",
                    on_click=_drop_pending,
                    args=(i,),
                )


# ============================================================================
# MODEL PREMIUM — email developer/pemilik app + user berbayar.
# User berbayar didaftarkan lewat Supabase: tabel premium_users
# (Supabase → Table Editor → Insert row → isi emailnya). Tidak perlu
# edit kode setiap ada pelanggan baru.
# ============================================================================
@st.cache_data(ttl=60)
def _email_premium_db() -> tuple[str, ...]:
    """Daftar email user berbayar dari tabel Supabase premium_users.
    Cache 60 detik supaya tidak request terus-menerus."""
    try:
        import os
        import requests

        def _secret(nama: str) -> str:
            try:
                nilai = st.secrets.get(nama)
                if nilai:
                    return str(nilai).strip()
            except Exception:
                pass
            return (os.environ.get(nama) or "").strip()

        url = _secret("SUPABASE_URL")
        key = _secret("SUPABASE_ANON_KEY")
        if not url or not key:
            return ()
        r = requests.get(
            url.rstrip("/") + "/rest/v1/premium_users?select=email",
            headers={"apikey": key, "Authorization": "Bearer " + key},
            timeout=8,
        )
        if r.status_code != 200:
            return ()
        return tuple(
            str(b.get("email") or "").strip().lower()
            for b in (r.json() or []) if b.get("email")
        )
    except Exception:
        return ()


def _boleh_premium() -> bool:
    """True bila user yang login sekarang berhak memakai model premium:
    email developer/pemilik app (welcome_gate.py, plus OWNER_EMAIL) ATAU
    email yang terdaftar di tabel Supabase premium_users (user berbayar)."""
    try:
        from welcome_gate import _email_developer
        user = st.session_state.get("_user_google") or {}
        email = (user.get("email") or "").strip().lower()
        if not email:
            return False
        if email in _email_developer():
            return True
        return email in _email_premium_db()
    except Exception:
        return False


@st.dialog("Model Premium 🔒")
def _dialog_premium() -> None:
    """Popup kecil saat user biasa mencoba memilih model premium."""
    st.markdown(
        "**Waduh maaf ya...** 😔  \n"
        "Tingkatkan dulu untuk menikmati produk Ampera Official"
    )
    c_kiri, c_kanan = st.columns(2)
    with c_kiri:
        if st.button("🚀 Tingkatkan", use_container_width=True, type="primary"):
            st.session_state.page = "tingkatkan"
            st.rerun()
    with c_kanan:
        if st.button("Nanti saja", use_container_width=True):
            st.rerun()

def _render_input_particle_morph(direction: str) -> None:
    """
    Particle morph ala Claude:
    INPUT -> menyebar -> melengkung turun -> tombol
    TOMBOL -> menyebar -> melengkung naik -> INPUT

    Timing:
    0.0 - 3.0 detik : delay, bentuk awal tetap terlihat
    3.0 - 5.0 detik : particle morph
    """

    reverse = direction == "return"

    html_fx = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<style>
html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
}

canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}
</style>
</head>

<body>
<canvas id="morph"></canvas>

<script>
(() => {

    const canvas = document.getElementById("morph");
    const ctx = canvas.getContext("2d");

    const reverse = __REVERSE__;

    const DPR = Math.min(
        window.devicePixelRatio || 1,
        2
    );

    const W = window.innerWidth;
    const H = window.innerHeight;

    canvas.width = W * DPR;
    canvas.height = H * DPR;

    ctx.setTransform(
        DPR,
        0,
        0,
        DPR,
        0,
        0
    );

    /*
     * ============================================================
     * TIMING
     * ============================================================
     */

    const MORPH = 3000;
    const TOTAL = MORPH;
    const start = performance.now();


    /*
     * ============================================================
     * INPUT
     * ============================================================
     */

    const cardW = Math.min(
        760,
        Math.max(0, W - 24)
    );

    const cardH =
        W <= 600
            ? 62
            : 56;

    const input = {
        x: (W - cardW) / 2,
        y: (H - cardH) / 2,
        w: cardW,
        h: cardH,
        r: 22
    };


    /*
     * ============================================================
     * TOMBOL HENTIKAN
     * ============================================================
     */

    const button = {
        w: 126,
        h: 30,
    
        x: (W - 126) / 2,
    
        /*
         * Pusat tombol HARUS sama dengan pusat
         * area morph supaya partikel menyatu
         * tepat ke tombol asli.
         */
        y: (H - 30) / 2,
    
        r: 999
    };
     * ============================================================
     * UTILITAS PARTIKEL
     * ============================================================
     */

    const inputPoints = [];
    const buttonPoints = [];

    function addPoint(
        array,
        x,
        y,
        color,
        size
    ) {
        array.push({
            x,
            y,
            color,
            size,

            angle:
                Math.random() *
                Math.PI *
                2,

            spread:
                18 +
                Math.random() * 28,

            drift:
                (Math.random() - 0.5) * 14
        });
    }


    /*
     * ============================================================
     * ROUNDED RECTANGLE
     * ============================================================
     */

    function roundedOutline(
        array,
        rect,
        step,
        color,
        size
    ) {

        const x = rect.x;
        const y = rect.y;
        const w = rect.w;
        const h = rect.h;
        const r = Math.min(
            rect.r,
            w / 2,
            h / 2
        );

        for (
            let px = x + r;
            px <= x + w - r;
            px += step
        ) {
            addPoint(
                array,
                px,
                y,
                color,
                size
            );

            addPoint(
                array,
                px,
                y + h,
                color,
                size
            );
        }

        for (
            let py = y + r;
            py <= y + h - r;
            py += step
        ) {
            addPoint(
                array,
                x,
                py,
                color,
                size
            );

            addPoint(
                array,
                x + w,
                py,
                color,
                size
            );
        }

        const corners = [
            [
                x + r,
                y + r,
                Math.PI,
                Math.PI * 1.5
            ],
            [
                x + w - r,
                y + r,
                Math.PI * 1.5,
                Math.PI * 2
            ],
            [
                x + w - r,
                y + h - r,
                0,
                Math.PI * 0.5
            ],
            [
                x + r,
                y + h - r,
                Math.PI * 0.5,
                Math.PI
            ]
        ];

        for (const c of corners) {

            for (
                let a = c[2];
                a < c[3];
                a += 0.11
            ) {

                addPoint(
                    array,

                    c[0] +
                    Math.cos(a) * r,

                    c[1] +
                    Math.sin(a) * r,

                    color,
                    size
                );
            }
        }
    }


    /*
     * ============================================================
     * INPUT PARTICLES
     * ============================================================
     */

    roundedOutline(
        inputPoints,
        input,
        6,
        "#9b8d86",
        2.0
    );


    /*
     * Permukaan input.
     */

    for (
        let y = input.y + 8;
        y < input.y + input.h - 8;
        y += 7
    ) {

        for (
            let x = input.x + 14;
            x < input.x + input.w - 14;
            x += 11
        ) {

            if (Math.random() < 0.20) {

                addPoint(
                    inputPoints,
                    x,
                    y,
                    "#d0c1af",
                    1.2
                );
            }
        }
    }


    /*
     * Placeholder teks.
     */

    for (
        let x = input.x + 70;
        x < Math.min(
            input.x + 330,
            input.x + input.w - 220
        );
        x += 6
    ) {

        const wave =
            Math.sin(x * 0.08) * 1.5;

        for (
            let y =
                input.y +
                input.h / 2 -
                5 +
                wave;

            y <=
                input.y +
                input.h / 2 +
                5 +
                wave;

            y += 4
        ) {

            if (Math.random() < 0.62) {

                addPoint(
                    inputPoints,
                    x,
                    y,
                    "#756a70",
                    1.5
                );
            }
        }
    }


    /*
     * Ikon input.
     */

    const icons = [
        input.x + 32,
        input.x + input.w - 112,
        input.x + input.w - 74,
        input.x + input.w - 34
    ];

    for (const px of icons) {

        for (
            let a = 0;
            a < Math.PI * 2;
            a += 0.25
        ) {

            addPoint(
                inputPoints,

                px +
                Math.cos(a) * 8,

                input.y +
                input.h / 2 +
                Math.sin(a) * 8,

                "#756a70",
                1.7
            );
        }
    }


    /*
     * ============================================================
     * TOMBOL PARTICLES
     * ============================================================
     */

    roundedOutline(
        buttonPoints,
        button,
        4.5,
        "#857462",
        2.0
    );


    /*
     * Ikon stop.
     */

    const stopX = button.x + 20;
    const stopY = button.y + button.h / 2;

    for (
        let a = 0;
        a < Math.PI * 2;
        a += 0.20
    ) {

        addPoint(
            buttonPoints,

            stopX +
            Math.cos(a) * 7,

            stopY +
            Math.sin(a) * 7,

            "#514653",
            1.8
        );
    }


    /*
     * Teks Hentikan sebagai titik.
     */

    const textCanvas =
        document.createElement("canvas");

    textCanvas.width = 180;
    textCanvas.height = 50;

    const textCtx =
        textCanvas.getContext("2d");

    textCtx.font =
        '500 13px "Space Grotesk", sans-serif';

    textCtx.textBaseline = "middle";
    textCtx.fillStyle = "#514653";

    textCtx.fillText(
        "Hentikan",
        0,
        25
    );

    const pixels =
        textCtx.getImageData(
            0,
            0,
            textCanvas.width,
            textCanvas.height
        ).data;

    for (
        let y = 0;
        y < textCanvas.height;
        y += 2
    ) {

        for (
            let x = 0;
            x < textCanvas.width;
            x += 2
        ) {

            const index =
                (
                    y *
                    textCanvas.width +
                    x
                ) * 4;

            if (
                pixels[index + 3] > 100
            ) {

                addPoint(
                    buttonPoints,

                    button.x + 34 + x,
                    button.y + y - 10,

                    "#514653",
                    1.4
                );
            }
        }
    }


    /*
     * ============================================================
     * NORMALISASI JUMLAH PARTIKEL
     * ============================================================
     *
     * Target sekitar 460 partikel,
     * mengikuti konsep demo yang kamu kirim.
     */

    const TARGET_COUNT = 460;

    function normalize(
        source
    ) {

        const result = [];

        for (
            let i = 0;
            i < TARGET_COUNT;
            i++
        ) {

            result.push(
                source[
                    i % source.length
                ]
            );
        }

        return result;
    }

    const sources =
        normalize(inputPoints);

    const targets =
        normalize(buttonPoints);


    /*
     * ============================================================
     * PAIR PARTICLES
     * ============================================================
     */

    const particles = [];

    for (
        let i = 0;
        i < TARGET_COUNT;
        i++
    ) {

        const a = sources[i];
        const b = targets[i];

        particles.push({

            sx: a.x,
            sy: a.y,

            tx: b.x,
            ty: b.y,

            color: a.color,
            targetColor: b.color,

            size:
                Math.max(
                    1.15,
                    (
                        a.size +
                        b.size
                    ) / 2
                ),

            angle:
                a.angle,

            spread:
                a.spread,

            drift:
                a.drift,

            phase:
                Math.random() *
                Math.PI *
                2
        });
    }


    /*
     * ============================================================
     * EASING
     * ============================================================
     */

    function clamp(v) {
        return Math.max(
            0,
            Math.min(1, v)
        );
    }

    function easeOutCubic(t) {
        return 1 -
            Math.pow(
                1 - t,
                3
            );
    }

    function easeInOutCubic(t) {

        return t < 0.5
            ? 4 * t * t * t
            : 1 -
              Math.pow(
                  -2 * t + 2,
                  3
              ) / 2;
    }

    function mix(a, b, t) {
        return a +
            (b - a) * t;
    }


    /*
     * ============================================================
     * WARNA
     * ============================================================
     */

    function hexToRgb(hex) {

        const value =
            hex.replace("#", "");

        return {
            r: parseInt(
                value.substring(0, 2),
                16
            ),
            g: parseInt(
                value.substring(2, 4),
                16
            ),
            b: parseInt(
                value.substring(4, 6),
                16
            )
        };
    }

    function rgbToHex(
        r,
        g,
        b
    ) {

        const toHex = v =>
            Math.round(v)
                .toString(16)
                .padStart(2, "0");

        return "#" +
            toHex(r) +
            toHex(g) +
            toHex(b);
    }


    /*
     * ============================================================
     * GHOST INPUT
     * ============================================================
     *
     * Ini membuat bentuk asli tetap terlihat
     * selama delay 3 detik.
     */

    function drawInputGhost(alpha) {

        if (alpha <= 0) {
            return;
        }

        ctx.save();

        ctx.globalAlpha = alpha;

        ctx.beginPath();

        ctx.roundRect(
            input.x,
            input.y,
            input.w,
            input.h,
            input.r
        );

        ctx.fillStyle =
            "rgba(248,239,222,0.98)";

        ctx.fill();

        ctx.strokeStyle =
            "rgba(159,126,72,0.38)";

        ctx.lineWidth = 1;

        ctx.stroke();

        ctx.restore();
    }


    /*
     * ============================================================
     * GHOST BUTTON
     * ============================================================
     */

    function drawButtonGhost(alpha) {

        if (alpha <= 0) {
            return;
        }

        ctx.save();

        ctx.globalAlpha = alpha;

        ctx.beginPath();

        ctx.roundRect(
            button.x,
            button.y,
            button.w,
            button.h,
            button.r
        );

        ctx.fillStyle =
            "rgba(248,239,222,0.98)";

        ctx.fill();

        ctx.strokeStyle =
            "rgba(159,126,72,0.38)";

        ctx.lineWidth = 1;

        ctx.stroke();

        ctx.restore();
    }


    /*
     * ============================================================
     * FRAME
     * ============================================================
     */

    function frame(now) {

        const elapsed =
            now - start;

        const progress =
            clamp(
                elapsed / TOTAL
            );

        ctx.clearRect(
            0,
            0,
            W,
            H
        );

        /*
         * ========================================================
         * MORPH 0 -> 1
         * ========================================================
         */

       const morphProgress =
           clamp(
               elapsed / MORPH
           );


        /*
         * 0.00 - 0.18
         *
         * Partikel keluar dari bentuk awal.
         */

        let spreadProgress =
            clamp(
                morphProgress / 0.18
            );


        /*
         * 0.18 - 1.00
         *
         * Partikel menuju bentuk target.
         */

        let travelProgress =
            clamp(
                (
                    morphProgress -
                    0.18
                ) / 0.82
            );

        travelProgress =
            easeInOutCubic(
                travelProgress
            );


        /*
         * Input ghost / button ghost
         */

        if (!reverse) {

            /*
             * Input menghilang
             * lebih dulu.
             */

            const ghost =
                1 -
                clamp(
                    morphProgress / 0.18
                );

            drawInputGhost(
                ghost * 0.95
            );

        } else {

            const ghost =
                1 -
                clamp(
                    morphProgress / 0.18
                );

            drawButtonGhost(
                ghost * 0.95
            );
        }


        /*
         * ========================================================
         * PARTICLES
         * ========================================================
         */

        for (const p of particles) {

            let x;
            let y;

            let targetColor =
                hexToRgb(
                    p.targetColor
                );

            let sourceColor =
                hexToRgb(
                    p.color
                );


            /*
             * ====================================================
             * STOP
             * ====================================================
             */

            if (!reverse) {

                /*
                 * FASE 1:
                 * partikel menyebar
                 */

                if (
                    morphProgress <
                    0.18
                ) {

                    const spread =
                        easeOutCubic(
                            spreadProgress
                        );

                    x =
                        p.sx +
                        Math.cos(
                            p.angle
                        ) *
                        p.spread *
                        spread;

                    y =
                        p.sy +
                        Math.sin(
                            p.angle
                        ) *
                        p.spread *
                        spread;

                } else {

                    /*
                     * Posisi setelah menyebar.
                     */

                    const spreadX =
                        p.sx +
                        Math.cos(
                            p.angle
                        ) *
                        p.spread;

                    const spreadY =
                        p.sy +
                        Math.sin(
                            p.angle
                        ) *
                        p.spread;


                    /*
                     * Kurva turun menuju tombol.
                     */

                    const curve =
                        Math.sin(
                            travelProgress *
                            Math.PI
                        );

                    x =
                        mix(
                            spreadX,
                            p.tx,
                            travelProgress
                        );

                    y =
                        mix(
                            spreadY,
                            p.ty,
                            travelProgress
                        )
                        +
                        curve *
                        18;
                }

            }


            /*
             * ====================================================
             * RETURN
             * ====================================================
             */

            else {

                /*
                 * Mulai dari tombol.
                 */

                const startX =
                    p.tx +
                    Math.cos(
                        p.angle
                    ) *
                    p.spread;

                const startY =
                    p.ty +
                    Math.sin(
                        p.angle
                    ) *
                    p.spread;


                if (
                    morphProgress <
                    0.18
                ) {

                    const spread =
                        easeOutCubic(
                            spreadProgress
                        );

                    x =
                        p.tx +
                        Math.cos(
                            p.angle
                        ) *
                        p.spread *
                        spread;

                    y =
                        p.ty +
                        Math.sin(
                            p.angle
                        ) *
                        p.spread *
                        spread;

                } else {

                    /*
                     * Kurva naik menuju input.
                     */

                    const curve =
                        Math.sin(
                            travelProgress *
                            Math.PI
                        );

                    x =
                        mix(
                            startX,
                            p.sx,
                            travelProgress
                        );

                    y =
                        mix(
                            startY,
                            p.sy,
                            travelProgress
                        )
                        -
                        curve *
                        18;
                }
            }


            /*
             * Sedikit floating motion.
             */

            x +=
                Math.sin(
                    now * 0.004 +
                    p.phase
                ) *
                p.drift *
                0.12;

            y +=
                Math.cos(
                    now * 0.003 +
                    p.phase
                ) *
                p.drift *
                0.08;


            /*
             * Warna berubah ketika
             * partikel mendekati target.
             */

            const colorT =
                Math.max(
                    0,
                    (morphProgress - 0.35) /
                    0.65
                );

            const r =
                mix(
                    sourceColor.r,
                    targetColor.r,
                    colorT
                );

            const g =
                mix(
                    sourceColor.g,
                    targetColor.g,
                    colorT
                );

            const b =
                mix(
                    sourceColor.b,
                    targetColor.b,
                    colorT
                );


            /*
             * Partikel fade setelah
             * bentuk target sudah terbentuk.
             */

            let alpha = 0.95;

            if (
                morphProgress >
                0.94
            ) {

                alpha =
                    0.95 *
                    (
                        1 -
                        (
                            morphProgress -
                            0.94
                        ) /
                        0.06
                    );
            }


            ctx.globalAlpha =
                Math.max(
                    0,
                    alpha
                );

            ctx.fillStyle =
                rgbToHex(
                    r,
                    g,
                    b
                );

            ctx.beginPath();

            ctx.arc(
                x,
                y,
                p.size,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }


        ctx.globalAlpha = 1;


        /*
         * Selesai
         */

        if (elapsed < TOTAL) {

            requestAnimationFrame(
                frame
            );

        } else {

            ctx.clearRect(
                0,
                0,
                W,
                H
            );
        }
    }


    requestAnimationFrame(frame);

})();
</script>
</body>
</html>
"""

    html_fx = html_fx.replace(
        "__REVERSE__",
        "true" if reverse else "false"
    )

    with st.container(key="yuki_morph_fx"):
        components.html(
            html_fx,
            height=120,
            scrolling=False,
        )


def render_input_controls(page_key: str = "chat", show_mode: bool = True) -> None:
    """Baris di bawah kotak ketik: [+] ........... [Nama Model]."""
    kp = "" if page_key == "chat" else f"{page_key}_"

    ctrl_plus, _sp, ctrl_model = st.columns([0.08, 1.64, 0.28])

    with ctrl_plus:
        with st.container(key=f"{kp}plus_menu"):
            with st.popover(":material/attach_file:", use_container_width=False,
                            help="Unggah file atau gambar"):
                gen = st.session_state.get("plus_uploader_gen", 0)

                with st.container(key=f"{kp}plus_upload_file"):
                    picked_file = st.file_uploader(
                        ":material/attach_file:  Upload file", type=IMAGE_INPUT_TYPES,
                        accept_multiple_files=True,
                        label_visibility="visible",
                        key=f"{kp}plus_uploader_file_{gen}",
                    )
                with st.container(key=f"{kp}plus_upload_image"):
                    picked_image = st.file_uploader(
                        ":material/photo_camera:  Upload gambar atau foto",
                        type=IMAGE_INPUT_TYPES,
                        accept_multiple_files=True,
                        label_visibility="visible",
                        key=f"{kp}plus_uploader_image_{gen}",
                    )

                picked = list(picked_file or []) + list(picked_image or [])
                sig = tuple(getattr(f, "name", "") for f in picked)
                last_sig = st.session_state.get(f"{kp}picked_sig")

                if picked and sig != last_sig:
                    ready = [
                        im for im in st.session_state.get("pending_images", [])
                        if im.get("status") != "loading"
                    ]
                    blobs = []
                    loaders = []
                    for f in picked:
                        try:
                            raw = f.getvalue()
                        except Exception:
                            continue
                        if not raw:
                            continue
                        name = getattr(f, "name", "gambar")
                        mime = (getattr(f, "type", "") or "image/png").lower()
                        if not mime.startswith("image/"):
                            mime = "image/png"
                        blobs.append({"name": name, "data": raw, "mime": mime})
                        loaders.append({
                            "name": name, "data": raw, "mime": mime,
                            "preview": b"", "status": "loading",
                        })
                    st.session_state[f"{kp}pending_blobs"] = blobs
                    st.session_state.pending_images = ready + loaders
                    st.session_state[f"{kp}picked_sig"] = sig
                    st.session_state[f"{kp}stage_now"] = True
                    st.rerun()

                if st.session_state.get(f"{kp}stage_now"):
                    blobs = st.session_state.pop(f"{kp}pending_blobs", [])
                    ready = [
                        im for im in st.session_state.get("pending_images", [])
                        if im.get("status") != "loading"
                    ]
                    seen = {(im["name"], len(im.get("data") or b"")) for im in ready}
                    for b in blobs:
                        key = (b["name"], len(b["data"]))
                        if key in seen:
                            continue
                        thumb, tmime = _make_square_preview(b["data"])
                        ready.append({
                            "name": b["name"],
                            "data": b["data"],
                            "mime": b["mime"],
                            "preview": thumb,
                            "preview_mime": tmime,
                            "status": "ready",
                        })
                        seen.add(key)
                    st.session_state.pending_images = ready
                    st.session_state[f"{kp}stage_now"] = False
                    st.rerun()

                st.markdown('<div class="plus-menu-divider"></div>',
                            unsafe_allow_html=True)

                if st.button(":material/screenshot:  Ambil tangkapan layar",
                             key=f"{kp}pm_screenshot", use_container_width=True):
                    st.toast("Ambil screenshot dengan tombol OS kamu, lalu "
                             "tempel (Ctrl+V) di kotak chat.",
                             icon=":material/screenshot:")

                web_check = " :orange[✓]" if st.session_state.get("web_search_on") else ""
                if st.button(f":material/public:  Pencarian web{web_check}",
                             key=f"{kp}pm_web", use_container_width=True):
                    st.session_state.web_search_on = not st.session_state.get("web_search_on", False)
                    st.rerun()

    with _sp:
        if st.session_state.messages or st.session_state.get("page") != "chat":
            st.markdown(
                '<div class="input-disclaimer">'
                "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                "</div>",
                unsafe_allow_html=True,
            )

    with ctrl_model:
        # Pengaman: kalau model terpilih ternyata premium tapi user ini
        # tidak berhak (misal terpilih sebelum aturan berlaku), kembalikan
        # ke model bawaan supaya chat tetap jalan normal.
        _terpilih = MODEL_BY_KEY.get(st.session_state.selected_model_key)
        if _terpilih and _terpilih.get("premium") and not _boleh_premium():
            st.session_state.selected_model_key = DEFAULT_MODEL_KEY

        current_key = st.session_state.selected_model_key
        current_model = MODEL_BY_KEY.get(current_key, MODEL_BY_KEY[DEFAULT_MODEL_KEY])
        current_name = current_model["name"]
        with st.popover(":material/psychology:", use_container_width=False, help="Pilih model AI",):
            # Tampilan "DNA DOUBLE HELIX" (model_dna.py):
            # heliks DNA beranimasi di atas, daftar model = anak tangga DNA.
            st.markdown(DNA_CSS, unsafe_allow_html=True)
            st.markdown(
                dna_header_html(current_name, current_model.get("desc", "")),
                unsafe_allow_html=True,
            )
            for m in MODEL_CATALOG:
                if not m.get(
                    "chat_selectable",
                    True,
                ):
                    continue

                is_active = (
                    m["key"]
                    == st.session_state.selected_model_key
                )
                # Model aktif TIDAK pakai tanda ✓ lagi — ditandai lewat
                # animasi glow putih berjalan (active_node_css).
                label = f"{m['name']}  \n:gray[{m['desc']}]"
                row_key = f"{kp}model_row_{m['key']}" + ("_premium" if m.get("premium") else "")
                if is_active:
                    # nyalakan titik basa model yang aktif
                    st.markdown(active_node_css(row_key), unsafe_allow_html=True)
                with st.container(key=row_key):
                    if st.button(label, key=f"{kp}model_{m['key']}", use_container_width=True):
                        if m.get("premium") and not _boleh_premium():
                            # User biasa: model premium TIDAK dipilih —
                            # tampilkan popup ajakan tingkatkan paket.
                            _dialog_premium()
                        else:
                            st.session_state.selected_model_key = m["key"]
                            st.rerun()
                            
                        
def process_user_input(user_input, answer_slot, is_fresh: bool = False) -> bool:
    """Simpan kiriman user ke thread aktif, lalu antri Yuki.
    Return True bila halaman perlu di-rerun."""
    if user_input is None:
        return False

    if isinstance(user_input, str):
        raw_text, send_files, send_audio = user_input, [], None
    else:
        raw_text = getattr(user_input, "text", "") or ""
        send_files = list(getattr(user_input, "files", None) or [])
        send_audio = getattr(user_input, "audio", None)

    text = (raw_text or "").strip()
    via_voice = False
    thread = active_thread()

    if send_audio is not None and not text:
        if CHAT_READY:
            try:
                with st.spinner(":material/mic:  Mentranskrip suara…"):
                    text = transcribe_audio(build_chat_client(), send_audio.getvalue())
                via_voice = bool(text)
            except Exception:
                text = ""
        if not text:
            thread.append({
                "id": next_msg_id(), "role": "assistant", "type": "text",
                "content": "Hmm, suaranya belum kebaca nih. Coba rekam lagi "
                           "lebih dekat ke mikrofon, atau ketik saja ya!",
                "time": now_wib(),
            })
            return True

    images = collect_images(send_files)
    pending = st.session_state.get("pending_images", [])
    if pending:
        keys = {(im["name"], len(im["data"])) for im in images}
        for im in pending:
            k = (im["name"], len(im["data"]))
            if k not in keys:
                images.append(im)
                keys.add(k)
        st.session_state.pending_images = []
        st.session_state.plus_uploader_gen = (
            st.session_state.get("plus_uploader_gen", 0) + 1
        )
    images = images[:MAX_IMAGES_PER_MESSAGE]

    if not (text or images):
        return False

    # Ada kiriman baru → catatan "anda menghentikan respon yuki..."
    # dari jawaban sebelumnya tidak perlu tampil lagi.
    st.session_state.pop("_yuki_dihentikan", None)

    now = now_wib()

    if is_fresh:
        st.markdown(_BOTTOM_RESET_CSS, unsafe_allow_html=True)

    user_msg = {
        "id": next_msg_id(), "role": "user", "type": "text",
        "content": text, "time": now,
    }
    if images:
        user_msg["images"] = images
    if via_voice:
        user_msg["via_voice"] = True
    thread.append(user_msg)
    note = f"{ICON_MIC} via suara" if via_voice else ""
    st.markdown(
        bubble_html("user", text, now, images_bubble_html(images), note),
        unsafe_allow_html=True,
    )

    st.session_state.pending_images = []
    st.session_state.plus_uploader_gen = st.session_state.get("plus_uploader_gen", 0) + 1

    # ROUTER NIAT (niat.py): kalau User tidak menyalakan mode gambar
    # sendiri, Yuki menebak dari kalimatnya. Saklar manual tetap menang —
    # User yang sengaja menyalakan mode gambar tidak akan dibantah.
    mode_manual = bool(st.session_state.image_mode and not images)
    if mode_manual:
        buat_gambar = True
    else:
        from niat import tebak_niat, GAMBAR
        buat_gambar = (
            tebak_niat(text, punya_gambar=bool(images)) == GAMBAR
            and get_settings().get("cap_image", True)
        )

    loader_mode = detect_loading_mode(
        text,
        page=str(
            st.session_state.get(
                "page"
            )
            or "chat"
        ),
        web_search=bool(
            st.session_state.get(
                "web_search_on"
            )
        ),
        image_mode=buat_gambar,
    )

    st.session_state["_yuki_loader_mode"] = loader_mode
    st.session_state["_yuki_loader_subject"] = loading_subject(text)
    st.session_state["_yuki_scroll_pending"] = True

    # Antrekan satu kali agar rerun pertama menempatkan pesan pengguna pada
    # riwayat normal. Pada run berikutnya maybe_run_yuki() memulai worker lalu
    # membiarkan halaman terus merender loader tanpa rerun kedua.
    st.session_state["_yuki_job"] = {
        "image_mode": buat_gambar,
        "text": text,
        "auto": buat_gambar and not mode_manual,
        "loader_mode": loader_mode,
    }
    return True
