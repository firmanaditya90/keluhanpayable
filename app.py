import streamlit as st
import pandas as pd
import os
import datetime
import requests

CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"

TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # Ganti dengan grup kamu

# ------ Utils ------

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            st.error(f"❌ Gagal kirim Telegram: {res.text}")
    except Exception as e:
        st.error(f"❌ Error kirim Telegram: {e}")

def simpan_diskusi(no_tiket, pengirim, isi):
    new_row = pd.DataFrame([{
        "no_tiket": no_tiket,
        "pengirim": pengirim,
        "isi": isi,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(CSV_DISKUSI, index=False)

def tampilkan_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        chat = df[df["no_tiket"] == no_tiket]
        if chat.empty:
            st.info("Belum ada diskusi.")
        else:
            for _, row in chat.iterrows():
                with st.chat_message("user" if row["pengirim"] == "User" else "assistant"):
                    st.markdown(f"_{row['timestamp']}_  \n**{row['pengirim']}**: {row['isi']}")
    else:
        st.info("Belum ada diskusi.")

# ------ UI ------

st.set_page_config("Diskusi Keluhan", layout="centered")
st.title("💬 Diskusi Keluhan SPM")

if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = ""

st.subheader("1️⃣ Masukkan Keluhan Baru")
with st.form("form_keluhan"):
    nama = st.text_input("Nama")
    email = st.text_input("Email")
    wa = st.text_input("Nomor WhatsApp")
    spm = st.text_input("Nomor SPM")
    invoice = st.text_input("Nomor Invoice")
    isi_keluhan = st.text_area("Keluhan")

    kirim = st.form_submit_button("🚀 Kirim Keluhan")
    if kirim and all([nama, email, wa, spm, invoice, isi_keluhan]):
        now = datetime.datetime.now()
        no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
        st.session_state["no_tiket"] = no_tiket

        keluhan_row = pd.DataFrame([{
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "no_tiket": no_tiket,
            "nama": nama,
            "email": email,
            "no_wa": wa,
            "no_spm": spm,
            "no_invoice": invoice,
            "keluhan": isi_keluhan
        }])
        if os.path.exists(CSV_KELUHAN):
            df = pd.read_csv(CSV_KELUHAN)
            df = pd.concat([df, keluhan_row], ignore_index=True)
        else:
            df = keluhan_row
        df.to_csv(CSV_KELUHAN, index=False)

        simpan_diskusi(no_tiket, "User", isi_keluhan)

        pesan = (
            f"<b>Keluhan Baru Masuk</b>\n"
            f"🧑 Nama: {nama}\n📧 Email: {email}\n📞 WA: {wa}\n"
            f"📄 SPM: {spm}\n🧾 Invoice: {invoice}\n"
            f"🗒️ Keluhan: {isi_keluhan}\n🎟️ Tiket: <b>{no_tiket}</b>\n\n"
            f"Balas dengan:\n/reply {no_tiket} Jawaban Anda"
        )
        kirim_telegram(pesan)
        st.success(f"Keluhan terkirim! Nomor Tiket: {no_tiket}")

# ------ Diskusi ------
no_tiket = st.session_state["no_tiket"]
if no_tiket:
    st.divider()
    st.subheader(f"💬 Diskusi Tiket: {no_tiket}")
    tampilkan_diskusi(no_tiket)

    with st.form("form_tanggapan"):
        tanggapan = st.text_area("Tanggapan Anda")
        kirim_tanggapan = st.form_submit_button("📤 Kirim Tanggapan")
        if kirim_tanggapan and tanggapan.strip():
            simpan_diskusi(no_tiket, "User", tanggapan)
            kirim_telegram(f"<b>Tanggapan dari Pelapor</b>\n🎟️ Tiket: <b>{no_tiket}</b>\n💬 {tanggapan}")
            st.success("✅ Tanggapan dikirim!")

    if st.button("✅ Tandai Keluhan Selesai"):
        simpan_diskusi(no_tiket, "User", "✅ Keluhan ditandai selesai.")
        kirim_telegram(f"✅ Keluhan Tiket <b>{no_tiket}</b> ditandai selesai oleh pelapor.")
        st.success("Tiket telah ditutup.")
        st.session_state["no_tiket"] = ""
