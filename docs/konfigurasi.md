# 🔑 Konfigurasi

Semua kredensial dibaca oleh `config.py` lewat fungsi `_get_secret()`, yang mencari nilai berurutan di:

1. **Streamlit Secrets** (`.streamlit/secrets.toml` atau panel Secrets di Streamlit Cloud)
2. **Environment variable**

Kalau keduanya kosong, fitur terkait otomatis dimatikan — aplikasi tidak crash.

---

## Daftar Variabel

| Variabel | Alias yang juga diterima | Wajib | Dipakai untuk |
|---|---|---|---|
| `GROQ_API_KEY` | `GROQ_KEY` | ✅ | Chat, analisis gambar, transkripsi suara |
| `CF_ACCOUNT_ID` | `CLOUDFLARE_ACCOUNT_ID` | ⬜ | Generate gambar |
| `CF_API_TOKEN` | `CLOUDFLARE_API_TOKEN` | ⬜ | Generate gambar |

Flag turunannya:

```python
CHAT_READY  = bool(GROQ_API_KEY)
IMAGE_READY = bool(CF_ACCOUNT_ID and CF_API_TOKEN)
```

---

## 1. Groq API Key (wajib)

Groq menyediakan tier gratis yang sangat cukup untuk pemakaian pribadi.

1. Buka <https://console.groq.com>
2. Daftar / masuk (bisa pakai akun Google atau GitHub).
3. Menu **API Keys** → **Create API Key**.
4. Beri nama, lalu **salin key-nya sekarang** — key hanya ditampilkan satu kali.
5. Key berformat `gsk_...`

Masukkan ke `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## 2. Cloudflare Workers AI (opsional)

Diperlukan hanya kalau ingin fitur **generate gambar** (model `@cf/black-forest-labs/flux-1-schnell`).

1. Buka <https://dash.cloudflare.com> dan masuk.
2. **Account ID** — terlihat di URL dashboard atau di sidebar kanan halaman Workers:
   `https://dash.cloudflare.com/<INI_ACCOUNT_ID>/...`
3. **API Token** — menu **My Profile → API Tokens → Create Token**.
   - Pilih **Create Custom Token**
   - Permissions: **Account → Workers AI → Read** (atau `Edit`)
   - Simpan tokennya.

```toml
CF_ACCOUNT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
CF_API_TOKEN  = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> Tanpa dua nilai ini, mode gambar tidak muncul di UI. Fitur lain tetap normal.

---

## 3. Contoh File Lengkap

`.streamlit/secrets.toml`:

```toml
# ── WAJIB ───────────────────────────────────
GROQ_API_KEY = "gsk_..."

# ── OPSIONAL: generate gambar ───────────────
CF_ACCOUNT_ID = "..."
CF_API_TOKEN  = "..."
```

Ada templat siap salin di **`.streamlit/secrets.toml.example`**.

### 🔒 Keamanan

- `.streamlit/secrets.toml` dan `.env` sudah ada di `.gitignore`.
- **Jangan pernah** menaruh key langsung di dalam `config.py` atau kode lain.
- Kalau key terlanjur ter-push ke GitHub, **cabut (revoke) key itu** di dashboard provider lalu buat yang baru — menghapus commit saja tidak cukup.

---

## 4. Model yang Dipakai

Semua ID model didefinisikan di `config.py`. Ubah di sana kalau provider mengganti nama model.

### Katalog chat (`MODEL_CATALOG`)

| Nama tampilan | ID model | Kelebihan | Premium |
|---|---|---|---|
| Trinity Easy | `openai/gpt-oss-20b` | Cepat untuk chat & coding ringan | — |
| Trinity Normal | `groq/compound-mini` | Web search ringkas & cepat | — |
| Trinity Normal | `qwen/qwen3.6-27b` | Bisa melihat & menganalisis gambar | — |
| Trinity Hard | `groq/compound` | Browsing web & eksekusi kode | ⭐ |
| Trinity Hard | `qwen/qwen3.6-27b` | Reasoning & matematika | ⭐ |
| Trinity Extreme | `openai/gpt-oss-120b` | Reasoning mendalam untuk tugas berat | ⭐ |

### Model khusus

| Konstanta | Nilai | Fungsi |
|---|---|---|
| `VISION_MODEL_ID` | `qwen/qwen3.6-27b` | Analisis gambar |
| `STT_MODEL` | `whisper-large-v3-turbo` | Transkripsi suara |
| `CF_IMAGE_MODEL` | `@cf/black-forest-labs/flux-1-schnell` | Generate gambar |

### Fallback otomatis

Kalau model utama ditolak provider (dihentikan / tidak ada), engine mencoba daftar cadangan secara berurutan:

```python
GROQ_MODEL_FALLBACKS   = ("openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b")
VISION_MODEL_FALLBACKS = ("qwen/qwen3.6-27b", "qwen/qwen3.8-27b")
```

Deteksi "model tidak tersedia" ditangani `errors.py → _is_model_unavailable_error()`.

### Batasan lain

| Konstanta | Nilai | Arti |
|---|---|---|
| `MAX_HISTORY_MESSAGES` | 40 | Jumlah pesan terakhir yang dikirim ke model |
| `MAX_IMAGES_PER_MESSAGE` | 5 | Maksimal gambar per pesan |
| `VISION_RECENT_MESSAGES` | 4 | Berapa pesan terakhir yang gambarnya ikut dikirim |
| `IMAGE_INPUT_TYPES` | png, jpg, jpeg, webp, gif | Format gambar yang diterima |
| `CF_DEFAULT_STEPS` | 4 | Jumlah langkah difusi FLUX |

---

## 5. Pengaturan Dalam Aplikasi

Selain secrets, ada ~50 opsi yang bisa diubah pengguna lewat halaman **Pengaturan** (9 tab).
Nilai bawaannya ada di `DEFAULT_SETTINGS` (`config.py`) dan tersimpan di `st.session_state["settings"]`.

### Tab Umum
| Kunci | Bawaan | Keterangan |
|---|---|---|
| `theme` | `Beige hangat` | Tema warna |
| `font_size` | `Normal` | Ukuran teks |
| `compact_mode` | `False` | Perkecil jarak antar pesan |
| `stream_speed` | `Sedang` | Kecepatan kalimat muncul |
| `min_think_seconds` | `10.0` | Durasi minimum animasi "berpikir" |
| `personality` | `Santai & kocak` | Kepribadian Yuki |
| `default_mode` | `Chat` | Mode saat aplikasi dibuka |

### Tab Akun
`display_name`, `email`, `username`, `bio`

### Tab Privasi
| Kunci | Bawaan |
|---|---|
| `allow_web_search` | `True` |
| `save_history` | `True` |
| `keep_voice` | `False` |
| `analytics` | `True` |
| `personalization` | `True` |
| `cloud_sync` | `False` |

### Tab Penagihan
`plan` (`Free`), `billing_cycle` (`Bulanan`), `payment_method`

### Tab Kemampuan
Saklar on/off per fitur: `cap_web_search`, `cap_artifacts`, `cap_voice`, `cap_vision`, `cap_image` — semuanya `True` secara bawaan.

### Tab Memori
`memories` (daftar catatan), `memory_on` (`True`), `memory_auto` (`False`)

### Tab Refleksi
`reflection_goal`, `reflection_habit`, `reflection_freq` (`Setiap hari`), `reflection_tone` (`Mendorong`)

### Tab Waktu & Fokus
`focus_minutes` (25), `break_minutes` (5), `work_start` (`09:00`), `work_end` (`18:00`), `tz_label` (`Asia/Jakarta (WIB)`), `focus_reminder`

### Tab Trinity Code
Isian key per-pengguna: `groq_key`, `cf_account_id`, `cf_token`, plus `temperature` (0.7) dan `advanced_errors` (`False`).

---

## 6. Kepribadian & Bahasa Yuki

`engines/groq_engine.py → build_system_prompt()` menyusun system prompt dari:

1. `YUKI_SYSTEM_PROMPT` — persona dasar (jenius, kocak, suka bercanda).
2. Pemetaan `personality` → instruksi tambahan:
   - **Santai & kocak** — pertahankan candaan receh
   - **Serius & ringkas** — kurangi candaan, langsung ke inti
   - **Mentor sabar** — jelaskan langkah demi langkah
   - **Profesional formal** — bahasa formal, minim emoji
3. `yuki_lang` — jika bukan `id`, ditambahkan instruksi menjawab dalam bahasa tersebut.
4. `custom_nickname` — panggilan untuk pengguna.
5. `custom_instruction` — instruksi bebas dari dialog **Sesuaikan**.

### 14 Bahasa yang Didukung

| Kode | Bahasa | Level | Kode | Bahasa | Level |
|---|---|---|---|---|---|
| `id` | Bahasa Indonesia | Penuh | `zh` | 中文 | Penuh |
| `en` | English | Penuh | `es` | Español | Penuh |
| `ms` | Bahasa Melayu | Penuh | `pt` | Português | Penuh |
| `su` | Basa Sunda | Beta | `fr` | Français | Penuh |
| `jv` | Basa Jawa | Beta | `de` | Deutsch | Penuh |
| `ja` | 日本語 | Penuh | `ar` | العربية | Beta |
| `ko` | 한국어 | Penuh | `hi` | हिन्दी | Beta |

Bahasa **antarmuka** (`ui_lang`) dan bahasa **jawaban Yuki** (`yuki_lang`) diatur terpisah.

---

## ➡️ Selanjutnya

- [Rincian fitur](fitur.md)
- [Deploy jadi link publik](deploy.md)
