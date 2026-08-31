# 📚 Dokumentasi Ampera Trinity AI

Selamat datang di dokumentasi lengkap **Ampera Trinity AI** — aplikasi web AI dengan asisten Yuki.

## Peta Dokumen

### 🚀 Mulai
| Dokumen | Untuk siapa | Isi |
|---|---|---|
| **[Instalasi](instalasi.md)** | Semua orang | Prasyarat, install, jalankan, troubleshooting |
| **[Konfigurasi](konfigurasi.md)** | Semua orang | Cara dapat API key, secrets, semua opsi pengaturan |
| **[Deploy](deploy.md)** | Pemilik aplikasi | Bikin link publik: Streamlit Cloud, HF Spaces, Docker, VPS |

### 📖 Memakai
| Dokumen | Untuk siapa | Isi |
|---|---|---|
| **[Fitur](fitur.md)** | Semua orang | Rincian tiap fitur & halaman aplikasi |
| **[Panduan Pengguna](panduan-pengguna.md)** | Pengguna akhir | Langkah demi langkah memakai aplikasi |
| **[FAQ](faq.md)** | Semua orang | Pertanyaan yang sering muncul |

### 🔧 Mengembangkan
| Dokumen | Untuk siapa | Isi |
|---|---|---|
| **[Arsitektur](arsitektur.md)** | Developer | Struktur modul, alur data, cara menambah fitur |
| **[Kontribusi](../CONTRIBUTING.md)** | Kontributor | Gaya kode, alur PR, checklist |
| **[Changelog](../CHANGELOG.md)** | Semua orang | Riwayat perubahan versi |

---

## Ringkasan 30 Detik

**Ampera Trinity AI** adalah aplikasi [Streamlit](https://streamlit.io) satu halaman dengan routing internal.
Semua state disimpan di `st.session_state` (tidak ada database), dan dua "engine" menangani AI:

```
Pengguna
   │
   ▼
app.py  ──routing──▶  halaman (chat / artefak / kursus / pengaturan / …)
   │
   ▼
chat_handlers.py  ──▶  engines/groq_engine.py   → Groq  (chat, vision, Whisper)
                  └─▶  engines/image_engine.py  → Cloudflare (FLUX)
   │
   ▼
ui_helpers.py + styles.py  ──▶  tampilan & animasi
```

## Kebutuhan Minimum

- Python **3.11+** (butuh `zoneinfo` dari pustaka standar)
- Koneksi internet
- **`GROQ_API_KEY`** — wajib untuk fitur chat
- `CF_ACCOUNT_ID` + `CF_API_TOKEN` — opsional, untuk generate gambar

## Butuh Bantuan Cepat?

| Masalah | Buka |
|---|---|
| Aplikasi tidak mau jalan | [Instalasi → Troubleshooting](instalasi.md#-troubleshooting) |
| "Fitur chat belum dikonfigurasi" | [Konfigurasi → Groq](konfigurasi.md#1-groq-api-key-wajib) |
| Tombol generate gambar tidak ada | [Konfigurasi → Cloudflare](konfigurasi.md#2-cloudflare-workers-ai-opsional) |
| Riwayat chat hilang | [FAQ](faq.md#kenapa-riwayat-chat-hilang-setelah-refresh) |
| Mau bikin link yang bisa dibagikan | [Deploy](deploy.md) |
