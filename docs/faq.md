# ❓ FAQ

Pertanyaan yang sering muncul seputar **Ampera Trinity AI**.

---

## Umum

### Apa itu Ampera Trinity AI?
Aplikasi web berbasis Streamlit dengan asisten AI bernama **Yuki**. Menggabungkan chat multi-model, analisis gambar, generate gambar, pembuatan artefak, dan kursus dalam satu tempat. Dibuat oleh **Ampera Official**.

### Apakah gratis?
Kodenya gratis dan open source (MIT). Tapi model AI-nya memanggil layanan pihak ketiga:
- **Groq** — punya tier gratis yang cukup besar untuk pemakaian pribadi.
- **Cloudflare Workers AI** — juga punya kuota gratis harian.

Jadi untuk pemakaian pribadi biasanya **tidak perlu bayar**.

### Siapa Yuki?
Persona asisten AI-nya: jenius, kocak, sedikit usil, suka lelucon receh, dan pakai emoji ekspresif. Kepribadiannya bisa diganti di Pengaturan → Umum → Kepribadian.

### Apakah butuh koneksi internet?
Ya. Semua model AI dipanggil lewat API, tidak ada yang berjalan lokal.

---

## Instalasi & Konfigurasi

### Python versi berapa yang dibutuhkan?
Minimal **3.11**. Aplikasi memakai `zoneinfo` dari pustaka standar.

### Di mana menaruh API key?
Di `.streamlit/secrets.toml`, atau sebagai environment variable. Lihat [konfigurasi.md](konfigurasi.md).

### Muncul "Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY)"
Aplikasi tidak menemukan key. Periksa:
1. File berada tepat di `.streamlit/secrets.toml`
2. Format TOML pakai tanda kutip: `GROQ_API_KEY = "gsk_..."`
3. Restart Streamlit setelah mengubah secrets

### Apakah wajib mengisi kredensial Cloudflare?
Tidak. Itu hanya untuk generate gambar. Tanpa kredensial tersebut, mode gambar disembunyikan dan fitur lain tetap normal.

### Bisakah memakai OpenAI atau Anthropic, bukan Groq?
Bisa dengan sedikit modifikasi. Engine memakai SDK `openai`, jadi cukup ubah `GROQ_BASE_URL` dan ID model di `config.py` ke provider apa pun yang kompatibel dengan API OpenAI.

---

## Pemakaian

### Kenapa riwayat chat hilang setelah refresh?
Karena semua data disimpan di `st.session_state` yang hanya hidup selama sesi browser. **Tidak ada database.** Kalau percakapan penting, gunakan **Unduh Chat** di sidebar untuk menyimpannya sebagai berkas Markdown.

Ingin riwayat permanen? Perlu menambahkan lapisan penyimpanan (SQLite/Postgres) — lihat [arsitektur.md](arsitektur.md#keterbatasan-yang-diketahui).

### Apa beda Trinity Easy, Normal, Hard, dan Extreme?
Tingkat kemampuan model. Easy paling cepat tapi paling dangkal, Extreme paling dalam tapi paling lambat. Rinciannya di [fitur.md](fitur.md#-1-multi-ai-groq).

### Kenapa jawaban muncul per kalimat, bukan langsung?
Itu disengaja. `stream_sentences()` menampilkan teks bertahap per kalimat dengan jeda 0,15 detik plus caret berkedip, supaya terasa hidup tapi tetap cepat dibaca.

### Pengaturan "Kecepatan aliran jawaban" tidak berpengaruh?
Betul — ini **keterbatasan yang diketahui**. Nilainya tersimpan di `settings["stream_speed"]`, tapi `stream_sentences()` masih memakai jeda tetap `SENTENCE_STREAM_DELAY = 0.15`. Ketiga pilihan (Lambat/Sedang/Cepat) saat ini menghasilkan kecepatan yang sama.

### Kenapa jawaban tetap lama padahal pertanyaannya sederhana?
Ada **durasi berpikir minimum** (`min_think_seconds`, bawaan 10 detik) supaya animasi tidak berkedip. Bisa dikecilkan di Pengaturan → Umum.

### Berapa gambar yang bisa dikirim sekaligus?
Maksimal **5** per pesan. Format: png, jpg, jpeg, webp, gif.

### Apakah Yuki ingat percakapan sebelumnya?
Dalam satu sesi, ya — 40 pesan terakhir dikirim sebagai konteks. Antar sesi, tidak, kecuali kamu menuliskannya di Pengaturan → **Memori**.

### Kenapa halaman Artefak dan Kursus punya riwayat sendiri?
Supaya konteksnya tidak tercampur. Tiap artefak dan tiap kursus punya thread terpisah, jadi Yuki tetap fokus pada satu pekerjaan.

### Bagaimana cara mengekspor percakapan?
Sidebar → **Unduh Chat**. Menghasilkan berkas `.md`.

### Bagaimana cara mengubah bahasa jawaban tanpa mengubah bahasa menu?
Sidebar → **Bahasa**. Ada dua pengaturan terpisah: bahasa antarmuka (`ui_lang`) dan bahasa Yuki (`yuki_lang`).

---

## Error

### "Model chat tidak tersedia lagi di provider"
Provider menghentikan model tersebut. Pilih tingkat model lain. Engine sebetulnya punya fallback otomatis, tapi kalau semua cadangan juga habis, ID model di `config.py` perlu diperbarui.

### "Kuota chat sedang penuh"
Batas rate limit tercapai. Tunggu beberapa menit, atau pakai API key milikmu sendiri lewat Pengaturan → **Trinity Code**.

### "Gagal membuat gambar"
Bisa karena kuota Cloudflare habis, prompt ditolak filter, atau jaringan bermasalah. Coba prompt lain atau ulangi nanti.

### Kenapa pesan errornya tidak detail?
Disengaja. `errors.py` menyembunyikan status HTTP dan jejak provider supaya informasi teknis tidak bocor ke pengguna. Aktifkan `advanced_errors` di tab Trinity Code untuk melihat detailnya.

### Ikon tampil sebagai teks `:material_xxx:`
Versi Streamlit terlalu lama. Jalankan `pip install --upgrade streamlit`.

---

## Deployment

### Bagaimana cara membuat link yang bisa dibagikan?
Paling mudah lewat **Streamlit Community Cloud** (gratis). Panduan lengkap: [deploy.md](deploy.md).

### Apakah aman dipublikasikan?
Kodenya tidak menyimpan key di dalam file, jadi aman dari sisi itu. Tapi aplikasi **tidak punya autentikasi** — siapa pun yang punya link akan memakai kuota API-mu. Untuk publik luas, tambahkan gerbang kata sandi atau minta pengunjung mengisi key sendiri.

### Apakah ada Dockerfile?
Belum ada di repo, tapi contoh lengkapnya tersedia di [deploy.md](deploy.md#-3-docker) dan tinggal disalin.

### Kenapa `enableXsrfProtection = false`?
Untuk memudahkan pengembangan lokal dan preview. Kalau dipasang di server publik sendiri, sebaiknya diubah jadi `true`.

### API key saya terlanjur ter-push ke GitHub, bagaimana?
**Segera cabut (revoke) key tersebut** di dashboard Groq/Cloudflare lalu buat yang baru. Menghapus commit saja tidak cukup — key yang sudah terekspos di riwayat Git harus dianggap bocor selamanya.

---

## Pengembangan

### Bagaimana cara menambah model, bahasa, atau kursus?
Semua data statis ada di `config.py`. Lihat [arsitektur.md → Cara Menambah Fitur](arsitektur.md#cara-menambah-fitur).

### Kenapa tidak memakai fitur multipage bawaan Streamlit?
Supaya sidebar dan CSS-nya bisa dikustomisasi sepenuhnya. Routing dilakukan manual lewat `st.session_state.page`.

### Kenapa `styles.py` sebesar itu?
Berisi seluruh CSS aplikasi (~1.790 baris), termasuk sekitar 20 `@keyframes` animasi, dalam satu tempat supaya mudah dicari.

### Apakah ada test otomatis?
Belum. Kontribusi untuk menambahkan `pytest` pada fungsi murni (`_sentence_chunks`, `extract_image_bytes`, `public_error_*`) sangat diterima — lihat [CONTRIBUTING.md](../CONTRIBUTING.md).

### Bagaimana cara berkontribusi?
Fork, buat branch, lalu kirim pull request. Panduannya di [CONTRIBUTING.md](../CONTRIBUTING.md).

---

Belum terjawab? Buka [issue di GitHub](https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai/issues).
