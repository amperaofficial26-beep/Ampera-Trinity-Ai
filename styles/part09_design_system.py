# -*- coding: utf-8 -*-
"""TRINITY PREMIUM UI — design system final (token warna, sidebar, topbar, main area, panel kanan, responsive, accessibility)

Dipecah dari styles.py asli (baris 5951-7916), isi CSS TIDAK diubah.
"""

CSS = r"""
/* ================================================================
   TRINITY PREMIUM UI — FINAL DESIGN SYSTEM
   Warm Ivory / Deep Plum / Soft Futuristic
================================================================ */


/* ================================================================
   CORE DESIGN TOKENS
================================================================ */

.stApp:has(.tr-chat-layout) {

    --tr-bg-premium: #F5EBDD;

    --tr-sidebar-premium: #EFE2D0;

    --tr-surface-premium: #FAF3E7;

    --tr-plum-premium: #49315C;

    --tr-plum-hover: #5B3D70;

    --tr-lavender-premium: #E8DDF0;

    --tr-blue-premium: #DFEAF0;

    --tr-sage-premium: #DDEADB;

    --tr-border-premium: #D8C9B6;

    --tr-text-premium: #30283A;

    --tr-text-secondary: #766F7A;

    --tr-shadow-soft:
        0 10px 30px rgba(48, 40, 58, 0.055);

    --tr-shadow-card:
        0 4px 16px rgba(48, 40, 58, 0.045);

    --tr-radius-lg: 22px;

    --tr-radius-md: 17px;

    --tr-radius-sm: 13px;

    --tr-sidebar-width: 210px;

    --tr-right-width: 270px;

    --tr-gap: 18px;
}


/* ================================================================
   BACKGROUND
================================================================ */

.stApp:has(.tr-chat-layout) {

    background:
        var(--tr-bg-premium)
        !important;

    color:
        var(--tr-text-premium)
        !important;
}


/* ================================================================
   SIDEBAR
================================================================ */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"] {

    width:
        var(--tr-sidebar-width)
        !important;

    min-width:
        var(--tr-sidebar-width)
        !important;

    max-width:
        var(--tr-sidebar-width)
        !important;

    background:
        var(--tr-sidebar-premium)
        !important;

    border-right:
        1px solid
        var(--tr-border-premium)
        !important;

    box-shadow:
        4px 0 18px
        rgba(48, 40, 58, 0.025)
        !important;
}


.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"] > div {

    padding:
        12px 10px
        12px 10px
        !important;
}


/* ================================================================
   SIDEBAR BRAND
================================================================ */

.stApp:has(.tr-chat-layout)
.sb-brand {

    display:
        flex
        !important;

    align-items:
        center
        !important;

    gap:
        11px
        !important;

    width:
        100%
        !important;

    min-height:
        58px
        !important;

    padding:
        9px 12px
        !important;

    margin:
        0 0 14px
        !important;

    background:
        rgba(250, 243, 231, 0.72)
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        17px
        !important;

    box-shadow:
        0 3px 12px
        rgba(48, 40, 58, 0.035)
        !important;
}


.stApp:has(.tr-chat-layout)
.sb-brand-logo {

    width:
        30px
        !important;

    height:
        30px
        !important;

    min-width:
        30px
        !important;

    display:
        flex
        !important;

    align-items:
        center
        !important;

    justify-content:
        center
        !important;
}


.stApp:has(.tr-chat-layout)
.sb-brand-logo .logo-sidebar {

    width:
        30px
        !important;

    height:
        30px
        !important;
}


.stApp:has(.tr-chat-layout)
.sb-brand-title {

    color:
        var(--tr-text-premium)
        !important;

    font-size:
        19px
        !important;

    font-weight:
        600
        !important;

    letter-spacing:
        -0.035em
        !important;
}


/* ================================================================
   SIDEBAR MENU
================================================================ */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
div.stButton {

    margin:
        1px 0
        !important;
}


.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
div.stButton > button {

    min-height:
        12px
        !important;

    padding:
        2px 11px
        !important;

    border:
        1px solid transparent
        !important;

    border-radius:
        12px
        !important;

    background:
        transparent
        !important;

    color:
        var(--tr-text-premium)
        !important;

    box-shadow:
        none
        !important;

    font-size:
        14px
        !important;

    font-weight:
        500
        !important;

    transition:
        background .22s ease,
        color .22s ease,
        transform .22s ease,
        border-color .22s ease
        !important;

    animation:
        none
        !important;
}


.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
div.stButton > button:hover {

    background:
        var(--tr-lavender-premium)
        !important;

    border-color:
        rgba(73, 49, 92, 0.06)
        !important;

    transform:
        translateX(2px)
        !important;
}


/* ACTIVE MENU */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
div.stButton > button[kind="primary"],

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
[data-testid="stBaseButton-primary"] {

    background:
        var(--tr-plum-premium)
        !important;

    color:
        #FAF3E7
        !important;

    border-color:
        var(--tr-plum-premium)
        !important;

    box-shadow:
        0 5px 14px
        rgba(73, 49, 92, 0.16)
        !important;
}


.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
div.stButton > button[kind="primary"]:hover {

    background:
        var(--tr-plum-hover)
        !important;

    transform:
        translateX(2px)
        !important;
}


/* Material icons sidebar */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
[data-testid="stIconMaterial"] {

    color:
        inherit
        !important;

    font-size:
        19px
        !important;
}


/* ================================================================
   SIDEBAR DIVIDER
================================================================ */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
.sb-divider {

    margin:
        10px 4px
        !important;

    border-top:
        1px solid
        rgba(216, 201, 182, 0.75)
        !important;
}


/* ================================================================
   USER PROFILE BOTTOM
================================================================ */

.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
.sb-account {

    width:
        var(--dash-sidebar, 230px)
        !important;

    max-width:
        var(--dash-sidebar, 230px)
        !important;

    left:
        0
        !important;

    bottom:
        0
        !important;

    padding:
        9px 10px
        !important;

    box-sizing:
        border-box
        !important;

    border-radius:
        0
        !important;

    background:
        rgba(250, 243, 231, 0.56)
        !important;
}


.stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"]
.sb-account .ava {

    width:
        31px
        !important;

    height:
        31px
        !important;

    border-radius:
        50%
        !important;

    background:
        #E6DCCB
        !important;

    color:
        var(--tr-plum-premium)
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;
}


/* ================================================================
   TOP HEADER
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-chat_topbar {

    position:
        fixed
        !important;

    top:
        12px
        !important;

    left:
        calc(
            var(--tr-sidebar-width)
            + var(--tr-gap)
        )
        !important;

    right:
        calc(
            var(--tr-right-width)
            + var(--tr-gap)
        )
        !important;

    width:
        auto
        !important;

    max-width:
        none
        !important;

    min-width:
        0
        !important;

    min-height:
        62px
        !important;

    padding:
        7px 9px
        !important;

    margin:
        0
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        21px
        !important;

    background:
        rgba(250, 243, 231, 0.90)
        !important;

    box-shadow:
        var(--tr-shadow-soft)
        !important;

    backdrop-filter:
        blur(16px)
        saturate(1.08)
        !important;

    -webkit-backdrop-filter:
        blur(16px)
        saturate(1.08)
        !important;

    transform:
        none
        !important;
}


/* Topbar columns */

.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
[data-testid="stHorizontalBlock"] {

    gap:
        8px
        !important;

    align-items:
        center
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
[data-testid="stColumn"] {

    min-width:
        0
        !important;
}


/* ================================================================
   TOPBAR BRAND
================================================================ */

.stApp:has(.tr-chat-layout)
.tr-brand-profile {

    min-height:
        46px
        !important;

    padding:
        5px 8px
        !important;

    gap:
        10px
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-brand-avatar {

    width:
        34px
        !important;

    height:
        34px
        !important;

    border-radius:
        11px
        !important;

    background:
        #EEE5D7
        !important;

    color:
        var(--tr-plum-premium)
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    font-size:
        18px
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-brand-name {

    font-size:
        15px
        !important;

    font-weight:
        600
        !important;

    color:
        var(--tr-text-premium)
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-brand-sub {

    font-size:
        11px
        !important;

    color:
        var(--tr-text-secondary)
        !important;
}


/* ================================================================
   AI SELECTOR
================================================================ */

.stApp:has(.tr-chat-layout)
.tr-assistant-pill {

    min-height:
        44px
        !important;

    padding:
        5px 13px
        !important;

    gap:
        10px
        !important;

    background:
        #F7EFE3
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        17px
        !important;

    transition:
        border-color .2s ease,
        box-shadow .2s ease
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-assistant-pill:hover {

    border-color:
        #BBA9C5
        !important;

    box-shadow:
        0 0 0 3px
        rgba(73, 49, 92, 0.045)
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-pill-icon {

    width:
        30px
        !important;

    height:
        30px
        !important;

    border-radius:
        10px
        !important;

    background:
        var(--tr-lavender-premium)
        !important;

    border:
        1px solid
        #D9CBE2
        !important;

    color:
        var(--tr-plum-premium)
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-pill-title {

    font-size:
        14px
        !important;

    font-weight:
        600
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-pill-sub {

    font-size:
        10.5px
        !important;

    color:
        var(--tr-text-secondary)
        !important;
}


/* ================================================================
   TOPBAR USER
================================================================ */

.stApp:has(.tr-chat-layout)
.tr-user-pill {

    min-height:
        44px
        !important;

    padding:
        5px 9px
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        16px
        !important;

    background:
        rgba(250, 243, 231, 0.58)
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-user-avatar {

    width:
        30px
        !important;

    height:
        30px
        !important;

    background:
        #E8DFD0
        !important;

    color:
        var(--tr-plum-premium)
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-user-copy b {

    font-size:
        13px
        !important;

    font-weight:
        600
        !important;
}


.stApp:has(.tr-chat-layout)
.tr-user-copy small {

    font-size:
        10px
        !important;

    color:
        var(--tr-text-secondary)
        !important;
}


/* ================================================================
   LOGOUT
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
div.stButton > button {

    min-height:
        40px
        !important;

    padding:
        6px 13px
        !important;

    border-radius:
        13px
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    background:
        #F8F0E5
        !important;

    color:
        var(--tr-text-premium)
        !important;

    font-size:
        12px
        !important;

    font-weight:
        500
        !important;

    box-shadow:
        none
        !important;

    animation:
        none
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
div.stButton > button:hover {

    background:
        #EFE3D3
        !important;

    transform:
        translateY(-1px)
        !important;
}


/* ================================================================
   MAIN AREA
================================================================ */

.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"] {

    width:
        100%
        !important;

    max-width:
        none
        !important;

    padding-top:
        92px
        !important;

    padding-left:
        calc(
            var(--tr-sidebar-width)
            + var(--tr-gap)
        )
        !important;

    padding-right:
        calc(
            var(--tr-right-width)
            + var(--tr-gap)
        )
        !important;

    padding-bottom:
        9rem
        !important;
}


.stApp:has(.tr-chat-layout)
[data-testid="stMainBlockContainer"]
> [data-testid="stVerticalBlock"] {

    width:
        min(
            760px,
            calc(
                100vw
                - var(--tr-sidebar-width)
                - var(--tr-right-width)
                - 54px
            )
        )
        !important;

    max-width:
        min(
            760px,
            calc(
                100vw
                - var(--tr-sidebar-width)
                - var(--tr-right-width)
                - 54px
            )
        )
        !important;

    margin-left:
        auto
        !important;

    margin-right:
        auto
        !important;
}

.stApp:has(.tr-chat-layout)
.trinity-greeting .logo-greeting {

    width:
        52px
        !important;

    height:
        52px
        !important;

    flex:
        0 0 52px
        !important;

    opacity:
        0.96
        !important;
}

/* Actual input */

.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"] {

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        21px
        !important;

    background:
        var(--tr-surface-premium)
        !important;

    box-shadow:
        0 8px 24px
        rgba(48, 40, 58, 0.055)
        !important;

    transition:
        border-color .24s ease,
        box-shadow .24s ease
        !important;
}


.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]:focus-within {

    border-color:
        rgba(73, 49, 92, 0.48)
        !important;

    box-shadow:
        0 0 0 3px
        rgba(73, 49, 92, 0.07),
        0 9px 28px
        rgba(48, 40, 58, 0.06)
        !important;
}


/* Text */

.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"] textarea {

    font-family:
        "Space Grotesk",
        sans-serif
        !important;

    font-size:
        13.5px
        !important;

    font-weight:
        450
        !important;

    color:
        var(--tr-text-premium)
        !important;

    line-height:
        1.4
        !important;

    padding-left:
        11px
        !important;

    padding-top:
        8px
        !important;
}


.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]
textarea::placeholder {

    color:
        var(--tr-text-secondary)
        !important;

    opacity:
        0.88
        !important;

    font-size:
        13.5px
        !important;

    font-weight:
        450
        !important;
}


/* ================================================================
   INPUT ICONS
================================================================ */

.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]
button {

    transition:
        background .2s ease,
        color .2s ease,
        transform .2s ease
        !important;

    animation:
        none
        !important;
}


.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]
button:hover {

    transform:
        translateY(-1px)
        !important;
}


/* Send = deep plum */

.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]
button[type="submit"] {

    background:
        var(--tr-plum-premium)
        !important;

    color:
        #FAF3E7
        !important;

    border:
        none
        !important;

    box-shadow:
        0 4px 10px
        rgba(73, 49, 92, 0.16)
        !important;
}


.stApp:has(.tr-chat-layout)
[data-testid="stChatInput"]
button[type="submit"]:hover {

    background:
        var(--tr-plum-hover)
        !important;
}


/* ================================================================
   RIGHT PANEL
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail {

    position:
        fixed
        !important;

    top:
        84px
        !important;

    right:
        var(--tr-gap)
        !important;

    bottom:
        16px
        !important;

    width:
        var(--tr-right-width)
        !important;

    max-width:
        var(--tr-right-width)
        !important;

    min-width:
        var(--tr-right-width)
        !important;

    padding:
        15px
        !important;

    margin:
        0
        !important;

    overflow-y:
        auto
        !important;

    overflow-x:
        hidden
        !important;

    background:
        var(--tr-surface-premium)
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        23px
        !important;

    box-shadow:
        var(--tr-shadow-soft)
        !important;

    backdrop-filter:
        blur(12px)
        !important;
}


/* ================================================================
   RIGHT PANEL HEADING
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail
.tr-rail-title-row {

    margin:
        2px 1px 10px
        !important;

    color:
        var(--tr-text-premium)
        !important;

    font-size:
        17px
        !important;

    font-weight:
        600
        !important;

    letter-spacing:
        -0.025em
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail
.rail-heading-icon {

    display:
        inline-flex
        !important;

    width:
        20px
        !important;

    height:
        20px
        !important;

    margin-right:
        6px
        !important;

    color:
        var(--tr-plum-premium)
        !important;

    vertical-align:
        -3px
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail
.tr-rail-title-row.with-link {

    margin-top:
        17px
        !important;

    padding-top:
        15px
        !important;

    border-top:
        1px solid
        rgba(216, 201, 182, 0.82)
        !important;
}


/* ================================================================
   ALL RIGHT PANEL CARDS
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail
div.stButton > button {

    border-radius:
        19px
        !important;

    border:
        1px solid
        rgba(216, 201, 182, 0.88)
        !important;

    color:
        var(--tr-text-premium)
        !important;

    box-shadow:
        none
        !important;

    transition:
        transform .22s ease,
        border-color .22s ease,
        background .22s ease,
        box-shadow .22s ease
        !important;

    animation:
        none
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-chat_right_rail
div.stButton > button:hover {

    transform:
        translateY(-2px)
        !important;

    box-shadow:
        0 6px 16px
        rgba(48, 40, 58, 0.055)
        !important;
}


/* ================================================================
   QUICK FEATURES — 2 x 2
================================================================ */

.stApp:has(.tr-chat-layout)
.st-key-rail_quick_chat
div.stButton > button {

    min-height:
        108px
        !important;

    padding:
        13px
        !important;

    background:
        var(--tr-lavender-premium)
        !important;

    border-color:
        #D9CBE2
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-rail_quick_multi
div.stButton > button {

    min-height:
        108px
        !important;

    padding:
        13px
        !important;

    background:
        var(--tr-blue-premium)
        !important;

    border-color:
        #CBDDE5
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-rail_quick_image
div.stButton > button {

    min-height:
        108px
        !important;

    padding:
        13px
        !important;

    background:
        #F3E9DB
        !important;

    border-color:
        #E4D5C2
        !important;
}


.stApp:has(.tr-chat-layout)
.st-key-rail_quick_upload
div.stButton > button {

    min-height:
        108px
        !important;

    padding:
        13px
        !important;

    background:
        var(--tr-sage-premium)
        !important;

    border-color:
        #C9DDC6
        !important;
}


/* Quick card typography */

.stApp:has(.tr-chat-layout)
.st-key-rail_quick_chat
button p,

.stApp:has(.tr-chat-layout)
.st-key-rail_quick_multi
button p,

.stApp:has(.tr-chat-layout)
.st-key-rail_quick_image
button p,

.stApp:has(.tr-chat-layout)
.st-key-rail_quick_upload
button p {

    color:
        var(--tr-text-premium)
        !important;
}


/* ================================================================
   MODEL CARDS
================================================================ */

.stApp:has(.tr-chat-layout)
[class*="st-key-rail_model_"]
div.stButton > button {

    min-height:
        62px
        !important;

    padding:
        11px 13px
        !important;

    background:
        #F8F0E4
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        17px
        !important;
}


/* Selected model */

.stApp:has(.tr-chat-layout)
[class*="st-key-rail_model_"]
div.stButton > button[kind="primary"] {

    position:
        relative
        !important;

    background:
        #F4EAF5
        !important;

    border:
        1.5px solid
        var(--tr-plum-premium)
        !important;

    box-shadow:
        0 0 0 3px
        rgba(73, 49, 92, 0.055)
        !important;
}


/* Default badge */

.stApp:has(.tr-chat-layout)
[class*="st-key-rail_model_"]
div.stButton > button[kind="primary"]::after {

    content:
        "Default"
        !important;

    position:
        absolute
        !important;

    top:
        9px
        !important;

    right:
        10px
        !important;

    padding:
        2px 7px
        !important;

    border-radius:
        999px
        !important;

    background:
        var(--tr-lavender-premium)
        !important;

    color:
        var(--tr-plum-premium)
        !important;

    font-size:
        9px
        !important;

    font-weight:
        600
        !important;
}


/* ================================================================
   RECENT CHAT CARDS
================================================================ */

.stApp:has(.tr-chat-layout)
[class*="st-key-rail_recent_"]
div.stButton > button {

    min-height:
        54px
        !important;

    padding:
        10px 12px
        !important;

    background:
        #F8F0E4
        !important;

    border:
        1px solid
        var(--tr-border-premium)
        !important;

    border-radius:
        16px
        !important;
}


/* ================================================================
   REMOVE EXCESSIVE GLOBAL BUTTON ANIMATION ON CHAT DASHBOARD
================================================================ */

.stApp:has(.tr-chat-layout)
div.stButton > button,

.stApp:has(.tr-chat-layout)
div.stDownloadButton > button,

.stApp:has(.tr-chat-layout)
[data-testid="stPopover"] > button {

    animation:
        none
        !important;

    transform-origin:
        center
        !important;
}


/* ================================================================
   RESPONSIVE
================================================================ */

@media (max-width: 1180px) {

    .stApp:has(.tr-chat-layout) {

        --tr-right-width: 0px;
    }


    .stApp:has(.tr-chat-layout)
    .st-key-chat_right_rail {

        display:
            none
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .st-key-chat_topbar {

        left:
            calc(
                var(--tr-sidebar-width)
                + 16px
            )
            !important;

        right:
            16px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    [data-testid="stMainBlockContainer"] {

        padding-right:
            16px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    [data-testid="stBottomBlockContainer"] {

        max-width:
            calc(
                100vw
                - var(--tr-sidebar-width)
                - 32px
            )
            !important;
    }
}


/* ================================================================
   TABLET
================================================================ */

@media (max-width: 820px) {

    .stApp:has(.tr-chat-layout) {

        --tr-sidebar-width: 76px;
    }


    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] {

        width:
            76px
            !important;

        min-width:
            76px
            !important;

        max-width:
            76px
            !important;

        padding:
            10px 6px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .sb-brand {

        justify-content:
            center
            !important;

        padding:
            8px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .sb-brand-title {

        display:
            none
            !important;
    }


    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"]
    div.stButton > button {

        justify-content:
            center
            !important;

        padding:
            8px
            !important;

        font-size:
            0
            !important;
    }


    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"]
    div.stButton > button
    [data-testid="stIconMaterial"] {

        font-size:
            20px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    [data-testid="stMainBlockContainer"] {

        padding-left:
            92px
            !important;

        padding-right:
            16px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .st-key-chat_topbar {

        left:
            92px
            !important;

        right:
            16px
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .tr-brand-name,
    .stApp:has(.tr-chat-layout)
    .tr-brand-sub {

        display:
            none
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .tr-assistant-pill {

        flex:
            1
            1
            auto
            !important;
    }


    .stApp:has(.tr-chat-layout)
    .tr-user-pill {

        display:
            none
            !important;
    }
}


/* ================================================================
   ACCESSIBILITY
================================================================ */

@media (prefers-reduced-motion: reduce) {

    .stApp:has(.tr-chat-layout) * {

        animation:
            none
            !important;

        transition:
            none
            !important;
    }
}
/* ================================================================
   🎛️ KONTROL POSISI KOLOM CHAT
   Hanya ubah angka di sini.
================================================================ */

.stApp:has(.tr-chat-layout) {

    /* ------------------------------------------------
       POSISI HORIZONTAL
       - kiri  = nilai negatif
       - kanan = nilai positif
       ------------------------------------------------ */
    --chat-shift: -70px;


    /* ------------------------------------------------
       POSISI VERTIKAL SAAT SUDAH ADA CHAT
       - 0px  = paling bawah
       - 30px = naik 30px
       - 60px = naik 60px
       ------------------------------------------------ */
    --chat-lift: 32px;


    /* ------------------------------------------------
       POSISI VERTIKAL SAAT BELUM MULAI CHAT
       Satuan vh.
       20vh = lebih dekat bawah
       26vh = posisi sekarang
       32vh = lebih ke atas
       ------------------------------------------------ */
    --chat-lift-fresh: 26vh;


    /* ------------------------------------------------
       LEBAR KOLOM CHAT
       ------------------------------------------------ */
    --chat-width: 46rem;
}

/* =========================================================
   TOPBAR — JANGAN BUAT HORIZONTAL PAGE OVERFLOW
   ========================================================= */

.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 10px !important;
    flex-wrap: nowrap !important;
    overflow-x: hidden !important;
}

/* Kolom topbar boleh mengecil mengikuti viewport */
.stApp:has(.tr-chat-layout)
.st-key-chat_topbar
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 0 !important;
    flex-shrink: 1 !important;
}

/* Teks kartu tetap satu baris tanpa memaksa seluruh layout melebar */
.stApp:has(.tr-chat-layout)
.topbar-card,
.stApp:has(.tr-chat-layout)
.user-profile-card,
.stApp:has(.tr-chat-layout)
.topbar-item {
    white-space: nowrap !important;
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Pastikan halaman chat tidak punya scroll horizontal */
.stApp:has(.tr-chat-layout) {
    overflow-x: hidden !important;
}

/* ================================================================
   SIDEBAR — TRINITY WARM NAVIGATION
================================================================ */
@media (min-width: 821px) {
    section[data-testid="stSidebar"] {
        width: 224px !important;
        min-width: 224px !important;
        max-width: 224px !important;
        background: #EFE2D0 !important;
        border-right: 1px solid #D8C9B6 !important;
        box-shadow: 5px 0 22px rgba(48, 40, 58, .035) !important;
    }

    .stApp:has(.tr-chat-layout) {
        --tr-sidebar-width: 224px !important;
        --dash-sidebar: 224px !important;
    }

    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] {
        width: var(--dash-sidebar) !important;
        min-width: var(--dash-sidebar) !important;
        max-width: var(--dash-sidebar) !important;
    }
}

section[data-testid="stSidebar"] > div {
    padding: 22px 14px 18px !important;
    background: #EFE2D0 !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-bottom: 84px !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
section[data-testid="stSidebar"] .element-container {
    margin: 0 !important;
}

/* Brand card: kompas besar, garis pemisah, dan nama Trinity. */
section[data-testid="stSidebar"] .sb-brand {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    width: auto !important;
    min-height: 104px !important;
    margin: 7px 0 30px !important;
    padding: 10px !important;
    border: 1px solid #E0D2C0 !important;
    border-radius: 31px !important;
    background: #F8F0E6 !important;
    box-shadow: 0 10px 24px rgba(76, 58, 43, .055) !important;
}
section[data-testid="stSidebar"] .sb-brand-logo {
    position: relative !important;
    display: grid !important;
    place-items: center !important;
    width: 70px !important;
    height: 70px !important;
    min-width: 70px !important;
    padding-right: 12px !important;
    border-right: 1px solid #D8C9B6 !important;
}
section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar {
    width: 70px !important;
    height: 70px !important;
}
section[data-testid="stSidebar"] .sb-brand-title {
    padding: 0 !important;
    color: #2E2040 !important;
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-size: 2rem !important;
    font-weight: 600 !important;
    letter-spacing: -.045em !important;
    line-height: 1 !important;
}

/* Semua item navigasi memakai tinggi dan jarak konsisten. */
section[data-testid="stSidebar"] div.stButton {
    margin: 4px 0 !important;
}
section[data-testid="stSidebar"] div.stButton > button {
    width: 100% !important;
    min-height: 46px !important;
    padding: 8px 16px !important;
    border: 1px solid transparent !important;
    border-radius: 999px !important;
    background: transparent !important;
    color: #3D2D4D !important;
    box-shadow: none !important;
    font-size: 1.02rem !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
    transition: background .18s ease, color .18s ease, transform .18s ease !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #E5D8C6 !important;
    color: #352346 !important;
    transform: translateX(2px) !important;
}
section[data-testid="stSidebar"] div.stButton > button > div,
section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] div.stButton > button p {
    margin: 0 !important;
    color: inherit !important;
    font-size: 1.02rem !important;
    font-weight: inherit !important;
    line-height: 1.25 !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] div.stButton > button [data-testid="stIconMaterial"] {
    width: 1.45rem !important;
    height: 1.45rem !important;
    flex: 0 0 1.45rem !important;
    color: inherit !important;
    font-size: 1.45rem !important;
    line-height: 1 !important;
}

/* Item yang sedang aktif: pill ungu seperti referensi. */
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    min-height: 54px !important;
    padding: 9px 17px !important;
    background: #4B315D !important;
    border-color: #4B315D !important;
    color: #FFF9F1 !important;
    box-shadow: 0 8px 18px rgba(75, 49, 93, .18) !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] [data-testid="stIconMaterial"] {
    color: #FFF9F1 !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background: #5B3D70 !important;
    border-color: #5B3D70 !important;
    transform: translateX(0) !important;
}

/* Room baru tampil sebagai menu ringan, bukan kartu penuh. */
section[data-testid="stSidebar"] .st-key-sb_new {
    margin-bottom: 6px !important;
}
section[data-testid="stSidebar"] .st-key-sb_new div.stButton > button {
    color: #3D2D4D !important;
    font-size: 1.04rem !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] .st-key-sb_new div.stButton > button:hover {
    background: #E5D8C6 !important;
}

/* Jarak antar grup utama dan kelompok Proyek. */
section[data-testid="stSidebar"] .sb-divider {
    height: 1px !important;
    margin: 18px 18px !important;
    background: #D8C9B6 !important;
    opacity: .9 !important;
}
section[data-testid="stSidebar"] .st-key-sb_menu_proyek,
section[data-testid="stSidebar"] .st-key-sb_menu_artefak,
section[data-testid="stSidebar"] .st-key-sb_menu_sesuaikan,
section[data-testid="stSidebar"] .st-key-sb_menu_desain,
section[data-testid="stSidebar"] .st-key-sb_menu_jadwal {
    margin: 2px 0 !important;
}
section[data-testid="stSidebar"] .st-key-sb_menu_jadwal div.stButton > button p {
    max-width: 126px !important;
}

/* Akun tetap berada di bawah, dengan warna yang menyatu dengan sidebar. */
section[data-testid="stSidebar"] .sb-account {
    width: 224px !important;
    max-width: 224px !important;
    padding: 12px 18px !important;
    border-top: 1px solid #D8C9B6 !important;
    background: #EFE2D0 !important;
}

@media (max-width: 820px) {
    section[data-testid="stSidebar"] > div {
        padding: 14px 7px 12px !important;
    }
    section[data-testid="stSidebar"] .sb-brand {
        min-height: 58px !important;
        margin: 4px 2px 16px !important;
        padding: 8px !important;
        border-radius: 19px !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] .sb-brand-logo {
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        padding-right: 0 !important;
        border-right: none !important;
    }
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar {
        width: 42px !important;
        height: 42px !important;
    }
    section[data-testid="stSidebar"] .sb-brand-title,
    section[data-testid="stSidebar"] div.stButton > button p {
        display: none !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        justify-content: center !important;
        padding: 8px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button > div,
    section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
        justify-content: center !important;
        width: auto !important;
    }
    section[data-testid="stSidebar"] div.stButton > button [data-testid="stIconMaterial"] {
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] .sb-divider {
        margin: 12px 5px !important;
    }
    section[data-testid="stSidebar"] .sb-account {
        width: 76px !important;
        max-width: 76px !important;
        padding: 10px 7px !important;
    }
}

/* Override desktop: logo sidebar harus memenuhi brand card, bukan hanya
   membesarkan slotnya. Ukuran span dan img dipaksa bersama-sama karena
   logo_img_html() membawa inline width/height. */
@media (min-width: 821px) {
    .stApp:has(.tr-chat-layout)
section[data-testid="stSidebar"] .sb-brand,
section[data-testid="stSidebar"] .sb-brand {
        min-height: 92px !important;
        box-sizing: border-box !important;
    }
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] .sb-brand-logo,
    section[data-testid="stSidebar"] .sb-brand-logo {
        width: 58px !important;
        height: 58px !important;
        min-width: 58px !important;
        padding-right: 6px !important;
        box-sizing: border-box !important;
        flex: 0 0 58px !important;
    }
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar,
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar,
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar img,
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar img {
        width: 50px !important;
        height: 50px !important;
        max-width: none !important;
    }
}

/* ================================================================
   SIDEBAR PARITY — SEMUA HALAMAN
   Override global ini sengaja berada di bagian paling akhir agar sidebar
   halaman non-chat memakai geometri yang sama dengan room chat utama.
================================================================ */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"],
button[kind="headerNoPadding"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
}

@media (min-width: 821px) {
    section[data-testid="stSidebar"] .sb-brand {
        min-height: 92px !important;
        box-sizing: border-box !important;
    }
    section[data-testid="stSidebar"] .sb-brand-logo {
        width: 58px !important;
        height: 58px !important;
        min-width: 58px !important;
        padding-right: 6px !important;
        box-sizing: border-box !important;
        flex: 0 0 58px !important;
    }
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar,
    section[data-testid="stSidebar"] .sb-brand-logo .logo-sidebar img {
        width: 50px !important;
        height: 50px !important;
        max-width: none !important;
    }
    section[data-testid="stSidebar"] {
        width: 224px !important;
        min-width: 224px !important;
        max-width: 224px !important;
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        max-height: 100vh !important;
        overflow-x: hidden !important;
        overflow-y: hidden !important;
    }
    section[data-testid="stSidebar"] > div {
        padding: 22px 14px 18px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        column-gap: 0 !important;
    }
    section[data-testid="stSidebar"] .element-container,
    section[data-testid="stSidebar"] div.stButton {
        margin-top: 0 !important;
        margin-bottom: 4px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        min-height: 40px !important;
        height: auto !important;
        padding: 6px 16px !important;
        border-radius: 999px !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        min-height: 40px !important;
        padding: 6px 16px !important;
    }
}

/* Room chat utama mempertahankan spacing sidebar compact yang lama. */
@media (min-width: 821px) {
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        row-gap: 0 !important;
        column-gap: 0 !important;
    }
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] .element-container,
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] div.stButton {
        margin-top: 1px !important;
        margin-bottom: 1px !important;
    }
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] div.stButton > button {
        min-height: 12px !important;
        height: auto !important;
        padding: 2px 11px !important;
        border-radius: 12px !important;
    }
    .stApp:has(.tr-chat-layout)
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        min-height: 12px !important;
        padding: 2px 11px !important;
    }
}
"""
