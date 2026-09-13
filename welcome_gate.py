# -*- coding: utf-8 -*-
"""
Gerbang pembuka aplikasi (dipisah dari app.py supaya mudah dirawat):

1. SPLASH — animasi pembuka elegan:
   - partikel logo Trinity MENYEBAR lalu BERGABUNG membentuk logo utuh
   - logo BERPUTAR (putar 3D sekali penuh)
   - efek GLOW berjalan dari kiri ke kanan menyapu logo
   - muncul tulisan "Trinity Ai", lalu "By Ampera Official" di bawahnya
   - jeda ±5 detik dengan animasi kecil: kabel steker yang dicolokkan
     ke stop kontak (menyalakan "daya") — lalu masuk ke halaman login.

2. LOGIN — halaman masuk dengan akun Google (logo + judul app tampil).
   Tombol Google sudah disiapkan; alur OAuth betulan menyusul setelah
   pemilik mendaftarkan aplikasi ke Google Cloud Console. Selama belum
   didaftarkan, tersedia tombol "Lanjut tanpa masuk (sementara)" supaya
   aplikasi tetap bisa dipakai/diuji.

Dipanggil dari app.py, di dalam main(), TEPAT DI ATAS render_sidebar():

    from welcome_gate import tampilkan_gerbang
    if tampilkan_gerbang():
        st.stop()

Tahapan disimpan di st.session_state["_tahap"]:
  "splash" -> "login" -> "app"  (sekali per sesi; tombol "Keluar" di
  sidebar menghapus semua session state, jadi otomatis kembali ke splash).
"""

from __future__ import annotations

import base64
import os
import time
import urllib.parse

import streamlit as st
import streamlit.components.v1 as components

# Durasi total animasi splash (detik). Garis waktu di dalam animasi
# berakhir ±14,65 detik; sisanya jeda aman sebelum halaman login muncul.
SPLASH_TOTAL_DETIK = 15.5


# ---------------------------------------------------------------------------
# LOGO
# ---------------------------------------------------------------------------
def _logo_data_url() -> str:
    """Logo Trinity sebagai data URL (PNG base64).

    Sumber utama: assets/logo_thinking_small.png lewat trinity_logo.py;
    cadangan: base64 tertanam di logo.py; cadangan terakhir: emoji 🔱.
    """
    b64 = ""
    try:
        from trinity_logo import LOGO_B64 as _b64_aset
        b64 = _b64_aset or ""
    except Exception:
        b64 = ""
    if not b64:
        try:
            from logo import LOGO_B64 as _b64_tanam
            b64 = _b64_tanam or ""
        except Exception:
            b64 = ""
    if b64:
        return "data:image/png;base64," + b64
    return (
        "data:image/svg+xml;utf8,"
        + urllib.parse.quote(
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
            "<text x='50' y='54' font-size='72' text-anchor='middle' "
            "dominant-baseline='middle'>🔱</text></svg>"
        )
    )


# ---------------------------------------------------------------------------
# SPLASH — layar penuh + animasi partikel
# ---------------------------------------------------------------------------
_CSS_LAYAR_PENUH = """<style>
  header[data-testid="stHeader"], #MainMenu, footer,
  section[data-testid="stSidebar"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"],
  [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] { display:none !important; }
  html, body, .stApp { background:#070504 !important; }
  /* Jadikan iframe animasi splash = LAYAR PENUH */
  .stApp iframe, .stCustomComponentContainer iframe,
  .element-container iframe {
    position:fixed !important; inset:0 !important;
    width:100vw !important; height:100vh !important;
    border:0 !important; z-index:99999 !important;
    background:#070504 !important;
  }
</style>"""


_HTML_SPLASH = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@700&family=Manrope:wght@500;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden}
body{background:radial-gradient(120vmax 90vmax at 50% 36%, #1E1610 0%, #120D09 46%, #070504 100%)}
#root{position:fixed;inset:0;font-family:'Manrope',system-ui,sans-serif}
#cv{position:fixed;inset:0;z-index:1;pointer-events:none}
#aura{position:fixed;z-index:0;pointer-events:none;opacity:0;border-radius:50%;
  background:radial-gradient(closest-side, rgba(238,217,182,.20), rgba(238,217,182,.06) 55%, transparent 78%)}
#panggung{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding-bottom:7vh;pointer-events:none}
#logoWrap{position:relative;width:min(34vmin,300px);height:min(34vmin,300px)}
#logoImg{display:block;width:100%;height:100%;object-fit:contain;opacity:0;
  filter:drop-shadow(0 10px 34px rgba(0,0,0,.55))}
#glowWrap{position:absolute;inset:0;overflow:hidden;
  -webkit-mask-image:url("__LOGO__");mask-image:url("__LOGO__");
  -webkit-mask-size:100% 100%;mask-size:100% 100%}
#glowBand{position:absolute;top:-12%;height:124%;width:40%;left:0;opacity:0;
  background:linear-gradient(100deg, rgba(255,233,199,0) 0%, rgba(255,233,199,.75) 42%,
    rgba(255,248,228,1) 50%, rgba(255,233,199,.75) 58%, rgba(255,233,199,0) 100%);
  filter:blur(1px)}
#judul{margin-top:5.5vmin;opacity:0;
  font-family:'Cormorant Garamond',Georgia,serif;font-weight:700;
  font-size:clamp(2.2rem,8.5vmin,3.8rem);letter-spacing:.13em;
  background:linear-gradient(93deg,#F8EFDF 10%,#E9C891 55%,#C0955E 92%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
#sub{margin-top:1.6vmin;opacity:0;font-weight:500;
  font-size:clamp(.78rem,2.7vmin,1.02rem);letter-spacing:.34em;color:#A8977E}
#colokWrap{margin-top:5vmin;opacity:0;width:clamp(150px,26vmin,225px)}
#colokWrap svg{width:100%;height:auto;display:block}
</style>
</head>
<body>
<div id="root">
  <div id="aura"></div>
  <div id="panggung">
    <div id="logoWrap">
      <img id="logoImg" src="__LOGO__" alt="Logo Trinity"/>
      <div id="glowWrap"><div id="glowBand"></div></div>
    </div>
    <h1 id="judul">Trinity Ai</h1>
    <div id="sub">By Ampera Official</div>
    <div id="colokWrap">
      <svg id="svgColok" viewBox="0 0 260 150" xmlns="http://www.w3.org/2000/svg">
        <!-- kabel (jalur digambar ulang tiap frame oleh JS) -->
        <path id="kabel" d="" fill="none" stroke="#6E5B45" stroke-width="5"
              stroke-linecap="round"/>
        <!-- stop kontak -->
        <g id="kontak">
          <rect x="178" y="34" width="56" height="88" rx="14"
                fill="#1E1712" stroke="#3E2F22" stroke-width="2"/>
          <rect x="186" y="42" width="40" height="72" rx="10" fill="#241B14"/>
          <circle cx="206" cy="63" r="4.6" fill="#0A0705"
                  stroke="#55432F" stroke-width="1.5"/>
          <circle cx="206" cy="89" r="4.6" fill="#0A0705"
                  stroke="#55432F" stroke-width="1.5"/>
          <circle id="ledHalo" cx="206" cy="47" r="9" fill="#7BE495" opacity="0"/>
          <circle id="led" cx="206" cy="47" r="3.2" fill="#4A3A2B"/>
        </g>
        <!-- steker (digeser oleh JS) -->
        <g id="steker">
          <rect x="-36" y="-15" width="40" height="56" rx="11"
                fill="#E8DCC8" stroke="#C9B896" stroke-width="2"/>
          <rect x="-31" y="4" width="10" height="18" rx="4" fill="#D7C9AF"/>
          <rect x="0" y="-2.4" width="30" height="4.8" rx="2.4" fill="#CDBFA5"/>
          <rect x="0" y="23.6" width="30" height="4.8" rx="2.4" fill="#CDBFA5"/>
        </g>
        <!-- percikan saat mencolok -->
        <g id="percik" opacity="0">
          <circle class="pk" cx="206" cy="63" r="2"   fill="#FFE9BE"/>
          <circle class="pk" cx="206" cy="63" r="1.5" fill="#FFD98F"/>
          <circle class="pk" cx="206" cy="89" r="2"   fill="#FFE9BE"/>
          <circle class="pk" cx="206" cy="89" r="1.5" fill="#FFD98F"/>
          <circle class="pk" cx="206" cy="76" r="1.8" fill="#FFF4DC"/>
        </g>
      </svg>
    </div>
  </div>
  <canvas id="cv"></canvas>
</div>
<script>
(function(){
  var cv=document.getElementById('cv'), ctx=cv.getContext('2d');
  var root=document.getElementById('root');
  var logoImg=document.getElementById('logoImg');
  var logoWrap=document.getElementById('logoWrap');
  var glowWrap=document.getElementById('glowWrap');
  var glowBand=document.getElementById('glowBand');
  var aura=document.getElementById('aura');
  var judul=document.getElementById('judul');
  var sub=document.getElementById('sub');
  var colokWrap=document.getElementById('colokWrap');
  var steker=document.getElementById('steker');
  var kabel=document.getElementById('kabel');
  var led=document.getElementById('led');
  var ledHalo=document.getElementById('ledHalo');
  var percik=document.getElementById('percik');
  var pks=[].slice.call(document.querySelectorAll('.pk'));
  var imgOk=true;

  // ---- garis waktu (ms). Total ±14.650 dtk; Python menunggu 15,5 dtk ---
  var KONVERGEN=3600, SPIN=2000, GLOW=1700, JUDUL=800, SUB=800,
      COLOK=5000, FADE=450;
  var T_IMG=KONVERGEN, T_SPIN=T_IMG+300, T_GLOW=T_SPIN+SPIN,
      T_JUDUL=T_GLOW+GLOW, T_SUB=T_JUDUL+JUDUL, T_COLOK=T_SUB+SUB,
      T_END=T_COLOK+COLOK;

  // ---- geometri colokan ------------------------------------------------
  var PLUG_X0=20, PLUG_X1=179, PLUG_Y=63, CONNECT=1400;
  var nyala=false, tColok=0;
  var PK_DIR=[[-1,-0.7],[1,0.8],[-1,0.6],[1,-0.8],[0.3,-1]];
  var PK_BASE=[];

  var W=0,H=0,DPR=1, logoRect={x:0,y:0,w:0,h:0};
  var pts=[], dust=[];

  function clamp01(v){return v<0?0:(v>1?1:v);}
  function easeInOutCubic(p){return p<0.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;}
  function easeOutCubic(p){return 1-Math.pow(1-p,3);}
  function easeOutBack(p){var c=1.7;return 1+(c+1)*Math.pow(p-1,3)+c*Math.pow(p-1,2);}

  function ukur(){
    W=window.innerWidth; H=window.innerHeight;
    DPR=Math.min(2, window.devicePixelRatio||1);
    cv.width=W*DPR; cv.height=H*DPR;
    cv.style.width=W+'px'; cv.style.height=H+'px';
    ctx.setTransform(DPR,0,0,DPR,0,0);
    var r=logoImg.getBoundingClientRect();
    logoRect={x:r.left,y:r.top,w:r.width,h:r.height};
    var s=Math.max(logoRect.w,logoRect.h)*1.8;
    aura.style.left=(logoRect.x+logoRect.w/2-s/2)+'px';
    aura.style.top=(logoRect.y+logoRect.h/2-s/2)+'px';
    aura.style.width=s+'px'; aura.style.height=s+'px';
  }

  // Partikel = piksel-piksel logo. Setiap partikel muncul dari titik acak
  // (menyebar), lalu terbang menuju posisi aslinya di logo (bergabung).
  function siapkanPartikel(){
    var S=300, off=document.createElement('canvas');
    off.width=S; off.height=S;
    var o=off.getContext('2d');
    var data=null;
    if(imgOk){
      try{ o.drawImage(logoImg,0,0,S,S); }catch(e){}
      try{ data=o.getImageData(0,0,S,S).data; }catch(e){ data=null; }
    }
    if(!data){
      o.clearRect(0,0,S,S);
      o.font='240px serif'; o.textAlign='center'; o.textBaseline='middle';
      o.fillStyle='#E8DCC8';
      try{ o.fillText('\\u2693', S/2, S/2); }catch(e){}
      try{ data=o.getImageData(0,0,S,S).data; }catch(e){ data=null; }
    }
    pts=[]; dust=[];
    if(!data) return;
    var step=4;
    for(var y=0;y<S;y+=step){
      for(var x=0;x<S;x+=step){
        var i=(y*S+x)*4;
        if(data[i+3]<120) continue;
        if(Math.random()<0.16) continue;
        // warna logo dicerahkan sedikit ke emas supaya hidup di latar gelap
        var r=Math.min(255, data[i]  *0.72+255*0.28)|0;
        var g=Math.min(255, data[i+1]*0.72+240*0.28)|0;
        var b=Math.min(255, data[i+2]*0.72+205*0.28)|0;
        pts.push({fx:x/S, fy:y/S, r:r, g:g, b:b,
          sx:Math.random()*W, sy:Math.random()*H,
          d:Math.random()*500, rad:1.2+Math.random()*1.4,
          ph:Math.random()*Math.PI*2});
      }
    }
    for(var k=0;k<42;k++){
      dust.push({x:Math.random()*W, y:Math.random()*H,
        r:0.6+Math.random()*1.1, sp:0.25+Math.random()*0.6,
        ph:Math.random()*Math.PI*2});
    }
    for(var m=0;m<pks.length;m++){
      PK_BASE.push([parseFloat(pks[m].getAttribute('cx')),
                    parseFloat(pks[m].getAttribute('cy'))]);
    }
  }

  function gambarDebu(t){
    ctx.globalCompositeOperation='source-over';
    for(var k=0;k<dust.length;k++){
      var m=dust[k];
      var y=m.y - t*0.007*m.sp; y=((y%H)+H)%H;
      var x=m.x + Math.sin(t/1400+m.ph)*10;
      var a=0.08+0.10*(0.5+0.5*Math.sin(t/650+m.ph));
      ctx.fillStyle='rgba(216,199,168,'+a.toFixed(3)+')';
      ctx.beginPath(); ctx.arc(x,y,m.r,0,6.2832); ctx.fill();
    }
  }

  function gambarPartikel(t){
    var pFade=imgOk?1-clamp01((t-T_IMG)/300):1;
    if(pFade<=0) return;
    ctx.globalCompositeOperation='lighter';
    for(var k=0;k<pts.length;k++){
      var p=pts[k];
      var lt=t-p.d;
      if(lt<0) continue;
      var pr=Math.min(1, lt/3000);
      var e=easeInOutCubic(pr);
      var tx=logoRect.x+p.fx*logoRect.w;
      var ty=logoRect.y+p.fy*logoRect.h;
      var wob=Math.sin(lt/230+p.ph)*(1-e)*16;
      var x=p.sx+(tx-p.sx)*e+wob*Math.cos(p.ph);
      var y=p.sy+(ty-p.sy)*e+wob*Math.sin(p.ph);
      var a=Math.min(1,lt/280)*(0.5+0.5*e)*pFade;
      ctx.fillStyle='rgba('+p.r+','+p.g+','+p.b+','+a.toFixed(3)+')';
      ctx.beginPath(); ctx.arc(x,y,p.rad,0,6.2832); ctx.fill();
    }
  }

  function kabelD(px,py,t){
    var sway=Math.sin(t/850)*3;
    var tx=px-36, ty=py+13;
    return 'M -30 148 C '+(px*0.35).toFixed(1)+' '+(152+sway).toFixed(1)+', '
      +(tx-26).toFixed(1)+' '+(ty+46+sway).toFixed(1)+', '
      +tx.toFixed(1)+' '+ty.toFixed(1);
  }

  function driveColok(t){
    var lt=t-T_COLOK;
    colokWrap.style.opacity=clamp01(lt/400).toFixed(3);
    if(lt<0){
      steker.setAttribute('transform','translate('+PLUG_X0+','+PLUG_Y+')');
      kabel.setAttribute('d', kabelD(PLUG_X0,PLUG_Y,t));
      return;
    }
    var p=clamp01(lt/CONNECT);
    var e=easeOutBack(p);
    var wob=Math.sin(p*24)*(1-p)*5;
    var px=PLUG_X0+(PLUG_X1-PLUG_X0)*e;
    var py=PLUG_Y+wob;
    steker.setAttribute('transform','translate('+px.toFixed(1)+','+py.toFixed(1)+')');
    kabel.setAttribute('d', kabelD(px,py,t));
    if(p>=1){
      if(!nyala){ nyala=true; tColok=t; led.setAttribute('fill','#7BE495'); }
      var pul=0.5+0.5*Math.abs(Math.sin((t-tColok)/520));
      ledHalo.setAttribute('opacity',(0.25+0.6*pul).toFixed(2));
      var sp=clamp01((t-tColok)/420);
      if(sp<1){
        percik.setAttribute('opacity',(1-sp).toFixed(2));
        for(var k=0;k<pks.length;k++){
          var d=PK_DIR[k%PK_DIR.length];
          pks[k].setAttribute('cx',(PK_BASE[k][0]+d[0]*sp*15).toFixed(1));
          pks[k].setAttribute('cy',(PK_BASE[k][1]+d[1]*sp*11).toFixed(1));
        }
      } else { percik.setAttribute('opacity','0'); }
    }
  }

  function setFade(el,t,start,dur,dy){
    var p=clamp01((t-start)/dur);
    if(p<=0){ el.style.opacity='0'; return; }
    var e=easeOutCubic(p);
    el.style.opacity=e.toFixed(3);
    el.style.transform='translateY('+((1-e)*dy).toFixed(1)+'px)';
  }

  var t0=0;
  function frame(now){
    if(!t0) t0=now;
    var t=now-t0;
    ctx.clearRect(0,0,W,H);
    gambarDebu(t);
    gambarPartikel(t);

    // partikel menyatu jadi gambar logo utuh
    var cf=imgOk?clamp01((t-T_IMG)/300):0;
    logoImg.style.opacity=cf.toFixed(3);

    // logo berputar (sekali penuh), lalu mengambang halus
    if(imgOk && t>=T_SPIN && t<T_SPIN+SPIN){
      var sp=easeInOutCubic((t-T_SPIN)/SPIN);
      logoWrap.style.transform='perspective(900px) rotateY('+(360*sp).toFixed(1)+'deg)';
    } else if(t>=T_SPIN+SPIN){
      logoWrap.style.transform='translateY('+(Math.sin(t/1100)*3.5).toFixed(1)+'px)';
    }

    // sapuan glow dari kiri ke kanan, hanya pada bentuk logo (mask)
    var gp=clamp01((t-T_GLOW)/GLOW);
    if(imgOk && gp>0 && gp<1){
      var ge=easeInOutCubic(gp);
      var wrapW=glowWrap.clientWidth, bandW=glowBand.offsetWidth||100;
      var x=-bandW*1.1+(wrapW+bandW*2.2)*ge;
      glowBand.style.transform='translateX('+x.toFixed(1)+'px) skewX(-14deg)';
      glowBand.style.opacity='0.95';
    } else { glowBand.style.opacity='0'; }

    // aura lembut di belakang logo (menguat setelah glow; "menyala" saat
    // steker dicolokkan)
    var ab=0.16+0.34*gp;
    if(nyala){ ab+=0.30*(1-clamp01((t-tColok)/700)); }
    aura.style.opacity=(ab*(0.92+0.08*Math.sin(t/900))).toFixed(3);

    // tulisan
    setFade(judul,t,T_JUDUL,JUDUL,20);
    setFade(sub,t,T_SUB,SUB,12);

    // animasi colokan
    driveColok(t);

    // redup di akhir, lalu halaman login dimuat oleh Python
    root.style.opacity=(t>T_END)?(1-clamp01((t-T_END)/FADE)).toFixed(3):'1';
    requestAnimationFrame(frame);
  }

  function mulai(){
    ukur(); siapkanPartikel();
    steker.setAttribute('transform','translate('+PLUG_X0+','+PLUG_Y+')');
    kabel.setAttribute('d', kabelD(PLUG_X0,PLUG_Y,0));
    requestAnimationFrame(frame);
  }
  window.addEventListener('resize', ukur);
  if(logoImg.complete && logoImg.naturalWidth>0){ mulai(); }
  else{
    logoImg.onload=function(){ mulai(); };
    logoImg.onerror=function(){ imgOk=false; mulai(); };
  }
})();
</script>
</body>
</html>"""


def _bangun_html_splash(logo_url: str) -> str:
    """Rakit HTML splash dengan logo tertanam (img + mask glow)."""
    return _HTML_SPLASH.replace("__LOGO__", logo_url)


def render_splash() -> None:
    """Tampilkan animasi splash layar penuh lalu lanjut ke halaman login."""
    st.markdown(_CSS_LAYAR_PENUH, unsafe_allow_html=True)
    components.html(_bangun_html_splash(_logo_data_url()),
                    height=200, scrolling=False)
    # Animasi berjalan di browser (iframe). Script ini menunggu sesuai
    # durasi totalnya, lalu pindah ke tahap login. (Kunci "_splash_cepat"
    # hanya untuk pengujian otomatis.)
    durasi = 0.3 if st.session_state.get("_splash_cepat") else SPLASH_TOTAL_DETIK
    time.sleep(durasi)
    st.session_state["_tahap"] = "login"
    st.rerun()


# ---------------------------------------------------------------------------
# LOGIN — halaman masuk dengan akun Google
# ---------------------------------------------------------------------------
_G_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
    '<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85'
    'C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19'
    'C12.43 13.72 17.74 9.5 24 9.5z"/>'
    '<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02'
    'h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36'
    ' 7.09-17.65z"/>'
    '<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59'
    's.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54'
    ' 2.56 10.78l7.97-6.19z"/>'
    '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6'
    'c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98'
    ' 6.19C6.51 42.62 14.62 48 24 48z"/>'
    '</svg>'
)
_G_ICON = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(_G_SVG.encode("utf-8")).decode("ascii")
)

_CSS_LOGIN = """<style>
  header[data-testid="stHeader"], #MainMenu, footer,
  section[data-testid="stSidebar"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"],
  [data-testid="stToolbar"], [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] { display:none !important; }
  .stApp { background:
      radial-gradient(1100px 700px at 50% 26%, #20170F 0%, #120D09 48%, #070504 100%)
      !important; }
  .block-container { max-width: 620px !important;
      padding-top: 12vh !important; padding-bottom: 8vh !important; }
  .login-wrap { text-align: center; animation: gerbangMuncul .8s ease both; }
  @keyframes gerbangMuncul {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:none; } }
  .login-logo-ring { width:96px; height:96px; margin:0 auto 18px;
     border-radius:50%; display:flex; align-items:center; justify-content:center;
     background:radial-gradient(closest-side, rgba(238,217,182,.14), transparent 75%);
     box-shadow:0 0 0 1px rgba(232,220,200,.22), 0 12px 44px rgba(0,0,0,.5); }
  .login-logo-ring img { width:64px; height:64px; object-fit:contain; }
  .login-judul { font-family:'Cormorant Garamond',Georgia,serif;
     font-weight:700; font-size:2.7rem; letter-spacing:.12em; margin:0;
     background:linear-gradient(93deg,#F8EFDF 10%,#E9C891 55%,#C0955E 92%);
     -webkit-background-clip:text; background-clip:text; color:transparent; }
  .login-sub { margin-top:6px; font-size:.92rem; letter-spacing:.34em;
     color:#A8977E; }
  .login-garis { width:150px; height:1px; margin:22px auto 14px;
     background:linear-gradient(90deg,transparent,rgba(232,200,150,.55),transparent); }
  .login-ajakan { font-size:.82rem; color:#8A7B67; letter-spacing:.06em; }
  .login-led { display:inline-block; width:7px; height:7px; border-radius:50%;
     background:#7BE495; margin-right:8px; vertical-align:middle;
     box-shadow:0 0 10px rgba(123,228,149,.8);
     animation: ledDenyut 1.6s ease-in-out infinite; }
  @keyframes ledDenyut { 0%,100%{opacity:.45;} 50%{opacity:1;} }
  .login-note { margin-top:14px; font-size:.78rem; color:#8A7B67;
     line-height:1.6; background:rgba(232,220,200,.05);
     border:1px solid rgba(232,220,200,.12); border-radius:12px;
     padding:10px 14px; }
  .st-key-btn_google_masuk button, button.st-key-btn_google_masuk {
     background:#FFFFFF !important; color:#1F1F1F !important;
     border:0 !important; border-radius:999px !important;
     font-weight:600 !important; padding:.6rem 1.5rem !important;
     box-shadow:0 10px 30px rgba(0,0,0,.45) !important;
     transition:transform .15s ease, box-shadow .15s ease !important; }
  .st-key-btn_google_masuk button:hover, button.st-key-btn_google_masuk:hover {
     transform:translateY(-1px);
     box-shadow:0 14px 36px rgba(0,0,0,.55) !important; }
  .st-key-btn_google_masuk button::before,
  button.st-key-btn_google_masuk::before {
     content:""; display:inline-block; width:20px; height:20px;
     margin-right:10px; vertical-align:middle;
     background:url("__GICON__") center/contain no-repeat; }
  .st-key-btn_tamu button, button.st-key-btn_tamu {
     background:transparent !important; color:#CDBFA9 !important;
     border:1px solid rgba(232,220,200,.25) !important;
     border-radius:999px !important; font-weight:500 !important;
     padding:.45rem 1.2rem !important; }
  .st-key-btn_tamu button:hover, button.st-key-btn_tamu:hover {
     border-color:rgba(232,220,200,.5) !important;
     color:#EFE4CE !important; }
</style>"""


def _google_terkonfigurasi() -> bool:
    """True bila pemilik sudah menaruh GOOGLE_CLIENT_ID (secrets/env)."""
    try:
        if st.secrets.get("GOOGLE_CLIENT_ID"):
            return True
    except Exception:
        pass
    return bool(os.environ.get("GOOGLE_CLIENT_ID"))


def _klik_google() -> None:
    if _google_terkonfigurasi():
        # TODO(pemilik): alur OAuth Google ditambahkan setelah aplikasi
        # didaftarkan ke Google Cloud Console (client id + secret).
        st.info(
            "Konfigurasi Google terdeteksi — alur masuk OAuth "
            "akan diaktifkan pada tahap berikutnya."
        )
    else:
        st.toast(
            "Login Google belum dikonfigurasi: pemilik belum mendaftarkan "
            "aplikasi ke Google Cloud Console.",
            icon="🔐",
        )


def _render_login() -> None:
    """Halaman login: logo + judul app + tombol Masuk dengan Google."""
    st.markdown(
        _CSS_LOGIN.replace("__GICON__", _G_ICON),
        unsafe_allow_html=True,
    )
    logo = _logo_data_url()
    st.markdown(
        '<div class="login-wrap">'
        f'<div class="login-logo-ring"><img src="{logo}" alt="Logo Trinity"/></div>'
        '<h1 class="login-judul">Trinity Ai</h1>'
        '<div class="login-sub">By Ampera Official</div>'
        '<div class="login-garis"></div>'
        '<div class="login-ajakan"><span class="login-led"></span>'
        "Masuk untuk melanjutkan</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    _kiri, _tengah, _kanan = st.columns([1, 1.15, 1])
    with _tengah:
        if st.button("Masuk dengan Google", key="btn_google_masuk"):
            _klik_google()

        if not _google_terkonfigurasi():
            st.markdown(
                '<div class="login-note">🔐 Login Google akan aktif otomatis '
                "setelah pemilik mendaftarkan aplikasi ke "
                "<b>Google Cloud Console</b>. Sementara itu, gunakan tombol "
                "di bawah untuk masuk.</div>",
                unsafe_allow_html=True,
            )
            if st.button("Lanjut tanpa masuk (sementara)", key="btn_tamu"):
                st.session_state["_tahap"] = "app"
                st.rerun()


# ---------------------------------------------------------------------------
# GERBANG — dipanggil app.py
# ---------------------------------------------------------------------------
def tampilkan_gerbang() -> bool:
    """Tampilkan splash/login bila sesi belum masuk aplikasi.

    Return True berarti app.py harus st.stop() (gerbang masih menguasai
    layar). Return False bila pengguna sudah masuk -> aplikasi jalan normal.
    """
    tahap = st.session_state.get("_tahap") or "splash"
    if tahap == "app":
        return False
    if tahap == "splash":
        render_splash()
        return True
    _render_login()
    return True
