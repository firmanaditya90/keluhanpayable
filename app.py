import streamlit as st
import pandas as pd
import datetime
import requests
import os

# Konfigurasi
CSV_KELUHAN = "keluhan_data.csv"
CSV_DISKUSI = "https://raw.githubusercontent.com/firmanaditya90/keluhanpayable/main/diskusi_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"

# Kirim ke Telegram
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            st.error(f"❌ Gagal kirim ke Telegram: {r.text}")
    except Exception as e:
        st.error(f"❌ Exception Telegram: {e}")

# Simpan keluhan
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_KELUHAN, index=False)

# Ambil diskusi dari GitHub CSV
def ambil_diskusi(no_tiket):
    try:
        df = pd.read_csv(CSV_DISKUSI)
        diskusi = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        return diskusi
    except Exception as e:
        st.warning("⚠️ Gagal mengambil diskusi. Mungkin file belum tersedia.")
        return pd.DataFrame()

# Kirim tanggapan user
def kirim_tanggapan(no_tiket, isi):
    pesan = f"/tanggapan {no_tiket} {isi}"
    kirim_telegram(pesan)

# Kirim pesan bahwa keluhan selesai
def akhiri_keluhan(no_tiket):
    pesan = f"✅ Keluhan <b>{no_tiket}</b> telah <b>SELESAI</b> oleh pelapor."
    kirim_telegram(pesan)

# ---------- UI ----------

st.set_page_config(page_title="Keluhan SPM", layout="centered")
st.title("📨 Pengaduan Verifikasi Pembayaran SPM")

# Inisialisasi session
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None

# Step 1: Form
with st.form("form_keluhan"):
    nama = st.text_input("Nama")
    email = st.text_input("Email")
    wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    invoice = st.text_input("Nomor Invoice")
    isi = st.text_area("Isi Keluhan")

    submit = st.form_submit_button("Kirim Keluhan")
    if submit:
        if all([nama, email, wa, no_spm, invoice, isi]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket

            data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": wa,
                "no_spm": no_spm,
                "no_invoice": invoice,
                "keluhan": isi
            }
            simpan_keluhan(data)

            pesan = (
                f"<b>📥 Keluhan Baru</b>\n"
                f"🧑 {nama}\n📧 {email}\n📞 {wa}\n"
                f"📄 SPM: {no_spm}\n🧾 Invoice: {invoice}\n"
                f"🗒️ Keluhan: {isi}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"🔁 Balas dengan: <code>/reply {no_tiket} jawaban</code>"
            )
            kirim_telegram(pesan)

            st.success(f"✅ Keluhan dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi!")

# Step 2: Tampilkan Diskusi
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.divider()
    st.subheader(f"🧾 Tiket Anda: {no_tiket}")

    if st.button("🔄 Refresh Diskusi"):
        diskusi = ambil_diskusi(no_tiket)
        if diskusi.empty:
            st.info("⏳ Belum ada tanggapan.")
        else:
            for _, row in diskusi.iterrows():
                with st.chat_message(row["pengirim"]):
                    st.markdown(f"🕐 {row['waktu']}\n\n{row['pesan']}")

    # Step 3: Tanggapan user
    st.subheader("✍️ Tanggapan Anda")
    tanggapan = st.text_area("Isi Tanggapan")
    if st.button("📤 Kirim Tanggapan"):
        if tanggapan.strip():
            kirim_tanggapan(no_tiket, tanggapan.strip())
            st.success("Tanggapan dikirim ke Telegram.")
        else:
            st.warning("⚠️ Tanggapan tidak boleh kosong.")

    # Step 4: Akhiri keluhan
    if st.button("✅ Selesai / Tutup Tiket"):
        akhiri_keluhan(no_tiket)
        st.success("Tiket ditandai selesai.")
