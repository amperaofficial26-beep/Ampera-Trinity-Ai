#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Main Application File
=========================================
File utama aplikasi Streamlit yang mengelola UI, routing halaman,
interaksi chat dengan Groq, dan generator gambar dengan Cloudflare Workers AI.

Jalankan dengan:
    streamlit run app.py
"""

import os
import json
import time
import base64
import requests
import streamlit as st
from openai import OpenAI

# Impor variabel & fungsi dari config.py
from config import (
    APP_NAME,
    APP_TAGLINE,
    LOGO_B64,
    GROQ_BASE_URL,
    MODEL_CATALOG,
    MODEL_BY_KEY,
    DEFAULT_MODEL_KEY,
    MAX_HISTORY_MESSAGES,
    YUKI_SYSTEM_PROMPT,
    DEFAULT_SETTINGS,
    get_secret,
)

# ============================================================================
# KONFIGURASI UTAMA STREAMLIT
# ============================================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon=f"data:image/png;base64,{LOGO_B64}",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# KREDENSIAL API
# ============================================================================
GROQ_API_KEY = get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

CHAT_READY = bool(GROQ_API_KEY)
IMAGE_READY = bool(CF_ACCOUNT_ID and CF_API_TOKEN)

# ============================================================================
# INISIALISASI SESSION STATE
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_key" not in st.session_state:
    st.session_state.selected_model_key = DEFAULT_MODEL_KEY
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Chat AI"
if "settings" not in st.session_state:
    st.session_state.settings = DEFAULT_SETTINGS.copy()
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# ============================================================================
# CUSTOM CSS / TAMPILAN
# ============================================================================
CUSTOM_CSS = """
<style>
    /* Styling Dasar Utama */
    .stApp {
        background-color: #faf8f5;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Brand */
    .trinity-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        padding: 20px 0 10px 0;
    }
    .trinity-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2d2b38;
        margin: 0;
    }
    .trinity-sub {
        text-align: center;
        color: #6b667b;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }

    /* Bubble Chat Custom */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f0ede6;
        border-right: 1px solid #e2ddd5;
    }
    
    /* Tombol Generator Foto */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
# ============================================================================
# FUNGSI PEMBANTU (HELPER FUNCTIONS)
# ============================================================================

def generate_image_cf(prompt: str, account_id: str, api_token: str):
    """
    Mengirimkan prompt ke Cloudflare Workers AI (Model Flux-1-Schnell)
    untuk menghasilkan gambar.
    """
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and "result" in result:
                image_b64 = result["result"].get("image")
                if image_b64:
                    return base64.b64decode(image_b64)
            st.error("Gagal memproses gambar dari respon Cloudflare.")
        else:
            st.error(f"Cloudflare API Error ({response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"Koneksi ke Cloudflare gagal: {e}")
    return None


def get_groq_response(messages: list, model_id: str, api_key: str):
    """
    Mengirimkan pesan riwayat ke Groq API menggunakan SDK OpenAI secara streaming.
    """
    client = OpenAI(
        base_url=GROQ_BASE_URL,
        api_key=api_key,
    )
    
    messages_for_api = [{"role": "system", "content": YUKI_SYSTEM_PROMPT}]
    for m in messages[-MAX_HISTORY_MESSAGES:]:
        messages_for_api.append({"role": m["role"], "content": m["content"]})

    return client.chat.completions.create(
        model=model_id,
        messages=messages_for_api,
        stream=True,
    )


# ============================================================================
# HEADER APLIKASI
# ============================================================================
st.markdown(
    f"""
    <div class="trinity-header">
        <img src="data:image/png;base64,{LOGO_B64}" width="50" height="50">
        <h1 class="trinity-title">{APP_NAME}</h1>
    </div>
    <p class="trinity-sub">{APP_TAGLINE}</p>
    """,
    unsafe_allow_html=True
)


# ============================================================================
# NAVIGATION TABS
# ============================================================================
tab_chat, tab_image, tab_settings = st.tabs(["💬 Chat AI (Yuki)", "🎨 Generator Foto (Flux)", "⚙️ Pengaturan"])


# ============================================================================
# TAB 1: CHAT AI (YUKI)
# ============================================================================
with tab_chat:
    # Cek status API Key
    if not CHAT_READY:
        st.warning("⚠️ GROQ_API_KEY belum terkonfigurasi. Silakan tambahkan API Key di Streamlit Secrets / Environment Variables.")
    
    # Tampilkan riwayat obrolan
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.write(content)

    # Input pesan pengguna
    if prompt := st.chat_input("Tanyakan sesuatu pada Yuki..."):
        # Masukkan ke riwayat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Proses respon AI jika siap
        if CHAT_READY:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    selected_model = MODEL_BY_KEY.get(
                        st.session_state.selected_model_key, MODEL_CATALOG[0]
                    )["id"]
                    
                    stream = get_groq_response(
                        st.session_state.messages,
                        selected_model,
                        GROQ_API_KEY
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi Yuki: {e}")


# ============================================================================
# TAB 2: GENERATOR FOTO (FLUX)
# ============================================================================
with tab_image:
    st.subheader("🎨 Generator Foto (Cloudflare Flux-1-Schnell)")
    st.write("Ubah ide teks Anda menjadi gambar visual yang menakjubkan.")

    if not IMAGE_READY:
        st.warning("⚠️ `CF_ACCOUNT_ID` dan `CF_API_TOKEN` belum terkonfigurasi di Secrets. Harap lengkapi untuk menggunakan fitur Generator Foto.")
    
    img_prompt = st.text_area(
        "Deskripsikan gambar yang ingin dibuat (Prompt):",
        placeholder="Contoh: A futuristic cyberpunk city in 3D render, glowing neon lights, rainy street, ultra detailed, 8k"
    )
    
    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        generate_btn = st.button("🚀 Buat Gambar", type="primary")

    if generate_btn and img_prompt:
        if not IMAGE_READY:
            st.error("Kredensial Cloudflare belum diisi di Secrets!")
        else:
            with st.spinner("Sedang memproses gambar dengan model Flux... Mohon tunggu sebentar."):
                img_bytes = generate_image_cf(img_prompt, CF_ACCOUNT_ID, CF_API_TOKEN)
                if img_bytes:
                    st.session_state.generated_images.insert(0, {
                        "prompt": img_prompt,
                        "bytes": img_bytes,
                        "time": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("Gambar berhasil dibuat!")

    # Tampilkan Galeri Gambar Hasil Generate
    if st.session_state.generated_images:
        st.markdown("---")
        st.subheader("🖼️ Galeri Gambar Terbaru")
        
        for idx, item in enumerate(st.session_state.generated_images):
            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(item["bytes"], caption=f"Hasil #{idx+1}", use_container_width=True)
            with col_info:
                st.markdown(f"**Prompt:**\n> {item['prompt']}")
                st.markdown(f"**Waktu:** {item['time']}")
                st.download_button(
                    label="💾 Unduh Gambar",
                    data=item["bytes"],
                    file_name=f"ampera_flux_{idx+1}.png",
                    mime="image/png",
                    key=f"dl_{idx}"
                )
            st.divider()


# ============================================================================
# TAB 3: PENGATURAN & SIDEBAR
# ============================================================================
with tab_settings:
    st.subheader("⚙️ Pengaturan Aplikasi")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.session_state.settings["display_name"] = st.text_input(
            "Nama Panggilan Anda:",
            value=st.session_state.settings.get("display_name", "User")
        )
        st.session_state.settings["theme"] = st.selectbox(
            "Tema Tampilan:",
            ["Beige hangat", "Gelap (Dark Mode)", "Terang (Light Mode)"],
            index=0
        )
    
    with col_s2:
        st.session_state.settings["allow_web_search"] = st.checkbox(
            "Aktifkan Web Search (Compound)",
            value=st.session_state.settings.get("allow_web_search", True)
        )
        st.session_state.settings["save_history"] = st.checkbox(
            "Simpan Sesi Obrolan",
            value=st.session_state.settings.get("save_history", True)
        )

    if st.button("Hapus Seluruh Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()


# ============================================================================
# SIDEBAR CONTROL & INFO MODEL
# ============================================================================
with st.sidebar:
    st.markdown("### 🤖 Pilihan Model AI")
    model_options = {m["key"]: f"{m['name']} ({m['desc']})" for m in MODEL_CATALOG}
    selected_key = st.selectbox(
        "Pilih Model Otak Yuki:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    st.session_state.selected_model_key = selected_key
    
    # Detail Model Aktif
    curr_model = MODEL_BY_KEY.get(selected_key, MODEL_CATALOG[0])
    st.info(f"**Model Aktif:**\n`{curr_model['id']}`\n\n_{curr_model['desc']}_")

    st.markdown("---")
    st.markdown("### 🔑 Status Kredensial API")
    st.write(f"• **Groq API:** {'✅ Aktif' if CHAT_READY else '❌ Belum Set'}")
    st.write(f"• **Cloudflare Workers AI:** {'✅ Aktif' if IMAGE_READY else '❌ Belum Set'}")
    
    st.markdown("---")
    if st.button("🗑️ Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"© Ampera Official — {APP_NAME}")
