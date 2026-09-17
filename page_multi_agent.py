# -*- coding: utf-8 -*-
"""Room chat premium Multi Trinity Agent."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from multi_agent import run_multi_agent
from state import mode_thread, next_msg_id
from ui_helpers import _page_footer, render_message


WIB = ZoneInfo("Asia/Jakarta")


def _now_wib() -> str:
    return datetime.now(WIB).strftime("%H:%M")


def page_multi_agent() -> None:
    """Render room khusus Multi Trinity Agent."""
    thread = mode_thread("multi_agent")

    st.markdown(
        """
        <div class="page-head">
          <div class="page-head-icon">✦</div>

          <div>
            <h2 class="page-title">
              Multi Trinity Agent
            </h2>

            <p class="page-sub">
              Panel seluruh model Trinity menganalisis,
              mengkritik, dan menyatukan jawaban profesional.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not thread:
        st.info(
            "Khusus Trinity Pro · Semua model yang tersedia "
            "bekerja sebagai satu panel."
        )

    for message in thread:
        render_message(message)

    prompt = st.chat_input(
        "Tanyakan sesuatu kepada Multi Trinity Agent…"
    )

    if prompt and prompt.strip():
        now = _now_wib()

        thread.append(
            {
                "id": next_msg_id(),
                "role": "user",
                "type": "text",
                "content": prompt.strip(),
                "time": now,
            }
        )

        with st.status(
            "Panel Trinity sedang menganalisis…",
            expanded=True,
        ) as status:
            st.write(
                "Mengirim pertanyaan ke seluruh model "
                "yang tersedia."
            )

            try:
                result = run_multi_agent(thread)

                st.write(
                    f"{result['success']} dari "
                    f"{result['total']} model berhasil "
                    "berpartisipasi."
                )

                status.update(
                    label="Sintesis profesional selesai",
                    state="complete",
                    expanded=False,
                )

                thread.append(
                    {
                        "id": next_msg_id(),
                        "role": "assistant",
                        "type": "text",
                        "content": result["answer"],
                        "time": _now_wib(),
                        "multi_agent": {
                            "success": result["success"],
                            "total": result["total"],
                        },
                    }
                )

            except Exception as exc:
                status.update(
                    label="Multi Agent belum berhasil",
                    state="error",
                )

                thread.append(
                    {
                        "id": next_msg_id(),
                        "role": "assistant",
                        "type": "text",
                        "content": (
                            "Multi Trinity Agent gagal "
                            f"memproses permintaan: {exc}"
                        ),
                        "time": _now_wib(),
                    }
                )

        st.rerun()

    _page_footer(
        in_chat=bool(thread)
    )
