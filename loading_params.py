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

import json
import random

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
  0%   { transform: scale(1)    rotate(0deg);
         filter: drop-shadow(0 0 4px rgba(124,58,237,.55))
                 drop-shadow(0 0 10px rgba(124,58,237,.30)); }
  12%  { transform: scale(1.22) rotate(0deg);
         filter: drop-shadow(0 0 6px rgba(155,92,255,.95))
                 drop-shadow(0 0 16px rgba(124,58,237,.60)); }
  24%  { transform: scale(1)    rotate(0deg);
         filter: drop-shadow(0 0 4px rgba(124,58,237,.55))
                 drop-shadow(0 0 10px rgba(124,58,237,.30)); }
  36%  { transform: scale(1.22) rotate(0deg);
         filter: drop-shadow(0 0 6px rgba(155,92,255,.95))
                 drop-shadow(0 0 16px rgba(124,58,237,.60)); }
  48%  { transform: scale(1)    rotate(0deg);
         filter: drop-shadow(0 0 5px rgba(155,92,255,.70))
                 drop-shadow(0 0 12px rgba(124,58,237,.40)); }
  60%  { transform: scale(1.15) rotate(180deg);
         filter: drop-shadow(0 0 6px rgba(255,255,255,.90))
                 drop-shadow(0 0 14px rgba(155,92,255,1))
                 drop-shadow(0 0 30px rgba(124,58,237,.85)); }
  72%  { transform: scale(1)    rotate(360deg);
         filter: drop-shadow(0 0 5px rgba(155,92,255,.70))
                 drop-shadow(0 0 12px rgba(124,58,237,.40)); }
  86%  { transform: scale(1.08) rotate(360deg);
         filter: drop-shadow(0 0 6px rgba(155,92,255,.80))
                 drop-shadow(0 0 14px rgba(124,58,237,.45)); }
  100% { transform: scale(1)    rotate(360deg);
         filter: drop-shadow(0 0 4px rgba(124,58,237,.55))
                 drop-shadow(0 0 10px rgba(124,58,237,.30)); }
}
.param-logo {
  display: inline-block;
  width: 26px; height: 26px;
  flex-shrink: 0;
  animation: trinitySpin 5s cubic-bezier(.45,.05,.35,1) infinite;
  will-change: transform, filter;
}
.param-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
.param-line { transition: opacity .25s ease; }
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
            .replace("__ORDER__", json.dumps(indices))
            .replace("__DUR__", str(durasi_ms)))
