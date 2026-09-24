# -*- coding: utf-8 -*-
"""Animasi logo thinking (shimmer/glow) & kotak loading pembuatan gambar ala ChatGPT

Dipecah dari styles.py asli (baris 2227-2447), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ====================================================================
   KOTAK LOADING PEMBUATAN GAMBAR ALA CHATGPT (Perimeter Shimmer Box)
   --------------------------------------------------------------------
   - Kotak kanvas persegi (aspect-ratio 1:1) ala ChatGPT / DALL-E.
   - Efek berkas cahaya / shimmer berputar 360° mengitari tepi samping kotak.
   - Gelombang shimmer halus menyapu di atas permukaan kanvas kotak.
   - Ikon kanvas berdenyut di tengah + status bertahap & mini progress bar.
==================================================================== */

.img-gen-box-wrapper,
.img-progress {
    position: relative !important;
    width: 100% !important;
    max-width: 340px !important;
    aspect-ratio: 1 / 1 !important;
    border-radius: 22px !important;
    padding: 2px !important;            /* tebal pita cahaya di tepi */
    overflow: hidden !important;
    isolation: isolate;                 /* pita cahaya tak bocor ke luar */
    margin: 8px 0 16px !important;
    box-shadow: 0 10px 34px rgba(44, 31, 51, 0.13) !important;
    display: block !important;
    background: #FFFFFF !important;     /* kotak putih ala ChatGPT */
    animation: thinkFadeIn 0.45s ease both !important;
    box-sizing: border-box !important;
}

/* Berkas shimmer cahaya yang berputar 360° mengitari tepi kotak.
   Memakai kotak pembungkus 1:1 yang diputar (bukan @property --angle),
   supaya jalan di semua browser termasuk Safari & Firefox. */
.img-gen-box-wrapper::before,
.img-progress::before {
    content: "";
    position: absolute;
    z-index: 0;
    top: 50%;
    left: 50%;
    width: 150%;
    aspect-ratio: 1 / 1;
    height: auto;
    background: conic-gradient(
        from 0deg,
        rgba(255, 255, 255, 0) 0deg,
        rgba(255, 255, 255, 0) 40deg,
        rgba(110, 84, 130, 0.25) 95deg,
        rgba(74, 53, 89, 0.95) 135deg,
        rgba(200, 178, 220, 0.95) 160deg,
        rgba(110, 84, 130, 0.25) 200deg,
        rgba(255, 255, 255, 0) 260deg,
        rgba(255, 255, 255, 0) 360deg
    );
    transform-origin: center center;
    animation: borderShimmerSpin 2.6s linear infinite;
    will-change: transform;
}

@keyframes borderShimmerSpin {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to   { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Saat selesai: pita cahaya berhenti & memudar */
.img-gen-box-wrapper.is-done::before { animation: none; opacity: 0; }
.img-gen-box-wrapper.is-done .img-gen-canvas-shimmer { animation: none; opacity: 0; }

/* Lapisan dalam kotak kanvas (putih) */
.img-gen-box-inner {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
    background: #FFFFFF;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* Gelombang shimmer menyapu diagonal di permukaan kanvas putih */
.img-gen-canvas-shimmer {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        115deg,
        rgba(240, 234, 246, 0) 30%,
        rgba(226, 216, 238, 0.75) 48%,
        rgba(240, 234, 246, 0) 66%
    );
    background-size: 260% 260%;
    animation: canvasShimmerWave 2.4s ease-in-out infinite;
    pointer-events: none;
    z-index: 2;
}

@keyframes canvasShimmerWave {
    0%   { background-position: 170% 170%; }
    100% { background-position: -70% -70%; }
}

/* Ikon tengah dengan breathing pulse */
.img-gen-center-icon {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: #2C1F33;
    color: #FFFFFF;
    display: grid;
    place-items: center;
    box-shadow: 0 6px 20px rgba(44, 31, 51, 0.20);
    animation: iconPulseBreath 2.2s ease-in-out infinite;
    margin-bottom: 14px;
    position: relative;
    z-index: 3;
}

@keyframes iconPulseBreath {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 6px 20px rgba(44, 31, 51, 0.20);
    }
    50% {
        transform: scale(1.06);
        box-shadow: 0 10px 28px rgba(74, 53, 89, 0.34);
    }
}

.img-gen-icon-svg {
    width: 27px;
    height: 27px;
    stroke: #FFFFFF;
}

/* Pembungkus status teks & progress */
.img-gen-status-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    z-index: 3;
    text-align: center;
    padding: 0 24px;
}

/* Teks status berganti sendiri lewat CSS (tanpa rerun server) */
.img-gen-phrases {
    position: relative;
    height: 1.4em;
    min-width: 210px;
}
.img-gen-phrase {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    white-space: nowrap;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    background: linear-gradient(
        90deg,
        #8C82A0 0%, #8C82A0 30%,
        #2C1F33 50%,
        #8C82A0 70%, #8C82A0 100%
    );
    background-size: 220% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 0;
    animation: shimmerSweep 2.6s linear infinite,
               imgPhraseCycle 20s ease-in-out infinite;
}
.img-gen-phrase:nth-child(1) { animation-delay: 0s, 0s; }
.img-gen-phrase:nth-child(2) { animation-delay: 0s, 5s; }
.img-gen-phrase:nth-child(3) { animation-delay: 0s, 10s; }
.img-gen-phrase:nth-child(4) { animation-delay: 0s, 15s; }
/* kalau cuma satu frasa (mis. "Selesai"), tampilkan terus */
.img-gen-phrase:only-child {
    opacity: 1;
    animation: shimmerSweep 2.6s linear infinite;
}
@keyframes imgPhraseCycle {
    0%   { opacity: 0; filter: blur(4px); }
    3%   { opacity: 1; filter: blur(0); }
    22%  { opacity: 1; filter: blur(0); }
    25%  { opacity: 0; filter: blur(4px); }
    100% { opacity: 0; }
}

.img-gen-mini-bar {
    position: relative;
    width: 140px;
    height: 4px;
    border-radius: 99px;
    background: rgba(44, 31, 51, 0.10);
    overflow: hidden;
}

/* Bar indeterminate: meluncur terus selama gambar dibuat */
.img-gen-mini-fill {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 42%;
    background: linear-gradient(90deg, rgba(44,31,51,0), #2C1F33, #6E5482, rgba(110,84,130,0));
    border-radius: 99px;
    animation: imgBarSlide 1.5s ease-in-out infinite;
}
@keyframes imgBarSlide {
    0%   { transform: translateX(-110%); }
    100% { transform: translateX(340%); }
}
.img-gen-box-wrapper.is-done .img-gen-mini-fill {
    animation: none;
    width: 100%;
    transform: none;
    background: #2C1F33;
}
"""
