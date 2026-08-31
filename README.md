<div align="center">

<img src="assets/logo_thinking_small.png" width="120" alt="Ampera Trinity AI" />

# Ampera Trinity AI

**Multi AI · Generate Foto · Chat — by Ampera Official**

Aplikasi web AI serba bisa berbasis [Streamlit](https://streamlit.io) dengan asisten bernama **Yuki**.
Satu aplikasi untuk chat multi-model, analisis & generate gambar, artefak, kursus, dan pengaturan lengkap.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036)](https://groq.com)
[![Cloudflare FLUX](https://img.shields.io/badge/Image-Cloudflare%20FLUX-F38020?logo=cloudflare&logoColor=white)](https://developers.cloudflare.com/workers-ai/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Dokumentasi](docs/) · [Instalasi](docs/instalasi.md) · [Konfigurasi](docs/konfigurasi.md) · [Deploy](docs/deploy.md) · [FAQ](docs/faq.md)

</div>

---

## ✨ Fitur Utama

| | Fitur | Keterangan |
|---|---|---|
| 💬 | **Multi AI (Groq)** | 4 tingkat model: Trinity Easy, Normal, Hard, Extreme — lengkap dengan fallback otomatis |
| 👁️ | **Analisis gambar** | Kirim sampai 5 gambar sekaligus, dibaca model vision |
| 🎨 | **Generate gambar** | Cloudflare Workers AI (FLUX.1 schnell) dengan progres bertahap |
| 🎙️ | **Input suara** | Transkripsi otomatis lewat Whisper Large v3 Turbo |
| 🗂️ | **Artefak** | 7 kategori ala Claude + penangkapan blok kode otomatis dari jawaban |
| 🎓 | **Trinity Kursus** | 10 kursus, Yuki jadi mentor di thread terpisah |
| 🌐 | **14 bahasa** | Bahasa antarmuka & bahasa jawaban Yuki bisa dibedakan |
| ⚙️ | **Pengaturan 9 tab** | Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, Refleksi, Waktu & Fokus, Trinity Code |
| ✍️ | **Animasi teks** | Jawaban muncul bertahap per kalimat + caret berkedip & animasi "sedang berpikir" |

Detail lengkap tiap fitur ada di **[docs/fitur.md](docs/fitur.md)**.

---

## 🚀 Mulai Cepat

```bash
# 1. Clone
git clone https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai.git
cd Ampera-Trinity-Ai

# 2. Virtual environment (disarankan)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependensi
pip install -r requirements.txt

# 4. API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
#    lalu isi GROQ_API_KEY di file tersebut

# 5. Jalankan
streamlit run app.py
```

Buka <http://localhost:8501>. Panduan lebih rinci: **[docs/instalasi.md](docs/instalasi.md)**.

---

## 🔑 Konfigurasi Singkat

Aplikasi membaca kredensial dari **Streamlit Secrets** atau **environment variable**:

| Variabel | Wajib? | Untuk |
|---|---|---|
| `GROQ_API_KEY` | ✅ Ya | Chat, vision, transkripsi suara |
| `CF_ACCOUNT_ID` | ⬜ Opsional | Generate gambar |
| `CF_API_TOKEN` | ⬜ Opsional | Generate gambar |

Tanpa key, aplikasi tetap jalan — fitur terkait otomatis dinonaktifkan lewat flag `CHAT_READY` / `IMAGE_READY`.
Cara mendapatkan key: **[docs/konfigurasi.md](docs/konfigurasi.md)**.

> ⚠️ **Jangan pernah commit `secrets.toml` atau API key ke Git.** File tersebut sudah masuk `.gitignore`.

---

## 🌍 Deploy Jadi Link Publik

Cara tercepat mendapatkan link yang bisa dibagikan adalah **Streamlit Community Cloud** (gratis):

1. Push repo ini ke GitHub.
2. Buka <https://share.streamlit.io> → **New app** → pilih repo ini, branch, dan `app.py`.
3. Di **Advanced settings → Secrets**, tempel:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
4. Deploy → dapat link `https://<nama-app>.streamlit.app`.

Opsi lain (Hugging Face Spaces, Docker, VPS): **[docs/deploy.md](docs/deploy.md)**.

---

## 📁 Struktur Proyek

```
Ampera-Trinity-Ai/
├── app.py                 # Entry point + routing 9 halaman
├── config.py              # Konstanta, katalog model/bahasa/kursus, pembacaan secrets
├── state.py               # Manajemen session_state: settings & thread pesan
├── chat_handlers.py       # Handler kirim pesan, input chat, mode gambar
├── sidebar.py             # Sidebar navigasi + dialog Proyek/Artefak/Sesuaikan
├── ui_helpers.py          # Komponen render (bubble, animasi teks, export .md)
├── styles.py              # Seluruh CSS & keyframes animasi
├── icons.py               # Helper ikon SVG & Material Symbols
├── logo.py                # Logo utama (base64)
├── trinity_logo.py        # Logo alternatif
├── errors.py              # Pesan error ramah pengguna
├── engines/
│   ├── groq_engine.py     # Chat streaming, fallback model, vision, STT
│   └── image_engine.py    # Generate gambar Cloudflare FLUX
├── assets/                # Gambar statis
├── docs/                  # 📚 Dokumentasi lengkap
└── .streamlit/config.toml # Konfigurasi server Streamlit
```

Penjelasan alur data & tanggung jawab tiap modul: **[docs/arsitektur.md](docs/arsitektur.md)**.

---

## 📚 Dokumentasi

| Dokumen | Isi |
|---|---|
| [docs/instalasi.md](docs/instalasi.md) | Prasyarat, langkah install, troubleshooting |
| [docs/konfigurasi.md](docs/konfigurasi.md) | API key, secrets, semua opsi pengaturan |
| [docs/fitur.md](docs/fitur.md) | Rincian setiap fitur & halaman |
| [docs/panduan-pengguna.md](docs/panduan-pengguna.md) | Cara pakai dari sisi pengguna |
| [docs/arsitektur.md](docs/arsitektur.md) | Struktur kode, alur data, cara menambah fitur |
| [docs/deploy.md](docs/deploy.md) | Streamlit Cloud, Hugging Face, Docker, VPS |
| [docs/faq.md](docs/faq.md) | Pertanyaan yang sering muncul |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Panduan kontribusi & gaya kode |
| [CHANGELOG.md](CHANGELOG.md) | Riwayat perubahan |

---

## 🛠️ Teknologi

- **Python 3.11+** · **Streamlit** — UI & state
- **openai** SDK (menunjuk ke endpoint Groq) — chat, vision, Whisper
- **requests** — Cloudflare Workers AI
- **Pillow** — pemrosesan gambar

---

## 🤝 Kontribusi

Pull request dan issue sangat diterima. Baca **[CONTRIBUTING.md](CONTRIBUTING.md)** lebih dulu.

## 📄 Lisensi

Dirilis di bawah [MIT License](LICENSE).

---

<div align="center">

Dibuat dengan ❤️ oleh **Ampera Official**

</div>
