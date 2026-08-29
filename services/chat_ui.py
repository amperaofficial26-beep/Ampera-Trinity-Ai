#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — Chat UI Component
=====================================
Modul UI untuk obrolan interaktif, uploader analisis gambar (Vision),
serta shortcut prompt khusus (seperti Watermark Generator).
"""

import base64
import time
import streamlit as st
from services.groq_service import GroqService


def render_chat_tab(groq_service: GroqService):
    st.markdown("### 💬 Obrolan Interaktif dengan Yuki")
    
    # Vision Image Uploader (Analisis Gambar)
    with st.expander("📷 Upload Gambar untuk Dianalisis Yuki (Vision AI)", expanded=False):
        uploaded_file = st.file_uploader("Pilih gambar (PNG/JPG):", type=["png", "jpg", "jpeg"])
        image_b64 = None
        if uploaded_file:
            bytes_data = uploaded_file.read()
            image_b64 = base64.b64encode(bytes_data).decode("utf-8")
            st.image(bytes_data, caption="Gambar Siap Dianalisis", width=250)

    # Display History Chat
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.write(content)

    # Chat Input
    if prompt := st.chat_input("Tanyakan sesuatu atau jelaskan gambar..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                selected_key = st.session_state.get("selected_model_key", "gpt_oss_20b")
                stream, model_used, start_time = groq_service.stream_chat_response(
                    st.session_state.messages,
                    selected_key,
                    image_b64=image_b64
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                latency = round(time.time() - start_time, 2)
                message_placeholder.markdown(full_response)
                
                st.caption(f"🤖 Model: `{model_used}` | ⏱️ Waktu respon: {latency}s")
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Gagal memproses pesan: {e}")
