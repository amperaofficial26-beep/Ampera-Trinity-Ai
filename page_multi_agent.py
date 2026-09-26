# -*- coding: utf-8 -*-
"""Room chat premium Multi Trinity Agent."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from logo import LOGO_B64
from multi_agent import run_multi_agent
from state import mode_thread, next_msg_id
from ui_helpers import _page_footer, render_message


WIB = ZoneInfo("Asia/Jakarta")

# ============================================================
# PENGATURAN POSISI MULTI AI — UBAH ANGKA DI BLOK INI SAJA
# ============================================================

# Header: logo, judul, dan subtitle.
MULTI_HEADER_X = -120
MULTI_HEADER_Y = 0

# Kartu fitur: empat kartu Analisis, Kritik, Sintesis, dan Hasil.
MULTI_CARDS_X = -120
MULTI_CARDS_Y = 0

# Kolom chat/input di bagian bawah.
MULTI_CHAT_X = 40
MULTI_CHAT_Y = 0

# Ukuran kartu dan kolom chat.
MULTI_CARDS_WIDTH = 1040
MULTI_CHAT_WIDTH = 760
MULTI_INPUT_WIDTH = 760
# ============================================================

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
/* ================================================================
   TRINITY AI ASSEMBLY
   ================================================================ */
.trinity-assembly {
  position: relative;

  width: min(360px, 100%);
  height: 104px;

  /*
   * Nilai 0 pada kiri-kanan membuat loader rata kiri.
   */
  margin:
    14px
    0;
    
  overflow: hidden;

  border:
    1px solid
    color-mix(
      in srgb,
      var(--tr-accent) 28%,
      var(--tr-border)
    );

  border-radius: 17px;

  background:
    color-mix(
      in srgb,
      var(--tr-surface) 94%,
      white 6%
    );

  box-shadow:
    0 9px 25px
    rgba(0, 0, 0, .08);
}


/* Trinity Core di sebelah kiri. */
/* ================================================================
   TRINITY CORE
   ================================================================ */
.assembly-core {
  position: absolute;

  z-index: 4;

  left: 10px;
  top: 10px;

  width: 88px;

  text-align: center;
}


/*
 * Logo diperbesar menjadi 58px.
 * scale(1.22) membantu memperbesar isi gambar yang masih
 * memiliki sedikit area transparan.
 */
.assembly-core img {
  display: block;

  width: 58px;
  height: 58px;

  object-fit: contain;

  margin:
    0
    auto;

  transform:
    scale(1.22);

  transform-origin:
    center;

  animation:
    corePulse
    2.142857s
    ease-in-out
    infinite;

  filter:
    drop-shadow(
      0
      0
      7px
      var(--tr-accent)
    );
}


.assembly-core b {
  display: block;

  color:
    var(--tr-text);

  font-size: 10px;

  letter-spacing: .12em;
}


.assembly-core small {
  display: block;

  color:
    var(--tr-text2);

  font-size: 8px;

  letter-spacing: .15em;
}

/* Kartu satu model aktif. */
.assembly-model {
  --step: 5.0s;

  position: absolute;

  z-index: 3;

  left: 116px;
  right: 12px;
  top: 15px;

  height: 61px;

  box-sizing: border-box;

  padding:
    9px
    10px;

  border-radius: 12px;

  border:
    1px solid
    var(--tr-border);

  background:
    var(--tr-bg);

  opacity: 0;

  animation:
    modelAssemble
    var(--step)
    ease-in-out
    both;

  animation-delay:
    calc(
      var(--i) * var(--step)
    );
}


.assembly-model strong {
  display: block;

  color:
    var(--tr-text);

  font-size: 11px;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


.assembly-state {
  position: relative;

  margin-top: 7px;

  color:
    var(--tr-text2);

  font-size: 9px;
}


/* Tulisan Thinking. */
.assembly-thinking {
  animation:
    thinkingSwap
    var(--step)
    both;

  animation-delay:
    calc(
      var(--i) * var(--step)
    );
}

.assembly-done {
  position: absolute;

  left: 0;

  opacity: 0;

  color: #9b741f;

  animation:
    doneSwap
    var(--step)
    both;

  animation-delay:
    calc(
      var(--i) * var(--step)
    );
}


/* Titik Thinking yang fade, bukan berputar. */
.assembly-dots i {
  display: inline-block;

  width: 3px;
  height: 3px;

  margin-left: 3px;

  border-radius: 50%;

  background:
    var(--tr-accent);

  animation:
    dotFade
    .65s
    infinite
    alternate;
}


.assembly-dots i:nth-child(2) {
  animation-delay: .18s;
}


.assembly-dots i:nth-child(3) {
  animation-delay: .36s;
}


.assembly-count {
  position: absolute;

  right: 9px;
  bottom: 5px;

  color:
    var(--tr-text2);

  font-size: 8px;
}

.assembly-wait {
  position: absolute;

  left: 112px;
  right: 12px;
  top: 39px;

  text-align: center;

  color:
    var(--tr-text2);

  font-size: 10px;

  opacity: 0;

  animation:
    assemblyWait
    .5s
    30s
    forwards;
}


@keyframes assemblyWait {
  to {
    opacity: 1;
  }
}

/* Kartu muncul, selesai, lalu masuk ke Trinity Core. */
@keyframes modelAssemble {
  0% {
    opacity: 0;

    transform:
      translateX(14px);
  }

  12%,
  58% {
    opacity: 1;

    transform:
      translateX(0);
  }

  72% {
    opacity: 1;

    transform:
      translateX(-4px);
  }

  92% {
    opacity: 0;

    transform:
      translateX(-112px)
      scale(.25);
  }

  100% {
    opacity: 0;
  }
}


/* Thinking hilang ketika proses selesai. */
@keyframes thinkingSwap {
  0%,
  52% {
    opacity: 1;
  }

  62%,
  100% {
    opacity: 0;
  }
}


/* Done muncul sebelum kartu masuk Core. */
@keyframes doneSwap {
  0%,
  52% {
    opacity: 0;
  }

  62%,
  82% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
}


/* Titik fade naik-turun sedikit. */
@keyframes dotFade {
  from {
    opacity: .18;

    transform:
      translateY(1px);
  }

  to {
    opacity: 1;

    transform:
      translateY(-1px);
  }
}


/* Core memberikan pulse saat model masuk. */
@keyframes corePulse {
  0%,
  65% {
    transform:
      scale(1.22);
  }

  86% {
    transform:
      scale(1.38);

    filter:
      drop-shadow(
        0
        0
        14px
        var(--tr-accent)
      );
  }

  100% {
    transform:
      scale(1.22);
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
/* ================================================================
   POSISI KONTEN MULTI AI
   ================================================================ */

.stApp:has(.tr-multi-ai-layout)
.multi-agent-content {
  width: min(
    var(--multi-chat-width),
    calc(100vw - 264px)
  ) !important;

  max-width: var(--multi-chat-width) !important;

  margin-left: auto !important;
  margin-right: auto !important;

  transform:
    translate(
      var(--multi-chat-x),
      var(--multi-chat-y)
    ) !important;
}
</style>
"""


def _now() -> str:
    return datetime.now(WIB).strftime("%H:%M")


def _assembly_html() -> str:
    """Loader 14 model: thinking, done, lalu menyatu ke Trinity Core."""
    nama_model = [
        "GPT-OSS 20B",
        "Compound Mini",
        "Qwen 3.8",
        "Plugsky Micro",
        "Plugsky Lite",
        "Aion RP",
        "Aion 2.0",
        "Aion 3 Mini",
        "Aion 3.0",
        "GPT-OSS 120B",
        "Compound",
        "DeepSeek V4",
        "Trinity Infinity",
        "GPT-5 Mini",
    ]

    logo = (
        f"data:image/png;base64,{LOGO_B64}"
    )

    kartu = []

    for index, nama in enumerate(nama_model):
        kartu.append(
            f'<div class="assembly-model" '
            f'style="--i:{index}">'

            f'<strong>'
            f'{index + 1:02d} · {nama}'
            f'</strong>'

            '<div class="assembly-state">'

            '<span class="assembly-thinking">'
            'Thinking'

            '<span class="assembly-dots">'
            '<i></i>'
            '<i></i>'
            '<i></i>'
            '</span>'

            '</span>'

            '<span class="assembly-done">'
            '✓ Done'
            '</span>'

            '</div>'
            '</div>'
        )

    return (
        '<div class="trinity-assembly">'
    
        '<div class="assembly-core">'
    
        f'<img src="{logo}" alt="Trinity">'
        '<b>TRINITY</b>'
        '<small>CORE</small>'
    
        '</div>'
    
        + "".join(kartu)
    
        + '<div class="assembly-wait">'
        'Menyatukan jawaban panel…'
        '</div>'
    
        + '<div class="assembly-count">'
        '14 AI · 30 DETIK'
        '</div>'
    
        '</div>'
    )


def page_multi_agent() -> None:
    """Render room khusus Multi Trinity Agent."""
    # Marker layout Multi AI.
    # Menggunakan layout utama Trinity tanpa panel kanan.
    st.markdown(
        '<div class="tr-chat-layout tr-multi-ai-layout"></div>',
        unsafe_allow_html=True,
    )
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
    # ============================================================
    # VARIABEL POSISI MULTI AI
    # CSS utama berada di styles.py.
    # Di sini hanya dikirim nilai konfigurasinya.
    # ============================================================
    
    st.markdown(
        f"""
        <style>
        /* Posisi header dan kartu diterapkan langsung pada markup HTML di bawah. */
        .stApp:has(.tr-multi-ai-layout) .multi-feature-grid {{
            width: min({MULTI_CARDS_WIDTH}px, calc(100vw - 48px)) !important;
        }}
        .stApp:has(.tr-multi-ai-layout)
        [data-testid="stBottomBlockContainer"]:has(.st-key-multi_position_input) {{
            width: min({MULTI_CHAT_WIDTH}px, calc(100vw - 48px)) !important;
            max-width: min({MULTI_CHAT_WIDTH}px, calc(100vw - 48px)) !important;
            transform: translate(
                {MULTI_CHAT_X}px,
                {MULTI_CHAT_Y}px
            ) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
   
    # HTML dirapatkan menjadi rangkaian string.
    # Ini mencegah Markdown menganggap tag <p> sebagai blok kode.
    logo = f"data:image/png;base64,{LOGO_B64}"
    hero = (
        f'<div class="multi-landing-hero" style="position:relative;left:{MULTI_HEADER_X}px;top:{MULTI_HEADER_Y}px;">'
        f'<div class="multi-landing-logo"><img src="{logo}" alt="Trinity"></div>'
        '<h1>Multi Trinity Agent</h1>'
        '<p>Seluruh model Trinity menganalisis, mengkritik, dan menyatukan<br>'
        'jawaban profesional dalam satu ruang kolaborasi.</p>'
        '</div>'
        f'<div class="multi-feature-grid" style="position:relative;left:{MULTI_CARDS_X}px;top:{MULTI_CARDS_Y}px;width:min({MULTI_CARDS_WIDTH}px,calc(100vw - 48px)) !important;">'
        '<div class="multi-feature-card">'
        '<span class="material-symbols-rounded">psychology</span>'
        '<strong>Analisis Mendalam</strong>'
        '<small>Memahami konteks dengan lebih komprehensif.</small>'
        '</div>'
        '<div class="multi-feature-card">'
        '<span class="material-symbols-rounded">shield</span>'
        '<strong>Kritik Konstruktif</strong>'
        '<small>Memberikan perspektif baru yang lebih kuat.</small>'
        '</div>'
        '<div class="multi-feature-card">'
        '<span class="material-symbols-rounded">hub</span>'
        '<strong>Sintesis Cerdas</strong>'
        '<small>Menyatukan jawaban terbaik dari semua model.</small>'
        '</div>'
        '<div class="multi-feature-card">'
        '<span class="material-symbols-rounded">bolt</span>'
        '<strong>Hasil Profesional</strong>'
        '<small>Solusi cepat, akurat, dan siap digunakan.</small>'
        '</div>'
        '</div>'
    )
    if not thread:
        st.markdown(hero, unsafe_allow_html=True,)
        
    with st.container(key="multi_chat_area"):
        for message in thread:
            render_message(message)

    prompt = st.chat_input(
        "Tanyakan sesuatu kepada Multi Trinity Agent…",
        key="multi_position_input",
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

        # Siapkan tempat untuk animasi Trinity AI Assembly.
        loader = st.empty()

        # Tampilkan loader sebelum seluruh model dipanggil.
        loader.markdown(
            _assembly_html(),
            unsafe_allow_html=True,
        )

        try:
            result = run_multi_agent(
                thread
            )

            from interactive_simulation import (
                extract_interactive_html,
                is_interactive_request,
            )
            answer, interactive_html = extract_interactive_html(
                result["answer"],
                allow_raw=is_interactive_request(thread),
            )

            reply = {
                "id": next_msg_id(),
                "role": "assistant",
                "type": "text",
                "content": answer,
                "time": _now(),
                "multi_agent": {
                    "success": result["success"],
                    "total": result["total"],
                },
            }

            if interactive_html:
                reply["interactive_html"] = (
                    interactive_html
                )

            thread.append(reply)

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

        # Jangan menggunakan loader.empty() di sini.
        # Loader akan dibersihkan otomatis oleh proses rerun.
        st.rerun()
      
    _page_footer(
        in_chat=bool(thread)
    )
