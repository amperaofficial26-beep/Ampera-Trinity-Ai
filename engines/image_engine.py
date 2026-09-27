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


# ============================================================================
# PROVIDER LAIN: Leonardo.ai, Ideogram, Google ImageFX, Microsoft Designer
# ----------------------------------------------------------------------------
# generate_image() di atas tetap jalur Cloudflare FLUX (bawaan). Fungsi
# generate_image_provider() di bawah memilih jalur sesuai provider yang
# dipilih User di panel kanan halaman AI Image.
#
# Catatan jujur soal kuota gratis:
#   - Leonardo & Ideogram : punya API RESMI, dipakai dengan API key. Jatah
#     gratis harian (150 Fast Token / 10 slow credit) berlaku di akun web;
#     pemakaian lewat API mengikuti kebijakan kredit akun masing-masing.
#   - ImageFX & Designer  : TIDAK punya API publik. Di sini dipakai jalur
#     internal web-nya dengan token/cookie akun sendiri — gratis sesuai
#     jatah harian akun, tapi token berumur pendek (ImageFX ±1 jam,
#     cookie Bing _U ±2-4 minggu) dan sewaktu-waktu bisa berubah.
# ============================================================================
import json as _json
import re as _re
import time as _time
import urllib.parse as _urlparse


def _png(raw: bytes) -> bytes:
    """Normalkan bytes gambar apa pun jadi PNG (kalau bisa)."""
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


def _unduh(url: str, timeout: int = 90) -> bytes:
    resp = requests.get(url, timeout=timeout)
    if resp.status_code >= 400 or not resp.content:
        raise RuntimeError(f"gagal mengunduh hasil ({resp.status_code})")
    return _png(resp.content)


def _ukuran_dari_rasio(rasio: str | None, sisi: int = 1024) -> tuple[int, int]:
    """Ubah key rasio (mis. '9:16') jadi ukuran piksel kelipatan 8."""
    from config import IMAGE_RATIOS

    info = next((r for r in IMAGE_RATIOS if r["key"] == rasio), None)
    w, h = (info["w"], info["h"]) if info else (1, 1)
    if w >= h:
        lebar, tinggi = sisi, int(round(sisi * h / w))
    else:
        lebar, tinggi = int(round(sisi * w / h)), sisi
    bulat = lambda n: max(512, int(round(n / 8)) * 8)   # noqa: E731
    return bulat(lebar), bulat(tinggi)


# ---------------------------------------------------------------- Leonardo --
def _gen_leonardo(prompt: str, rasio: str | None) -> bytes:
    from config import LEONARDO_API_BASE, LEONARDO_API_KEY, LEONARDO_MODEL_ID

    if not LEONARDO_API_KEY:
        raise RuntimeError("LEONARDO_API_KEY belum diisi.")

    lebar, tinggi = _ukuran_dari_rasio(rasio)
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {LEONARDO_API_KEY}",
        "content-type": "application/json",
    }
    body = {
        "prompt": prompt,
        "modelId": LEONARDO_MODEL_ID,
        "width": lebar,
        "height": tinggi,
        "num_images": 1,
    }
    resp = requests.post(f"{LEONARDO_API_BASE}/generations",
                         headers=headers, json=body, timeout=90)
    if resp.status_code >= 400:
        raise RuntimeError(public_error_image(resp.status_code,
                                              resp.text[:300]))
    data = resp.json() or {}
    gid = ((data.get("sdGenerationJob") or {}).get("generationId")
           or (data.get("generations_by_pk") or {}).get("id"))
    if not gid:
        raise RuntimeError("Leonardo tidak mengembalikan generationId.")

    # Generasi Leonardo asinkron: tunggu sampai status COMPLETE.
    batas = _time.time() + 150
    while _time.time() < batas:
        _time.sleep(3)
        cek = requests.get(f"{LEONARDO_API_BASE}/generations/{gid}",
                           headers=headers, timeout=45)
        if cek.status_code >= 400:
            continue
        info = (cek.json() or {}).get("generations_by_pk") or {}
        status = (info.get("status") or "").upper()
        if status == "COMPLETE":
            gambar = info.get("generated_images") or []
            if not gambar:
                raise RuntimeError("Leonardo selesai tapi tanpa gambar.")
            return _unduh(gambar[0].get("url") or "")
        if status == "FAILED":
            raise RuntimeError("Leonardo gagal memproses prompt ini.")
    raise RuntimeError("timeout")


# ---------------------------------------------------------------- Ideogram --
_IDEOGRAM_ASPEK = {
    "1:1": ("1x1", "ASPECT_1_1"),
    "4:5": ("4x5", "ASPECT_4_5"),
    "9:16": ("9x16", "ASPECT_9_16"),
    "16:9": ("16x9", "ASPECT_16_9"),
    "4:3": ("4x3", "ASPECT_4_3"),
}


def _gen_ideogram(prompt: str, rasio: str | None) -> bytes:
    from config import IDEOGRAM_API_KEY, IDEOGRAM_API_LEGACY, IDEOGRAM_API_V3

    if not IDEOGRAM_API_KEY:
        raise RuntimeError("IDEOGRAM_API_KEY belum diisi.")

    v3_aspek, legacy_aspek = _IDEOGRAM_ASPEK.get(rasio or "1:1",
                                                 ("1x1", "ASPECT_1_1"))
    headers = {"Api-Key": IDEOGRAM_API_KEY, "Content-Type": "application/json"}

    # Jalur utama: endpoint v3. Kalau ditolak (mis. akun belum punya akses),
    # jatuh ke endpoint lama /generate yang masih dilayani Ideogram.
    percobaan = [
        (IDEOGRAM_API_V3, {
            "prompt": prompt,
            "aspect_ratio": v3_aspek,
            "rendering_speed": "DEFAULT",
        }),
        (IDEOGRAM_API_LEGACY, {
            "image_request": {
                "prompt": prompt,
                "model": "V_2",
                "aspect_ratio": legacy_aspek,
                "magic_prompt_option": "AUTO",
            },
        }),
    ]

    galat = ""
    for url, body in percobaan:
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=180)
        except requests.RequestException as e:
            galat = str(e)
            continue
        if resp.status_code >= 400:
            galat = f"{resp.status_code} {resp.text[:200]}"
            continue
        data = resp.json() or {}
        daftar = data.get("data") or []
        if daftar and isinstance(daftar[0], dict):
            tautan = daftar[0].get("url")
            if tautan:
                return _unduh(tautan)
        galat = "respons tanpa gambar"
    raise RuntimeError(public_error_image(None, galat or "gagal"))


# ------------------------------------------------------------ Google ImageFX --
_IMAGEFX_ASPEK = {
    "1:1": "IMAGE_ASPECT_RATIO_SQUARE",
    "4:5": "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR",
    "9:16": "IMAGE_ASPECT_RATIO_PORTRAIT",
    "16:9": "IMAGE_ASPECT_RATIO_LANDSCAPE",
    "4:3": "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE",
}


def _gen_imagefx(prompt: str, rasio: str | None) -> bytes:
    from config import IMAGEFX_AUTH_TOKEN, IMAGEFX_ENDPOINT, IMAGEFX_MODEL

    token = IMAGEFX_AUTH_TOKEN
    if not token:
        raise RuntimeError("IMAGEFX_AUTH_TOKEN belum diisi.")
    token = token.strip().removeprefix("Bearer ").strip()

    body = {
        "userInput": {
            "candidatesCount": 1,
            "prompts": [prompt],
            "seed": None,
        },
        "clientContext": {"sessionId": ";1", "tool": "IMAGE_FX"},
        "modelInput": {"modelNameType": IMAGEFX_MODEL},
        "aspectRatio": _IMAGEFX_ASPEK.get(rasio or "1:1",
                                          "IMAGE_ASPECT_RATIO_SQUARE"),
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://labs.google",
        "Referer": "https://labs.google/",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"),
    }
    resp = requests.post(IMAGEFX_ENDPOINT, headers=headers,
                         data=_json.dumps(body), timeout=180)
    if resp.status_code in (401, 403):
        raise RuntimeError(
            "Token ImageFX kedaluwarsa. Ambil ulang dari labs.google/fx "
            "lalu perbarui IMAGEFX_AUTH_TOKEN."
        )
    if resp.status_code >= 400:
        raise RuntimeError(public_error_image(resp.status_code,
                                              resp.text[:300]))
    data = resp.json() or {}
    panel = (data.get("imagePanels") or [{}])[0]
    gambar = (panel.get("generatedImages") or [{}])[0]
    b64 = gambar.get("encodedImage")
    if not b64:
        raise RuntimeError("ImageFX tidak mengembalikan gambar.")
    return _png(base64.b64decode(b64, validate=False))


# -------------------------------------------------- Microsoft Designer / Bing --
_BING_IMG_RE = _re.compile(r'src="(https://[^"]*?/th/id/OIG[^"]*?)"')


def _gen_designer(prompt: str, rasio: str | None) -> bytes:
    from config import DESIGNER_BASE, DESIGNER_COOKIE_SRCH, DESIGNER_COOKIE_U

    if not DESIGNER_COOKIE_U:
        raise RuntimeError("BING_COOKIE_U belum diisi.")

    sesi = requests.Session()
    sesi.cookies.set("_U", DESIGNER_COOKIE_U, domain=".bing.com")
    if DESIGNER_COOKIE_SRCH:
        sesi.cookies.set("SRCHHPGUSR", DESIGNER_COOKIE_SRCH,
                         domain=".bing.com")
    sesi.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/124.0 Safari/537.36"),
        "Referer": f"{DESIGNER_BASE}/images/create/",
        "Origin": DESIGNER_BASE,
    })

    q = _urlparse.quote(prompt)
    # rt=4 → pakai Boost (cepat); kalau Boost habis Bing otomatis
    # mengalihkan ke antrean kecepatan normal (rt=3), bukan menolak.
    url = f"{DESIGNER_BASE}/images/create?q={q}&rt=4&FORM=GENCRE"
    resp = sesi.post(url, data={"q": prompt, "qs": "ds"},
                     allow_redirects=False, timeout=90)

    lokasi = resp.headers.get("Location") or ""
    if not lokasi:
        resp = sesi.post(
            f"{DESIGNER_BASE}/images/create?q={q}&rt=3&FORM=GENCRE",
            data={"q": prompt, "qs": "ds"}, allow_redirects=False, timeout=90,
        )
        lokasi = resp.headers.get("Location") or ""
    if not lokasi:
        teks = resp.text or ""
        if "being reviewed" in teks or "gerakan" in teks:
            raise RuntimeError("Prompt ditolak filter konten Bing.")
        raise RuntimeError(
            "Cookie Bing (_U) tidak diterima atau sudah kedaluwarsa."
        )

    id_hasil = lokasi.split("id=")[-1].split("&")[0] if "id=" in lokasi else \
        lokasi.rstrip("/").split("/")[-1].split("?")[0]
    poll = f"{DESIGNER_BASE}/images/create/async/results/{id_hasil}?q={q}"

    batas = _time.time() + 240
    while _time.time() < batas:
        _time.sleep(3)
        cek = sesi.get(poll, timeout=45)
        if cek.status_code >= 400:
            continue
        tautan = _BING_IMG_RE.findall(cek.text or "")
        if tautan:
            bersih = tautan[0].split("?")[0] + "?pid=ImgGn"
            return _unduh(bersih)
    raise RuntimeError("timeout")


# ------------------------------------------------------------- Dispatcher --
_PROVIDER_FN = {
    "leonardo": _gen_leonardo,
    "ideogram": _gen_ideogram,
    "imagefx": _gen_imagefx,
    "designer": _gen_designer,
}


def generate_image_provider(prompt: str, provider: str | None = None,
                            rasio: str | None = None) -> bytes:
    """Buat gambar lewat provider pilihan User.

    provider kosong / tidak dikenal / "cloudflare" → jalur FLUX bawaan.
    """
    from config import IMAGE_PROVIDER_BY_KEY, IMAGE_PROVIDER_DEFAULT

    key = (provider or IMAGE_PROVIDER_DEFAULT or "cloudflare").strip()
    info = IMAGE_PROVIDER_BY_KEY.get(key)
    if info and not info.get("ready"):
        butuh = ", ".join(info.get("butuh") or [])
        raise RuntimeError(
            f"{info.get('nama', key)} belum dikonfigurasi pemilik aplikasi "
            f"({butuh})."
        )
    fn = _PROVIDER_FN.get(key)
    if fn is None:
        return generate_image(prompt)
    return fn(prompt, rasio)
