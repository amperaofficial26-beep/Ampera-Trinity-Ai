# 🖥️ Situs Dokumentasi (GitHub Pages)

Dokumentasi ini juga terbit sebagai situs web di **GitHub Pages**:

> **<https://amperaofficial26-beep.github.io/Ampera-Trinity-Ai/>**

Halaman ini menjelaskan cara kerjanya, cara membangunnya secara lokal, dan cara menambah halaman baru.

---

## Cara Kerjanya

```
docs/*.md  ──┐
CONTRIBUTING.md ─┤
CHANGELOG.md ────┤──▶  tools/build_site.py  ──▶  _site/  ──▶  GitHub Pages
tools/theme/ ────┘         (Python + markdown)      (HTML statis)
```

Berkas Markdown adalah **satu-satunya sumber kebenaran**. Situs dibuat ulang dari berkas itu, jadi isi dokumentasi di GitHub dan di situs tidak pernah berbeda.

### Kenapa tidak memakai Jekyll?

| Alasan | Penjelasan |
|---|---|
| Tanpa dependensi Ruby | Cukup Python yang memang sudah dipakai proyek ini |
| Kontrol penuh atas tampilan | Tema "Beige hangat" dibuat menyesuaikan aplikasi |
| Bisa diuji lokal | Jalankan satu perintah, hasilnya persis seperti di produksi |
| Build cepat | Sekitar satu detik untuk seluruh situs |

Berkas `.nojekyll` otomatis dibuat di hasil build supaya GitHub Pages menyajikan HTML apa adanya tanpa memproses ulang.

---

## Berkas yang Terlibat

| Berkas | Fungsi |
|---|---|
| `tools/build_site.py` | Pembangun situs: Markdown → HTML, sidebar, daftar isi, peta situs |
| `tools/check_links.py` | Memeriksa tautan menggantung sebelum diterbitkan |
| `tools/theme/assets/style.css` | Seluruh tampilan situs (tema Beige hangat) |
| `tools/theme/assets/highlight.css` | Warna sorotan sintaks blok kode |
| `tools/theme/assets/script.js` | Menu mobile, pencarian sidebar, tombol salin, sorot daftar isi |
| `tools/pages-workflow.yml` | Templat alur kerja GitHub Actions (pasang sekali, lihat di bawah) |
| `.github/workflows/pages.yml` | Alur kerja aktif setelah templat dipasang |
| `_site/` | Hasil build — **tidak** ikut Git, dibuat ulang oleh CI |

---

## Membangun Secara Lokal

```bash
pip install markdown pygments

# Bangun saja
python tools/build_site.py

# Bangun lalu buka server lokal di http://localhost:8000
python tools/build_site.py --serve

# Periksa tautan
python tools/check_links.py
```

Hasilnya ada di folder `_site/`.

---

## Penerbitan Otomatis

Alur kerja `.github/workflows/pages.yml` (templat: `tools/pages-workflow.yml`) berjalan setiap kali ada **push ke `main`** yang menyentuh:

- `docs/**`
- `tools/**`
- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- `assets/**`

Langkahnya: pasang Python → bangun situs → periksa tautan → terbitkan. Kalau ada tautan rusak, penerbitan **dibatalkan** supaya situs yang tayang tidak pernah membawa tautan mati.

Bisa juga dijalankan manual lewat tab **Actions → Terbitkan Dokumentasi → Run workflow**.

### Setup satu kali di GitHub

**Langkah 1 — pasang alur kerjanya.**
Templatnya ada di `tools/pages-workflow.yml`. Salin isinya, lalu di GitHub pilih
**Add file → Create new file**, beri nama `.github/workflows/pages.yml`,
tempel isinya, dan commit ke `main`.

> Berkas ini tidak bisa dibuat oleh otomasi karena GitHub mewajibkan izin khusus
> (`workflows`) untuk menulis ke folder `.github/workflows/`. Karena itu templatnya
> disimpan di `tools/` dan dipasang manual sekali saja.

**Langkah 2 — aktifkan Pages.**
Repositori → **Settings** → **Pages** → bagian *Build and deployment* →
**Source: GitHub Actions**.

Cukup sekali; setelah itu semuanya berjalan otomatis.

---

## Isi Situs

| Halaman | Sumber |
|---|---|
| Beranda (landing page) | Ditulis langsung di `tools/build_site.py` |
| Ikhtisar Dokumentasi | `docs/README.md` |
| Instalasi | `docs/instalasi.md` |
| Konfigurasi | `docs/konfigurasi.md` |
| Deploy | `docs/deploy.md` |
| Fitur | `docs/fitur.md` |
| Panduan Pengguna | `docs/panduan-pengguna.md` |
| FAQ | `docs/faq.md` |
| Arsitektur | `docs/arsitektur.md` |
| Situs Dokumentasi | `docs/situs-dokumentasi.md` (halaman ini) |
| Kontribusi | `CONTRIBUTING.md` |
| Changelog | `CHANGELOG.md` |

Ditambah `404.html`, `sitemap.xml`, dan `robots.txt` yang dibuat otomatis.

---

## Fitur Situs

| Fitur | Keterangan |
|---|---|
| Sidebar berkelompok | Dibagi jadi Mulai · Memakai · Mengembangkan |
| Pencarian cepat | Menyaring daftar halaman; tekan <kbd>/</kbd> untuk fokus |
| Daftar isi kanan | Otomatis dari judul h2 & h3, menyorot bagian yang sedang dibaca |
| Tombol salin | Muncul saat kursor berada di atas blok kode |
| Navigasi prev/next | Tautan halaman sebelumnya & berikutnya di bawah konten |
| Tautan sunting | Membuka berkas Markdown-nya langsung di editor GitHub |
| Responsif | Sidebar berubah jadi menu geser di layar kecil |
| Aksesibilitas | Tautan lewati konten, fokus keyboard jelas, `prefers-reduced-motion` dihormati |
| Ramah cetak | Sidebar & elemen navigasi disembunyikan saat dicetak |

---

## Menambah Halaman Baru

1. Tulis berkas Markdown-nya, misalnya `docs/keamanan.md`.
2. Daftarkan di senarai `PAGES` dalam `tools/build_site.py`:

   ```python
   {"src": "docs/keamanan.md",  "out": "keamanan.html",
    "title": "Keamanan",        "icon": "🔒", "group": "Mengembangkan",
    "desc": "Praktik pengamanan kunci API dan deployment.",
    "keywords": "keamanan security kunci api token"},
   ```
3. Tambahkan tautannya di `docs/README.md` dan tabel dokumentasi di `README.md`.
4. Bangun ulang dan periksa:

   ```bash
   python tools/build_site.py && python tools/check_links.py
   ```

Urutan di `PAGES` sekaligus menentukan urutan sidebar dan navigasi prev/next.

---

## Mengubah Tampilan

Semua warna diatur lewat CSS custom property di bagian atas `tools/theme/assets/style.css`:

```css
:root {
  --bg:      #f6f1e7;   /* latar */
  --surface: #fffdf8;   /* kartu & tabel */
  --text:    #33291d;   /* teks utama */
  --accent:  #b0763a;   /* aksen cokelat hangat */
  ...
}
```

Ganti nilainya untuk mengubah seluruh tema sekaligus.

---

## Catatan Tentang Jangkar

Fungsi `slugify()` di `tools/build_site.py` sengaja meniru pustaka `github-slugger` **persis** — termasuk mempertahankan tanda hubung di awal untuk judul yang diawali emoji.

Judul `## 🚀 3. Docker` menghasilkan id `-3-docker` di GitHub **dan** di situs ini. Karena itu tautan seperti `[Docker](deploy.md#-3-docker)` berfungsi di kedua tempat tanpa perlu ditulis dua versi.

---

## Masalah Umum

<details>
<summary><b>Situs tidak berubah setelah push</b></summary>

1. Cek tab **Actions** — apakah alur kerjanya berjalan dan berhasil?
2. Pastikan berkas yang diubah termasuk dalam daftar `paths` di `pages.yml`.
3. Pastikan **Settings → Pages → Source** sudah disetel ke **GitHub Actions**.
</details>

<details>
<summary><b>Alur kerja gagal di langkah "Periksa tautan"</b></summary>

Ada tautan menggantung. Jalankan lokal untuk melihat daftarnya:

```bash
python tools/build_site.py && python tools/check_links.py
```
</details>

<details>
<summary><b>CSS tidak termuat / tampilan berantakan</b></summary>

Biasanya cache browser. Lakukan hard refresh (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>R</kbd>).
</details>
