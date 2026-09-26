# -*- coding: utf-8 -*-
"""
ANIMASI LOADING "PARAMETER" — pengganti SEMUA animasi thinking lama.

Konsep:
  - Ada 18 parameter LLM/inference (temperature, top-k, vram, dst.).
  - Setiap kali loading, dipilih ACAK 5 parameter (random.sample di sisi
    Python, jadi tiap chat beda urutan), masing-masing tampil 5 detik
    => total satu putaran 25 detik. Kalau API belum selesai, putarannya
    mengulang dari awal (loop).
  - Nilai parameternya "hidup": naik-turun/berganti lewat JavaScript murni
    di browser, jadi tetap bergerak walau server sedang menunggu API.

Dipakai chat_handlers.py lewat: components.html(param_loading_html(), ...)

>>> ATUR JUMLAH & DURASI DI SINI <<<
"""

from __future__ import annotations

import html
import json
import random
import re

# >>> GANTI WARNA GLOW DI SINI (satu tempat untuk semuanya) <<<
# Format hex "#RRGGBB". Dipakai untuk glow logo DAN glow berjalan di teks
# pada loader PARAMETER (chat biasa) di bawah.
#   "#EDE2D1" = krem sidebar (sekarang)
#   "#E8B04B" = emas   |  "#7C3AED" = ungu violet  |  "#2C1F33" = ungu gelap
WARNA_GLOW = "#FFFFFF"

# >>> WARNA UNTUK LOADING KHUSUS (web/file/design/code/card/schedule) <<<
# Disamakan dengan palet resmi Trinity di styles.py (beige + ungu):
#   Aksen utama  : #4A3559 (Deep Violet) — ikon, kursor kode, puncak sapuan glow
#   Aksen lembut : #7E7387 — titik-titik berdenyut mode web
AKSEN_KHUSUS = "#4A3559"
AKSEN_KHUSUS_LEMBUT = "#7E7387"


def _rgb(hex_color: str) -> str:
    """'#FFFFFF' -> '237,226,209' (untuk ditanam ke rgba() di CSS)."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

# Logo Trinity (PNG base64) — sama dengan logo tab/sapaan/label Yuki.
# Kalau modul logo tidak ada / logonya kosong, jatuh ke ikon gerigi.
try:
    from logo import LOGO_B64
except Exception:
    LOGO_B64 = ""

JUMLAH_PARAM_PER_LOADING = 5   # 5 x 5 detik = 25 detik total per putaran
DURASI_PER_PARAM_MS = 5000     # 5 detik per parameter

# Urutan indeks 0-17 (dipakai random.sample):
NAMA_PARAMETER = [
    "temperature",            # 0
    "top-k",                  # 1
    "top-p",                  # 2
    "max_tokens",             # 3
    "presence_penalty",       # 4
    "frequency_penalty",      # 5
    "seed",                   # 6
    "min_p",                  # 7
    "stop_sequences",         # 8
    "repetition_penalty",     # 9
    "typical_p",              # 10
    "mirostat",               # 11
    "batch_size",             # 12
    "vram",                   # 13
    "quantization",           # 14
    "gpu_layers",             # 15
    "tensor_parallel_size",   # 16
    "num_threads",            # 17
]


def pilih_parameter(jumlah: int = JUMLAH_PARAM_PER_LOADING) -> list[int]:
    """Ambil acak `jumlah` indeks parameter tanpa duplikat."""
    return random.sample(range(len(NAMA_PARAMETER)), jumlah)


_HTML = """<style>
/* LOGO TRINITY: denyut 2x -> putar cepat 360 -> denyut 2x -> putar lagi.
   Satu siklus 5 detik (pas dengan durasi per parameter):
     0%-24%  : denyut #1 (membesar-mengecil, glow lembut)
     24%-48% : denyut #2
     48%-72% : PUTAR CEPAT 360 derajat + glow menyala terang
     72%-100%: kembali tenang (denyut kecil), siap siklus berikutnya  */
@keyframes trinitySpin {
  0%   { transform: scale(1)    rotate(0deg);   filter: drop-shadow(0 0 3px rgba(__GLOW__,.55)); }
  12%  { transform: scale(1.22) rotate(0deg);   filter: drop-shadow(0 0 8px rgba(__GLOW__,.55)); }
  24%  { transform: scale(1)    rotate(0deg);   filter: drop-shadow(0 0 3px rgba(__GLOW__,.55)); }
  36%  { transform: scale(1.22) rotate(0deg);   filter: drop-shadow(0 0 8px rgba(__GLOW__,.55)); }
  48%  { transform: scale(1)    rotate(0deg);   filter: drop-shadow(0 0 4px rgba(__GLOW__,.55)); }
  60%  { transform: scale(1.15) rotate(180deg); filter: drop-shadow(0 0 14px rgba(__GLOW__,.55)); }
  72%  { transform: scale(1)    rotate(360deg); filter: drop-shadow(0 0 4px rgba(__GLOW__,.55)); }
  86%  { transform: scale(1.08) rotate(360deg); filter: drop-shadow(0 0 6px rgba(__GLOW__,.55)); }
  100% { transform: scale(1)    rotate(360deg); filter: drop-shadow(0 0 3px rgba(__GLOW__,.55)); }
}
.param-logo {
  display: inline-block;
  width: 26px; height: 26px;
  flex-shrink: 0;
  animation: trinitySpin 5s cubic-bezier(.45,.05,.35,1) infinite;
  will-change: transform, filter;
}
.param-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
/* GLOW BERJALAN pada teks parameter: pita terang menyapu kiri -> kanan
   terus-menerus (gradient di-clip ke huruf, posisinya digeser CSS). */
@keyframes glowSweep {
  0%   { background-position: 130% 0; }
  100% { background-position: -30% 0; }
}
.param-line {
  transition: opacity .25s ease;
  background: linear-gradient(
      100deg,
      #6B6172 0%, #6B6172 38%,
      rgba(__GLOW__,1) 50%,
      #6B6172 62%, #6B6172 100%
  );
  background-size: 220% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  animation: glowSweep 2.4s linear infinite;
}
</style>
<div style="display:flex;align-items:center;justify-content:flex-start;padding:1.5rem 0;">
  <div style="display:flex;align-items:center;gap:10px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:13.5px;color:#6B6172;">
    <span class="param-logo">__LOGO__</span>
    <span id="pline" class="param-line">menyetel parameter…</span>
  </div>
</div>
<script>
(function(){
  const el   = document.getElementById('pline');
  const BAR  = 14;
  const ORDER = __ORDER__;   // indeks parameter terpilih (acak dari Python)
  const DUR   = __DUR__;     // durasi per parameter (ms)

  function bar(p){ p=Math.max(0,Math.min(100,p));
    const f=Math.round(p/100*BAR); return '\u2588'.repeat(f)+'\u2591'.repeat(BAR-f); }
  function ri(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
  function cl(v,a,b){ return Math.max(a,Math.min(b,v)); }
  function hex(n){ return n.toString(16).toUpperCase(); }

  // ---- 18 adegan parameter (indeks HARUS cocok dgn NAMA_PARAMETER) ----
  const R = [
    /* 0 temperature */ function(){ let v=0.7;
      return setInterval(function(){ v=cl(v+(Math.random()-.5)*.18,.05,1.5);
        el.textContent='temperature = '+v.toFixed(2)+'  ['+bar(v/1.5*100)+']'; },110); },
    /* 1 top-k */ function(){ let k=40;
      return setInterval(function(){ k=cl(k+ri(-7,7),1,100);
        el.textContent='top-k = '+k+'  ['+bar(k)+']'; },120); },
    /* 2 top-p */ function(){ let p=.9;
      return setInterval(function(){ p=cl(p+(Math.random()-.5)*.1,.01,1);
        el.textContent='top-p = '+p.toFixed(2)+'  ['+bar(p*100)+']'; },100); },
    /* 3 max_tokens */ function(){ let t=0,M=4096;
      return setInterval(function(){ t+=ri(40,180); if(t>M)t=0;
        el.textContent='max_tokens: '+t+'/'+M+'  ['+bar(t/M*100)+']'; },90); },
    /* 4 presence_penalty */ function(){ let v=0;
      return setInterval(function(){ v=cl(v+(Math.random()-.5)*.3,-2,2);
        el.textContent='presence_penalty = '+(v>=0?'+':'')+v.toFixed(2)+'  ['+bar((v+2)/4*100)+']'; },110); },
    /* 5 frequency_penalty */ function(){ let v=0;
      return setInterval(function(){ v=cl(v+(Math.random()-.5)*.3,-2,2);
        el.textContent='frequency_penalty = '+(v>=0?'+':'')+v.toFixed(2)+'  ['+bar((v+2)/4*100)+']'; },110); },
    /* 6 seed */ function(){
      return setInterval(function(){ const s=ri(0,2147483647);
        el.textContent='seed = '+s+'  (0x'+hex(s%65536).padStart(4,'0')+')'; },140); },
    /* 7 min_p */ function(){ let p=.1;
      return setInterval(function(){ p=cl(p+(Math.random()-.5)*.05,0,.5);
        el.textContent='min_p = '+p.toFixed(3)+'  ['+bar(p/.5*100)+']'; },100); },
    /* 8 stop_sequences */ function(){
      const s=['</s>','\\\\n\\\\n','###','<|eot_id|>','```','<|im_end|>']; let i=0;
      return setInterval(function(){ i=(i+1)%s.length;
        el.textContent='stop_sequences: menguji "'+s[i]+'"'; },400); },
    /* 9 repetition_penalty */ function(){ let v=1.1;
      return setInterval(function(){ v=cl(v+(Math.random()-.5)*.06,1,1.5);
        el.textContent='repetition_penalty = '+v.toFixed(2)+'  ['+bar((v-1)/.5*100)+']'; },110); },
    /* 10 typical_p */ function(){ let p=.6;
      return setInterval(function(){ p=cl(p+(Math.random()-.5)*.09,.1,1);
        el.textContent='typical_p = '+p.toFixed(2)+'  ['+bar(p*100)+']'; },100); },
    /* 11 mirostat */ function(){ let tau=5,eta=.1;
      return setInterval(function(){ tau=cl(tau+(Math.random()-.5)*.6,2,8);
        eta=cl(eta+(Math.random()-.5)*.02,.05,.2);
        el.textContent='mirostat: \\u03C4='+tau.toFixed(1)+' \\u03B7='+eta.toFixed(2)+'  ['+bar(tau/8*100)+']'; },130); },
    /* 12 batch_size */ function(){ const b=[1,2,4,8,16,32,64,128,256]; let i=0;
      return setInterval(function(){ i=(i+1)%b.length;
        el.textContent='batch_size = '+b[i]+'  ['+bar((i+1)/b.length*100)+']'; },350); },
    /* 13 vram */ function(){ let p=ri(30,70);
      return setInterval(function(){ p=cl(p+ri(-6,8),5,98);
        el.textContent='vram ['+bar(p)+'] '+p+'% / 24GB'; },100); },
    /* 14 quantization */ function(){
      const q=['FP16','INT8','Q8_0','Q6_K','Q5_K_M','Q4_K_M']; let i=0;
      return setInterval(function(){ i=(i+1)%q.length;
        el.textContent='quantization: '+q[i]+(i===q.length-1?' \\u2713':' \\u2026'); },420); },
    /* 15 gpu_layers */ function(){ let g=0,M=80;
      return setInterval(function(){ g+=ri(1,4); if(g>M)g=0;
        el.textContent='gpu_layers: '+g+'/'+M+'  ['+bar(g/M*100)+']'; },110); },
    /* 16 tensor_parallel_size */ function(){ const t=[1,2,4,8]; let i=0;
      return setInterval(function(){ i=(i+1)%t.length; let gp='';
        for(let k=0;k<t[i];k++) gp+='GPU'+k+' ';
        el.textContent='tensor_parallel_size = '+t[i]+'  ['+gp.trim()+']'; },500); },
    /* 17 num_threads */ function(){ let n=16;
      return setInterval(function(){ n=cl(n+ri(-3,3),1,32);
        el.textContent='num_threads = '+n+'  ['+bar(n/32*100)+']'; },120); },
  ];

  let idx=0, timer=null;
  function scene(){
    if(timer) clearInterval(timer);
    timer = R[ORDER[idx]]();
    idx = (idx+1) % ORDER.length;   // habis 5 parameter -> ulang (loop)
  }
  scene();
  setInterval(scene, DUR);
})();
</script>"""


def _logo_tag() -> str:
    """<img> logo Trinity; jatuh ke ikon gerigi bila logo tidak tersedia."""
    if LOGO_B64:
        return ('<img src="data:image/png;base64,' + LOGO_B64
                + '" alt="logo Trinity"/>')
    return ('<span style="font-size:17px;line-height:26px;font-weight:bold;'
            'color:#2C1F33;display:block;text-align:center;">&#9881;</span>')


def param_loading_html(indices: list[int] | None = None,
                       durasi_ms: int = DURASI_PER_PARAM_MS) -> str:
    """HTML+JS animasi parameter. `indices` None = pilih acak sendiri."""
    if not indices:
        indices = pilih_parameter()
    return (_HTML
            .replace("__LOGO__", _logo_tag())
            .replace("__GLOW__", _rgb(WARNA_GLOW))     # ← BARIS BARU
            .replace("__ORDER__", json.dumps(indices))
            .replace("__DUR__", str(durasi_ms)))

# Loading khusus. Chat biasa tetap menggunakan animasi parameter di atas.
SPECIAL_LOADING = {
    "web": {
        "duration": 8,
        "phrases": (
            "Menelusuri web tentang {subject}",
            "Memverifikasi tentang {subject}",
        ),
    },
    "code": {
        "duration": 10,
        "phrases": (
            "Used bash",
            "Menjalankan mode coding",
            "Menjelajahi bahasa kode",
        ),
    },
    "card": {
        "duration": 10,
        "phrases": (
            "Membuat kartu {subject}",
            "Menimbang susunan yang tepat",
            "Menjalankan ulang",
        ),
    },
    "design": {
        "duration": 15,
        "phrases": (
            "Melukis",
            "Membayangkan",
            "Membuat sketsa",
            "Memoles",
            "Membuat hasil akhir",
        ),
    },
    "schedule": {
        "duration": 12,
        "phrases": (
            "Menyusun rencana Anda",
            "Memilih waktu yang tepat",
            "Menyesuaikan",
        ),
    },
    "file": {
        "duration": 15,
        "phrases": (
            "Menyusun teks",
            "Memilah kata",
            "Membaca ulang",
        ),
    },
}
_SPECIAL_PATTERNS = {
    "code": re.compile(
        r"\b(?:buat(?:kan)?|tulis|perbaiki|debug|refactor|coding|kode|program|"
        r"script|fungsi|class|api|html|css|javascript|python|sql|bash)\b",
        re.I,
    ),
    "card": re.compile(
        r"\b(?:kartu|bandingkan|perbandingan|langkah[- ]?demi[- ]?langkah|"
        r"tautan|link|peta|lokasi|itinerary|rencana perjalanan|terjemah)\b",
        re.I,
    ),
    "schedule": re.compile(
        r"\b(?:jadwal|agenda|kalender|rencana harian|pengingat|deadline|"
        r"pukul|jam\s+\d)\b",
        re.I,
    ),
    "file": re.compile(
        r"\b(?:buat(?:kan)?|susun|hasilkan)\b.{0,45}\b(?:file|dokumen|pdf|"
        r"docx|xlsx|csv|pptx|presentasi|laporan|surat)\b",
        re.I | re.S,
    ),
}
# ---------------------------------------------------------------------------
# IKON MODE. "web" memakai bentuk kaca pembesar asli (bukan globe) supaya
# sama persis dengan referensi demo — lingkaran lensa + tangkai diagonal.
# Semua ikon di bawah memakai currentColor, jadi warnanya ikut CSS
# `.special-icon { color: AKSEN_KHUSUS }` di special_loading_html().
# ---------------------------------------------------------------------------
_ICON_SVG = {
    "web": (
        '<circle cx="10" cy="10" r="6"/>'
        '<line x1="15" y1="15" x2="21" y2="21"/>'
    ),
    "code": (
        '<path d="m8 9-4 3 4 3'
        'M16 9l4 3-4 3M14 5l-4 14"/>'
    ),
    "card": (
        '<rect x="3" y="5" width="18" height="14" rx="2"/>'
        '<path d="M7 9h10M7 13h6"/>'
    ),
    "design": (
        '<path d="m14.5 4.5 5 5L9 20H4v-5L14.5 4.5Z"/>'
        '<path d="m12 7 5 5"/>'
    ),
    "schedule": (
        '<rect x="3" y="5" width="18" height="16" rx="2"/>'
        '<path d="M16 3v4M8 3v4M3 10h18"/>'
    ),
    "file": (
        '<path d="M6 2h8l4 4v16H6z"/>'
        '<path d="M14 2v5h5M9 13h6M9 17h6"/>'
    ),
}

def loading_subject(text: str) -> str:
    """Ringkas permintaan untuk frasa 'tentang X'."""
    clean = " ".join(
        str(text or "").split()
    )

    clean = re.sub(
        (
            r"^(?:tolong\s+)?"
            r"(?:buatkan|buat|cari|carikan|tampilkan|jelaskan|susun)\s+"
        ),
        "",
        clean,
        flags=re.I,
    )

    clean = clean.strip(
        " .,:;!?"
    )

    if len(clean) > 46:
        return (
            clean[:46].rstrip()
            + "…"
        )

    return (
        clean
        or "permintaan Anda"
    )

def detect_loading_mode(
    text: str,
    *,
    page: str = "chat",
    web_search: bool = False,
    image_mode: bool = False,
) -> str:
    """Pilih loading khusus; string kosong berarti loading chat biasa."""
    if web_search:
        return "web"

    if (
        image_mode
        or page == "desain"
        or page == "image"
    ):
        return "design"

    if (
        page == "jadwal"
        or _SPECIAL_PATTERNS[
            "schedule"
        ].search(text or "")
    ):
        return "schedule"

    if _SPECIAL_PATTERNS[
        "file"
    ].search(text or ""):
        return "file"

    if _SPECIAL_PATTERNS[
        "card"
    ].search(text or ""):
        return "card"

    if _SPECIAL_PATTERNS[
        "code"
    ].search(text or ""):
        return "code"

    return ""


def special_loading_duration(
    mode: str,
) -> float:
    return float(
        (
            SPECIAL_LOADING.get(mode)
            or {}
        ).get(
            "duration",
            0,
        )
    )

def special_loading_html(
    mode: str,
    subject: str = "",
) -> str:
    """Loading khusus — ikon & sapuan glow memakai warna aksen Trinity
    (AKSEN_KHUSUS / AKSEN_KHUSUS_LEMBUT), disamakan dengan demo animasi
    5-mode (web/file/design/code/card)."""
    config = SPECIAL_LOADING.get(
        mode
    )

    if not config:
        return param_loading_html()

    duration = float(
        config["duration"]
    )

    phrases = [
        phrase.format(
            subject=html.escape(
                subject
                or "permintaan Anda"
            )
        )
        for phrase in config[
            "phrases"
        ]
    ]

    count = max(
        1,
        len(phrases),
    )

    slot = (
        duration
        / count
    )

    active_end = max(
        8.0,
        (
            100.0
            / count
        )
        - 4.0,
    )

    # Mode "code": kursor berkedip ditempel di UJUNG teks (bukan di ikon),
    # supaya kelihatan seperti kursor yang sedang mengetik, bukan elemen
    # mengambang yang menutupi/berdempetan dengan teksnya.
    caret_html = (
        '<span class="type-caret"></span>' if mode == "code" else ""
    )

    spans = "".join(
        (
            '<span class="special-phrase" '
            f'style="animation-delay:'
            f'{index * slot:.3f}s">'
            f"{phrase}{caret_html}"
            "</span>"
        )
        for index, phrase
        in enumerate(phrases)
    )

    icon = _ICON_SVG.get(mode, _ICON_SVG["file"])
    aksen_rgb = _rgb(AKSEN_KHUSUS)

    # Titik-titik berdenyut (seperti demo "Mencari di web ...") — hanya
    # dirender untuk mode web, disembunyikan CSS-nya untuk mode lain.
    dots_html = (
        '<span class="special-dots"><span></span><span></span><span></span></span>'
        if mode == "web" else ""
    )

    return f"""
<style>
/* Sapuan glow sama dengan loader parameter biasa: gradient di-clip ke teks.
   Puncaknya sekarang pakai AKSEN_KHUSUS (ungu Trinity), bukan putih polos. */
@keyframes specialGlowSweep {{
  0% {{ background-position:130% 0; }}
  100% {{ background-position:-30% 0; }}
}}
/* Gerak per mode — karakter animasi tiap ikon beda, warnanya seragam
   memakai currentColor (diatur lewat .special-icon di bawah). */
@keyframes specialWebSweep {{
  0%,100% {{ transform:translateX(-1.5px) rotate(-2deg); }}
  50% {{ transform:translateX(1.5px) rotate(2deg); }}
}}
@keyframes specialLineIn {{
  0% {{ opacity:.18; stroke-dashoffset:18; }}
  30%,72% {{ opacity:1; stroke-dashoffset:0; }}
  100% {{ opacity:.18; stroke-dashoffset:-18; }}
}}
@keyframes specialBlurFocus {{
  0%,100% {{ filter:blur(2.2px); opacity:.48; }}
  50% {{ filter:blur(0); opacity:1; }}
}}
@keyframes specialCaret {{
  0%,45% {{ opacity:1; }}
  46%,100% {{ opacity:0; }}
}}
@keyframes specialCardPulse {{
  0%,100% {{ opacity:.38; transform:scale(.95); }}
  50% {{ opacity:1; transform:scale(1); }}
}}
@keyframes specialCalendarTick {{
  0%,100% {{ stroke-dashoffset:16; opacity:.3; }}
  45%,72% {{ stroke-dashoffset:0; opacity:1; }}
}}
@keyframes specialDotPulse {{
  0%,60%,100% {{ opacity:.25; transform:scale(.8); }}
  30% {{ opacity:1; transform:scale(1); }}
}}
@keyframes specialPhraseCycle {{
    0% {{
        opacity: 0;
        filter: blur(4px);
    }}

    4% {{
        opacity: 1;
        filter: blur(0);
    }}

    {active_end:.2f}% {{
        opacity: 1;
        filter: blur(0);
    }}

    {min(active_end + 4.0, 99.0):.2f}% {{
        opacity: 0;
        filter: blur(4px);
    }}

    100% {{
        opacity: 0;
    }}
}}

.special-loader {{
  display:flex; align-items:center; justify-content:flex-start;
  min-height:50px; padding:7px 0; color:#6B6172;
  font:500 12.5px/1.35 Inter,ui-sans-serif,system-ui,sans-serif;
}}
.special-row {{
  position:relative; display:flex; align-items:center; gap:8px;
  overflow:hidden;
}}
.special-icon {{
  position:relative; width:19px; height:19px; flex:0 0 19px;
  color:{AKSEN_KHUSUS}; transform-origin:center; will-change:transform,filter,opacity;
}}
.special-icon svg {{ width:100%; height:100%; display:block; fill:none; stroke:currentColor;
  stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}
.special-loader.mode-web .special-icon {{ animation:specialWebSweep 1.4s ease-in-out infinite; }}
.special-loader.mode-file .special-icon svg path:last-child {{
  stroke-dasharray:18; animation:specialLineIn 1.8s ease-in-out infinite;
}}
.special-loader.mode-design .special-icon {{ animation:specialBlurFocus 2s ease-in-out infinite; }}
.special-loader.mode-code .special-icon::after {{
  content:""; position:absolute; right:-3px; top:2px; width:1.5px; height:15px;
  border-radius:2px; background:{AKSEN_KHUSUS};
  animation:specialCaret .8s step-end infinite;
}}
.special-loader.mode-card .special-icon {{ animation:specialCardPulse 1.4s ease-in-out infinite; }}
.special-loader.mode-schedule .special-icon svg path:last-child {{
  stroke-dasharray:16; animation:specialCalendarTick 1.8s ease-in-out infinite;
}}
.special-dots {{ display:none; align-items:center; margin-left:2px; }}
.special-loader.mode-web .special-dots {{ display:inline-flex; }}
.special-dots span {{
  width:4px; height:4px; border-radius:50%;
  background:{AKSEN_KHUSUS_LEMBUT}; margin-right:3px;
  animation:specialDotPulse 1.2s ease-in-out infinite;
}}
.special-dots span:nth-child(2) {{ animation-delay:.15s; }}
.special-dots span:nth-child(3) {{ animation-delay:.3s; }}
.special-phrases {{ position:relative; display:block; width:min(72vw,520px); height:18px; 
}}

.special-phrase {{
  position:absolute; inset:0 auto auto 0; opacity:0; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; max-width:100%;
  background:linear-gradient(
    100deg,
    #6B6172 0%, #6B6172 38%,
    rgba({aksen_rgb},1) 50%,
    #6B6172 62%, #6B6172 100%
  );
  background-size:220% 100%;
  -webkit-background-clip:text;
  background-clip:text;
  -webkit-text-fill-color:transparent;
  color:transparent;
  animation:
    specialPhraseCycle {duration:.3f}s ease infinite,
    specialGlowSweep 2.4s linear infinite;
}}

@media (prefers-reduced-motion:reduce) {{
  .special-icon,
  .special-icon svg path,
  .special-icon::after,
  .special-dots span {{
    animation: none !important;
    transform: none !important;
    filter: none !important;
    opacity: .6 !important;
  }}

  .special-phrase {{
    animation: none !important;
    opacity: 0;
    background: none;
    -webkit-text-fill-color: #6B6172;
    color: #6B6172;
  }}

  .special-phrase:first-child {{
    opacity: 1;
  }}
}}
</style>

<div class="special-loader mode-{mode}">
    <div class="special-row">
        <span class="special-icon">
            <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
            >
                {icon}
            </svg>
        </span>

        <span class="special-phrases">
            {spans}
        </span>

        {dots_html}
    </div>
</div>
""".strip()
