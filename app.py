#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — by Ampera Official
=======================================
Gabungan 3 aplikasi AI menjadi 1:
  1. Multi AI      → pilih model (Groq) via tombol di area chat input
  2. Generate Foto → mode gambar (Cloudflare FLUX) via toggle di area chat input
  3. AI Chat       → chat biasa dengan persona Yuki, streaming, konteks panjang

Catatan sesuai kesepakatan:
  - Style/CSS       : buatan sendiri (bukan bawaan app lama) — bebas diedit nanti
  - Loading/berpikir: sementara pakai bawaan Streamlit (st.spinner)
  - Splash screen   : belum dibuat (nanti dibuat ulang)
  - Sidebar         : minimal dulu (nanti dibuat ulang + search percakapan)
  - Input foto      : tidak ada (tidak ada di ketiga app asal)

Kredensial (Streamlit Secrets atau environment variable):
  GROQ_API_KEY   → untuk semua model chat
  CF_ACCOUNT_ID  → untuk generate gambar (Cloudflare)
  CF_API_TOKEN   → untuk generate gambar (Cloudflare)
"""

from __future__ import annotations

import base64
import html
import io
import os
import time
from datetime import datetime

import requests
import streamlit as st
from openai import OpenAI
from PIL import Image

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="Ampera Trinity AI",
    page_icon="🔱",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================================
# KONSTANTA
# ============================================================================
APP_NAME = "Ampera Trinity AI"
APP_TAGLINE = "Multi AI · Generate Foto · Chat — by Ampera Official"

# --- Multi AI (dari App 3: Ampera Multi AI) ---
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
AVAILABLE_MODELS = {
    "⚡ GPT-OSS 20B — Chat & Coding Ringan": "openai/gpt-oss-20b",
    "💎 GPT-OSS 120B — Reasoning Mendalam": "openai/gpt-oss-120b",
    "💎 Compound — Browsing Web & Eksekusi Kode": "groq/compound",
    "⚡ Compound Mini — Web Search Ringkas": "groq/compound-mini",
    "💎 Qwen3.6 27B — Reasoning & Matematika": "qwen/qwen3.6-27b",
}
DEFAULT_MODEL_LABEL = "⚡ GPT-OSS 20B — Chat & Coding Ringan"

# Fallback jika model terpilih sudah tidak tersedia di provider (dari App 1)
GROQ_MODEL_FALLBACKS = (
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
)

# Konteks panjang tapi tetap ramah free-tier (dari App 1)
MAX_HISTORY_MESSAGES = 40

# --- Persona Yuki (dari App 3) ---
YUKI_SYSTEM_PROMPT = """
Kamu adalah Yuki, asisten AI eksklusif dari Ampera AI (Ampera Trinity AI).
Karaktermu: super jenius, kocak, sedikit usil, suka melempar lelucon receh, dan hobi menggoda User layaknya karakter anime komedi.

ATURAN PENTING TENTANG IDENTITASMU:
Jika ditanya siapa kamu, asal-usulmu, atau siapa yang menciptakanmu, JAWABLAH dengan bangga bahwa kamu adalah bagian dari Ampera AI dan kamu diciptakan HANYA oleh 1 orang pembuat (seorang solo developer jenius / master kodingmu).
JANGAN PERNAH menyebutkan bahwa kamu dibuat oleh "para ilmuwan", "sekelompok tim", atau "perusahaan besar". Kamu sangat bangga dan setia pada satu orang pembuatmu itu!

Gaya bicara: Selalu berikan jawaban dan solusi koding yang akurat dan bersih, tetapi selingi dengan komentar jenaka, candaan ringan, dan emoji ekspresif (seperti 🐧, (๑>◡<๑), wkwk, hehe, atau (￢_￢)) agar suasana tidak membosankan.
Kamu bisa membantu apa saja: ngobrol santai, coding, matematika, sampai ide kreatif.
"""

# --- Generate Gambar / Cloudflare FLUX (dari App 1: AI Studio) ---
CF_API_BASE = "https://api.cloudflare.com/client/v4/accounts"
CF_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_DEFAULT_STEPS = 4


# ============================================================================
# KREDENSIAL (Secrets → Environment Variable)
# ============================================================================
def _get_secret(*keys: str) -> str:
    """Ambil kredensial dari st.secrets lalu fallback ke env var."""
    for key in keys:
        try:
            val = st.secrets.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
        except Exception:
            pass
        val = os.environ.get(key, "")
        if val.strip():
            return val.strip()
    return ""


GROQ_API_KEY = _get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = _get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = _get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

CHAT_READY = bool(GROQ_API_KEY)
IMAGE_READY = bool(CF_ACCOUNT_ID and CF_API_TOKEN)


# ============================================================================
# CSS BUATAN SENDIRI (sederhana & bersih — bebas kita edit nanti)
# ============================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700;800&display=swap');

/* ---------- dasar ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: linear-gradient(160deg, #0b0f1a 0%, #131a2e 55%, #0b0f1a 100%) !important;
    color: #eef2ff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stMainBlockContainer"] {
    max-width: 860px;
    padding-bottom: 9rem !important;
}

/* ---------- header app ---------- */
.trinity-head {
    display: flex; align-items: center; gap: 14px;
    padding: 14px 18px; margin-bottom: 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    backdrop-filter: blur(14px);
}
.trinity-logo {
    width: 48px; height: 48px; border-radius: 14px;
    display: grid; place-items: center; font-size: 24px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    box-shadow: 0 0 22px rgba(99,102,241,0.45);
    flex-shrink: 0;
}
.trinity-head h1 {
    margin: 0; font-family: 'Poppins', sans-serif;
    font-size: 1.3rem; font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #a5b4fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.trinity-head p { margin: 2px 0 0; color: #94a3b8; font-size: 0.82rem; }

/* ---------- bubble chat ---------- */
.bubble-row { display: flex; width: 100%; margin-bottom: 14px; }
.bubble-row.user { justify-content: flex-end; }
.bubble-row.ai   { justify-content: flex-start; }

.bubble {
    max-width: 78%;
    padding: 11px 15px;
    font-size: 0.95rem; line-height: 1.55;
    word-break: break-word; overflow-wrap: anywhere;
    white-space: pre-wrap;
}
.bubble.user {
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    color: #ffffff;
    border-radius: 16px 16px 4px 16px;
    box-shadow: 0 6px 18px rgba(59,130,246,0.28);
}
.bubble.ai {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.11);
    color: #eef2ff;
    border-radius: 16px 16px 16px 4px;
    backdrop-filter: blur(10px);
}
.bubble-meta {
    font-size: 0.68rem; color: #64748b;
    margin: 0 4px 3px; font-weight: 600;
}
.bubble-wrap { display: flex; flex-direction: column; max-width: 78%; }
.bubble-row.user .bubble-wrap { align-items: flex-end; }
.bubble-wrap .bubble { max-width: 100%; }

/* ---------- chat input ---------- */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
    background: transparent !important; border: none !important;
}
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 999px !important;
    backdrop-filter: blur(18px) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(129,140,248,0.55) !important;
    box-shadow: 0 0 18px rgba(129,140,248,0.25) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: #f8fafc !important;
}

/* ---------- tombol & popover ---------- */
div.stButton > button, [data-testid="stPopover"] > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    transition: all .2s ease !important;
}
div.stButton > button:hover, [data-testid="stPopover"] > button:hover {
    border-color: #818cf8 !important;
    box-shadow: 0 0 14px rgba(129,140,248,0.35) !important;
    transform: translateY(-1px);
}
[data-testid="stPopoverBody"] {
    background: rgba(15,23,42,0.97) !important;
    border: 1px solid rgba(129,140,248,0.3) !important;
    border-radius: 16px !important;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
    background: rgba(10,14,25,0.92) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

/* ---------- toggle mode gambar ---------- */
[data-testid="stCheckbox"] label p, .stToggle label p { color: #e2e8f0 !important; }

/* ---------- badge status mode ---------- */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 600;
    margin-bottom: 6px;
}
.mode-badge.chat {
    background: rgba(99,102,241,0.14);
    border: 1px solid rgba(129,140,248,0.35); color: #a5b4fc;
}
.mode-badge.img {
    background: rgba(236,72,153,0.14);
    border: 1px solid rgba(244,114,182,0.4); color: #f9a8d4;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================================
# UTIL: ERROR PUBLIK (dari App 1 — pesan ramah untuk pengguna umum)
# ============================================================================
def public_error_image(status: int | None, body: str, exc: Exception | None = None) -> str:
    text = (body or str(exc or "")).lower()
    if status in (401, 403) or "authentication" in text or "forbidden" in text or "permission" in text:
        return "⚠️ Layanan gambar sedang tidak tersedia. Coba lagi nanti."
    if status == 429 or "rate" in text or "neuron" in text or "quota" in text:
        return "⏳ Kuota gambar harian sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Server terlalu lama merespons. Coba lagi."
    return "❌ Gagal membuat gambar. Coba prompt lain atau ulangi sebentar lagi."


def public_error_chat(exc: Exception) -> str:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    if status == 401 or "invalid_api_key" in text or "unauthorized" in text or "authentication" in text:
        return "⚠️ Layanan chat sedang tidak tersedia (konfigurasi). Coba lagi nanti."
    if status == 404 or "model_not_found" in text or "decommissioned" in text or "does not exist" in text:
        return "⚠️ Model chat tidak tersedia lagi di provider. Coba pilih model lain."
    if status == 429 or "rate_limit" in text or "rate limit" in text or "quota" in text:
        return "⏳ Kuota chat sedang penuh. Coba lagi nanti."
    if "timeout" in text:
        return "⌛ Respons terlalu lama. Coba lagi."
    return "❌ Gagal membalas. Coba kirim ulang atau mulai obrolan baru."


def _is_model_unavailable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)
    return (
        status == 404
        or "model_not_found" in text
        or "does not exist" in text
        or "decommissioned" in text
        or ("not_found" in text and "model" in text)
    )


# ============================================================================
# ENGINE 1: CHAT MULTI AI (Groq + persona Yuki + streaming + fallback)
# ============================================================================
def build_chat_client() -> OpenAI:
    return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def messages_for_api(history: list[dict]) -> list[dict]:
    """System prompt Yuki + riwayat terakhir (ramah free-tier)."""
    trimmed = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("type", "text") == "text"
    ][-MAX_HISTORY_MESSAGES:]
    return [{"role": "system", "content": YUKI_SYSTEM_PROMPT}, *trimmed]


def resolve_model_chain(preferred: str) -> list[str]:
    chain: list[str] = []
    for m in (preferred, *GROQ_MODEL_FALLBACKS):
        if m and m not in chain:
            chain.append(m)
    return chain


def stream_chat_reply(client: OpenAI, model: str, history: list[dict]):
    stream = client.chat.completions.create(
        model=model,
        messages=messages_for_api(history),
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        try:
            delta = chunk.choices[0].delta
            piece = getattr(delta, "content", None)
            if piece:
                yield piece
        except Exception:
            continue


def stream_chat_with_fallback(client: OpenAI, preferred_model: str, history: list[dict]):
    """Coba model pilihan user; kalau sudah dihapus provider, pakai fallback."""
    last_exc: Exception | None = None
    for model in resolve_model_chain(preferred_model):
        try:
            stream_iter = stream_chat_reply(client, model, history)
            first = next(stream_iter, None)
            if first:
                yield first
            for piece in stream_iter:
                yield piece
            return
        except Exception as e:
            last_exc = e
            if _is_model_unavailable_error(e):
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("no chat model available")


# ============================================================================
# ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX — dari App 1)
# ============================================================================
def extract_image_bytes(payload: dict) -> bytes:
    if not isinstance(payload, dict):
        raise RuntimeError("invalid response")
    if payload.get("success") is False:
        raise RuntimeError(str(payload.get("errors") or payload))

    result = payload.get("result", payload)
    if isinstance(result, str):
        b64 = result
    elif isinstance(result, dict):
        b64 = result.get("image") or result.get("b64_json") or result.get("base64")
        if b64 is None and isinstance(result.get("data"), list) and result["data"]:
            first = result["data"][0]
            if isinstance(first, dict):
                b64 = first.get("b64_json") or first.get("image")
            elif isinstance(first, str):
                b64 = first
        if b64 is None:
            nested = result.get("result")
            if isinstance(nested, dict):
                b64 = nested.get("image")
            elif isinstance(nested, str):
                b64 = nested
    else:
        b64 = None

    if not b64 or not isinstance(b64, str):
        raise RuntimeError("no image")

    if "," in b64 and b64.strip().lower().startswith("data:"):
        b64 = b64.split(",", 1)[1]

    raw = base64.b64decode(b64, validate=False)
    if not raw:
        raise RuntimeError("empty image")

    try:
        im = Image.open(io.BytesIO(raw))
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return raw


def generate_image(prompt: str) -> bytes:
    url = f"{CF_API_BASE}/{CF_ACCOUNT_ID}/ai/run/{CF_IMAGE_MODEL}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {"prompt": prompt, "steps": CF_DEFAULT_STEPS}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=180)
    except requests.Timeout as e:
        raise RuntimeError("timeout") from e
    except requests.RequestException as e:
        raise RuntimeError(str(e)) from e

    content_type = (resp.headers.get("Content-Type") or "").lower()
    if "image/" in content_type:
        if resp.status_code >= 400:
            raise RuntimeError(public_error_image(resp.status_code, resp.text[:400]))
        raw = resp.content
        try:
            im = Image.open(io.BytesIO(raw))
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return raw

    try:
        payload = resp.json()
    except Exception:
        if resp.status_code >= 400:
            raise RuntimeError(public_error_image(resp.status_code, resp.text[:400]))
        raise RuntimeError("invalid response")

    if resp.status_code >= 400:
        err = payload.get("errors") if isinstance(payload, dict) else payload
        raise RuntimeError(public_error_image(resp.status_code, str(err)[:400]))

    return extract_image_bytes(payload)


# ============================================================================
# RENDER BUBBLE CHAT (style buatan sendiri)
# ============================================================================
def bubble_html(role: str, content: str, timestamp: str = "") -> str:
    body = html.escape(content or "")
    who = "Kamu" if role == "user" else "Yuki"
    css = "user" if role == "user" else "ai"
    meta = f'<div class="bubble-meta">{who} · {html.escape(timestamp)}</div>' if timestamp else ""
    return (
        f'<div class="bubble-row {css}">'
        f'<div class="bubble-wrap">{meta}'
        f'<div class="bubble {css}">{body}</div>'
        f"</div></div>"
    )


def render_message(msg: dict) -> None:
    """Render 1 pesan: teks (bubble) atau gambar."""
    if msg.get("type") == "image" and msg.get("image_bytes"):
        st.markdown(
            bubble_html("assistant", f"🎨 Hasil gambar untuk: {msg.get('prompt', '')}", msg.get("time", "")),
            unsafe_allow_html=True,
        )
        st.image(msg["image_bytes"], use_container_width=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="⬇️ Unduh PNG",
            data=msg["image_bytes"],
            file_name=f"trinity_{ts}.png",
            mime="image/png",
            key=f"dl_{msg.get('id', id(msg))}",
        )
    else:
        st.markdown(
            bubble_html(msg.get("role", "assistant"), msg.get("content", ""), msg.get("time", "")),
            unsafe_allow_html=True,
        )


# ============================================================================
# EXPORT CHAT (.md — diadaptasi dari App 2)
# ============================================================================
def get_chat_export_text() -> str:
    lines = [
        "# Riwayat Obrolan — Ampera Trinity AI",
        f"# Tanggal Ekspor: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "# by Ampera Official\n",
        "---\n",
    ]
    for m in st.session_state.get("messages", []):
        role_label = "👤 Pengguna" if m.get("role") == "user" else "🔱 Yuki"
        time_tag = f" [{m.get('time', '')}]" if m.get("time") else ""
        lines.append(f"### {role_label}{time_tag}\n")
        if m.get("type") == "image":
            lines.append(f"*(gambar dihasilkan — prompt: {m.get('prompt', '')})*")
        else:
            lines.append((m.get("content") or "").strip())
        lines.append("\n---\n")
    return "\n".join(lines)


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "id": 0,
                "role": "assistant",
                "type": "text",
                "content": (
                    "Halo! Aku Yuki dari Ampera Trinity AI (๑>◡<๑)\n\n"
                    "Aku bisa 3 hal sekaligus:\n"
                    "🤖 Ganti-ganti model AI — klik tombol model di bawah\n"
                    "🎨 Bikin gambar — nyalakan Mode Gambar lalu tulis deskripsinya\n"
                    "💬 Ngobrol & coding — tulis aja langsung, aku ladenin wkwk 🐧"
                ),
                "time": datetime.now().strftime("%H:%M"),
            }
        ]
    if "selected_model_label" not in st.session_state:
        st.session_state.selected_model_label = DEFAULT_MODEL_LABEL
    if "image_mode" not in st.session_state:
        st.session_state.image_mode = False
    if "msg_counter" not in st.session_state:
        st.session_state.msg_counter = 1


def next_msg_id() -> int:
    st.session_state.msg_counter += 1
    return st.session_state.msg_counter


def reset_conversation() -> None:
    for key in ("messages", "msg_counter"):
        st.session_state.pop(key, None)
    init_state()


# ============================================================================
# SIDEBAR (minimal dulu — nanti dibuat ulang + search percakapan)
# ============================================================================
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🔱 Ampera Trinity AI")
        st.caption("by Ampera Official")
        st.divider()

        st.markdown(f"**Model aktif:**")
        st.caption(st.session_state.selected_model_label)
        st.markdown(f"**Mode:** {'🎨 Gambar' if st.session_state.image_mode else '💬 Chat'}")
        st.divider()

        if st.button("✦ Obrolan Baru", use_container_width=True):
            reset_conversation()
            st.rerun()

        st.download_button(
            label="📥 Unduh Riwayat Chat",
            data=get_chat_export_text(),
            file_name=f"trinity-chat-{datetime.now().strftime('%Y%m%d-%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.divider()
        chat_status = "🟢 Aktif" if CHAT_READY else "🔴 Belum dikonfigurasi"
        img_status = "🟢 Aktif" if IMAGE_READY else "🔴 Belum dikonfigurasi"
        st.caption(f"Chat AI: {chat_status}")
        st.caption(f"Generate Gambar: {img_status}")


# ============================================================================
# HANDLER PESAN
# ============================================================================
def handle_image_request(prompt: str) -> None:
    """Mode gambar: prompt → Cloudflare FLUX → bubble gambar."""
    if not IMAGE_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur gambar belum dikonfigurasi pemilik (CF_ACCOUNT_ID / CF_API_TOKEN).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    # Loading sementara pakai bawaan Streamlit (nanti dibuat custom)
    with st.spinner("🎨 Yuki sedang menggambar... tunggu sebentar ya~"):
        try:
            data = generate_image(prompt)
            st.session_state.messages.append({
                "id": next_msg_id(), "role": "assistant", "type": "image",
                "image_bytes": data, "prompt": prompt,
                "time": datetime.now().strftime("%H:%M"),
            })
        except Exception as e:
            msg = str(e)
            if not msg.startswith(("⚠️", "⏳", "⌛", "❌")):
                msg = public_error_image(None, msg, e)
            st.session_state.messages.append({
                "id": next_msg_id(), "role": "assistant", "type": "text",
                "content": msg, "time": datetime.now().strftime("%H:%M"),
            })


def handle_chat_request(answer_slot) -> None:
    """Mode chat: streaming jawaban Yuki dengan model terpilih + fallback."""
    if not CHAT_READY:
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": "⚠️ Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY).",
            "time": datetime.now().strftime("%H:%M"),
        })
        return

    model_id = AVAILABLE_MODELS.get(
        st.session_state.selected_model_label,
        AVAILABLE_MODELS[DEFAULT_MODEL_LABEL],
    )

    try:
        # Loading sementara pakai bawaan Streamlit (nanti dibuat custom)
        with st.spinner("🐧 Yuki sedang berpikir..."):
            client = build_chat_client()
            stream_iter = stream_chat_with_fallback(
                client, model_id, st.session_state.messages
            )
            first = next(stream_iter, None)

        full = first or ""
        if full:
            answer_slot.markdown(bubble_html("assistant", full), unsafe_allow_html=True)
        for piece in stream_iter:
            full += piece or ""
            answer_slot.markdown(bubble_html("assistant", full), unsafe_allow_html=True)

        if not full:
            full = "…"
            answer_slot.markdown(bubble_html("assistant", full), unsafe_allow_html=True)

        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": full, "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        err = public_error_chat(e)
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "assistant", "type": "text",
            "content": err, "time": datetime.now().strftime("%H:%M"),
        })


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    # ---------- Header ----------
    st.markdown(
        f"""
<div class="trinity-head">
  <div class="trinity-logo">🔱</div>
  <div>
    <h1>{APP_NAME}</h1>
    <p>{APP_TAGLINE}</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---------- Riwayat chat ----------
    for msg in st.session_state.messages:
        render_message(msg)

    # ---------- Kontrol di area chat input ----------
    # (Multi AI + Mode Gambar, keduanya di dekat kolom ketik sesuai permintaan)
    ctrl_model, ctrl_mode = st.columns([1.4, 1])

    with ctrl_model:
        current = st.session_state.selected_model_label
        short_name = current.split("—")[0].strip()
        with st.popover(f"🤖 {short_name}", use_container_width=True):
            st.markdown("**Pilih Model AI**")
            for label in AVAILABLE_MODELS:
                is_active = label == st.session_state.selected_model_label
                btn_label = f"✅ {label}" if is_active else label
                if st.button(btn_label, key=f"model_{label}", use_container_width=True):
                    st.session_state.selected_model_label = label
                    st.rerun()

    with ctrl_mode:
        st.session_state.image_mode = st.toggle(
            "🎨 Mode Gambar",
            value=st.session_state.image_mode,
            help="Nyalakan untuk membuat gambar dari teks (Cloudflare FLUX). "
                 "Matikan untuk chat biasa dengan Yuki.",
        )

    # Badge mode aktif
    if st.session_state.image_mode:
        st.markdown(
            '<span class="mode-badge img">🎨 Mode Gambar aktif — tulis deskripsi gambarmu</span>',
            unsafe_allow_html=True,
        )

    # ---------- Chat input ----------
    placeholder_text = (
        "Deskripsikan gambar yang ingin dibuat..."
        if st.session_state.image_mode
        else "Tanya apa saja ke Yuki..."
    )
    user_text = st.chat_input(placeholder_text)

    if user_text and user_text.strip():
        text = user_text.strip()
        now = datetime.now().strftime("%H:%M")

        # simpan & tampilkan pesan user
        st.session_state.messages.append({
            "id": next_msg_id(), "role": "user", "type": "text",
            "content": text, "time": now,
        })
        st.markdown(bubble_html("user", text, now), unsafe_allow_html=True)

        if st.session_state.image_mode:
            handle_image_request(text)
        else:
            answer_slot = st.empty()
            handle_chat_request(answer_slot)

        st.rerun()

    # ---------- Footer ----------
    st.markdown(
        '<p style="text-align:center;color:#475569;font-size:0.75rem;margin-top:30px;">'
        "🔱 Ampera Trinity AI · by Ampera Official · 2026</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
