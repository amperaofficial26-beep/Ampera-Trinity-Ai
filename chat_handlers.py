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


# --- Durasi tampilan kotak loading pembuatan gambar (detik) ---------------
# IMAGE_MIN_SECONDS : kotak minimal tampil selama ini walau API sudah selesai,
#                     supaya animasi shimmer sempat terlihat.
# IMAGE_DONE_SECONDS: jeda singkat pada keadaan "Selesai" sebelum gambar muncul.
# IMAGE_MAX_SECONDS : batas aman menunggu API sebelum dianggap timeout.
IMAGE_MIN_SECONDS = 6.0
IMAGE_DONE_SECONDS = 0.7
IMAGE_MAX_SECONDS = 200.0


def maybe_run_yuki(answer_slot) -> bool:
    job = st.session_state.get("_yuki_job")
    if not job:
        return False
    if not st.session_state.get("_yuki_ui_flushed"):
        st.session_state["_yuki_ui_flushed"] = True
        return True
    st.session_state.pop("_yuki_job", None)
    st.session_state.pop("_yuki_ui_flushed", None)
    if job.get("image_mode"):
        handle_image_request(job.get("text") or "")
    else:
        handle_chat_request(answer_slot)
    return True

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
    result: dict = {"data": None, "error": None}

    def _worker() -> None:
        try:
            result["data"] = generate_image(prompt)
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
    progress_slot.markdown(image_progress_html(), unsafe_allow_html=True)

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


def handle_chat_request(answer_slot) -> None:
    thread = active_thread()
    if not CHAT_READY:
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": now_wib(),
        })
        return

    s = get_settings()
    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_key,
        AVAILABLE_MODELS[DEFAULT_MODEL_KEY],
    )
    last_user = next(
        (m for m in reversed(thread) if m.get("role") == "user"),
        None,
    )
    has_images = bool(last_user and last_user.get("images"))
    if has_images:
        model_id = VISION_MODEL_ID
    elif st.session_state.get("web_search_on") and s.get("cap_web_search", True):
        model_id = AVAILABLE_MODELS["compound"]

    from ui_helpers import THINKING_MIN_SECONDS
    think_slot = st.empty()
    think_slot.markdown(thinking_html(THINKING_PHRASES_CHAT), unsafe_allow_html=True)
    t0 = time.time()
    min_think = float(s.get("min_think_seconds", THINKING_MIN_SECONDS))

    try:
        client = build_chat_client()
        full = "".join(
            piece or ""
            for piece in stream_chat_with_fallback(
                client, model_id, thread, vision=has_images
            )
        )
        elapsed = time.time() - t0
        if elapsed < min_think:
            time.sleep(min_think - elapsed)
        think_slot.empty()
        if not full:
            full = "…"
        stream_sentences(answer_slot, full)
        reply = {
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": now_wib(),
        }
        thread.append(reply)
        _capture_artifacts_from_reply(full)
    except Exception as e:
        think_slot.empty()
        err = public_error_chat(e)
        thread.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": now_wib(),
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


def render_input_controls(page_key: str = "chat", show_mode: bool = True) -> None:
    """Baris di bawah kotak ketik: [+] ........... [Nama Model]."""
    kp = "" if page_key == "chat" else f"{page_key}_"

    ctrl_plus, _sp, ctrl_model = st.columns([0.08, 1.64, 0.28])

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
    st.session_state["_yuki_job"] = {
        "image_mode": bool(st.session_state.image_mode and not images),
        "text": text,
    }
    return True
