# Changelog

Semua perubahan penting pada **Ampera Trinity AI** dicatat di berkas ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.1.0/),
dan proyek ini memakai [Semantic Versioning](https://semver.org/lang/id/).

---

## [Belum dirilis]

### Ditambahkan
- Dokumentasi lengkap di folder `docs/`: instalasi, konfigurasi, fitur, panduan pengguna, arsitektur, deploy, dan FAQ
- `CONTRIBUTING.md` — panduan kontribusi, gaya kode, dan aturan arsitektur
- `LICENSE` — MIT License
- `CHANGELOG.md` — berkas ini
- `.streamlit/secrets.toml.example` — templat kredensial siap salin

### Diubah
- `README.md` ditulis ulang: badge, tabel fitur, mulai cepat, struktur proyek, dan tautan ke dokumentasi
- `.gitignore` diperluas — kini mencakup `.streamlit/secrets.toml`, `.env`, cache, dan berkas editor/OS

### Diketahui belum beres
- Pengaturan `stream_speed` (Lambat/Sedang/Cepat) belum memengaruhi `SENTENCE_STREAM_DELAY`
- Beberapa entri `MODEL_CATALOG` menunjuk ID model yang sama
- Belum ada test otomatis dan `Dockerfile` resmi

---

## [1.0.0]

Rilis awal aplikasi.

### Ditambahkan
- **Chat multi-model (Groq)** — 6 model dalam 4 tingkat: Trinity Easy, Normal, Hard, Extreme, dengan fallback otomatis
- **Analisis gambar** — hingga 5 gambar per pesan lewat model vision
- **Generate gambar** — Cloudflare Workers AI FLUX.1 schnell dengan progres bertahap
- **Input suara** — transkripsi Whisper Large v3 Turbo
- **Halaman Artefak** — 7 kategori ala Claude, thread terpisah per artefak
- **Penangkapan kode otomatis** — blok kode panjang dari jawaban disimpan sebagai artefak
- **Trinity Kursus** — 10 topik dengan kurikulum 4 modul otomatis
- **14 bahasa** — bahasa antarmuka dan bahasa jawaban Yuki diatur terpisah
- **Pengaturan 9 tab** — Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, Refleksi, Waktu & Fokus, Trinity Code
- **Persona Yuki** — 4 pilihan kepribadian, panggilan khusus, dan instruksi kustom
- **Animasi teks** — streaming per kalimat, caret berkedip, animasi "sedang berpikir", dan ~20 keyframes transisi UI
- **Proyek & riwayat** — pengelompokan obrolan, arsip otomatis, ekspor percakapan ke Markdown
- **Penanganan error ramah pengguna** — detail teknis tidak bocor ke antarmuka
