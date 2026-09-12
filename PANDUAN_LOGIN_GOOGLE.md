# Panduan Login Google — Ampera Trinity AI

Panduan mendaftarkan aplikasi di Google supaya pengguna bisa **masuk dengan akun Google**. Ikuti langkahnya sekali saja, kira-kira 10–15 menit. Setelah selesai, kirimkan **Client ID** dan **Client Secret** (atau pasang sendiri di Secrets), lalu kode loginnya akan dipasang di aplikasi.

---

## 1. Masuk ke Google Cloud Console

1. Buka **https://console.cloud.google.com** dan login dengan akun Google kamu (pakai akun amperaofficial26@gmail.com biar seragam).
2. Klik menu project di kiri atas (logo Google Cloud di sampingnya) → **New Project / Project Baru**.
3. Nama project: misalnya `Ampera Trinity AI` → klik **Create**.
4. Pastikan project yang aktif di kiri atas adalah project yang barusan dibuat.

## 2. Isi OAuth Consent Screen (layar izin)

1. Di menu kiri: **APIs & Services → OAuth consent screen** (kadang bernama *Google Auth Platform*).
2. Pilih **External** (Eksternal) → **Create / Get started**.
3. Isi:
   - **App name**: `Ampera Trinity AI`
   - **User support email**: pilih email kamu
   - **Developer contact**: email kamu lagi
4. Simpan. Bagian Scopes tidak perlu diubah (cukup email + profil dasar).

## 3. Buat OAuth Client ID

1. Menu kiri: **APIs & Services → Credentials**.
2. Klik **+ Create Credentials → OAuth client ID**.
3. Application type: **Web application**.
4. Name: `Ampera Trinity AI Web`.
5. Di bagian **Authorized redirect URIs** → **Add URI**, isi alamat aplikasi kamu, contoh:

   ```
   https://ampera-trinity-ai.streamlit.app/
   ```

   (Ganti dengan domain Streamlit Cloud kamu yang sebenarnya — buka aplikasi dan salin alamatnya, akhiri dengan `/`.)

6. Klik **Create**. Muncul popup **Your Client ID** dan **Your Client Secret** → **salin keduanya** dan simpan di tempat aman (notepad dulu tidak apa-apa).

> Catatan: sementara status aplikasi masih **Testing**, hanya email yang kamu tambahkan sebagai **Tester** (di OAuth consent screen → Audience/Testers) yang bisa login. Tambahkan email kamu sendiri dulu untuk mencoba.

## 4. Simpan kredensial di Streamlit Cloud

Di Streamlit Cloud: buka aplikasi → **Settings (⋯) → Secrets**, lalu tambahkan:

```toml
GROQ_API_KEY = "gsk_..."

GOOGLE_CLIENT_ID = "xxxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-xxxxx"
```

Klik **Save**. (Kalau tidak ingin memasang sendiri, kirim Client ID & Secret ke proses pengembangan dan nanti ditempelkan bersama secrets lainnya.)

## 5. Selesai — lanjut implementasi

Setelah Client ID + Secret tersimpan:

- [ ] Login dengan Google akan dipasang di aplikasi (tombol "Masuk dengan Google" di halaman masuk).
- [ ] Sebelum produksi, di Google Cloud klik **OAuth consent screen → Publish app** supaya semua orang bisa login (bukan cuma tester).
- [ ] Kalau alamat aplikasi berubah (ganti subdomain), **redirect URI di langkah 3 harus ikut ditambah/diperbarui**.

---

Dibuat oleh **Ampera Official — Palembang, Indonesia** · amperaofficial26@gmail.com
