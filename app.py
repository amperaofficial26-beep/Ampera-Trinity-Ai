#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Main Application
====================================
Jalankan dengan:
    streamlit run app.py
"""

import os
import sys
import streamlit as st

# Ensure root directory is in system path for clean imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Configuration
import config

# Import Services
from services.groq_service import GroqService
from services.flux_service import FluxService

# Import UI Components
from components.chat_ui import render_chat_tab
from components.gallery_ui import render_gallery_tab
from components.metrics_ui import render_metrics_tab

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
# MATERIAL ICONS CDN & CLEAN LAYOUT STYLING
# ============================================================================
MATERIAL_STYLE_CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

<style>
    /* Google Material Symbols Class */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 22px;
        display: inline-block;
        line-height: 1;
        text-transform: none;
        letter-spacing: normal;
        word-wrap: normal;
        white-space: nowrap;
        direction: ltr;
        vertical-align: middle;
    }

    /* Clean Header Styling */
    .main-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0 15px 0;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 20px;
    }
    
    .main-header-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.2;
    }

    .main-header-sub {
        font-size: 0.88rem;
        color: #666666;
        margin: 2px 0 0 0;
    }

    /* Clean Tab & Card Overrides */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

st.markdown(MATERIAL_STYLE_CSS, unsafe_allow_html=True)

# ============================================================================
# SERVICE INITIALIZATION
# ============================================================================
GROQ_API_KEY = config.get_secret("GROQ_API_KEY", "GROQ_KEY")
CF_ACCOUNT_ID = config.get_secret("CF_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID")
CF_API_TOKEN = config.get_secret("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")

groq_service = GroqService(GROQ_API_KEY)
flux_service = FluxService(CF_ACCOUNT_ID, CF_API_TOKEN)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model_key" not in st.session_state:
    st.session_state.selected_model_key = config.DEFAULT_MODEL_KEY
if "settings" not in st.session_state:
    st.session_state.settings = config.DEFAULT_SETTINGS.copy()
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

# ============================================================================
# MAIN HEADER (Material Icons Only)
# ============================================================================
st.markdown(
    f"""
    <div class="main-header">
        <span class="material-symbols-outlined" style="font-size: 34px;">auto_awesome</span>
        <div>
            <h1 class="main-header-title">{config.APP_NAME}</h1>
            <p class="main-header-sub">{config.APP_TAGLINE}</p>
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
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="material-symbols-outlined">smart_toy</span>
            <strong style="font-size: 1rem;">Model AI</strong>
        </div>
    """, unsafe_allow_html=True)
    
    model_options = {m["key"]: f"{m['name']}" for m in config.MODEL_CATALOG}
    selected_key = st.selectbox(
        "Pilih Model Otak:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.selected_model_key = selected_key
    
    curr_model = config.MODEL_BY_KEY.get(selected_key, config.MODEL_CATALOG[0])
    st.caption(f"ID: `{curr_model['id']}`")
    st.caption(f"_{curr_model['desc']}_")

    st.markdown("---")
    
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="material-symbols-outlined">key</span>
            <strong style="font-size: 1rem;">Status Server API</strong>
        </div>
    """, unsafe_allow_html=True)
    
    groq_status = "Aktif" if GROQ_API_KEY else "Tidak Aktif"
    flux_status = "Aktif" if flux_service.is_ready() else "Tidak Aktif"
    
    st.write(f"• **Groq AI:** {groq_status}")
    st.write(f"• **Cloudflare Flux:** {flux_status}")
    
    st.markdown("---")
    
    if st.button("Bersihkan Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"© Ampera Official — {config.APP_NAME}")

# ============================================================================
# MAIN NAVIGATION TABS
# ============================================================================
tab_chat, tab_gallery, tab_metrics = st.tabs([
    "Chat AI & Vision", 
    "Generator Foto", 
    "System & Export"
])

with tab_chat:
    render_chat_tab(groq_service)

with tab_gallery:
    render_gallery_tab(flux_service)

with tab_metrics:
    render_metrics_tab(groq_service, flux_service)
