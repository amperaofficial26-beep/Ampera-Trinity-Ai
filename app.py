#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Main Application Orchestrator (Claude Style UI)
===================================================================
"""

import os
import sys
import streamlit as st

# Fix Module Import Path untuk Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config

APP_NAME = config.APP_NAME
APP_TAGLINE = config.APP_TAGLINE
LOGO_B64 = config.LOGO_B64
MODEL_CATALOG = config.MODEL_CATALOG
MODEL_BY_KEY = config.MODEL_BY_KEY
DEFAULT_MODEL_KEY = config.DEFAULT_MODEL_KEY
DEFAULT_SETTINGS = config.DEFAULT_SETTINGS
get_secret = config.get_secret

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
# CLAUDE AI MINIMALIST CUSTOM CSS
# ============================================================================
CLAUDE_STYLE_CSS = """
<style>
    /* Global Background & Typography khas Claude (Warm Beige / Warm Neutral) */
    .stApp {
        background-color: #faf8f5 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #2c2b29 !important;
    }

    /* Sidebar Clean styling */
    section[data-testid="stSidebar"] {
        background-color: #f3f0ea !important;
        border-right: 1px solid #e6e2d8 !important;
    }

    /* Header Title styling */
    .claude-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .claude-title {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1e1e1e;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .claude-sub {
        font-size: 0.95rem;
        color: #6e6b63;
        margin-top: 5px;
        font-weight: 400;
    }

    /* Custom Styling untuk Chat Messages */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }
    
    /* User Chat Bubble */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f0ebe1 !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
    }
    
    /* Assistant Chat Bubble */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff !important;
        border: 1px solid #e8e4dc !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }

    /* Custom Input Textbox seperti Claude */
    .stChatInputContainer textarea {
        background-color: #ffffff !important;
        border: 1px solid #dcd7cd !important;
        border-radius: 20px !important;
        color: #2c2b29 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }
    .stChatInputContainer textarea:focus {
        border-color: #da7756 !important;
        box-shadow: 0 0 0 2px rgba(218, 119, 86, 0.2) !important;
    }

    /* Button Styling ala Claude (Terracotta Accent) */
    .stButton > button {
        background-color: #da7756 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #c46445 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(218, 119, 86, 0.25) !important;
    }

    /* Tabs Minimalis khas Anthropic */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #e6e2d8;
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre;
        border-radius: 8px;
        color: #6e6b63;
        font-weight: 500;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e8e2d5 !important;
        color: #1e1e1e !important;
        font-weight: 600 !important;
    }
    
    /* Hide Streamlit Branding Element */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(CLAUDE_STYLE_CSS, unsafe_allow_html=True)

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
# HEADER BRANDING (CLAUDE STYLE)
# ============================================================================
st.markdown(
    f"""
    <div class="claude-header">
        <img src="data:image/png;base64,{LOGO_B64}" width="55" height="55" style="margin-bottom: 5px;">
        <h1 class="claude-title">{APP_NAME}</h1>
        <p class="claude-sub">{APP_TAGLINE}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# SIDEBAR CONTROL
# ============================================================================
with st.sidebar:
    st.markdown("### 🤖 Model AI")
    model_options = {m["key"]: f"{m['name']} ({m['desc']})" for m in MODEL_CATALOG}
    selected_key = st.selectbox(
        "Pilih Model Otak:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    st.session_state.selected_model_key = selected_key
    
    curr_model = MODEL_BY_KEY.get(selected_key, MODEL_CATALOG[0])
    st.info(f"**Model Aktif:**\n`{curr_model['id']}`")

    st.markdown("---")
    st.markdown("### 🔑 Status API")
    st.write(f"• **Groq AI:** {'✅ Aktif' if GROQ_API_KEY else '❌ Belum Set'}")
    st.write(f"• **Cloudflare Flux:** {'✅ Aktif' if flux_service.is_ready() else '❌ Belum Set'}")
    
    st.markdown("---")
    if st.button("🗑️ Bersihkan Percakapan", use_container_width=True):
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
