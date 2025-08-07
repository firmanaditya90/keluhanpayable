import streamlit as st
import pandas as pd
import datetime
import requests
import os

# ====================== KONFIGURASI ======================
CSV_FILE = "keluhan_data.csv"
BALASAN_FILE = "balasan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # Gantilah dengan Chat ID grup kamu

# ====================== FUNGSI ===========================
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        st.error(f"Gagal kirim ke Telegram. Status: {response.status_code}")
        st.json(response.json())

def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df_lama = pd.read_csv(CSV_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_FILE, index=False)

def cek_balasan(no_tiket):
    if os.path.exists(BALASAN_FILE):
        df = pd.read_csv(BALASAN_FILE)
        match = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not match.empty:
            return match.iloc[-1]["balasan"]
    return None

# ======================== UI =============================
st.set_page_config(page_title="📨 Sistem Keluhan SPM", layout="centered")

st.title("📨 Sistem Pengaduan Verifikasi Pembayaran SPM")

menu = st.sidebar.radio("Pilih Menu", ["📝 Isi Keluhan", "🔍 Cek Tiket"])

# ---------------- ISI KELUHAN ------------------
if menu == "📝 Isi Keluhan":
    st.header("📝 Form Pengaduan")

    with st.form("form_keluhan"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email Aktif")
        no_wa = st.text_input("Nomor WhatsApp")
        no_spm = st.text_input("Nomor SPM")
        no_invoice = st.text_input("Nomor Invoice")
        keluhan = st.text_area("Isi Keluhan")
        submitted = st.form_submit_button("Kirim Keluhan")

        if submitted:
            if all([nama, email, no_wa, no_spm, no_invoice, keluhan]):
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
                    f"<b>📩 Keluhan Baru</b>\n"
                    f"👤 Nama: {nama}\n"
                    f"📧 Email: {email}\n"
                    f"📱 WhatsApp: {no_wa}\n"
                    f"📄 No SPM: {no_spm}\n"
                    f"🧾 No Invoice: {no_invoice}\n"
                    f"📝 Keluhan: {keluhan}\n"
                    f"🎟️ No Tiket: <b>{no_tiket}</b>\n\n"
                    f"Balas dengan format:\n<code>/reply {no_tiket} isi_balasan</code>"
                )
                kirim_telegram(pesan_telegram)

                st.success("✅ Keluhan berhasil dikirim!")
                st.info(f"🎟️ Nomor Tiket Anda: {no_tiket}")
                st.caption("📌 Silakan simpan nomor tiket untuk cek balasan dari tim.")
            else:
                st.warning("⚠️ Semua kolom harus diisi lengkap!")

# ---------------- CEK TIKET ------------------
elif menu == "🔍 Cek Tiket":
    st.header("🔍 Cek Status Keluhan")

    no_tiket_input = st.text_input("Masukkan Nomor Tiket Anda")

    if st.button("🔄 Refresh Balasan"):
        if no_tiket_input:
            balasan = cek_balasan(no_tiket_input)
            if balasan:
                st.success(f"📬 Balasan dari Tim:\n\n{balasan}")
            else:
                st.info("⏳ Belum ada balasan dari tim. Mohon tunggu ya.")
        else:
            st.warning("⚠️ Masukkan nomor tiket terlebih dahulu.")
