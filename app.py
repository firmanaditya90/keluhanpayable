
import streamlit as st
import pandas as pd
import datetime
import requests
import os

# Konfigurasi
CSV_FILE = "keluhan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-4738584397"

# Fungsi kirim Telegram
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# Fungsi simpan keluhan
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df_lama = pd.read_csv(CSV_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_FILE, index=False)

# Judul app
st.title("📨 Form Keluhan Verifikasi Pembayaran")

# Sidebar: pilih halaman
menu = st.sidebar.selectbox("Menu", ["Isi Keluhan", "Lihat Riwayat (Admin)"])

if menu == "Isi Keluhan":
    st.subheader("Form Pengisian Keluhan")

    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    if st.button("Kirim Keluhan"):
        if nama and email and no_spm and no_invoice and keluhan:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "timestamp": timestamp,
                "nama": nama,
                "email": email,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": keluhan
            }
            simpan_keluhan(data)
            pesan_telegram = (
                f"<b>Keluhan Baru Diterima</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📄 No SPM: {no_spm}\n"
                f"🧾 No Invoice: {no_invoice}\n"
                f"📝 Keluhan: {keluhan}\n"
                f"🕒 Waktu: {timestamp}"
            )
            kirim_telegram(pesan_telegram)
            st.success("✅ Keluhan berhasil dikirim!")
        else:
            st.warning("Mohon lengkapi semua data.")

elif menu == "Lihat Riwayat (Admin)":
    st.subheader("🔐 Login Admin")

    password = st.text_input("Masukkan Password", type="password")

    if password == "admin123":  # Ganti password sesuai keinginanmu
        st.success("Akses diterima.")
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df)
        else:
            st.info("Belum ada data keluhan.")
    elif password:
        st.error("Password salah.")
