# 🌍 Deploy — Bikin Link yang Bisa Dibagikan

Empat cara mempublikasikan **Ampera Trinity AI**, dari yang paling mudah.

| Cara | Biaya | Kesulitan | Cocok untuk |
|---|---|---|---|
| [Streamlit Community Cloud](#-1-streamlit-community-cloud-paling-mudah) | Gratis | ⭐ | Rekomendasi utama |
| [Hugging Face Spaces](#-2-hugging-face-spaces) | Gratis | ⭐⭐ | Alternatif, komunitas AI |
| [Docker](#-3-docker) | Tergantung host | ⭐⭐⭐ | Deployment yang dapat direproduksi |
| [VPS sendiri](#-4-vps-sendiri) | Berbayar | ⭐⭐⭐⭐ | Domain sendiri, kontrol penuh |

---

## 🚀 1. Streamlit Community Cloud (paling mudah)

Hasil akhir: `https://<nama-app>.streamlit.app`

### Langkah

**a. Pastikan kode sudah ada di GitHub**

```bash
git add .
git commit -m "siap deploy"
git push origin main
```

**b. Buat aplikasi**

1. Buka <https://share.streamlit.io> → masuk dengan akun GitHub.
2. Klik **New app**.
3. Isi:
   | Kolom | Nilai |
   |---|---|
   | Repository | `amperaofficial26-beep/Ampera-Trinity-Ai` |
   | Branch | `main` |
   | Main file path | `app.py` |
4. Klik **Advanced settings** → bagian **Secrets**, tempel:
   ```toml
   GROQ_API_KEY = "gsk_..."
   CF_ACCOUNT_ID = "..."
   CF_API_TOKEN = "..."
   ```
   *(dua terakhir opsional)*
5. Pilih **Python version 3.11** bila tersedia.
6. Klik **Deploy** dan tunggu build selesai (± 2–5 menit).

**c. Bagikan linknya** 🎉

### Mengelola

| Kebutuhan | Cara |
|---|---|
| Ubah API key | Dashboard app → **Settings → Secrets** (app restart otomatis) |
| Update kode | Cukup `git push` — Streamlit Cloud rebuild otomatis |
| Lihat error | Menu **Manage app** di pojok kanan bawah → log |
| Aplikasi "tertidur" | Normal di tier gratis; pengunjung berikutnya membangunkannya |

> ⚠️ Aplikasi ini **tanpa autentikasi**. Siapa pun yang punya link akan memakai kuota API-mu. Untuk pemakaian publik, pertimbangkan menambahkan gerbang kata sandi sederhana atau mewajibkan pengunjung mengisi key-nya sendiri lewat tab **Trinity Code**.

---

## 🤗 2. Hugging Face Spaces

Hasil akhir: `https://huggingface.co/spaces/<user>/<nama>`

1. Buka <https://huggingface.co/new-space>.
2. Isi nama, pilih **SDK: Streamlit**, lalu **Create Space**.
3. Push kode:
   ```bash
   git remote add hf https://huggingface.co/spaces/<user>/<nama>
   git push hf main
   ```
4. Space → **Settings → Variables and secrets** → tambahkan `GROQ_API_KEY` sebagai **Secret**.

Karena `config.py` juga membaca environment variable, secrets Hugging Face langsung terbaca tanpa perubahan kode.

---

## 🐳 3. Docker

Belum ada `Dockerfile` di repo. Buat berkas berikut di root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

Tambahkan `.dockerignore`:

```
.venv/
__pycache__/
*.py[cod]
.git/
.streamlit/secrets.toml
docs/
```

Build & jalankan:

```bash
docker build -t ampera-trinity-ai .

docker run -p 8501:8501 \
  -e GROQ_API_KEY="gsk_..." \
  -e CF_ACCOUNT_ID="..." \
  -e CF_API_TOKEN="..." \
  ampera-trinity-ai
```

Atau pakai `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      GROQ_API_KEY: ${GROQ_API_KEY}
      CF_ACCOUNT_ID: ${CF_ACCOUNT_ID}
      CF_API_TOKEN: ${CF_API_TOKEN}
    restart: unless-stopped
```

```bash
docker compose up -d
```

Image Docker ini bisa dipakai di Railway, Render, Fly.io, Google Cloud Run, dan sejenisnya.

---

## 🖥️ 4. VPS Sendiri

Untuk domain sendiri (misalnya `ai.domainmu.com`) dengan HTTPS.

### a. Siapkan aplikasi

```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx

git clone https://github.com/amperaofficial26-beep/Ampera-Trinity-Ai.git
cd Ampera-Trinity-Ai
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

mkdir -p .streamlit
cat > .streamlit/secrets.toml <<'EOF'
GROQ_API_KEY = "gsk_..."
EOF
chmod 600 .streamlit/secrets.toml
```

### b. Jalankan sebagai service systemd

`/etc/systemd/system/ampera.service`:

```ini
[Unit]
Description=Ampera Trinity AI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Ampera-Trinity-Ai
ExecStart=/home/ubuntu/Ampera-Trinity-Ai/.venv/bin/streamlit run app.py \
          --server.port=8501 --server.address=127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ampera
sudo systemctl status ampera
```

### c. Reverse proxy Nginx

`/etc/nginx/sites-available/ampera`:

```nginx
server {
    listen 80;
    server_name ai.domainmu.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host       $host;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ampera /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

> Header `Upgrade`/`Connection` **wajib** — Streamlit memakai WebSocket.

### d. HTTPS gratis

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ai.domainmu.com
```

### e. Perketat keamanan

Karena sudah di belakang HTTPS, ubah `.streamlit/config.toml`:

```toml
[server]
address = "127.0.0.1"
port = 8501
enableCORS = true
enableXsrfProtection = true
headless = true
runOnSave = false
```

---

## ✅ Checklist Sebelum Publik

- [ ] `.streamlit/secrets.toml` **tidak** ter-commit (`git log --all -- .streamlit/secrets.toml` harus kosong)
- [ ] Tidak ada API key ter-hardcode: `grep -rn "gsk_" --include=*.py .`
- [ ] `requirements.txt` sudah lengkap
- [ ] Aplikasi diuji dengan Python 3.11
- [ ] `LICENSE` sesuai keinginan
- [ ] Sudah paham risiko kuota (aplikasi tanpa login)
- [ ] Untuk VPS: `enableXsrfProtection = true` dan HTTPS aktif

---

## 🩺 Masalah Saat Deploy

<details>
<summary><b>Build gagal di Streamlit Cloud</b></summary>

Cek log lewat **Manage app**. Penyebab tersering: versi Python yang dipilih di bawah 3.11 (`zoneinfo` tidak ada).
</details>

<details>
<summary><b>Aplikasi jalan tapi chat error terus</b></summary>

Secrets belum tersimpan. Buka **Settings → Secrets**, pastikan format TOML dengan tanda kutip, lalu **Reboot app**.
</details>

<details>
<summary><b>Halaman blank / terus "Connecting…"</b></summary>

Reverse proxy tidak meneruskan WebSocket. Pastikan header `Upgrade` dan `Connection "upgrade"` ada di konfigurasi Nginx.
</details>

<details>
<summary><b>Kuota API cepat habis</b></summary>

Aplikasi tanpa login, jadi semua pengunjung berbagi key-mu. Solusi: tambahkan gerbang kata sandi, atau arahkan pengguna mengisi key sendiri di tab **Trinity Code**.
</details>
