
# 📄 Aplikasi Keluhan Verifikasi Pembayaran (Streamlit)

Aplikasi ini dibuat menggunakan **Streamlit** untuk menangani **keluhan verifikasi pembayaran**.  
Pengguna dapat mengisi form keluhan, dan data akan tersimpan secara otomatis serta (opsional) mengirim notifikasi ke Telegram admin/PIC.

---

## 🎯 Fitur Utama

- Form pengisian keluhan (No SPM, No Invoice, Keluhan, Email)
- Simpan data ke file `keluhan_data.csv`
- Notifikasi otomatis ke Telegram (jika dikonfigurasi)
- Menu Admin: lihat dan unduh riwayat keluhan

---

## 🚀 Cara Menjalankan di Lokal

1. **Clone repositori ini** atau unduh file `app.py` dan `keluhan_data.csv`
2. Install library yang dibutuhkan:
   ```bash
   pip install streamlit pandas requests
   ```
3. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deploy Gratis di Streamlit Cloud

1. Login ke https://streamlit.io/cloud menggunakan akun GitHub
2. Klik **"New app"**
3. Pilih repo ini, isi `app.py` sebagai file utama
4. Klik **Deploy**

Aplikasi kamu akan tersedia secara publik.

---

## 💬 Konfigurasi Telegram (Opsional)

1. Buat bot di Telegram via [@BotFather](https://t.me/BotFather)
2. Dapatkan `TELEGRAM_BOT_TOKEN`
3. Chat dengan bot, lalu dapatkan `chat_id` kamu dari `getUpdates`
4. Edit bagian atas `app.py`:

```python
TELEGRAM_BOT_TOKEN = "TOKEN_KAMU"
TELEGRAM_CHAT_ID = "CHAT_ID_KAMU"
```

---

## 🗂️ Struktur File

```
📁 keluhan-streamlit/
│
├── app.py               # File utama aplikasi Streamlit
├── keluhan_data.csv     # Penyimpanan data keluhan
└── README.md            # Dokumentasi ini
```

---

## 👨‍💻 Dibuat oleh

> Sistem Otomatis Laporan Keluhan Pembayaran  
> Dengan ❤️ menggunakan Streamlit + Telegram API
