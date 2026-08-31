# 🔧 Instalasi

Panduan menjalankan **Ampera Trinity AI** di komputer sendiri.

---

## 📋 Prasyarat

| Kebutuhan | Versi | Catatan |
|---|---|---|
| Python | **3.11 atau lebih baru** | Aplikasi memakai `zoneinfo` dari pustaka standar |
| pip | terbaru | `python -m pip install --upgrade pip` |
| Git | apa saja | Hanya untuk clone repo |
| Koneksi internet | — | Semua model AI dipanggil lewat API |

Cek versi Python:

```bash
python --version
# Python 3.11.x  ✅
```

Kalau masih 3.10 ke bawah, install versi baru dari [python.org](https://www.python.org/downloads/) atau lewat `pyenv`.

---

## 1. Clone Repositori

```bash
git clone https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai.git
cd Ampera-Trinity-Ai
```

---

## 2. Buat Virtual Environment

Sangat disarankan supaya dependensi tidak bentrok dengan proyek lain.

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Kalau berhasil, prompt terminal akan diawali `(.venv)`.

---

## 3. Install Dependensi

```bash
pip install -r requirements.txt
```

Paket yang dipasang:

| Paket | Fungsi |
|---|---|
| `streamlit` | Kerangka aplikasi web & manajemen state |
| `openai` | SDK yang dipakai untuk memanggil endpoint Groq (chat, vision, Whisper) |
| `requests` | Memanggil REST API Cloudflare Workers AI |
| `Pillow` | Membaca, meresize, dan mengubah gambar jadi base64 |

---

## 4. Siapkan API Key

Salin templat secrets lalu isi key milikmu:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Buka `.streamlit/secrets.toml` dan isi minimal `GROQ_API_KEY`:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxx"
```

> 📖 Cara mendapatkan key (gratis) ada di **[konfigurasi.md](konfigurasi.md)**.
>
> 🔒 File `.streamlit/secrets.toml` sudah masuk `.gitignore` — jangan sampai ter-commit.

**Alternatif — environment variable** (tanpa file secrets):

```bash
# Linux / macOS
export GROQ_API_KEY="gsk_..."

# Windows PowerShell
$env:GROQ_API_KEY = "gsk_..."
```

---

## 5. Jalankan Aplikasi

```bash
streamlit run app.py
```

Terminal akan menampilkan:

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Buka **<http://localhost:8501>** di browser. 🎉

---

## ⚙️ Konfigurasi Server

Berkas `.streamlit/config.toml` yang sudah ada di repo:

```toml
[server]
address = "0.0.0.0"          # bisa diakses dari perangkat lain di jaringan yang sama
port = 8501
enableCORS = false
enableXsrfProtection = false
headless = true              # tidak otomatis membuka browser
runOnSave = true             # auto-reload saat file disimpan

[browser]
gatherUsageStats = false     # tidak mengirim telemetri
```

Ganti port kalau 8501 sudah dipakai:

```bash
streamlit run app.py --server.port 8600
```

---

## 🩺 Troubleshooting

<details>
<summary><b>ModuleNotFoundError: No module named 'streamlit'</b></summary>

Virtual environment belum aktif atau dependensi belum terpasang.

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
</details>

<details>
<summary><b>ModuleNotFoundError: No module named 'zoneinfo'</b></summary>

Python-mu di bawah 3.9. Upgrade ke **Python 3.11+**.
</details>

<details>
<summary><b>Port 8501 is already in use</b></summary>

Ada instance Streamlit lain yang masih hidup.

```bash
# Lihat & matikan
pkill -f streamlit                 # Linux/macOS
# atau jalankan di port lain
streamlit run app.py --server.port 8600
```
</details>

<details>
<summary><b>Muncul "Fitur chat belum dikonfigurasi pemilik (GROQ_API_KEY)"</b></summary>

Aplikasi tidak menemukan key. Periksa:

1. File berada tepat di `.streamlit/secrets.toml` (bukan di folder lain).
2. Formatnya TOML dan pakai tanda kutip: `GROQ_API_KEY = "gsk_..."`.
3. Restart Streamlit setelah mengubah secrets — perubahan tidak selalu terbaca otomatis.

Detail: [konfigurasi.md](konfigurasi.md).
</details>

<details>
<summary><b>Mode generate gambar tidak muncul</b></summary>

`CF_ACCOUNT_ID` dan `CF_API_TOKEN` belum diisi, jadi flag `IMAGE_READY` bernilai `False`.
Ini normal — fitur chat tetap berjalan. Lihat [konfigurasi.md](konfigurasi.md#2-cloudflare-workers-ai-opsional).
</details>

<details>
<summary><b>Ikon tampil sebagai teks mentah <code>:material_xxx:</code></b></summary>

Versi Streamlit terlalu lama. Upgrade:

```bash
pip install --upgrade streamlit
```
</details>

<details>
<summary><b>Tombol lampiran / rekam suara tidak ada</b></summary>

Fitur ini bergantung parameter `accept_file` dan `accept_audio` pada `st.chat_input`, yang hanya ada di Streamlit versi baru.
`config.py` mendeteksinya otomatis (`CHAT_INPUT_SUPPORTS_FILE` / `CHAT_INPUT_SUPPORTS_AUDIO`) dan menyembunyikan tombolnya bila tidak didukung.
Solusinya: `pip install --upgrade streamlit`.
</details>

<details>
<summary><b>Perubahan kode tidak terlihat di browser</b></summary>

`runOnSave` sudah aktif, tapi kadang perlu manual: tekan **R** di halaman, atau menu ☰ → **Rerun**.
Untuk perubahan pada CSS di `styles.py`, lakukan hard refresh (`Ctrl+Shift+R`).
</details>

---

## ➡️ Selanjutnya

- [Konfigurasi API key & pengaturan](konfigurasi.md)
- [Kenali semua fitur](fitur.md)
- [Deploy jadi link publik](deploy.md)
