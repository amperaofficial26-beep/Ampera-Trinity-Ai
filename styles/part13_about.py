# -*- coding: utf-8 -*-
"""Halaman "Tentang Kami" (page_tentang.py) — panel hero bermaskot,
kartu logo & produk, nilai/visi, dan kartu kutipan senja."""

CSS = r"""
/* ================================================================
   HALAMAN TENTANG KAMI — kerangka halaman (lebar penuh)
   ================================================================ */
.stApp:has(.about-page-shell) { background: #F5EBDD !important; }
.stApp:has(.about-page-shell) [data-testid="stMain"],
.stApp:has(.about-page-shell) [data-testid="stAppViewContainer"] {
    background: transparent !important;
}
body .stApp:has(.about-page-shell) [data-testid="stMain"],
body .stApp:has(.about-page-shell) [data-testid="stMain"] > div {
    padding: 0 !important;
    width: 100% !important;
    max-width: none !important;
}
body .stApp:has(.about-page-shell) section[data-testid="stSidebar"] {
    display: none !important;
}
body .stApp:has(.about-page-shell) [data-testid="stMainBlockContainer"],
body .stApp:has(.about-page-shell) .stMainBlockContainer {
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 64px 16px 48px !important;
}
body .stApp:has(.about-page-shell)
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    gap: 14px !important;
}
.about-page-shell { display: none !important; }

/* ================================================================
   HERO
   ================================================================ */
.ab-hero {
    position: relative;
    display: flex;
    align-items: stretch;
    gap: 18px;
    overflow: hidden;
    padding: 26px 28px;
    border: 1px solid #EADFCD;
    border-radius: 26px;
    background:
        radial-gradient(120% 150% at 78% 10%,
                        rgba(244, 233, 248, .85) 0%,
                        rgba(255, 253, 249, 0) 60%),
        linear-gradient(135deg, #FFFDF9 0%, #FBF2E6 55%, #F6EDF6 100%);
    box-shadow: 0 18px 44px rgba(76, 58, 43, .10);
}
.ab-hero::after {   /* kilau bintang halus di latar */
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        radial-gradient(3px 3px at 62% 18%, rgba(201, 170, 93, .55), transparent),
        radial-gradient(2px 2px at 70% 52%, rgba(201, 170, 93, .45), transparent),
        radial-gradient(2px 2px at 54% 72%, rgba(154, 128, 173, .40), transparent),
        radial-gradient(2px 2px at 88% 30%, rgba(201, 170, 93, .35), transparent);
}
.ab-hero-copy { flex: 1 1 46%; min-width: 0; z-index: 1; }
.ab-badge {
    display: inline-block;
    margin-bottom: 12px;
    padding: 5px 13px;
    border: 1px solid #E6DAC6;
    border-radius: 999px;
    background: #FFFDF9;
    color: #6B5B45;
    font-size: .74rem;
    font-weight: 700;
    letter-spacing: .02em;
}
.ab-hero-copy h1 {
    margin: 0 0 8px !important;
    color: #2E2040 !important;
    font-size: 2.05rem !important;
    font-weight: 800 !important;
    line-height: 1.16 !important;
    letter-spacing: -.02em;
}
.ab-slogan {
    margin: 0 0 12px !important;
    color: #5C4A6B !important;
    font-size: .98rem !important;
    font-weight: 650 !important;
}
.ab-desc {
    margin: 0 0 16px !important;
    max-width: 520px;
    color: #7C7080 !important;
    font-size: .9rem !important;
    line-height: 1.65 !important;
}
.ab-chips { display: flex; flex-wrap: wrap; gap: 10px; }
.ab-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 14px;
    border: 1px solid #EADFCD;
    border-radius: 999px;
    background: rgba(255, 253, 249, .9);
    color: #4A3559;
    font-size: .84rem;
    font-weight: 620;
}
.ab-chip .mi { font-size: 17px; color: #6B4F86; }

/* ---- Maskot ---- */
.ab-hero-art {
    position: relative;
    flex: 0 1 260px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    z-index: 1;
}
.ab-maskot {
    width: 100%;
    max-width: 232px;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 16px 26px rgba(76, 58, 43, .18));
}
.ab-maskot-tag {
    position: absolute;
    right: 2px;
    bottom: 2px;
    display: flex;
    flex-direction: column;
    color: #4A3559;
    font-family: "Segoe Script", "Brush Script MT", cursive;
    font-size: 1.1rem;
    line-height: 1.1;
    text-align: right;
}
.ab-maskot-tag small {
    color: #9A8B9A;
    font-size: .72rem;
    font-family: Inter, system-ui, sans-serif;
}

/* ---- Lencana AOG ---- */
.ab-hero-brand {
    flex: 0 0 150px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    padding-left: 18px;
    border-left: 1px solid rgba(214, 199, 176, .7);
    text-align: center;
    z-index: 1;
}
.ab-brand-mark {
    display: grid;
    place-items: center;
    width: 54px;
    height: 54px;
    margin-bottom: 4px;
}
.ab-brand-mark img.ab-brand-logo {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    vertical-align: middle !important;
}
.ab-brand-name {
    color: #2E2040;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: .06em;
    line-height: 1;
}
.ab-brand-sub {
    color: #6B5B45;
    font-size: .6rem;
    font-weight: 700;
    letter-spacing: .14em;
}
.ab-brand-sub2 {
    color: #9A8B7A;
    font-size: .58rem;
    font-weight: 600;
    letter-spacing: .3em;
}

/* ================================================================
   KARTU ISI
   ================================================================ */
.ab-card {
    height: 100%;
    box-sizing: border-box;
    padding: 18px 20px 20px;
    border: 1px solid #EADFCD;
    border-radius: 22px;
    background: linear-gradient(180deg, #FFFDF9 0%, #FDF8F1 100%);
    box-shadow: 0 12px 30px rgba(76, 58, 43, .07);
}
.ab-card-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}
.ab-head-ic {
    display: grid;
    place-items: center;
    flex: 0 0 46px;
    width: 46px;
    height: 46px;
    padding: 8px;
    box-sizing: border-box;
    border-radius: 14px;
    background: linear-gradient(145deg, #3A2A4C, #241A33);
    color: #F2E4C3;
}
.ab-head-ic img.ab-head-logo {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    vertical-align: middle !important;
}
.ab-head-ic-sq {
    background: #F1E9F4;
    color: #4A3559;
}
.ab-head-ic-sq .mi { font-size: 22px; }
.ab-card-head b {
    display: block;
    color: #2E2040;
    font-size: 1.02rem;
    font-weight: 750;
}
.ab-card-head i {
    display: block;
    color: #8A7F8A;
    font-size: .84rem;
    font-style: normal;
}
.ab-card-text {
    margin: 0 0 14px !important;
    color: #7C7080 !important;
    font-size: .86rem !important;
    line-height: 1.6 !important;
}

/* ---- Grid item kecil ---- */
.ab-mini-grid { display: grid; gap: 10px; }
.ab-mini-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.ab-mini-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.ab-mini {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 14px 10px 15px;
    border: 1px solid #EFE6D8;
    border-radius: 16px;
    background: #FFFDF9;
    text-align: center;
    transition: transform .16s ease, box-shadow .16s ease,
                border-color .16s ease;
}
.ab-mini:hover {
    transform: translateY(-2px);
    border-color: #DCC9E4;
    box-shadow: 0 10px 22px rgba(76, 58, 43, .09);
}
.ab-mini-ic {
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: 12px;
    background: #F4ECF7;
    color: #4A3559;
}
.ab-mini-ic .mi { font-size: 19px; }
.ab-mini-prod .ab-mini-ic { background: #FAF1E4; color: #6B4F86; }
.ab-mini-name {
    color: #2E2040;
    font-size: .86rem;
    font-weight: 700;
    line-height: 1.25;
}
.ab-mini-desc {
    color: #8A7F8A;
    font-size: .74rem;
    line-height: 1.45;
}

/* ================================================================
   KARTU KUTIPAN (senja kota)
   ================================================================ */
.ab-quote {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
    min-height: 168px;
    box-sizing: border-box;
    overflow: hidden;
    padding: 24px 26px;
    border-radius: 22px;
    background: linear-gradient(135deg, #3B2B50 0%, #513663 48%, #7A4F63 100%);
    box-shadow: 0 16px 38px rgba(46, 32, 64, .28);
}
.ab-quote-sky {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(60% 80% at 82% 22%, rgba(243, 198, 134, .45), transparent 65%),
        radial-gradient(2px 2px at 24% 24%, rgba(255, 255, 255, .55), transparent),
        radial-gradient(2px 2px at 44% 14%, rgba(255, 255, 255, .4), transparent),
        radial-gradient(2px 2px at 66% 40%, rgba(255, 255, 255, .35), transparent);
}
.ab-quote-city {   /* siluet kota + pantulan air */
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 46%;
    background:
        linear-gradient(180deg, rgba(27, 18, 38, 0) 0%,
                        rgba(27, 18, 38, .55) 55%, rgba(27, 18, 38, .8) 100%),
        repeating-linear-gradient(90deg,
            rgba(255, 228, 176, .22) 0 3px,
            transparent 3px 16px);
}
.ab-quote-text {
    position: relative;
    z-index: 1;
    margin: 0 0 10px !important;
    color: #FFF6E7 !important;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1.04rem !important;
    font-style: italic;
    font-weight: 600 !important;
    line-height: 1.6 !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, .3);
}
.ab-quote-by {
    position: relative;
    z-index: 1;
    color: rgba(255, 240, 220, .8);
    font-size: .8rem;
    font-weight: 600;
}

/* ================================================================
   RESPONSIF
   ================================================================ */
@media (max-width: 1100px) {
    .ab-hero { flex-wrap: wrap; }
    .ab-hero-copy { flex: 1 1 100%; }
    .ab-hero-art { flex: 1 1 60%; }
    .ab-hero-brand {
        flex: 0 0 auto;
        border-left: none;
        padding-left: 0;
    }
}
@media (max-width: 820px) {
    body .stApp:has(.about-page-shell) [data-testid="stMainBlockContainer"] {
        padding: 70px 10px 48px !important;
    }
    .ab-hero { padding: 20px 16px; }
    .ab-hero-copy h1 { font-size: 1.6rem !important; }
    .ab-mini-3, .ab-mini-4 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
"""
