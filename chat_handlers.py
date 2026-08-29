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

from PIL import Image
import streamlit as st

from config import (
    AVAILABLE_MODELS, DEFAULT_MODEL_KEY, IMAGE_INPUT_TYPES, IMAGE_READY,
    CHAT_READY, MAX_IMAGES_PER_MESSAGE, MODEL_BY_KEY, MODEL_CATALOG,
    VISION_MODEL_ID,
)
from engines.groq_engine import (
    build_chat_client, collect_images, stream_chat_with_fallback,
    transcribe_audio,
)
from engines.image_engine import generate_image
from errors import public_error_chat, public_error_image
from icons import ICON_MIC
from state import active_thread, get_settings, next_msg_id
from ui_helpers import (
    THINKING_PHRASES_CHAT, _BOTTOM_RESET_CSS, _capture_artifacts_from_reply,
    bubble_html, image_progress_html, images_bubble_html, stream_sentences,
    thinking_html,
)
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

def now_wib() -> str:
    return datetime.now(WIB).strftime("%H:%M")


# ============================================================================
# MODE GAMBAR
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar.
    Hasil masuk ke thread aktif (chat utama, artefak, atau kursus)."""
    thread = active_thread()
    if not IMAGE_READY:
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Progress bar % + shimmer (generate jalan di thread background,
    # persentase naik perlahan mengikuti tahapan label)
    progress_slot = st.empty()

    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
        except Exception as exc:  # simpan untuk ditampilkan di thread utama
            result["error"] = exc

    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()

    # Tahapan label + target % (label berganti seiring progress naik)
    stages = [
        (0, "Membayangkan gambarnya"),
        (30, "Menyiapkan kanvas"),
        (55, "Melukis perlahan"),
        (80, "Menajamkan detail"),
    ]
    pct = 0.0
    t0 = time.time()
    IMAGE_MIN_SECONDS = 10.0
    while worker.is_alive() or (time.time() - t0) < IMAGE_MIN_SECONDS:
        # naik perlahan, melambat mendekati 92% selama masih menunggu
        if pct < 60:
            pct += 2.4
        elif pct < 85:
            pct += 1.1
        elif pct < 92:
            pct += 0.35
        label = stages[0][1]
        for threshold, name in stages:
            if pct >= threshold:
                label = name
        progress_slot.markdown(image_progress_html(pct, label), unsafe_allow_html=True)
        time.sleep(0.35)
        if not worker.is_alive() and (time.time() - t0) >= IMAGE_MIN_SECONDS:
            break

    worker.join(timeout=200)

    if result["error"] is None and result["data"]:
        # sentuhan akhir: lompat mulus ke 100%
        progress_slot.markdown(image_progress_html(100, "Selesai"), unsafe_allow_html=True)
        time.sleep(0.6)
        progress_slot.empty()
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "image",
            "image_bytes": result["data"], "prompt": prompt,
            "time": datetime.now().strftime("%H:%M"),
        })
    else:
        progress_slot.empty()
        e = result["error"] or RuntimeError("no image")
        msg = str(e)
        if not msg.startswith(("Layanan", "Kuota", "Server terlalu",
                               "Gagal membuat", "Respons terlalu")):
            msg = public_error_image(None, msg, e)
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": msg, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MODE CHAT
# ============================================================================
def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback.
    Jawaban masuk ke THREAD AKTIF (chat utama, artefak, atau kursus)."""
    thread = active_thread()
    if not CHAT_READY:
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    s = get_settings()
    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )
    # Pesan bergambar WAJIB lewat model vision (model teks tidak bisa lihat gambar)
    last_user = next(
        (m for m in reversed(thread) if m.get("role") == "user"),
        None,
    )
    has_images = bool(last_user and last_user.get("images"))
    if has_images:
        model_id = VISION_MODEL_ID
    elif st.session_state.get("web_search_on") and s.get("cap_web_search", True):
        # Toggle "Pencarian web" ala Claude → pakai model Compound
        # (satu-satunya model Groq di katalog ini yang bisa browsing).
        model_id = AVAILABLE_MODELS["compound"]

    # Thinking ala Claude — frasa berganti-ganti selama beberapa detik
    from ui_helpers import THINKING_MIN_SECONDS
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()
    # Durasi "berpikir" minimum bisa diatur di Pengaturan → Umum
    min_think = float(s.get("min_think_seconds", THINKING_MIN_SECONDS))

    try:
        client = build_chat_client()
        # Kumpulkan seluruh jawaban SELAMA animasi berpikir masih berjalan
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, thread, vision=has_images
            )
        )

        # Tahan sampai proses berpikir genap minimal beberapa detik
        elapsed = time.time() - t0
        if elapsed < min_think:
            time.sleep(min_think - elapsed)
        think_slot.empty()

        if not full:
            full = "…"

        # Jawaban muncul bertahap per kalimat (bukan kata per kata)
        stream_sentences(answer_slot, full)

        reply = {
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        }
        thread.append(reply)
        _capture_artifacts_from_reply(full)
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# KONTROL KOTAK INPUT (dipakai bersama oleh chat utama, Artefak, dan Kursus)
# ============================================================================
def _make_square_preview(data: bytes, size: int = 160) -> tuple[bytes, str]:
    """Thumbnail persegi kecil untuk tampilan saja. File asli tidak diubah."""
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
    
def render_pending_preview(page_key: str = "chat") -> None:
    """Thumbnail lampiran — dipanggil di container sendiri di atas chat input."""
    kp = "" if page_key == "chat" else f"{page_key}_"
    pending = st.session_state.get("pending_images", [])
    if not pending:
        return
    st.markdown(_pending_cards_html(pending), unsafe_allow_html=True)
    rm_cols = st.columns([1] * len(pending) + [6])
    for i, _im in enumerate(pending):
        with rm_cols[i]:
            if st.button("✕", key=f"{kp}pending_rm_{i}", help="Hapus lampiran"):
                st.session_state.pending_images.pop(i)
                st.rerun()
                
def render_input_controls(page_key: str = "chat", show_mode: bool = True) -> None:
    """Isi dok bawah: [+] [Gambar] ... [Nama Model], preview tepat di atas chat input."""
    kp = "" if page_key == "chat" else f"{page_key}_"

    # [menu] [Gambar] ....spacer.... [Nama Model]
    ctrl_plus, ctrl_mode, _sp, ctrl_model = st.columns([0.08, 0.22, 1.22, 0.28])

    with ctrl_plus:
        with st.container(key=f"{kp}plus_menu"):
            with st.popover(":material/add:", use_container_width=False,
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

                # Fase 1: baca file SEKARANG (sebelum popover nutup), tampilkan loading
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

                # Fase 2: pakai bytes yang sudah disimpan (tidak butuh file_uploader lagi)
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
                            "data": b["data"],          # asli, resolusi utuh
                            "mime": b["mime"],
                            "preview": thumb,           # kecil, cuma untuk layar
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

    with ctrl_mode:
        if show_mode:
            st.session_state.image_mode = st.toggle(
                "Gambar",
                value=st.session_state.image_mode,
                key=f"{kp}toggle_gambar",
                help="Nyalakan untuk membuat gambar dari teks. "
                     "Matikan untuk chat biasa dengan Yuki.",
            )

    with _sp:
        if st.session_state.messages or st.session_state.get("page") != "chat":
            st.markdown(
                '<div class="input-disclaimer">'
                "Yuki adalah AI dan bisa membuat kesalahan. Harap periksa kembali respons."
                "</div>",
                unsafe_allow_html=True,
            )

    with ctrl_model:
        current_key = st.session_state.selected_model_key
        current_name = MODEL_BY_KEY.get(current_key, MODEL_BY_KEY[DEFAULT_MODEL_KEY])["name"]
        with st.popover(current_name, use_container_width=False):
            for m in MODEL_CATALOG:
                is_active = m["key"] == st.session_state.selected_model_key
                check = " :orange[✓]" if is_active else ""
                label = f"{m['name']}{check}  \n:gray[{m['desc']}]"
                row_key = f"{kp}model_row_{m['key']}" + ("_premium" if m.get("premium") else "")
                with st.container(key=row_key):
                    if st.button(label, key=f"{kp}model_{m['key']}", use_container_width=True):
                        st.session_state.selected_model_key = m["key"]
                        st.rerun()

    # Preview TEPAT di atas kotak chat (elemen terakhir di st.bottom)
    pending = st.session_state.get("pending_images", [])
    if pending:
        st.markdown(_pending_cards_html(pending), unsafe_allow_html=True)
        rm_cols = st.columns([1] * len(pending) + [6])
        for i, _im in enumerate(pending):
            with rm_cols[i]:
                if st.button("✕", key=f"{kp}pending_rm_{i}", help="Hapus lampiran"):
                    st.session_state.pending_images.pop(i)
                    st.rerun()
# ============================================================================
# PEMROSESAN KIRIMAN USER
# ============================================================================
def process_user_input(user_input, answer_slot, is_fresh: bool = False) -> bool:
    """Simpan kiriman user ke thread aktif, render bubble-nya, lalu panggil
    Yuki. Return True bila halaman perlu di-rerun.
    Dipanggil dari HALAMAN (bukan dari dalam dok bawah)."""
    if user_input is None:
        return False

    # Bongkar nilai chat input: teks + lampiran + rekaman (bila didukung)
    if isinstance(user_input, str):
        raw_text, send_files, send_audio = user_input, [], None
    else:
        raw_text = getattr(user_input, "text", "") or ""
        send_files = list(getattr(user_input, "files", None) or [])
        send_audio = getattr(user_input, "audio", None)

    text = (raw_text or "").strip()
    via_voice = False
    thread = active_thread()

    # Kiriman suara tanpa teks → transkrip dulu dengan Groq Whisper
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
                "time": datetime.now().strftime("%H:%M"),
            })
            return True

    images = collect_images(send_files)
    # Gabungkan lampiran yang di-stage lewat menu ⋯ (hindari duplikat)
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

    now = datetime.now().strftime("%H:%M")

    # Begitu KIRIM ditekan: kotak input langsung turun ke bawah dan scroll
    # diaktifkan lagi (menimpa CSS halaman awal).
    if is_fresh:
        st.markdown(_BOTTOM_RESET_CSS, unsafe_allow_html=True)

    # simpan & tampilkan pesan user (+ thumbnail lampiran)
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

    # Ada lampiran gambar → selalu chat vision (Yuki melihat gambarnya),
    # walau toggle "Gambar" sedang aktif sekalipun.
    if st.session_state.image_mode and not images:
        handle_image_request(text)
    else:
        handle_chat_request(answer_slot)

    return True
