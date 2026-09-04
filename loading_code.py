import streamlit as st

def inject_code_loading_css() -> None:
    pass

def code_loading_html(nama_file: str = "", done: bool = False, mode: str = "code") -> str:
    if done:
        return ""

    # Menentukan interval berdasarkan mode:
    # "code" = 7000ms (7 detik per adegan)
    # "biasa" = 1200ms (1.2 detik per adegan agar cepat berganti dalam durasi ~10 detik)
    interval = 7000 if mode == "code" else 1200

    html_template = """<style>
@keyframes thinkingPulse {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; filter: drop-shadow(0 0 4px #3C3489); }
  100% { transform: scale(1); opacity: 0.8; }
}
.thinking-logo {
  animation: thinkingPulse 1.5s ease-in-out infinite;
}
</style>
<div style="display:flex;align-items:center;justify-content:flex-start;padding:1.5rem 0;">
  <div style="display:flex;align-items:center;gap:10px;font-family:var(--font-mono);font-size:14px;color:var(--text-secondary);">
    <span id="dot" class="thinking-logo" style="display:inline-block;flex-shrink:0;font-size:15px;line-height:1;font-weight:bold;">&lt;/&gt;</span>
    <span id="line">Menyalakan mode coding</span>
  </div>
</div>
<script>
(function(){
  const lineEl = document.getElementById('line');
  const BAR_LEN = 14;

  function bar(pct){
    const filled = Math.round((pct/100)*BAR_LEN);
    return '█'.repeat(filled) + '░'.repeat(BAR_LEN-filled);
  }
  function rand(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
  function ri(min,max){ return Math.floor(Math.random()*(max-min+1))+min; }
  function hex(n){ return n.toString(16).toUpperCase(); }

  let timers = [];
  function clearTimers(){ timers.forEach(clearInterval); timers=[]; }

  // 1. KV / VRAM (1-100 naik turun)
  function runKV(){
    let pct = ri(20, 80);
    const label = rand(['vram','KV','cache','ctx']);
    const t = setInterval(()=>{
      pct += ri(-8, 10);
      if(pct > 100) pct = 100;
      if(pct < 1) pct = 1;
      lineEl.textContent = `${label}[${bar(pct)}] ${pct}%`;
    }, 100);
    timers.push(t);
  }

  // 2. PPL (1-100 naik turun dengan status tag)
  function runPPL(){
    let v = ri(20,90);
    const t = setInterval(()=>{
      v += ri(-12,12);
      if(v < 1) v = 1; if(v > 100) v = 100;
      const pct = Math.min(100, Math.round((v/100)*100));
      const tag = v > 75 ? 'BAD' : v > 40 ? 'OK' : 'GOOD';
      lineEl.textContent = `PPL: ${v} [${bar(pct)}] ${tag}`;
    }, 110);
    timers.push(t);
  }

  // 3. A: B: C: D: (naik turun acak dengan bar tersegmentasi)
  function runABCD(){
    let vals = {A:ri(1,8), B:ri(1,8), C:ri(1,8), D:ri(1,8)};
    const t = setInterval(()=>{
      Object.keys(vals).forEach(k=>{ vals[k] = Math.max(1, Math.min(8, vals[k]+ri(-1,1))); });
      const seg = k => '█'.repeat(vals[k]);
      lineEl.textContent = `A|${seg('A')}  | B|${seg('B')}  | C|${seg('C')}  | D|${seg('D')}`;
    }, 120);
    timers.push(t);
  }

  // 4. top-p (1-100 / 0.01 - 1.0 naik turun)
  function runTopP(){
    let p = Math.random();
    const t = setInterval(()=>{
      p += (Math.random()-0.5)*0.12;
      p = Math.max(0.01, Math.min(1.0, p));
      const pct = Math.round(p*100);
      lineEl.textContent = `top-p: [${bar(pct)}] p=${p.toFixed(2)}`;
    }, 100);
    timers.push(t);
  }

  // Simbol & Angka Lainnya yang Berganti-ganti
  function runSymbols(){
    const items = [
      '∇·F = ρ/ε₀', '∂²u/∂t² = c²∇²u', 'lim(x→∞) 1/x = 0',
      '∫e^(-x²) dx = √π', '∑(k=1→∞) 1/k² = π²/6', 'det(A) = ad − bc'
    ];
    let i = ri(0,items.length-1);
    lineEl.textContent = 'Menghitung  ' + items[i];
    const t = setInterval(()=>{
      i = (i+1) % items.length;
      lineEl.textContent = 'Menghitung  ' + items[i];
    }, 280);
    timers.push(t);
  }

  function runWeirdSymbols(){
    const items = [
      '⊕ ⊗ ⊙ ⊘ ⊚', '∮ ∯ ∰ ∱ ∲', '⌈x⌉ ⌊x⌋',
      'ℵ₀ < ℵ₁ < ℵ₂', '⊢ ⊨ ⊤ ⊥', '≺ ≻ ≼ ≽'
    ];
    let i = ri(0,items.length-1);
    lineEl.textContent = 'Merangkai  ' + items[i];
    const t = setInterval(()=>{
      i = (i+1) % items.length;
      lineEl.textContent = 'Merangkai  ' + items[i];
    }, 280);
    timers.push(t);
  }

  function runCode(){
    const templates = [
      ['const x =', 1, 999, ''],
      ['arr[', 0, 99, '] processed'],
      ['batch_size =', 8, 256, ''],
      ['epoch', 1, 50, '/50'],
    ];
    const tpl = rand(templates);
    let v = tpl[1];
    lineEl.textContent = `${tpl[0]} ${v}${tpl[3]}`;
    const t = setInterval(()=>{
      v++;
      if(v > tpl[2]) v = tpl[1];
      lineEl.textContent = `${tpl[0]} ${v}${tpl[3]}`;
    }, 80);
    timers.push(t);
  }

  function runDelta(){
    let a = ri(900,1400), b = ri(900,1400);
    const t = setInterval(()=>{
      a += ri(-15,20); b += ri(-15,20);
      const d = Math.abs(a-b);
      lineEl.textContent = `A:${a} >>> B:${b}  Δ=${d}`;
    }, 90);
    timers.push(t);
  }

  function runHash(){
    let v = ri(0,65535);
    const t = setInterval(()=>{
      v = (v + ri(1,700)) % 65536;
      lineEl.textContent = `hash: 0x${hex(v).padStart(4,'0')}`;
    }, 70);
    timers.push(t);
  }

  // Urutan rotasi animasi
  const runners = [runKV, runPPL, runABCD, runTopP, runSymbols, runWeirdSymbols, runCode, runDelta, runHash];
  let idx = 0;

  function nextScene(){
    clearTimers();
    runners[idx]();
    idx = (idx+1) % runners.length;
  }

  nextScene();
  // Berganti adegan sesuai durasi mode
  setInterval(nextScene, INTERVAL_PLACEHOLDER);
})();
</script>"""

    return html_template.replace("INTERVAL_PLACEHOLDER", str(interval))
