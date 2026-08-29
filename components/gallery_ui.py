#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Gallery & Prompt Generator UI
=================================================
Modul UI untuk pembuatan gambar (Flux-1-Schnell), pemoles prompt otomatis (Prompt Enhancer),
serta galeri hasil gambar interaktif.
"""

import time
import streamlit as st
from services.flux_service import FluxService


def render_gallery_tab(flux_service: FluxService):
    st.markdown("### 🎨 Generator Foto (Cloudflare Workers AI - Flux)")
    st.write("Buat foto resolusi tinggi, logo, visual 3D, atau animasi dari prompt teks Anda.")

    if not flux_service.is_ready():
        st.warning("⚠️ `CF_ACCOUNT_ID` dan `CF_API_TOKEN` belum dikonfigurasi di Secrets. Silakan lengkapi terlebih dahulu.")

    col_input, col_style = st.columns([3, 1])
    
    with col_style:
        style_choice = st.selectbox(
            "Gaya Visual:",
            ["Photorealistic", "Anime / Manga", "3D Render", "Cyberpunk", "Watermark Logo"]
        )

    with col_input:
        raw_prompt = st.text_area(
            "Deskripsi Gambar (Prompt):",
            placeholder="Contoh: Tulisan Alfalah Media dengan logo watermark elegan, latar belakang transparan/gelap, lighting studio premium",
            height=100
        )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        generate_btn = st.button("🚀 Buat Gambar", type="primary", use_container_width=True)
    with col_btn2:
        enhance_btn = st.button("🪄 Poles Prompt Otomatis", use_container_width=True)

    # Logika Enhance Prompt
    if enhance_btn and raw_prompt:
        enhanced = flux_service.enhance_prompt(raw_prompt, style_choice)
        st.info(f"**Prompt Hasil Poles:**\n`{enhanced}`")

    # Logika Generate Gambar
    if generate_btn and raw_prompt:
        if not flux_service.is_ready():
            st.error("Kredensial Cloudflare API belum lengkap!")
        else:
            final_prompt = flux_service.enhance_prompt(raw_prompt, style_choice)
            with st.spinner(f"Membuat gambar bergaya {style_choice} dengan model Flux... Mohon tunggu..."):
                try:
                    img_bytes = flux_service.generate_image(final_prompt)
                    if img_bytes:
                        st.session_state.generated_images.insert(0, {
                            "prompt": final_prompt,
                            "style": style_choice,
                            "bytes": img_bytes,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success("Gambar berhasil dibuat!")
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")

    # Display Galeri Hasil Gambar
    if st.session_state.generated_images:
        st.markdown("---")
        st.markdown("### 🖼️ Galeri Hasil Sesi Ini")
        
        for idx, item in enumerate(st.session_state.generated_images):
            c_img, c_detail = st.columns([1, 1])
            with c_img:
                st.image(item["bytes"], caption=f"Hasil #{idx+1} — {item['style']}", use_container_width=True)
            with c_detail:
                st.markdown(f"**Gaya:** {item['style']}")
                st.markdown(f"**Prompt:**\n> {item['prompt']}")
                st.markdown(f"**Waktu:** {item['time']}")
                st.download_button(
                    label="💾 Unduh Gambar (PNG)",
                    data=item["bytes"],
                    file_name=f"ampera_flux_{idx+1}.png",
                    mime="image/png",
                    key=f"dl_gal_{idx}"
                )
            st.divider()
