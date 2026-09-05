# Analisis Repositori — Ampera Trinity AI

> Dokumen acuan untuk pengembangan aplikasi Streamlit selanjutnya.
> Dibuat: 5 September 2026 · Basis: commit `8556f27` (branch `main`)

---

## 1. Ringkasan Aplikasi

**Ampera Trinity AI** adalah aplikasi web chat AI berbasis **Streamlit** (murni Python, tanpa framework frontend terpisah) dengan persona asisten bernama **Yuki**. Total kode ± **9.800 baris** di 21 file Python.

Fitur inti:
- 💬 Chat multi-model (Groq + 3 provider OpenAI-compatible lain)
- 🖼️ Generate gambar (Cloudflare Workers AI — FLUX-1 Schnell)
- 👁️ Analisis gambar (model vision) & 🎤 input suara (Whisper STT)
- 🗂️ Artefak ala Claude (blok kode dipotong jadi file + panel kanan)
- 🃏 Kartu kaya (perbandingan, langkah, link, peta, itinerary, terjemahan, palet)
- 🎓 Kursus (Yuki jadi mentor, thread terpisah per kursus)
- 🎨 AI Desain & 📅 AI Penjadwal (mode persona khusus)
- 🌐 14 bahasa antarmuka + bahasa jawaban
- ⚙️ Pengaturan 9 tab (Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, Refleksi, Waktu & Fokus, Trinity Code)

---

## 2. Peta Struktur Kode

| File | Baris | Peran |
|---|---:|---|
| `app.py` | 1.306 | Entry point: routing 11 halaman via `st.session_state.page` + semua halaman statis (pengaturan, bahasa, bantuan, dll.) |
| `config.py` | 561 | **Semua data statis**: katalog model, persona/system prompt Yuki, aturan klarifikasi/kartu/quick-reply, katalog kursus & artefak, 14 bahasa, `DEFAULT_SETTINGS`, pembacaan API key |
| `state.py` | 257 | Satu-satunya pintu ke `st.session_state`: thread chat utama / artefak / kursus / mode, settings, riwayat percakapan |
| `chat_handlers.py` | 710 | Alur kirim pesan: mode chat (streaming + fallback) & mode gambar, kontrol chat input (menu ➕, toggle, popover model) |
| `engines/groq_engine.py` | 250 | Klien Groq: build system prompt dinamis, streaming + fallback model, vision, Whisper STT |
| `engines/compatible_engine.py` | 122 | Klien generik OpenAI-compatible (Plugsky, Aion Labs, Final Router) |
| `engines/image_engine.py` | 103 | Cloudflare FLUX: request + ekstraksi base64 → PNG |
| `artifacts.py` | 684 | Panel artefak kanan: daftar file, viewer kode dengan syntax highlight, salin, unduh ZIP |
| `cards.py` | 441 | Parser & renderer blok `[[KARTU:...]]` menjadi kartu visual |
| `ui_helpers.py` | 748 | Komponen render kecil: bubble chat, animasi "thinking", parser quick reply, ekspor chat |
| `sidebar.py` | 383 | Sidebar ala Claude: navigasi `go()`, riwayat "Hari ini", dialog Proyek/Artefak/Sesuaikan |
| `styles.py` | 2.771 | **Seluruh CSS** aplikasi (± 98 KB) sebagai string Python |
| `page_desain.py` / `page_jadwal.py` | 114/266 | Halaman mode AI Desain & AI Penjadwal (persona ditambahkan ke system prompt) |
<<<<<<< HEAD
| `icons.py`, `logo.py`, `trinity_logo.py`, `anim.py`, `loading_params.py` | — | Ikon Material, logo base64, animasi CSS & loading parameter |
=======
| `icons.py`, `logo.py`, `trinity_logo.py`, `anim.py`, `loading_code.py` | — | Ikon Material, logo base64, animasi CSS |
>>>>>>> 171a4430aa3ca0a3f8e2c5962e8ae3bf0fde7c9b
| `errors.py` | 42 | Pesan error publik + deteksi "model tidak tersedia" (pemicu fallback) |

**Routing halaman** (`st.session_state.page`): `chat` (default) · `artefak` · `pengaturan` · `bahasa` · `bantuan` · `tingkatkan` · `aplikasi` · `kursus` · `pelajari` · `desain` · `jadwal`.

---

## 3. Arsitektur & Alur Data

```
app.py (router)
  ├─ sidebar.py ──► go(page) ──► st.session_state.page
  ├─ halaman chat/artefak/kursus/desain/jadwal
  │     └─ chat_handlers.py (proses kiriman user)
  │           ├─ engines/groq_engine.py      ← Groq (default)
  │           ├─ engines/compatible_engine.py ← Plugsky / Aion / Final Router
  │           └─ engines/image_engine.py      ← Cloudflare FLUX
  │     └─ jawaban ─► parse_cards() + parse_quick_replies() + ambil_artefak()
  └─ state.py  ←– satu-satunya akses ke st.session_state
```

Pola penting yang **harus dipertahankan** saat mengembangkan:
1. **State hanya lewat `state.py`** — jangan tulis `st.session_state` langsung dari halaman baru.
2. **Data statis hanya di `config.py`** — tambah model/bahasa/kursus cukup edit katalog, tanpa sentuh UI.
3. **Thread terpisah per konteks** — chat utama, tiap artefak, tiap kursus, tiap mode punya riwayat sendiri (`artifact_msgs_{id}`, `course_msgs_{id}`).
4. **Persona modular** — system prompt dirakit di `build_system_prompt()`: `YUKI_SYSTEM_PROMPT` + `CARD_RULES` + prompt mode (desain/jadwal) + preferensi user. Mode baru = tambah 1 prompt di config + 1 cabang di fungsi ini.
5. **Protokol blok teks dari model**: `[[PILIHAN]]` (quick reply), `[[KARTU:jenis]]` (kartu visual), pagar kode ``` ``` (artefak). Fitur output baru sebaiknya ikut pola blok ini.
6. **Fallback model**: error "model unavailable" (`errors.py`) memicu percobaan model berikutnya di `GROQ_MODEL_FALLBACKS` / `VISION_MODEL_FALLBACKS`.

---

## 4. Konfigurasi & Kredensial

Dibaca via `st.secrets` → fallback `os.environ` (`config.py::_get_secret`):

| Key | Untuk | Wajib? |
|---|---|---|
| `GROQ_API_KEY` (atau `GROQ_KEY`) | Chat, vision, Whisper | Ya (fitur utama) |
| `CF_ACCOUNT_ID` + `CF_API_TOKEN` | Generate gambar FLUX | Opsional (`IMAGE_READY`) |
| `PLUGSKY_API_KEY` | Provider Plugsky | Opsional |
| `AION_API_KEY` | Provider Aion Labs | Opsional |
| `FINAL_ROUTER_API_KEY` | Provider Final Router | Opsional |

Aplikasi tetap jalan tanpa key (fitur dimatikan lewat flag `CHAT_READY` / `IMAGE_READY`). Impor `openai` dibuat tahan-gagal agar app tidak crash di Python terlalu baru.

**Dependensi** (`requirements.txt`, dipatok): `streamlit >=1.40,<2` · `openai >=1.60,<2` · `requests` · `Pillow`. Target deploy: **Streamlit Cloud, Python 3.12** (catatan di requirements: 3.14 belum didukung pydantic-core).

---

## 5. Temuan / Potensi Masalah ⚠️

1. **Katalog model tidak konsisten** (`config.py::MODEL_CATALOG`):
   - `llama4_scout` (desc: "bisa melihat gambar") justru memakai id `qwen/qwen3.6-27b` — nama key & isi tidak cocok.
   - `qwen/qwen3.6-27b` dan fallback `qwen/qwen3.8-27b` **bukan model ID Groq yang dikenal** — vision & fallback berisiko selalu gagal. (Model vision Groq yang nyata mis. `meta-llama/llama-4-scout-17b-16e-instruct`.)
   - Banyak entri berbagi nama tampilan sama ("Trinity Normal" ×2, "Trinity Hard" ×2, "Trinity Plus" ×7) — membingungkan di popover pemilih model.
2. **Provider eksternal belum terverifikasi**: base URL Plugsky / Aion / Final Router hard-coded; perlu dites nyata sebelum diandalkan.
3. **`styles.py` 2.771 baris CSS dalam satu string** — berat untuk dirawat; banyak selektor internal Streamlit yang rapuh terhadap upgrade versi Streamlit.
4. **`app.py` 1.306 baris** — halaman pengaturan (9 tab) dan halaman statis lain masih menumpuk di file utama; kandidat utama untuk dipecah ke `pages_*/`.
5. **Keamanan**: `.streamlit/config.toml` mematikan CORS & XSRF protection — wajar untuk demo, perlu ditinjau untuk produksi.
6. **File sampah**: `assets/P` (file tak jelas) sebaiknya dihapus.
7. **Tidak ada test & CI** — belum ada pytest/GitHub Actions; regresi hanya ketahuan manual.
8. **Fitur "kosmetik"**: tab Akun/Penagihan/Privasi hanya menyimpan ke session state (tidak ada backend/auth/database nyata); riwayat chat **hilang saat refresh** karena semuanya di `st.session_state`.

---

## 6. Rekomendasi Pengembangan Selanjutnya

**Prioritas tinggi (perbaikan):**
- [ ] Bereskan `MODEL_CATALOG`: ID model Groq yang valid, nama tampilan unik, hapus duplikat.
- [ ] Verifikasi/uji provider Plugsky, Aion, Final Router — atau beri label "eksperimental".
- [ ] Hapus `assets/P`.

**Prioritas menengah (struktur):**
- [ ] Pecah `app.py`: pindahkan `page_pengaturan`, `page_bahasa`, `page_bantuan`, dll. ke modul terpisah (mis. folder `pages_app/`).
- [ ] Pecah `styles.py` per komponen, atau muat dari file `.css`.
- [ ] Tambah persistensi opsional (SQLite/JSON) untuk riwayat chat & pengaturan agar tahan refresh.
- [ ] Tambah test dasar (parser kartu, parser quick reply, `ambil_artefak`, fallback engine) + GitHub Actions.

**Prioritas fitur (mengikuti pola yang ada):**
- Mode/persona baru → tambah `*_PROMPT` di `config.py` + cabang di `build_system_prompt()` + halaman `page_*.py` + rute di `app.py::main()`.
- Jenis kartu baru → tulis `_render_<jenis>()` di `cards.py` + daftarkan di `RENDERER` + tambah contoh di `CARD_RULES`.
- Model/provider baru → entri di `MODEL_CATALOG` (dengan field `provider`) + config di `PROVIDER_CONFIG` (`compatible_engine.py`).

---

## 7. Cara Menjalankan

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_..."          # atau via .streamlit/secrets.toml
streamlit run app.py                    # port 8501, bind 0.0.0.0
```
