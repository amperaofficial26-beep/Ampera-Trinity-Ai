#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ampera Trinity AI — System Metrics & Analytics UI
=================================================
Modul UI untuk memantau performa aplikasi, status kredensial,
dan ekspor data percakapan.
"""

import streamlit as st
from services.storage_service import StorageService


def render_metrics_tab(groq_service, flux_service):
    st.markdown("### 📊 Dashboard Status System & Export")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Total Pesan Chat", len(st.session_state.messages))
    with col_m2:
        st.metric("Total Gambar Dibuat", len(st.session_state.generated_images))
    with col_m3:
        st.metric("Status Server API", "Online ⚡")

    st.divider()
    st.markdown("### 📥 Ekspor Riwayat Percakapan")
    
    if st.session_state.messages:
        json_data = StorageService.export_to_json(st.session_state.messages)
        txt_data = StorageService.export_to_txt(st.session_state.messages)
        md_data = StorageService.export_to_markdown(st.session_state.messages)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "💾 Ekspor Format JSON",
                data=json_data,
                file_name="ampera_chat_history.json",
                mime="application/json"
            )
        with c2:
            st.download_button(
                "📄 Ekspor Format TXT",
                data=txt_data,
                file_name="ampera_chat_history.txt",
                mime="text/plain"
            )
        with c3:
            st.download_button(
                "📝 Ekspor Format Markdown",
                data=md_data,
                file_name="ampera_chat_history.md",
                mime="text/markdown"
            )
    else:
        st.info("Belum ada riwayat percakapan untuk diekspor.")
