# ✨ Fitur

Rincian lengkap setiap kemampuan **Ampera Trinity AI**.

---

## 💬 1. Multi AI (Groq)

Enam pilihan model yang dikelompokkan jadi empat tingkat kesulitan.

| Tingkat | Model | Cocok untuk |
|---|---|---|
| **Trinity Easy** | `openai/gpt-oss-20b` | Ngobrol santai, tanya jawab cepat, coding ringan |
| **Trinity Normal** | `groq/compound-mini` | Pertanyaan yang butuh info terbaru dari web |
| **Trinity Normal** | `qwen/qwen3.6-27b` | Pesan yang menyertakan gambar |
| **Trinity Hard** ⭐ | `groq/compound` | Riset mendalam, browsing + eksekusi kode |
| **Trinity Hard** ⭐ | `qwen/qwen3.6-27b` | Matematika & penalaran bertahap |
| **Trinity Extreme** ⭐ | `openai/gpt-oss-120b` | Tugas paling berat, analisis panjang |

**Cara kerja:**
- Jawaban di-*stream* dari Groq lewat SDK `openai` yang diarahkan ke `https://api.groq.com/openai/v1`.
- Hanya **40 pesan terakhir** yang dikirim sebagai konteks (`MAX_HISTORY_MESSAGES`).
- Jika model ditolak provider, engine otomatis pindah ke model cadangan (`GROQ_MODEL_FALLBACKS`) tanpa mengganggu pengguna.
- Pemilihan model bisa ditimpa otomatis: ada gambar → model vision; tombol web search aktif → `groq/compound`.

---

## 👁️ 2. Analisis Gambar (Vision)

- Kirim hingga **5 gambar** per pesan (`MAX_IMAGES_PER_MESSAGE`).
- Format: `png`, `jpg`, `jpeg`, `webp`, `gif`.
- Gambar diresize & dikonversi ke base64 oleh Pillow sebelum dikirim.
- Hanya gambar dari **4 pesan terakhir** yang ikut dikirim ulang (`VISION_RECENT_MESSAGES`) supaya payload tidak membengkak.
- Model: `qwen/qwen3.6-27b` dengan cadangan `qwen/qwen3.8-27b`.

Contoh pemakaian: minta jelaskan diagram, baca teks di foto, kritik desain UI, identifikasi objek.

---

## 🎨 3. Generate Gambar (Cloudflare FLUX)

- Model **FLUX.1 schnell** (`@cf/black-forest-labs/flux-1-schnell`) lewat Cloudflare Workers AI.
- 4 langkah difusi (`CF_DEFAULT_STEPS`) — cepat, hemat kuota.
- Ada **progress bar bertahap** dengan label yang berubah dan durasi minimum 10 detik supaya terasa mulus.
- Respons base64 di-parse fleksibel oleh `extract_image_bytes()` (mendukung beberapa bentuk struktur JSON Cloudflare).
- Error diterjemahkan jadi pesan ramah oleh `errors.py` — kuota penuh, timeout, dsb, tanpa membocorkan detail teknis.

> Aktif hanya bila `CF_ACCOUNT_ID` dan `CF_API_TOKEN` terisi.

---

## 🎙️ 4. Input Suara (Speech-to-Text)

- Model **`whisper-large-v3-turbo`** di Groq.
- Rekam langsung dari `st.chat_input` (butuh Streamlit versi baru yang mendukung `accept_audio`).
- Hasil transkripsi masuk ke kolom pesan, bisa diedit sebelum dikirim.
- Pengaturan privasi `keep_voice` (bawaan **mati**) menentukan apakah audio disimpan.

---

## 🗂️ 5. Artefak

Dua hal berbeda memakai nama "artefak":

### a. Halaman Artefak — 7 kategori
Kotak pilihan ala Claude. Setiap kategori punya *brief* siap pakai yang membuat Yuki menawarkan 3 ide lebih dulu, baru mengerjakan pilihanmu.

| Kategori | Contoh hasil |
|---|---|
| 🌐 Aplikasi dan situs web | Landing page, dashboard, web app interaktif |
| 📄 Dokumen dan templat | Proposal, CV, surat, laporan |
| 🎮 Permainan | Teka-teki, arcade, kuis berbasis Canvas |
| ✅ Alat produktivitas | To-do list, kalkulator, tracker, timer |
| 🖌️ Proyek kreatif | Cerita, puisi, skrip, konsep desain |
| ❓ Kuis atau survei | Kuis interaktif dengan skor otomatis |
| ➕ Mulai dari awal | Kanvas kosong, jelaskan idemu sendiri |

Tiap artefak punya **thread percakapan sendiri**, jadi tidak tercampur dengan chat utama.

### b. Penangkapan kode otomatis
`_capture_artifacts_from_reply()` memindai setiap jawaban Yuki, mengambil blok ```` ``` ```` yang panjangnya **lebih dari 40 karakter**, lalu menyimpannya sebagai artefak ringan yang bisa dibuka lagi dari sidebar — tanpa perlu scroll riwayat panjang.

---

## 🎓 6. Trinity Kursus

Sepuluh kursus dengan Yuki sebagai mentor:

| | Kursus | Level |
|---|---|---|
| 📣 | Pemasaran | Pemula → Lanjut |
| 🤝 | Penjualan | Pemula → Lanjut |
| 🎨 | Desain | Pemula → Lanjut |
| ✍️ | Copywriting | Pemula → Menengah |
| ✨ | Branding | Menengah |
| 💰 | Keuangan | Pemula |
| ⏱️ | Produktivitas | Pemula |
| 🎤 | Public speaking | Pemula → Menengah |
| 📸 | Konten kreator | Pemula → Lanjut |
| 🤖 | AI untuk bisnis | Pemula |

Setiap kursus otomatis punya **kurikulum 4 modul** (`course_curriculum()`):

1. Fondasi — istilah penting & peta besar
2. Alat & workflow yang benar-benar terpakai
3. Strategi tingkat lanjut + studi kasus nyata
4. Proyek praktik & evaluasi hasil belajar

Sama seperti artefak, tiap kursus punya thread terpisah.

---

## 🌐 7. Multi Bahasa (14)

Bahasa **antarmuka** dan bahasa **jawaban Yuki** diatur terpisah.

**Level Penuh (11):** Indonesia, English, Melayu, 日本語, 한국어, 中文, Español, Português, Français, Deutsch
**Level Beta (4):** Basa Sunda, Basa Jawa, العربية, हिन्दी

---

## ⚙️ 8. Pengaturan — 9 Tab

| Tab | Isi singkat |
|---|---|
| **Umum** | Tema, ukuran teks, mode ringkas, kecepatan aliran jawaban, kepribadian Yuki |
| **Akun** | Nama tampilan, email, username, bio |
| **Privasi** | Web search, simpan riwayat, simpan suara, analitik, personalisasi, sinkron cloud |
| **Penagihan** | Paket Free / Trinity Pro, siklus tagihan, metode pembayaran |
| **Kemampuan** | Saklar on/off: web search, artefak, suara, vision, generate gambar |
| **Memori** | Daftar hal yang diingat Yuki, memori otomatis |
| **Refleksi** | Target, kebiasaan, frekuensi, nada dorongan |
| **Waktu & Fokus** | Timer fokus/istirahat, jam kerja, zona waktu, pengingat |
| **Trinity Code** | Isi API key sendiri, temperature, mode error detail |

---

## ✍️ 9. Animasi & Pengalaman Visual

| Animasi | Di mana | Cara kerja |
|---|---|---|
| **Streaming per kalimat** | Jawaban Yuki | `stream_sentences()` memecah teks per kalimat/baris (regex `[.!?]+\|\n`), tampil bertahap dengan jeda 0,15 detik |
| **Caret berkedip** | Ujung bubble saat mengetik | CSS `caretBlink 0.8s step-end infinite` |
| **"Sedang berpikir"** | Sebelum jawaban muncul | Frasa berputar + shimmer teks (`phraseCycle`, `shimmerSweep`, `thinkFadeIn`) |
| **Logo berdenyut** | Saat memproses | `logoPulse`, `starPulse`, `shineSweep` |
| **Progres gambar** | Mode generate gambar | Bar bertahap + label berubah (`pendingShimmer`, `pendingSpin`) |
| **Transisi UI** | Tombol, kartu, halaman | `trinityBtnIn`, `trinityCardIn`, `trinityPageIn`, `trinityProIn` |

Ada juga **durasi berpikir minimum** (`min_think_seconds`, bawaan 10 detik): kalau model menjawab lebih cepat, animasi tetap ditahan supaya transisinya tidak berkedip.

> Catatan: pecahan dibuat per **kalimat**, bukan per karakter — lebih cepat dibaca tapi tetap terasa hidup.

---

## 📂 10. Proyek, Riwayat, dan Ekspor

| Fitur | Keterangan |
|---|---|
| **Proyek** | Kelompokkan obrolan dalam wadah bernama, dipilih lewat dialog di sidebar |
| **Riwayat percakapan** | Obrolan lama diarsipkan otomatis; judulnya diambil dari 48 karakter pertama pesan pengguna |
| **Chat baru** | Mengarsipkan obrolan aktif lalu mengosongkan thread |
| **Sesuaikan** | Atur panggilan untukmu + instruksi khusus yang selalu diikuti Yuki |
| **Unduh chat** | Ekspor seluruh percakapan sebagai berkas Markdown (`.md`) |
| **Umpan balik** | Tombol 👍 / 👎 di tiap jawaban |
| **Salin** | Tombol salin isi jawaban |

---

## 🛡️ 11. Penanganan Error

`errors.py` menerjemahkan error teknis jadi kalimat yang aman dibaca pengguna:

| Situasi | Pesan yang tampil |
|---|---|
| Key salah / 401 | "Layanan chat sedang tidak tersedia (konfigurasi). Coba lagi nanti." |
| Model dihentikan / 404 | "Model chat tidak tersedia lagi di provider. Coba pilih model lain." |
| Kuota habis / 429 | "Kuota chat sedang penuh. Coba lagi nanti." |
| Timeout | "Respons terlalu lama. Coba lagi." |
| Lainnya | "Gagal membalas. Coba kirim ulang atau mulai obrolan baru." |

Status HTTP dan jejak provider **tidak pernah** ditampilkan ke UI, kecuali `advanced_errors` diaktifkan di tab Trinity Code.

---

## ➡️ Selanjutnya

- [Panduan pengguna langkah demi langkah](panduan-pengguna.md)
- [Arsitektur kode](arsitektur.md)
