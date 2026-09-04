import streamlit as st

def inject_code_loading_css() -> None:
    pass

def code_loading_html(nama_file: str = "", done: bool = False) -> str:
    if done:
        return ""

    return """<style>
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
    <span id="dot" class="thinking-logo" style="display:inline-block;flex-shrink:0;font-size:16px;line-height:1;">✦</span>
    <span id="line">Menyalakan mode coding...</span>
  </div>
</div>
<script>
(function(){
  const lineEl = document.getElementById('line');
  const BAR_LEN = 14;

  function bar(pct){
    const filled = Math.round((pct/100) * BAR_LEN);
    return '█'.repeat(filled) + '░'.repeat(BAR_LEN - filled);
  }

  // Tahapan teks yang akan berganti seiring berjalannya persentase bar (total 30 detik)
  const stages = [
    { at: 0, text: 'Menyalakan mode coding...' },
    { at: 12, text: 'Menghitung ∇·F = ρ/ε₀' },
    { at: 25, text: 'Merangkai ⊕ ⊗ ⊙ ⊘ ⊚' },
    { at: 40, text: 'Memuat cache VRAM & context...' },
    { at: 55, text: 'Mengoptimalkan top-p & parameter' },
    { at: 70, text: 'Menghitung perplexity (PPL)' },
    { at: 85, text: 'Menyusun hash & finalisasi kode' },
    { at: 95, text: 'Hampir selesai...' }
  ];

  const startTime = Date.now();
  const totalDuration = 30000; // 30 detik

  function updateLoading() {
    const elapsed = Date.now() - startTime;
    let pct = Math.min(100, Math.floor((elapsed / totalDuration) * 100));

    // Cari teks yang sesuai dengan progress saat ini
    let currentText = stages[0].text;
    for (let i = stages.length - 1; i >= 0; i--) {
      if (pct >= stages[i].at) {
        currentText = stages[i].text;
        break;
      }
    }

    // Tampilkan format: [████░░░░░░] 35% — Teks Status
    lineEl.textContent = `[${bar(pct)}] ${pct}% — ${currentText}`;

    if (pct < 100) {
      requestAnimationFrame(updateLoading);
    }
  }

  updateLoading();
})();
</script>"""
