# -*- coding: utf-8 -*-
"""
ENGINE 2: GENERATE GAMBAR (Cloudflare FLUX)
"""

from __future__ import annotations

import base64
import io

import requests
from PIL import Image

from config import CF_ACCOUNT_ID, CF_API_TOKEN, CF_API_BASE, CF_IMAGE_MODEL, CF_DEFAULT_STEPS
from errors import public_error_image

# ---------------------------------------------------------------------------
# PROMPT PANJANG → diringkas otomatis
#
# FLUX.1-schnell di Cloudflare hanya mampu membaca ±256 token prompt
# (encoder T5-nya lebih kecil daripada FLUX Dev yang 512). Prompt yang
# lebih panjang ditolak dengan HTTP 400 — sebelumnya ke pengguna hanya
# muncul error generik "Gagal membuat gambar". Karena itu prompt panjang
# diringkas dulu oleh model chat (Groq, cepat), dengan pemotongan di
# batas kalimat sebagai cadangan kalau peringkasan gagal.
# ---------------------------------------------------------------------------
PROMPT_BATAS_KARAKTER = 1000   # ±256 token; lebih dari ini tidak aman
PROMPT_TARGET_KARAKTER = 820   # target hasil ringkasan/pemotongan

_INSTRUKSI_RINGKAS = (
    "You condense image-generation prompts for the FLUX text-to-image "
    "model, which reads at most about 256 tokens. Rewrite the user's "
    "prompt into ONE compact paragraph of at most 750 characters, in the "
    "SAME language as the original. Keep: the main subject and scene, the "
    "most important visual details, the style/photorealism keywords, the "
    "camera and composition notes, and a short 'no ...' list with the most "
    "important exclusions. Merge duplicates and drop filler. Output ONLY "
    "the condensed prompt — no explanations, no quotes, no markdown."
)


def _potong_prompt(prompt: str) -> str:
    """Potong prompt di batas kalimat (tidak di tengah kata)."""
    if len(prompt) <= PROMPT_TARGET_KARAKTER:
        return prompt
    potongan = prompt[: PROMPT_TARGET_KARAKTER + 120]
    for tanda in (". ", "! ", "? ", "; ", ", "):
        idx = potongan.rfind(tanda)
        if idx >= PROMPT_TARGET_KARAKTER // 2:
            return potongan[: idx + 1].strip()
    return prompt[:PROMPT_TARGET_KARAKTER].rsplit(" ", 1)[0].strip() + " …"


def ringkas_prompt_panjang(prompt: str) -> tuple[str, str]:
    """Siapkan prompt agar muat di batas baca model gambar FLUX.

    Return (prompt_siap, catatan). catatan kosong berarti prompt tidak
    diubah. Kalau panjang: coba diringkas oleh model chat; kalau gagal
    atau hasilnya masih panjang, dipotong di batas kalimat.
    """
    p = " ".join(prompt.split())
    if len(p) <= PROMPT_BATAS_KARAKTER:
        return p, ""

    ringkas = ""
    try:
        from config import GROQ_API_KEY, DEFAULT_MODEL_KEY
        if GROQ_API_KEY:
            from engines.groq_engine import build_chat_client, resolve_model_chain
            client = build_chat_client()
            model = resolve_model_chain(DEFAULT_MODEL_KEY)[0]
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _INSTRUKSI_RINGKAS},
                    {"role": "user", "content": p},
                ],
                temperature=0.2,
                max_tokens=350,
                stream=False,
                timeout=25,
            )
            ringkas = (resp.choices[0].message.content or "").strip()
            # Buang kutip pembungkus kalau model menambahkannya.
            if len(ringkas) >= 2 and ringkas[0] == ringkas[-1] and ringkas[0] in "\"'`":
                ringkas = ringkas[1:-1].strip()
    except Exception:
        ringkas = ""

    cara = "diringkas otomatis oleh AI"
    if not ringkas or len(ringkas) > PROMPT_BATAS_KARAKTER:
        ringkas = _potong_prompt(p)
        cara = "dipotong otomatis di batas kalimat"

    catatan = (
        f"Prompt asli {len(p):,} karakter — {cara} jadi {len(ringkas):,} "
        "karakter, karena model gambar hanya mampu membaca ±256 token."
    )
    return ringkas, catatan


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
