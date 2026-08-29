#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Cloudflare Flux Service Module
==================================================
Menangani eksekusi pembuatan gambar menggunakan Cloudflare Workers AI
serta fitur Prompt Enhancer kustom.
"""

import base64
import requests


class FluxService:
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"

    def is_ready(self) -> bool:
        return bool(self.account_id and self.api_token)

    def enhance_prompt(self, user_prompt: str, style: str = "Photorealistic") -> str:
        """
        Otomatis memperkaya prompt singkat menjadi prompt profesional untuk Flux.
        """
        style_modifiers = {
            "Photorealistic": "hyper-realistic, 8k resolution, highly detailed, photorealistic, professional photography, natural lighting, bokeh",
            "Anime / Manga": "anime art style, vibrant colors, Makoto Shinkai style, highly detailed illustration, 4k",
            "3D Render": "3D Blender render, Octane Render, Raytracing, vivid lighting, soft shadows, isometric 3d",
            "Cyberpunk": "cyberpunk style, glowing neon lights, rainy street reflections, dark moody atmosphere, ultra detailed",
            "Watermark Logo": "vector logo design, clean typography, minimalist graphic, isolated on black background, professional branding"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["Photorealistic"])
        return f"{user_prompt}, {modifier}"

    def generate_image(self, prompt: str):
        """
        Mengirimkan API request ke Cloudflare Flux-1-Schnell.
        """
        if not self.is_ready():
            raise ValueError("Kredensial Cloudflare belum diisi.")

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt}

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success") and "result" in res_json:
                image_b64 = res_json["result"].get("image")
                if image_b64:
                    return base64.b64decode(image_b64)
            raise ValueError("Respon API sukses tetapi gambar tidak ditemukan.")
        else:
            raise ValueError(f"Cloudflare Error ({response.status_code}): {response.text}")
