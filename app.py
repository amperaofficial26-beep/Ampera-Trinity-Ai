#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Main Application (Claude-Style Layout)
==========================================================
"""

import os
import sys
import base64
import streamlit as st

# Setup Root Directory Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
from services.groq_service import GroqService
from services.flux_service import FluxService

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=f"data:image/png;base64,{config.LOGO_B64}",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CLAUDE-STYLE CLEAN UI & MATERIAL SYMBOLS CSS
# ============================================================================
CLAUDE_STYLE_CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    /* 1. Typography & Polos (Tanpa Background Berlebihan) */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        background-color: #ffffff !important;
        color: #2d2d2d !important;
    }
    
    /* 2. Material Symbols Setup */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        display: inline-block;
        line-height: 1;
        vertical-align: middle;
    }

    /* 3. Header Utama Ala Claude (Minimalis & Clean) */
    .claude-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0 20px 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 24px;
    }
    
    .claude-brand {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .claude-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
        letter-spacing: -0.3px;
    }

    .claude-subtitle {
        font-size: 0.85rem;
        color: #707070;
        margin: 0;
    }

    /* 4. Chat Messages Styling (Bentuk Kartu Rapi ala Claude) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f9f9fb !important;
        border: 1px solid #ececef !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff !important;
        border: 1px solid #f0f0f0 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }

    /* 5. Custom Control Area di Bawah Input Chat */
    .input-tools-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: -10px;
        padding: 8px 4px;
    }

    /* Sembunyikan Elemen Default Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(CLAUDE_STYLE_CSS, unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SERVICES & SESSION
# ============================================================================
GROQ_API_KEY = config.get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = config.get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = config.get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

groq_service = GroqService(GROQ_API_KEY)
flux_service = FluxService(CF_ACCOUNT_ID, CF_API_TOKEN)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_key" not in st.session_state:
    st.session_state.selected_model_key = config.DEFAULT_MODEL_KEY
if "attached_image_b64" not in st.session_state:
    st.session_state.attached_image_b64 = None

# ============================================================================
# HEADER UTAMA
# ============================================================================
st.markdown(
    f"""
    <div class="claude-header">
        <div class="claude-brand">
            <span class="material-symbols-outlined" style="font-size: 28px; color: #d97706;">auto_awesome</span>
            <div>
                <h1 class="claude-title">{config.APP_NAME}</h1>
                <p class="claude-subtitle">{config.APP_TAGLINE}</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# SIDEBAR CONTROL
# ============================================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span class="material-symbols-outlined">tune</span>
            <span style="font-weight: 600; font-size: 0.95rem;">Model & Sistem</span>
        </div>
    """, unsafe_allow_html=True)
    
    model_options = {m["key"]: f"{m['name']}" for m in config.MODEL_CATALOG}
    st.session_state.selected_model_key = st.selectbox(
        "Pilih Model:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0,
        label_visibility="collapsed"
    )
    
    curr_model = config.MODEL_BY_KEY.get(st.session_state.selected_model_key, config.MODEL_CATALOG[0])
    st.caption(f"_{curr_model['desc']}_")

    st.markdown("---")
    
    if st.button("Bersihkan Percakapan", use_container_width=True):
        st.session_state.messages = []
        st.session_state.attached_image_b64 = None
        st.rerun()

# ============================================================================
# AREA UTAMA CHAT (CLAUDE STYLE)
# ============================================================================

# 1. Tampilkan Riwayat Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_b64" in msg and msg["image_b64"]:
            st.image(base64.b64decode(msg["image_b64"]), width=220)

# 2. Area Input Chat + Tombol Gambar Di Bawah Input
user_input = st.chat_input("Tulis pesan untuk Yuki...")

# Expander Tombol Lampirkan Gambar / Mode Gambar (Diletakkan di Bawah Input)
with st.expander("📷 Lampirkan Gambar / Mode Vision", expanded=False):
    uploaded_file = st.file_uploader(
        "Pilih gambar untuk dianalisis oleh AI", 
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        file_bytes = uploaded_file.read()
        st.session_state.attached_image_b64 = base64.b64encode(file_bytes).decode("utf-8")
        col_img, col_info = st.columns([1, 4])
        with col_img:
            st.image(file_bytes, width=100)
        with col_info:
            st.caption("Gambar siap dikirim bersama pesan berikutnya.")
            if st.button("Hapus Gambar"):
                st.session_state.attached_image_b64 = None
                st.rerun()

# 3. Logika Eksekusi Pesan
if user_input:
    # Simpan pesan user
    msg_data = {"role": "user", "content": user_input}
    if st.session_state.attached_image_b64:
        msg_data["image_b64"] = st.session_state.attached_image_b64
    
    st.session_state.messages.append(msg_data)
    
    # Rerun untuk merender tampilan pesan terbaru
    st.rerun()
