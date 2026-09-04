import streamlit as st

def inject_code_loading_css() -> None:
    pass

def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    if done:
        return ""

    # Posisi HTML harus menempel di batas kiri tanpa spasi agar tidak dianggap sebagai Markdown Code Block
    return """<h2 class="sr-only">Loading gabungan bergaya ASCII: simbol matematika dan aneh, potongan kode dengan angka bergulir, dan metrik progress bar, dengan kecepatan lebih lambat</h2>
<div style="display:flex;align-items:center;justify-content:center;padding:2.5rem 0;">
  <div style="display:flex;align-items:center;gap:10px;font-family:var(--font-mono);font-size:14px;color:var(--text-secondary);">
    <span id="dot" style="width:7px;height:7px;border-radius:50%;background:#3C3489;display:inline-block;flex-shrink:0;"></span>
    <span id="line">Menyalakan mode coding</span>
  </div>
</div>
<script>
(function(){
  const lineEl = document.getElementById('line');
  const BAR_LEN = 16;

  function bar(pct){
    const filled = Math.round((pct/100)*BAR_LEN);
    return '█'.repeat(filled) + '░'.repeat(BAR_LEN-filled);
  }
  function rand(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
  function ri(min,max){ return Math.floor(Math.random()*(max-min+1))+min; }
  function hex(n){ return n.toString(16).toUpperCase(); }

  let timers = [];
  function clearTimers(){ timers.forEach(clearInterval); timers=[]; }

  function runSymbols(){
    const items = [
      '∇·F = ρ/ε₀', '∂²u/∂t² = c²∇²u', 'lim(x→∞) 1/x = 0',
      '∫e^(-x²) dx = √π', '∑(k=1→∞) 1/k² = π²/6', 'det(A) = ad − bc',
      'eⁱᵖⁱ + 1 = 0', 'f(x) = Σ aₙxⁿ', '∇f(x*) = 0',
      'sin²θ + cos²θ = 1', 'n! ≈ √(2πn)(n/e)ⁿ', '∀x∈ℝ, ∃y: y>x',
      'P(A∩B) = P(A)·P(B|A)', 'Rμν − ½gμνR = 8πG Tμν'
    ];
    let i = ri(0,items.length-1);
    lineEl.textContent = 'Menghitung  ' + items[i];
    const t = setInterval(()=>{
      i = (i+1) % items.length;
      lineEl.textContent = 'Menghitung  ' + items[i];
    }, 260);
    timers.push(t);
  }

  function runWeirdSymbols(){
    const items = [
      '⊕ ⊗ ⊙ ⊘ ⊚', '∮ ∯ ∰ ∱ ∲', '⌈x⌉ ⌊x⌋',
      'ℵ₀ < ℵ₁ < ℵ₂', '⊢ ⊨ ⊤ ⊥', '≺ ≻ ≼ ≽',
      '∴ ∵ ∷ ∶', '⋃ ⋂ ⊆ ⊇ ⊊', '⟨ψ|φ⟩ = 0',
      'ℤ/nℤ ≅ ℤₙ', '∂Ω → ∅', '⨁ ⨂ ⨀',
      'ℜ(z) + ℑ(z)i', '⊞ ⊟ ⊠ ⊡', '⋈ ⋉ ⋊ ⋋',
      '☯ ⚛ ⚡ ⌬', '↯ ↺ ↻ ⟲ ⟳'
    ];
    let i = ri(0,items.length-1);
    lineEl.textContent = 'Merangkai  ' + items[i];
    const t = setInterval(()=>{
      i = (i+1) % items.length;
      lineEl.textContent = 'Merangkai  ' + items[i];
    }, 260);
    timers.push(t);
  }

  function runCode(){
    const templates = [
      ['const x =', 1, 999, ''],
      ['arr[', 0, 99, '] processed'],
      ['for i <', 1, 100, ''],
      ['port', 1000, 9999, ''],
      ['batch_size =', 8, 256, ''],
      ['status', 100, 599, ''],
      ['epoch', 1, 50, '/50'],
      ['line', 1, 500, ''],
    ];
    const tpl = rand(templates);
    let v = tpl[1];
    lineEl.textContent = `${tpl[0]} ${v}${tpl[3]}`;
    const t = setInterval(()=>{
      v++;
      if(v > tpl[2]) v = tpl[1];
      lineEl.textContent = `${tpl[0]} ${v}${tpl[3]}`;
    }, 70);
    timers.push(t);
  }

  function runKV(){
    let pct = 0;
    const label = rand(['KV','cache','ctx','vram']);
    const t = setInterval(()=>{
      pct += ri(2,5);
      if(pct>100) pct=100;
      lineEl.textContent = `${label}[${bar(pct)}] ${pct}%`;
    }, 70);
    timers.push(t);
  }

  function runDelta(){
    let a = ri(900,1400), b = ri(900,1400);
    const t = setInterval(()=>{
      a += ri(-15,20); b += ri(-15,20);
      const d = Math.abs(a-b);
      lineEl.textContent = `A:${a} >>> B:${b}  Δ=${d}`;
    }, 80);
    timers.push(t);
  }

  function runPPL(){
    let v = ri(20,150);
    const t = setInterval(()=>{
      v += ri(-8,8);
      if(v<5) v=5; if(v>200) v=200;
      const pct = Math.min(100, Math.round((v/200)*100));
      const tag = v>80 ? 'BAD' : v>30 ? 'OK' : 'GOOD';
      lineEl.textContent = `PPL: ${v} [${bar(pct)}] ${tag}`;
    }, 80);
    timers.push(t);
  }

  function runABCD(){
    let vals = {A:ri(1,8), B:ri(1,8), C:ri(1,8), D:ri(1,8)};
    const t = setInterval(()=>{
      Object.keys(vals).forEach(k=>{ vals[k] = Math.max(1, Math.min(8, vals[k]+ri(-1,1))); });
      const seg = k => '█'.repeat(vals[k]);
      lineEl.textContent = `A|${seg('A')}  | B|${seg('B')}  | C|${seg('C')}  | D|${seg('D')}`;
    }, 110);
    timers.push(t);
  }

  function runTopP(){
    let p = Math.random();
    const t = setInterval(()=>{
      p += (Math.random()-0.5)*0.08;
      p = Math.max(0.1, Math.min(0.99,p));
      const pct = Math.round(p*100);
      lineEl.textContent = `top-p: [${bar(pct)}] p=${p.toFixed(2)}`;
    }, 90);
    timers.push(t);
  }

  function runHash(){
    let v = ri(0,65535);
    const t = setInterval(()=>{
      v = (v + ri(1,700)) % 65536;
      lineEl.textContent = `hash: 0x${hex(v).padStart(4,'0')}`;
    }, 60);
    timers.push(t);
  }

  const runners = [runSymbols, runWeirdSymbols, runCode, runKV, runDelta, runPPL, runABCD, runTopP, runHash];
  let idx = 0;

  function nextScene(){
    clearTimers();
    runners[idx]();
    idx = (idx+1) % runners.length;
  }

  nextScene();
  setInterval(nextScene, 3200);
})();
</script>"""
