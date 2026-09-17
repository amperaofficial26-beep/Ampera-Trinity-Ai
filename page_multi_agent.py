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


_AGENT_CSS = """
<style>
.agent-hero {
  display: flex;
  align-items: center;
  gap: 16px;

  margin:
    10px
    0
    24px;
}

.agent-hero-icon {
  width: 52px;
  height: 52px;

  display: grid;
  place-items: center;

  flex:
    0
    0
    52px;

  border-radius: 16px;

  color: #2d2115;

  background:
    linear-gradient(
      145deg,
      #f3d47d,
      #bd8125
    );

  font-size: 25px;

  box-shadow:
    0 8px 22px rgba(111, 74, 23, .20),
    0 0 20px rgba(218, 166, 55, .24);
}

.agent-hero h1 {
  margin: 0;

  color: var(--tr-text);

  font-size: 2rem;
  line-height: 1.15;
}

.agent-hero p {
  margin:
    6px
    0
    0;

  color: var(--tr-text2);

  font-size: .96rem;
  line-height: 1.55;
}

.agent-pro-note {
  padding:
    12px
    15px;

  margin:
    0
    0
    22px;

  border-radius: 14px;

  background:
    color-mix(
      in srgb,
      var(--tr-surface) 88%,
      white 12%
    );

  border:
    1px solid
    var(--tr-border);

  color: var(--tr-text2);

  font-size: .88rem;
}


/* ================================================================
   LOADING MULTI AGENT
   ================================================================ */
.agent-thinking {
  display: flex;
  align-items: center;

  gap: 14px;

  padding:
    17px
    18px;

  margin:
    16px
    0;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--tr-accent) 35%,
      var(--tr-border)
    );

  border-radius: 16px;

  background:
    var(--tr-surface);

  box-shadow:
    0 8px 24px
    rgba(0, 0, 0, .07);
}

.agent-orbit {
  position: relative;

  width: 42px;
  height: 42px;

  flex:
    0
    0
    42px;

  animation:
    agentSpin
    2.4s
    linear
    infinite;
}

.agent-orbit::before,
.agent-orbit::after {
  content: "✦";

  position: absolute;

  color:
    var(--tr-accent);
}

.agent-orbit::before {
  left: 8px;
  top: 3px;

  font-size: 27px;

  animation:
    agentPulse
    1.2s
    ease-in-out
    infinite;
}

.agent-orbit::after {
  right: 0;
  bottom: 2px;

  font-size: 11px;
}

.agent-thinking b {
  display: block;

  color: var(--tr-text);

  font-size: .95rem;
}

.agent-thinking span {
  color: var(--tr-text2);

  font-size: .82rem;
}

@keyframes agentSpin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes agentPulse {
  50% {
    filter:
      drop-shadow(
        0
        0
        8px
        var(--tr-accent)
      );

    transform:
      scale(1.15);
  }
}

@media (max-width: 600px) {
  .agent-hero h1 {
    font-size: 1.55rem;
  }

  .agent-hero-icon {
    width: 46px;
    height: 46px;

    flex:
      0
      0
      46px;
  }
}
</style>
"""


def _now() -> str:
    """Waktu WIB untuk metadata pesan."""
    return datetime.now(WIB).strftime("%H:%M")


def page_multi_agent() -> None:
    """Render room khusus Multi Trinity Agent."""

    # Pengaman server-side. Halaman tetap tertutup jika pengguna
    # mencoba mengubah session state secara manual.
    from chat_handlers import _boleh_premium

    if not _boleh_premium():
        st.warning(
            "Multi Trinity Agent hanya tersedia "
            "untuk pengguna Trinity Pro."
        )

        if st.button(
            "Kembali ke Chat",
            type="primary",
        ):
            st.session_state.page = "chat"
            st.rerun()

        return

    thread = mode_thread("multi_agent")

    st.markdown(
        _AGENT_CSS,
        unsafe_allow_html=True,
    )

    # HTML dirapatkan menjadi rangkaian string.
    # Ini mencegah Markdown menganggap tag <p> sebagai blok kode.
    hero = (
        '<div class="agent-hero">'
        '<div class="agent-hero-icon">✦</div>'
        '<div>'
        '<h1>Multi Trinity Agent</h1>'
        '<p>'
        'Seluruh model Trinity menganalisis, mengkritik, '
        'dan menyatukan jawaban profesional dalam satu room.'
        '</p>'
        '</div>'
        '</div>'
    )

    st.markdown(
        hero,
        unsafe_allow_html=True,
    )

    if not thread:
        st.markdown(
            '<div class="agent-pro-note">'
            '✦ Khusus Trinity Pro · Model yang tersedia '
            'bekerja sebagai satu panel; model yang gagal '
            'tidak menghentikan proses.'
            '</div>',
            unsafe_allow_html=True,
        )

    for message in thread:
        render_message(message)

    prompt = st.chat_input(
        "Tanyakan sesuatu kepada Multi Trinity Agent…"
    )

    if prompt and prompt.strip():
        thread.append(
            {
                "id": next_msg_id(),
                "role": "user",
                "type": "text",
                "content": prompt.strip(),
                "time": _now(),
            }
        )

        loader = st.empty()

        loader.markdown(
            '<div class="agent-thinking">'
            '<div class="agent-orbit"></div>'
            '<div>'
            '<b>Panel Trinity sedang berpikir…</b>'
            '<span>'
            'Menelaah konteks, menguji jawaban, '
            'dan menyusun sintesis.'
            '</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        try:
            result = run_multi_agent(thread)

            thread.append(
                {
                    "id": next_msg_id(),
                    "role": "assistant",
                    "type": "text",
                    "content": result["answer"],
                    "time": _now(),
                    "multi_agent": {
                        "success": result["success"],
                        "total": result["total"],
                    },
                }
            )

            st.toast(
                f"{result['success']} dari "
                f"{result['total']} model berpartisipasi."
            )

        except Exception as exc:
            thread.append(
                {
                    "id": next_msg_id(),
                    "role": "assistant",
                    "type": "text",
                    "content": (
                        "Multi Trinity Agent gagal memproses "
                        f"permintaan: {exc}"
                    ),
                    "time": _now(),
                }
            )

        finally:
            loader.empty()

        st.rerun()

    _page_footer(
        in_chat=bool(thread)
    )
