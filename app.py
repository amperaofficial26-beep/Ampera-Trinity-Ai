#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Main Application Orchestrator
=================================================
File utama penggerak aplikasi Streamlit yang mengintegrasikan
layanan API (Groq, Cloudflare Flux) dan Komponen UI.

Jalankan dengan:
    streamlit run app.py
"""

import streamlit as st
from config import (
    APP_NAME,
    APP_TAGLINE,
    LOGO_B64,
    MODEL_CATALOG,
    MODEL_BY_KEY,
    DEFAULT_MODEL_KEY,
    DEFAULT_SETTINGS,
    get_secret,
)
from services.groq_service import GroqService
from services.flux_service import FluxService
from components.chat_ui import render_chat_tab
from components.gallery_ui import render_gallery_tab
from components.metrics_ui import render_metrics_tab

# ============================================================================
# KONFIGURASI HALAMAN UTAMA STREAMLIT
# ============================================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon=f"data:image/png;base64,{LOGO_B64}",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# INITIALIZE SERVICES & KREDENSIAL
# ============================================================================
GROQ_API_KEY = get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

groq_service = GroqService(GROQ_API_KEY)
flux_service = FluxService(CF_ACCOUNT_ID, CF_API_TOKEN)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_key" not in st.session_state:
    st.session_state.selected_model_key = DEFAULT_MODEL_KEY
if "settings" not in st.session_state:
    st.session_state.settings = DEFAULT_SETTINGS.copy()
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# ============================================================================
# HEADER BRANDING
# ============================================================================
st.markdown(
    f"""
    <div style="text-align: center; padding: 10px 0;">
        <img src="data:image/png;base64,{LOGO_B64}" width="65" height="65">
        <h1 style="margin: 5px 0 0 0; font-size: 2.3rem;">{APP_NAME}</h1>
        <p style="color: #666; font-size: 0.95rem;">{APP_TAGLINE}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# SIDEBAR CONTROL & CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown("### 🤖 Otak AI (Yuki)")
    model_options = {m["key"]: f"{m['name']} ({m['desc']})" for m in MODEL_CATALOG}
    selected_key = st.selectbox(
        "Pilih Model Utama:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    st.session_state.selected_model_key = selected_key
    
    curr_model = MODEL_BY_KEY.get(selected_key, MODEL_CATALOG[0])
    st.info(f"**Model Aktif:**\n`{curr_model['id']}`\n\n_{curr_model['desc']}_")

    st.markdown("---")
    st.markdown("### 🔑 Status API Key")
    st.write(f"• **Groq AI:** {'✅ Aktif' if GROQ_API_KEY else '❌ Belum Set'}")
    st.write(f"• **Cloudflare Flux:** {'✅ Aktif' if flux_service.is_ready() else '❌ Belum Set'}")
    
    st.markdown("---")
    if st.button("🗑️ Bersihkan Sesi Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"© Ampera Official — {APP_NAME}")

# ============================================================================
# NAVIGATION TABS UTAMA
# ============================================================================
tab_chat, tab_gallery, tab_metrics = st.tabs([
    "💬 Chat AI & Vision", 
    "🎨 Generator Foto (Flux)", 
    "📊 System & Export"
])

with tab_chat:
    render_chat_tab(groq_service)

with tab_gallery:
    render_gallery_tab(flux_service)

with tab_metrics:
    render_metrics_tab(groq_service, flux_service)
