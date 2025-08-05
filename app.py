
import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os

# -----------------------------
# KONFIGURASI
TELEGRAM_BOT_TOKEN = "ISI_TOKEN_BOT_KAMU"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID_PIC"
CSV_FILE = "keluhan_data.csv"
# -----------------------------

st.set_page_config(page_title="Form Keluhan Verifikasi Pembayaran", layout="centered")

st.title("🧾 Form Keluhan Verifikasi Pembayaran")

menu = st.sidebar.selectbox("Menu", ["Formulir Keluhan", "Riwayat Keluhan (Admin)"])

if menu == "Formulir Keluhan":
    with st.form("keluhan_form"):
        no_spm = st.text_input("Nomor SPM", max_chars=50)
        no_invoice = st.text_input("Nomor Invoice", max_chars=50)
        keluhan = st.text_area("Deskripsikan Keluhan Anda")
        email = st.text_input("Email Aktif (opsional)")
        submitted = st.form_submit_button("Kirim Keluhan")

    if submitted:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "Tanggal": timestamp,
            "No SPM": no_spm,
            "No Invoice": no_invoice,
            "Keluhan": keluhan,
            "Email": email
        }

        # Simpan ke CSV
        df = pd.DataFrame([data])
        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode='a', index=False, header=False)
        else:
            df.to_csv(CSV_FILE, index=False)

        st.success("✅ Keluhan berhasil dikirim.")

        # Kirim ke Telegram
        try:
            pesan = f"""
📨 *Keluhan Verifikasi Pembayaran Baru*
🧾 No SPM: `{no_spm}`
📄 Invoice: `{no_invoice}`
🗣️ Keluhan: {keluhan}
📧 Email: {email if email else '-'}
🕒 Tanggal: {timestamp}
"""
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            params = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": pesan,
                "parse_mode": "Markdown"
            }
            response = requests.post(telegram_url, params=params)
            if response.status_code == 200:
                st.info("📩 Notifikasi telah dikirim ke PIC via Telegram.")
            else:
                st.warning("Gagal mengirim notifikasi Telegram.")
        except Exception as e:
            st.error(f"Terjadi error: {e}")

elif menu == "Riwayat Keluhan (Admin)":
    st.header("📋 Daftar Keluhan Masuk")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
        st.download_button("📥 Download Data", df.to_csv(index=False), file_name="riwayat_keluhan.csv")
    else:
        st.info("Belum ada data keluhan.")
