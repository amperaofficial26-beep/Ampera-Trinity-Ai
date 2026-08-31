# 🧭 Panduan Pengguna

Cara memakai **Ampera Trinity AI** dari sisi pengguna. Tidak perlu paham kode.

---

## Sekilas Antarmuka

```
┌───────────────┬──────────────────────────────────────┐
│               │                                      │
│   SIDEBAR     │           AREA UTAMA                 │
│               │                                      │
│ • Chat baru   │   Sapaan besar + riwayat pesan       │
│ • Proyek      │                                      │
│ • Artefak     │                                      │
│ • Kursus      │                                      │
│ • Riwayat     │   ┌────────────────────────────┐     │
│ • Pengaturan  │   │  ➕  Ketik pesan…    🎙 ➤  │     │
│ • Bahasa      │   └────────────────────────────┘     │
│ • Bantuan     │                                      │
└───────────────┴──────────────────────────────────────┘
```

Saat pertama dibuka, halaman sengaja dibuat bersih: hanya sapaan besar dan kolom input di tengah.

---

## 1. Mengobrol dengan Yuki

1. Ketik pertanyaan di kolom bawah.
2. Tekan **Enter** atau klik tombol kirim.
3. Muncul animasi "sedang berpikir", lalu jawaban keluar bertahap per kalimat.

**Yuki bisa membantu:** ngobrol santai, coding, matematika, ide kreatif, analisis gambar, dan menyusun dokumen.

### Tips prompt yang bagus

| Kurang bagus | Lebih bagus |
|---|---|
| "buatkan website" | "buatkan landing page satu file HTML untuk kedai kopi, warna cokelat hangat, ada menu dan tombol WhatsApp" |
| "jelaskan Python" | "jelaskan konsep decorator Python untuk pemula, pakai 2 contoh kode singkat" |
| "perbaiki kode ini" | "perbaiki kode ini, errornya `KeyError: 'nama'` saat memproses baris kosong" + tempel kodenya |

---

## 2. Memilih Tingkat Model

Pemilih model ada di dekat kolom input.

| Pilih | Kalau kamu butuh |
|---|---|
| **Trinity Easy** | Jawaban cepat, pertanyaan ringan |
| **Trinity Normal** | Info terbaru dari web, atau kirim gambar |
| **Trinity Hard** ⭐ | Riset serius, matematika, eksekusi kode |
| **Trinity Extreme** ⭐ | Tugas berat yang butuh analisis panjang |

> Semakin tinggi tingkatnya, semakin lambat tapi semakin dalam jawabannya. Mulai dari Easy, naikkan kalau kurang memuaskan.

---

## 3. Mengirim Gambar

1. Klik tombol **➕** di kiri kolom input.
2. Pilih hingga **5 gambar** (png, jpg, jpeg, webp, gif).
3. Pratinjau muncul di atas kolom input — bisa dihapus sebelum dikirim.
4. Ketik pertanyaanmu, misalnya *"tolong jelaskan grafik ini"*, lalu kirim.

Aplikasi otomatis berpindah ke model vision, tidak perlu diatur manual.

---

## 4. Membuat Gambar

1. Aktifkan **mode gambar** lewat tombol di dekat kolom input.
2. Tulis deskripsi gambar (prompt) — makin detail makin bagus.
3. Tunggu progress bar selesai (± 10 detik).
4. Gambar muncul di percakapan dan bisa diunduh.

**Contoh prompt:**
> kucing oranye memakai kacamata bulat, duduk di tumpukan buku, cahaya senja lembut, gaya ilustrasi cat air

> Tombol ini hanya muncul kalau pemilik aplikasi sudah mengisi kredensial Cloudflare.

---

## 5. Bicara Lewat Suara

1. Klik ikon **🎙 mikrofon** di kolom input.
2. Izinkan akses mikrofon di browser.
3. Bicara, lalu hentikan rekaman.
4. Teks hasil transkripsi muncul — periksa dan edit bila perlu, lalu kirim.

---

## 6. Mencari di Web

Aktifkan tombol **web search** sebelum mengirim pesan. Aplikasi akan memakai model `Trinity Hard` yang mampu browsing, cocok untuk pertanyaan tentang berita atau harga terbaru.

---

## 7. Halaman Artefak

Untuk membuat sesuatu yang "jadi", bukan sekadar mengobrol.

1. Sidebar → **Artefak**.
2. Pilih salah satu dari 7 kotak kategori.
3. Yuki menawarkan **3 ide** terlebih dahulu.
4. Pilih satu, lalu Yuki mengerjakannya sampai selesai.

Setiap artefak punya percakapan sendiri, jadi bisa dilanjutkan kapan saja tanpa tercampur chat utama.

Blok kode panjang dari jawaban Yuki juga otomatis tersimpan sebagai artefak — buka lewat sidebar untuk menyalinnya lagi.

---

## 8. Trinity Kursus

1. Sidebar → **Trinity kursus**.
2. Pilih topik (Pemasaran, Desain, Copywriting, dll).
3. Yuki jadi mentor dan menyusun 4 modul.
4. Belajar bertahap, tanya bebas di tengah jalan.

---

## 9. Mengganti Bahasa

Sidebar → **Bahasa**. Ada dua pengaturan terpisah:

- **Bahasa antarmuka** — teks tombol & menu.
- **Bahasa Yuki** — bahasa jawabannya.

Contoh: antarmuka Indonesia, tapi Yuki menjawab dalam English. Tersedia 14 bahasa.

---

## 10. Mengatur Kepribadian Yuki

**Cara cepat** — sidebar → **Sesuaikan**:
- **Panggilan** — mau dipanggil apa oleh Yuki.
- **Instruksi khusus** — misalnya *"selalu jawab singkat dan pakai poin-poin"*.

**Cara lengkap** — Pengaturan → Umum → **Kepribadian**:

| Pilihan | Gaya jawaban |
|---|---|
| Santai & kocak | Banyak candaan receh dan emoji (bawaan) |
| Serius & ringkas | Langsung ke inti, minim basa-basi |
| Mentor sabar | Langkah demi langkah, ada contoh & pengecekan |
| Profesional formal | Bahasa formal, tanpa emoji berlebihan |

---

## 11. Riwayat, Proyek, dan Ekspor

| Ingin | Lakukan |
|---|---|
| Mulai obrolan baru | Sidebar → **Chat baru** (obrolan lama otomatis diarsipkan) |
| Buka obrolan lama | Klik judulnya di daftar riwayat sidebar |
| Kelompokkan obrolan | Sidebar → dialog **Proyek** → buat proyek baru |
| Simpan percakapan | Sidebar → **Unduh Chat** → menghasilkan berkas `.md` |
| Beri penilaian | Tombol 👍 / 👎 di bawah jawaban |
| Salin jawaban | Tombol salin di bawah jawaban |

> ⚠️ Riwayat hanya bertahan selama tab browser terbuka. Tutup atau refresh = hilang. Unduh dulu kalau penting.

---

## 12. Timer Fokus

Pengaturan → **Waktu dan fokus**: atur durasi fokus (bawaan 25 menit), istirahat (5 menit), jam kerja, dan pengingat. Cocok untuk metode Pomodoro sambil ditemani Yuki.

---

## 13. Memori

Pengaturan → **Memori**: simpan hal-hal yang ingin selalu diingat Yuki, misalnya *"saya pakai Python dan lebih suka contoh dengan FastAPI"*. Bisa dimatikan lewat saklar `memory_on`.

---

## ❓ Masalah Umum

| Gejala | Solusi |
|---|---|
| "Fitur chat belum dikonfigurasi" | Pemilik aplikasi belum memasang API key |
| "Kuota chat sedang penuh" | Batas pemakaian tercapai, tunggu beberapa saat |
| "Model chat tidak tersedia lagi" | Pilih tingkat model lain |
| Jawaban terpotong | Minta *"lanjutkan"* pada pesan berikutnya |
| Jawaban keliru | Naikkan tingkat model, atau perjelas pertanyaan |
| Gambar gagal dibuat | Ganti prompt atau ulangi beberapa saat lagi |

Selebihnya: **[FAQ](faq.md)**.
