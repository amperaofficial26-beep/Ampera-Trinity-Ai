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


def _apply_size(raw: bytes, size_key: str | None) -> bytes:
    preset = IMAGE_SIZE_BY_KEY.get(size_key or DEFAULT_IMAGE_SIZE_KEY)
    if not preset:
        return raw
    return fit_to_size(raw, int(preset["w"]), int(preset["h"]))


def fit_to_size(raw: bytes, width: int, height: int) -> bytes:
    """Potong tengah (center-crop) ke rasio target lalu skalakan ke ukuran itu.

    Model flux-1-schnell di Cloudflare tidak punya parameter width/height,
    jadi pengaturan ukuran dikerjakan di sini. Center-crop dipakai supaya
    gambar tidak gepeng/melar seperti kalau langsung di-resize paksa.
    """
    if not raw or width <= 0 or height <= 0:
        return raw
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
        src_w, src_h = im.size
        if not src_w or not src_h:
            return raw

        target_ratio = width / height
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:          # sumber terlalu lebar -> pangkas kiri-kanan
            new_w = int(round(src_h * target_ratio))
            left = (src_w - new_w) // 2
            box = (left, 0, left + new_w, src_h)
        else:                                  # sumber terlalu tinggi -> pangkas atas-bawah
            new_h = int(round(src_w / target_ratio))
            top = (src_h - new_h) // 2
            box = (0, top, src_w, top + new_h)
        im = im.crop(box).resize((width, height), Image.LANCZOS)

        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue()
    except Exception:
        # Kalau apa pun gagal, kembalikan gambar aslinya — jangan sampai
        # pengaturan ukuran malah membatalkan hasil yang sudah jadi.
        return raw


def generate_image(prompt: str, size_key: str | None = None) -> bytes:
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
            raw = buf.getvalue()
        except Exception:
            pass
        return _apply_size(raw, size_key)

    try:
        payload = resp.json()
    except Exception:
        if resp.status_code >= 400:
            raise RuntimeError(public_error_image(resp.status_code, resp.text[:400]))
        raise RuntimeError("invalid response")

    if resp.status_code >= 400:
        err = payload.get("errors") if isinstance(payload, dict) else payload
        raise RuntimeError(public_error_image(resp.status_code, str(err)[:400]))

    return _apply_size(extract_image_bytes(payload), size_key)
