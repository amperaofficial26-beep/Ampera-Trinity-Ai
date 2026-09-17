# -*- coding: utf-8 -*-
"""
PENAMBAL OTOMATIS — fitur Tampilan (wallpaper & warna).

Menyalin fungsi secara manual gampang salah: badan fungsi ikut
terpotong, indentasi berubah, atau indeks tab lupa digeser. Skrip ini
melakukan semuanya sendiri dan aman dijalankan berulang kali (kalau
sudah tertambal, dia berhenti dan tidak menambal dua kali).

Cara pakai — dari folder root repo (yang ada app.py-nya):

    python patch_tampilan/terapkan_patch.py

Yang dikerjakan:
  1. cek tampilan.py sudah ada
  2. app.py   : tambah import, sisip _set_tampilan(), tambah tab,
                geser indeks tab, panggil inject_tampilan()
  3. config.py: gabungkan TAMPILAN_DEFAULTS
  4. verifikasi hasil akhirnya lolos kompilasi Python

Cadangan otomatis dibuat: app.py.bak dan config.py.bak
"""

from __future__ import annotations

import os
import py_compile
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app.py")
CFG = os.path.join(ROOT, "config.py")
BLOK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "_set_tampilan.py")


def gagal(pesan: str) -> None:
    print(f"\n  GAGAL: {pesan}\n")
    sys.exit(1)


def main() -> None:
    print("\n=== Penambal fitur Tampilan ===\n")

    # ---- prasyarat --------------------------------------------------
    if not os.path.exists(APP):
        gagal("app.py tidak ditemukan. Jalankan dari folder root repo.")
    if not os.path.exists(os.path.join(ROOT, "tampilan.py")):
        gagal("tampilan.py belum ada. Salin dulu file itu ke root repo.")
    if not os.path.exists(BLOK):
        gagal("patch_tampilan/_set_tampilan.py tidak ditemukan.")

    app = open(APP, encoding="utf-8").read()
    cfg = open(CFG, encoding="utf-8").read()
    blok = open(BLOK, encoding="utf-8").read().rstrip() + "\n\n\n"

    shutil.copy(APP, APP + ".bak")
    shutil.copy(CFG, CFG + ".bak")
    print("  cadangan  : app.py.bak, config.py.bak")

    # ---- 1. import --------------------------------------------------
    if "from tampilan import" in app:
        print("  [lewat]   import tampilan sudah ada")
    else:
        jangkar = "from styles import inject_css"
        if jangkar not in app:
            gagal("baris 'from styles import inject_css' tidak ditemukan.")
        app = app.replace(jangkar, jangkar + """
from tampilan import (
    PALET_NAMES, WALLPAPER_NAMES, SUDUT_NAMES, DEFAULT_PALET,
    inject_tampilan, kartu_pratinjau, siapkan_wallpaper_unggahan,
    palet_aktif, _valid_hex,
)""", 1)
        print("  [ok]      import tampilan")

    # ---- 2. fungsi _set_tampilan ------------------------------------
    if "def _set_tampilan(" in app:
        print("  [lewat]   _set_tampilan() sudah ada")
    else:
        jangkar = "def _set_akun() -> None:"
        if jangkar not in app:
            gagal("fungsi _set_akun() tidak ditemukan.")
        app = app.replace(jangkar, blok + jangkar, 1)
        print("  [ok]      fungsi _set_tampilan()")

    # ---- 3. selectbox Tema lama -------------------------------------
    lama = '''    st.markdown('<div class="set-section">Tampilan</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        theme = st.selectbox("Tema", THEME_OPTIONS, index=_opt_index(THEME_OPTIONS, s["theme"]),
                             key="set_theme", help="Tema beige hangat adalah tampilan bawaan Trinity.")
    with c2:'''
    baru = '''    # Pemilih "Tema" lama dipindah ke tab "Tampilan" (tampilan.py) yang
    # benar-benar mengubah warna aplikasi. Selectbox lama hanya menyimpan
    # nilai tanpa efek apa pun.
    st.markdown('<div class="set-section">Tampilan</div>', unsafe_allow_html=True)
    st.caption("Wallpaper dan warna aplikasi diatur di tab **Tampilan**.")
    c2, c3 = st.columns(2)
    with c2:'''
    if lama in app:
        app = app.replace(lama, baru, 1)
        app = app.replace('            "theme": theme, "font_size": font,',
                          '            "font_size": font,', 1)
        print("  [ok]      selectbox Tema lama dihapus")
    else:
        print("  [lewat]   selectbox Tema lama sudah tidak ada")

    # ---- 4. daftar tab ----------------------------------------------
    if '":material/palette:  Tampilan",' in app:
        print("  [lewat]   tab Tampilan sudah terdaftar")
    else:
        jangkar = '''        ":material/tune:  Umum",
        ":material/person:  Akun",'''
        if jangkar not in app:
            gagal("daftar st.tabs() Pengaturan tidak ditemukan.")
        app = app.replace(jangkar, '''        ":material/tune:  Umum",
        ":material/palette:  Tampilan",
        ":material/person:  Akun",''', 1)

        # Indeks digeser dari BELAKANG supaya tidak saling menimpa.
        urut = [
            (7, "_set_waktu_fokus", 8),
            (6, "_set_refleksi", 7),
            (5, "_set_memori", 6),
            (4, "_set_kemampuan", 5),
            (3, "_set_penagihan", 4),
            (2, "_set_privasi", 3),
            (1, "_set_akun", 2),
        ]
        for lama_i, fn, baru_i in urut:
            src = f"    with tabs[{lama_i}]:\n        {fn}()"
            dst = f"    with tabs[{baru_i}]:\n        {fn}()"
            if src not in app:
                gagal(f"blok 'with tabs[{lama_i}]: {fn}()' tidak ditemukan.")
            app = app.replace(src, dst, 1)

        app = app.replace("    with tabs[0]:\n        _set_umum()",
                          "    with tabs[0]:\n        _set_umum()\n"
                          "    with tabs[1]:\n        _set_tampilan()", 1)
        print("  [ok]      tab Tampilan + indeks digeser")

    # ---- 5. inject_tampilan() ---------------------------------------
    if "inject_tampilan()" in app.split("def main()")[-1]:
        print("  [lewat]   inject_tampilan() sudah dipanggil")
    else:
        jangkar = "    init_state()\n    inject_css()\n    inject_anim_css()"
        if jangkar not in app:
            gagal("blok init_state()/inject_css() di main() tidak ditemukan.")
        app = app.replace(jangkar, jangkar + """
    # Lapisan tampilan pilihan User — HARUS sesudah inject_css()
    # supaya menimpa tema bawaan, bukan tertimpa.
    inject_tampilan()""", 1)
        print("  [ok]      panggilan inject_tampilan()")

    # ---- 6. config.py -----------------------------------------------
    if "TAMPILAN_DEFAULTS" in cfg:
        print("  [lewat]   config.py sudah tertambal")
    else:
        jangkar = '    "temperature": 0.7,\n}'
        if jangkar not in cfg:
            gagal("akhir DEFAULT_SETTINGS di config.py tidak ditemukan.")
        cfg = cfg.replace(jangkar, jangkar + """

# Pengaturan tampilan (wallpaper & warna) tinggal di tampilan.py supaya
# daftar palet/wallpaper dan nilai bawaannya ada di satu tempat.
try:
    from tampilan import TAMPILAN_DEFAULTS as _TAMPILAN_DEFAULTS
except Exception:  # pragma: no cover
    _TAMPILAN_DEFAULTS = {}
DEFAULT_SETTINGS.update(_TAMPILAN_DEFAULTS)""", 1)
        print("  [ok]      config.py")

    # ---- tulis + verifikasi -----------------------------------------
    open(APP, "w", encoding="utf-8").write(app)
    open(CFG, "w", encoding="utf-8").write(cfg)

    for f in (APP, CFG, os.path.join(ROOT, "tampilan.py")):
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            shutil.copy(APP + ".bak", APP)
            shutil.copy(CFG + ".bak", CFG)
            gagal(f"hasil tambalan tidak lolos kompilasi:\n{e}\n"
                  "Perubahan sudah dikembalikan dari cadangan.")

    print("\n  SELESAI — semua file lolos kompilasi.")
    print("  Jalankan: streamlit run app.py")
    print("  Buka: Pengaturan > tab Tampilan\n")


if __name__ == "__main__":
    main()
