# Menjalankan LYRA AI STUDIO di Android

Arah pengembangan saat ini: **offline-first**. Fitur dasar aplikasi
(dashboard, daftar engine, pengaturan) harus bisa dibuka tanpa
internet; kode API dan layanan online diisi belakangan lewat halaman
**Pengaturan** di dalam aplikasi. Ada dua cara menjalankan LYRA di HP.

## Cara 1 — Pasang sebagai aplikasi (PWA) — paling cepat untuk percobaan

1. Buka **https://lyra-ai-studio.vercel.app** di Chrome Android
   (satu kali saat online).
2. Ketuk menu **⋮** → **"Tambahkan ke Layar Utama"** / **"Install app"**.
3. Ikon **LYRA** muncul di layar utama seperti aplikasi biasa.
4. Setelah kunjungan pertama, aplikasi tetap bisa dibuka **offline**:
   tampilan dan fitur dasar dimuat dari cache perangkat, dan daftar
   engine menampilkan data terakhir yang tersimpan (ditandai
   "Mode offline").
5. Kode API diisi nanti di menu **Pengaturan** — tersimpan hanya di
   perangkat ini (localStorage), tidak dikirim ke mana pun selain
   alamat API yang kamu tentukan.

Catatan: status engine secara langsung (live) tetap butuh koneksi ke
backend. Yang bekerja offline adalah aplikasi dan fitur dasarnya.

## Cara 2 — Backend ikut jalan di HP (Termux, full offline)

Untuk menjalankan **seluruh tumpukan** (backend + frontend) di HP
tanpa server sama sekali:

1. Pasang **Termux** (dari F-Droid atau GitHub resmi Termux — versi
   Play Store sudah lama tidak diperbarui).
2. Di Termux:

   ```bash
   pkg update && pkg install -y python git
   git clone https://github.com/aluxlox-gif/lyra-ai-studio.git
   cd lyra-ai-studio
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

3. Buka **http://127.0.0.1:8000** di browser HP. Aplikasi berjalan
   penuh secara lokal; dari alamat localhost ini PWA juga bisa
   dipasang ke layar utama.
4. (Opsional) Layanan Voicebox cadangan di sesi Termux kedua:

   ```bash
   cd lyra-ai-studio/services/voicebox_fallback
   pip install -r requirements.txt
   uvicorn main:app --host 127.0.0.1 --port 17493
   ```

   Sintesis suaranya sendiri memakai layanan Microsoft (edge-tts),
   jadi langkah ini tetap butuh internet — sisanya offline.

## Pengaturan yang relevan

| Di mana | Untuk apa |
| --- | --- |
| Halaman **Pengaturan** di aplikasi | Alamat API, token, ID profil suara — disimpan di perangkat, diisi nanti |
| `.env` di server/Termux | Konfigurasi backend (`VOICEBOX_BASE_URL`, token internal, dll.) — lihat `.env.example` |
