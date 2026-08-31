# 🏗️ Arsitektur

Dokumen untuk developer yang ingin membaca, memodifikasi, atau memperluas kode.

---

## Prinsip Desain

1. **Satu modul, satu tanggung jawab.** Data statis di `config.py`, state di `state.py`, tampilan di `ui_helpers.py` + `styles.py`, panggilan AI di `engines/`.
2. **`app.py` hanya merakit.** Isinya routing dan definisi halaman — tidak ada logika AI di dalamnya.
3. **State hanya lewat `state.py`.** Halaman dan engine dilarang menyentuh `st.session_state` secara langsung untuk struktur data bersama.
4. **Error tidak bocor.** Semua pesan yang tampil ke pengguna disaring `errors.py`.
5. **Rahasia tidak di kode.** Kredensial hanya lewat Streamlit Secrets / environment variable.

---

## Peta Modul

| Modul | Baris | Tanggung jawab |
|---|---:|---|
| `app.py` | ~1.310 | Konfigurasi halaman, routing, definisi 9 halaman |
| `styles.py` | ~1.790 | Seluruh CSS & `@keyframes` |
| `logo.py` | ~520 | Logo utama dalam base64 |
| `chat_handlers.py` | ~480 | Alur kirim pesan, render input, mode gambar |
| `ui_helpers.py` | ~380 | Bubble pesan, animasi teks, ekspor `.md`, tangkap artefak |
| `config.py` | ~280 | Konstanta, katalog, `DEFAULT_SETTINGS`, pembacaan secrets |
| `engines/groq_engine.py` | ~215 | System prompt, chat streaming, fallback, vision, STT |
| `sidebar.py` | ~215 | Navigasi + dialog Proyek / Artefak / Sesuaikan |
| `state.py` | ~185 | Inisialisasi state, thread pesan, riwayat percakapan |
| `engines/image_engine.py` | ~105 | Generate gambar Cloudflare + parsing respons |
| `trinity_logo.py` | ~105 | Logo alternatif |
| `icons.py` | ~90 | Ikon SVG & helper `mi()` |
| `errors.py` | ~40 | Terjemahan error jadi pesan publik |

---

## Diagram Ketergantungan

```
                       app.py
                          │
      ┌───────────┬───────┼────────┬──────────────┐
      ▼           ▼       ▼        ▼              ▼
  sidebar.py  ui_helpers  styles  chat_handlers  state.py
      │           │                    │            │
      └───────────┴────────┬───────────┘            │
                           ▼                        │
                       engines/                     │
                  ┌────────┴────────┐               │
                  ▼                 ▼               │
           groq_engine.py    image_engine.py        │
                  │                 │               │
                  └────────┬────────┘               │
                           ▼                        ▼
                       errors.py                config.py
```

`config.py` adalah daun (tidak mengimpor modul internal lain), sehingga aman diimpor dari mana saja tanpa impor melingkar.

---

## Alur Data: Satu Pesan Chat

```
1. Pengguna mengetik  →  chat_handlers.render_input_controls()
2. process_user_input()
      ├─ gambar yang di-stage diambil dari session_state.pending_images
      ├─ pesan pengguna ditambahkan ke active_thread()
      └─ st.rerun()
3. maybe_run_yuki()  →  handle_chat_request(answer_slot)
      ├─ cek CHAT_READY
      ├─ tentukan model:
      │     ada gambar          → VISION_MODEL_ID
      │     web search aktif    → groq/compound
      │     selain itu          → model pilihan pengguna
      ├─ tampilkan animasi "berpikir" (thinking_html)
      ├─ build_chat_client()  →  OpenAI(base_url = Groq)
      ├─ stream_chat_with_fallback()
      │     ├─ build_system_prompt()  ← persona + settings + custom
      │     ├─ 40 pesan terakhir dikirim
      │     └─ error "model tidak ada" → coba model cadangan
      ├─ tahan sampai min_think_seconds terpenuhi
      ├─ stream_sentences()  → tampil bertahap per kalimat + caret
      ├─ simpan balasan ke thread
      └─ _capture_artifacts_from_reply()  → simpan blok kode panjang
```

## Alur Data: Generate Gambar

```
1. Mode gambar aktif  →  prompt dikirim
2. Thread pekerja memanggil image_engine
      └─ POST  https://api.cloudflare.com/client/v4/accounts/{id}/ai/run/{model}
3. Loop utama menampilkan progress bar bertahap
      └─ minimum 10 detik supaya transisi tidak berkedip
4. extract_image_bytes(payload)
      └─ menangani berbagai bentuk: result str / dict / data[] / nested
5. Berhasil → pesan bertipe "image" ditambahkan ke thread
   Gagal    → public_error_image() → pesan ramah
```

---

## Manajemen State

Semua data hidup di `st.session_state` (**tidak ada database**).

### Kunci utama

| Kunci | Tipe | Isi |
|---|---|---|
| `messages` | `list[dict]` | Thread chat utama |
| `page` | `str` | Halaman aktif |
| `settings` | `dict` | Semua pengaturan pengguna |
| `selected_model_key` | `str` | Model yang dipilih |
| `image_mode` | `bool` | Mode generate gambar |
| `web_search_on` | `bool` | Saklar web search |
| `pending_images` | `list` | Lampiran yang menunggu dikirim |
| `conversations` | `list[dict]` | Riwayat percakapan `{id, title, messages}` |
| `projects` | `list[dict]` | Proyek `{id, name}` |
| `artifacts` | `list[dict]` | Artefak `{id, title, content, time}` |
| `custom_nickname` / `custom_instruction` | `str` | Hasil dialog Sesuaikan |
| `artifact_msgs_{id}` | `list[dict]` | Thread per artefak |
| `course_msgs_{key}` | `list[dict]` | Thread per kursus |

### Struktur pesan

```python
{
    "id": 7,                       # dari next_msg_id()
    "role": "assistant",           # "user" | "assistant"
    "type": "text",                # "text" | "image"
    "content": "Halo! ...",        # untuk type="text"
    "image_bytes": b"...",         # untuk type="image"
    "prompt": "kucing oranye...",  # untuk type="image"
    "images": [...],               # lampiran pada pesan user
    "time": "14:32",               # WIB
    "feedback": None,              # None | "up" | "down"
}
```

### Thread terpisah

`active_thread()` memilih thread berdasarkan halaman aktif:

| Halaman | Thread |
|---|---|
| `artefak` | `artifact_thread(artifact_active_id)` |
| `kursus` | `course_thread(course_active_key)` |
| lainnya | `messages` (chat utama) |

Ini mencegah jawaban antar konteks saling tercampur.

### Pola aman membaca settings

```python
def get_settings() -> dict:
    base = dict(DEFAULT_SETTINGS)
    base.update(st.session_state.get("settings") or {})
    return base
```

Kunci baru yang ditambahkan ke `DEFAULT_SETTINGS` otomatis tersedia, bahkan untuk sesi lama — tidak perlu migrasi.

---

## Routing Halaman

Routing dilakukan manual lewat `st.session_state.page`, bukan multipage bawaan Streamlit — supaya sidebar dan CSS-nya sepenuhnya bisa dikustomisasi.

| `page` | Fungsi di `app.py` |
|---|---|
| `chat` | `render_chat_page()` |
| `artefak` | `page_artefak()` |
| `pengaturan` | `page_pengaturan()` |
| `bahasa` | `page_bahasa()` |
| `bantuan` | `page_bantuan()` |
| `tingkatkan` | `page_tingkatkan()` |
| `aplikasi` | `page_aplikasi()` |
| `kursus` | `page_kursus()` |
| `pelajari` | `page_pelajari()` |

Berpindah halaman memakai `sidebar.go("nama_halaman")`, yang menyetel `page` lalu memanggil `st.rerun()`.

---

## Deteksi Kapabilitas Streamlit

Karena `st.chat_input` berubah antar versi, `config.py` memeriksa tanda tangan fungsinya saat impor:

```python
_CHAT_INPUT_PARAMS = inspect.signature(st.chat_input).parameters
CHAT_INPUT_SUPPORTS_FILE  = "accept_file"  in _CHAT_INPUT_PARAMS
CHAT_INPUT_SUPPORTS_AUDIO = "accept_audio" in _CHAT_INPUT_PARAMS
```

Fitur lampiran/suara disembunyikan otomatis di Streamlit lama, tanpa error.

---

## Catatan Tentang Ikon

Streamlit hanya menerjemahkan sintaks `:material/nama:` pada teks markdown biasa. Begitu berada di dalam tag HTML, sintaks itu tampil mentah.

Karena itu `icons.py` menyediakan `mi("nama")` yang menghasilkan `<span>` dengan font **Material Symbols Rounded** dan ligatur nama ikon — dipakai khusus di dalam string HTML pada `st.markdown(..., unsafe_allow_html=True)`.

---

## Cara Menambah Fitur

### Menambah model AI

`config.py` → `MODEL_CATALOG`:

```python
{"key": "model_baru", "name": "Trinity Ultra",
 "desc": "Penjelasan singkat", "id": "provider/nama-model", "premium": True},
```

`AVAILABLE_MODELS` dan `MODEL_BY_KEY` terbentuk otomatis dari daftar ini.

### Menambah bahasa

`config.py` → `SUPPORTED_LANGUAGES`:

```python
{"code": "th", "flag": "🇹🇭", "name": "ไทย",
 "native": "Thai", "level": "Beta", "yuki": True},
```

### Menambah kategori artefak

`config.py` → `ARTIFACT_CATEGORIES`. Isi `brief` menentukan instruksi awal yang dikirim ke Yuki.

### Menambah kursus

`config.py` → `COURSE_CATALOG`. Kurikulum 4 modulnya dibuat otomatis oleh `course_curriculum()`.

### Menambah halaman baru

1. Tulis `def page_baru()` di `app.py`.
2. Daftarkan di router dalam `main()`.
3. Tambahkan judulnya ke `PAGE_TITLES` di `config.py`.
4. Tambahkan tombol navigasinya di `sidebar.py` dengan `go("baru")`.

### Menambah pengaturan baru

1. Tambahkan kunci + nilai bawaan ke `DEFAULT_SETTINGS`.
2. Tambahkan widget-nya di fungsi tab terkait (`_set_umum()`, `_set_privasi()`, dst).
3. Simpan lewat `_save_settings({"kunci": nilai})`.
4. Baca di tempat lain dengan `get_settings()["kunci"]`.

---

## Keterbatasan yang Diketahui

| Keterbatasan | Dampak | Kemungkinan solusi |
|---|---|---|
| State hanya di memori | Riwayat hilang saat refresh | Tambahkan SQLite / Postgres |
| Tanpa autentikasi | Semua pengunjung berbagi kuota API | Tambah login / `st.experimental_user` |
| `stream_speed` belum terpasang | Pilihan Lambat/Sedang/Cepat belum berpengaruh; `SENTENCE_STREAM_DELAY` masih tetap `0.15` | Petakan pilihan ke nilai jeda di `stream_sentences()` |
| Beberapa entri model menunjuk ID sama | "Trinity Normal" dan "Trinity Hard" sebagian identik | Ganti ID di `MODEL_CATALOG` |
| `enableXsrfProtection = false` | Longgar untuk deployment publik | Aktifkan bila dipasang di server sendiri |
| Belum ada test otomatis | Regresi baru terlihat manual | Tambahkan `pytest` untuk fungsi murni |

---

## Referensi

- [Streamlit — Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Groq — OpenAI compatibility](https://console.groq.com/docs/openai)
- [Cloudflare Workers AI — Text to Image](https://developers.cloudflare.com/workers-ai/models/)
