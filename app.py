import streamlit as st
import pandas as pd
import datetime
import requests
import os

# Konfigurasi file dan bot Telegram
CSV_FILE = "keluhan_data.csv"
BALASAN_FILE = "balasan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # ID grup atau user

# Fungsi kirim pesan ke Telegram
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            st.warning(f"Gagal kirim ke Telegram: {response.text}")
    except Exception as e:
        st.error(f"Error kirim Telegram: {e}")

# Fungsi simpan data keluhan
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df_lama = pd.read_csv(CSV_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_FILE, index=False)

# Fungsi cek balasan berdasarkan nomor tiket
def cek_balasan(no_tiket):
    if os.path.exists(BALASAN_FILE):
        df = pd.read_csv(BALASAN_FILE)
        match = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not match.empty:
            return match.iloc[-1]["balasan"]
    return None

# UI Streamlit
st.set_page_config(page_title="Sistem Keluhan Pembayaran", layout="centered")
st.title("📨 Sistem Keluhan Verifikasi Pembayaran")

menu = st.sidebar.selectbox("Menu", ["Isi Keluhan", "Cek Tiket"])

# Halaman: Isi Keluhan
if menu == "Isi Keluhan":
    st.subheader("Form Pengisian Keluhan")

    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    if st.button("Kirim Keluhan"):
        if nama and email and no_wa and no_spm and no_invoice and keluhan:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            no_tiket = f"TIKET-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            data = {
                "timestamp": timestamp,
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": no_wa,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": keluhan
            }
            simpan_keluhan(data)

            pesan_telegram = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"📄 SPM: {no_spm}\n"
                f"🧾 Invoice: {no_invoice}\n"
                f"🗒️ Keluhan: {keluhan}\n\n"
                f"Harap balas dengan format:\n"
                f"/reply {no_tiket} [isi_balasan]"
            )
            kirim_telegram(pesan_telegram)

            st.success("✅ Keluhan berhasil dikirim!")
            st.info(f"Nomor Tiket Anda: {no_tiket}")
            st.write("Simpan nomor tiket untuk mengecek status balasan.")
        else:
            st.warning("Harap lengkapi semua kolom!")

# Halaman: Cek Tiket
elif menu == "Cek Tiket":
    st.subheader("🔍 Cek Status Tiket")
    input_tiket = st.text_input("Masukkan Nomor Tiket")

    if st.button("Cek Status"):
        if input_tiket:
            balasan = cek_balasan(input_tiket)
            if balasan:
                st.markdown("### ✅ Balasan dari Tim:")
                st.success(balasan)
            else:
                st.info("❗ Belum ada balasan dari tim. Mohon bersabar.")
        else:
            st.warning("Masukkan nomor tiket terlebih dahulu.")
