# 🤝 Panduan Kontribusi

Terima kasih sudah tertarik mengembangkan **Ampera Trinity AI**! Dokumen ini menjelaskan cara berkontribusi.

---

## Sebelum Mulai

1. Baca **[docs/arsitektur.md](docs/arsitektur.md)** untuk memahami struktur kode.
2. Jalankan aplikasi secara lokal — lihat **[docs/instalasi.md](docs/instalasi.md)**.
3. Untuk perubahan besar, buka **issue** dulu supaya bisa didiskusikan sebelum kamu menulis banyak kode.

---

## Alur Kerja

```bash
# 1. Fork repo lewat tombol Fork di GitHub, lalu clone hasil fork-mu
git clone https://github.com/<username>/Ampera-Trinity-Ai.git
cd Ampera-Trinity-Ai

# 2. Buat branch baru
git checkout -b fitur/nama-fitur-singkat

# 3. Siapkan lingkungan
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Kerjakan perubahanmu, lalu uji
streamlit run app.py

# 5. Commit & push
git add .
git commit -m "feat: tambahkan X"
git push origin fitur/nama-fitur-singkat

# 6. Buka Pull Request ke branch main
```

### Penamaan branch

| Awalan | Untuk |
|---|---|
| `fitur/` | Fitur baru |
| `perbaikan/` | Perbaikan bug |
| `docs/` | Perubahan dokumentasi |
| `refactor/` | Rapikan kode tanpa mengubah perilaku |

### Format pesan commit

Ikuti [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     fitur baru
fix:      perbaikan bug
docs:     dokumentasi
style:    format/CSS, tanpa perubahan logika
refactor: perapian kode
perf:     peningkatan performa
chore:    pekerjaan pemeliharaan
```

Contoh:

```
feat: hubungkan pengaturan stream_speed ke stream_sentences
fix: cegah crash saat gambar melebihi 5 buah
docs: tambahkan panduan deploy Docker
```

---

## Gaya Kode

Ikuti konvensi yang sudah ada di repo:

| Aturan | Contoh |
|---|---|
| Header di setiap file | `# -*- coding: utf-8 -*-` |
| Impor masa depan | `from __future__ import annotations` |
| Docstring **bahasa Indonesia** | menjelaskan *kenapa*, bukan sekadar *apa* |
| Type hint | `def fungsi(x: str) -> list[dict]:` |
| Pemisah bagian | `# ====...====` dengan judul kapital |
| Panjang baris | usahakan ≤ 100 karakter |
| Nama privat | diawali `_`, contoh `_sentence_chunks()` |

Contoh gaya yang diharapkan:

```python
# ============================================================================
# NAMA BAGIAN
# ============================================================================
def nama_fungsi(param: str) -> dict:
    """Penjelasan singkat dalam bahasa Indonesia.

    Jelaskan alasan di balik keputusan teknis bila tidak jelas dari kodenya.
    """
    ...
```

---

## Aturan Arsitektur

Supaya kode tetap rapi, hormati pembagian tanggung jawab berikut:

| Jenis perubahan | Tempat yang benar |
|---|---|
| Data statis (model, bahasa, kursus, artefak) | `config.py` |
| Struktur `session_state` | `state.py` — **jangan** akses langsung dari halaman lain |
| Panggilan API AI | `engines/` |
| CSS & animasi | `styles.py` |
| Komponen render kecil | `ui_helpers.py` |
| Halaman baru | `app.py` + daftarkan di `sidebar.py` dan `PAGE_TITLES` |
| Pesan error ke pengguna | `errors.py` |

❌ **Jangan:**
- Menaruh logika AI di `app.py`
- Menulis CSS inline di luar `styles.py`
- Mengakses `st.session_state["messages"]` langsung — pakai `active_thread()`
- Menambahkan dependensi baru tanpa alasan kuat

---

## 🔒 Keamanan

- **Jangan pernah** meng-commit API key, token, atau `.streamlit/secrets.toml`.
- Kredensial baru harus dibaca lewat `_get_secret()` di `config.py`.
- Pesan error ke pengguna harus melewati `errors.py` — jangan tampilkan status HTTP atau jejak provider mentah.
- Sebelum commit, cek cepat:
  ```bash
  grep -rn "gsk_\|Bearer " --include=*.py .
  git status --porcelain | grep secrets
  ```

Menemukan celah keamanan? Jangan buka issue publik — hubungi pemilik repo secara privat.

---

## Menguji Perubahan

Belum ada test otomatis, jadi lakukan pengujian manual:

- [ ] Aplikasi jalan tanpa error: `streamlit run app.py`
- [ ] Chat biasa berfungsi
- [ ] Halaman yang tersentuh perubahan tetap normal
- [ ] Sidebar & navigasi antar halaman tidak rusak
- [ ] Berjalan **tanpa** API key (tidak boleh crash, hanya fitur nonaktif)
- [ ] Tidak ada warning baru di terminal

### Ingin menambahkan test? Sangat diterima!

Kandidat terbaik adalah fungsi murni yang tidak butuh Streamlit:

| Fungsi | Modul |
|---|---|
| `_sentence_chunks()` | `ui_helpers.py` |
| `extract_image_bytes()` | `engines/image_engine.py` |
| `public_error_chat()` / `public_error_image()` | `errors.py` |
| `_is_model_unavailable_error()` | `errors.py` |
| `course_curriculum()` | `config.py` |
| `_conversation_title()` | `state.py` |

---

## Ide Kontribusi

Beberapa hal yang sudah teridentifikasi dan menunggu dikerjakan:

| Prioritas | Tugas |
|---|---|
| 🔴 | Hubungkan pengaturan `stream_speed` ke `SENTENCE_STREAM_DELAY` (saat ini pilihannya tidak berpengaruh) |
| 🔴 | Perbaiki `MODEL_CATALOG` — beberapa tingkat menunjuk ID model yang sama |
| 🟡 | Tambahkan test `pytest` untuk fungsi murni |
| 🟡 | Tambahkan `Dockerfile` resmi ke repo |
| 🟡 | Opsi animasi per-karakter (typewriter) sebagai alternatif per-kalimat |
| 🟢 | Penyimpanan riwayat permanen (SQLite) |
| 🟢 | Gerbang autentikasi sederhana untuk deployment publik |
| 🟢 | Terjemahan teks antarmuka yang saat ini masih hardcoded |
| 🟢 | GitHub Actions untuk lint & smoke test |

---

## Melaporkan Bug

Sertakan informasi ini di issue:

```markdown
**Deskripsi**
Apa yang terjadi.

**Langkah reproduksi**
1. …
2. …

**Yang diharapkan**
…

**Lingkungan**
- OS:
- Versi Python:
- Versi Streamlit:
- Cara menjalankan: lokal / Streamlit Cloud / Docker

**Log / screenshot**
(sensor API key sebelum menempel!)
```

---

## Lisensi

Dengan berkontribusi, kamu setuju kontribusimu dirilis di bawah [MIT License](LICENSE).
