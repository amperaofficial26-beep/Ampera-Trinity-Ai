# Ampera Trinity AI

**Multi AI · Generate Foto · Chat — by Ampera Official**

Aplikasi web AI berbasis [Streamlit](https://streamlit.io) dengan asisten AI **Yuki**. Satu aplikasi untuk chat multi-model, analisis gambar, artefak, kursus, dan berbagai pengaturan lengkap.

Dibuat oleh **Ampera Official — Palembang, Indonesia**. Punya produk lain juga? Cek **Ampera Upscale Studio** untuk memperbesar & mempertajam gambar dengan AI.

## ✨ Fitur Utama

- 💬 **Multi AI** — 14 tingkat model (Trinity Seed sampai Trinity Sovereign) dari berbagai provider, dengan fallback otomatis
- 🖼️ **Analisis & generate gambar** — model bervision + image engine
- 🗂️ **Artefak** — jawaban dengan kategori ala Claude
- 🎓 **Trinity Kursus** — Yuki jadi mentor di thread khusus
- 🌐 **14 bahasa** — antarmuka + bahasa jawaban bisa diganti
- ⚙️ **Pengaturan lengkap** — 8 tab: Umum, Akun, Privasi, Penagihan, Kemampuan, Memori, Refleksi, Waktu & Fokus

## 💎 Paket Trinity Pro

| Paket | Harga | Catatan |
|---|---|---|
| Bulanan | **Rp 19.000** / bulan | Bebas berhenti kapan saja |
| Tahunan | **Rp 49.000** / tahun | Paling hemat — setara Rp 4.083/bulan |
| Selamanya | **Rp 435.000** sekali bayar | Bayar sekali, pakai selamanya |

Untuk berlangganan, hubungi **amperaofficial26@gmail.com** — pembayaran diatur langsung di sana.

## 🚀 Menjalankan Secara Lokal

1. Clone repo ini:
   ```bash
   git clone https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai.git
   cd Ampera-Trinity-Ai
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Siapkan API key Groq (lihat bagian di bawah), lalu jalankan:
   ```bash
   streamlit run app.py
   ```

## 🔑 Konfigurasi API Key

Aplikasi membaca kredensial dari **Streamlit Secrets** atau environment variable (lihat `config.py`). Untuk Streamlit Cloud, tambahkan di *Settings → Secrets*:

```toml
GROQ_API_KEY = "gsk_..."
```

## 📁 Struktur Proyek

| File | Fungsi |
|---|---|
| `app.py` | File utama: routing & navigasi antar halaman |
| `config.py` | Konstanta & katalog (model, bahasa, artefak, kursus, identitas & harga Ampera) |
| `state.py` | Manajemen state sesi |
| `chat_handlers.py` | Handler kirim pesan & render input chat |
| `sidebar.py` | Sidebar navigasi |
| `ui_helpers.py` | Komponen render kecil |
| `engines/` | Engine AI (Groq & image) |
| `styles.py` | Seluruh CSS |
| `anim.py` | Animasi halaman & elemen (iOS-style page transition) |
| `panel_file.py` | Dock file "daftar buatan Yuki" |
| `icons.py` | Ikon (Material Icons) |
| `logo.py`, `trinity_logo.py` | Logo |

---

© Ampera Official — Palembang, Indonesia · amperaofficial26@gmail.com
