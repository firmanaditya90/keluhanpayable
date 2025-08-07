import streamlit as st
import pandas as pd
import datetime
import requests
import os
import html

# Konfigurasi
CSV_KELUHAN = "keluhan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # ID Supergroup

# Fungsi aman kirim ke Telegram
def escape_html(text):
    return html.escape(text)

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
        st.error(f"❌ Exception saat kirim Telegram: {e}")

def simpan_csv(filepath, new_row):
    df_new = pd.DataFrame([new_row])
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filepath, index=False)

def tampilkan_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df_tiket = df[df["no_tiket"] == no_tiket]
        for _, row in df_tiket.iterrows():
            st.markdown(
                f"<i>{row['timestamp']}</i><br><b>{row['pengirim']}:</b> {row['isi']}",
                unsafe_allow_html=True
            )

# Setup Streamlit
st.set_page_config("Form Keluhan", layout="centered")
st.title("📨 Pengaduan Verifikasi Pembayaran")

# Session state
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_dikirim" not in st.session_state:
    st.session_state["keluhan_dikirim"] = False
if "tanggapan_dikirim" not in st.session_state:
    st.session_state["tanggapan_dikirim"] = False
if "selesai_dikirim" not in st.session_state:
    st.session_state["selesai_dikirim"] = False

# Step 1: Isi Keluhan
with st.form("form_keluhan"):
    st.subheader("📝 Formulir Keluhan")
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    isi_keluhan = st.text_area("Isi Keluhan")

    submit = st.form_submit_button("📤 Kirim Keluhan")
    if submit and not st.session_state["keluhan_dikirim"]:
        if all([nama, email, wa, no_spm, no_invoice, isi_keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket

            keluhan_data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": wa,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": isi_keluhan
            }
            simpan_csv(CSV_KELUHAN, keluhan_data)

            simpan_csv(CSV_DISKUSI, {
                "timestamp": keluhan_data["timestamp"],
                "no_tiket": no_tiket,
                "pengirim": "User",
                "isi": isi_keluhan
            })

            pesan_telegram = (
                f"<b>Keluhan Baru</b>\n"
                f"🧑 Nama: {escape_html(nama)}\n"
                f"📧 Email: {escape_html(email)}\n"
                f"📱 WA: {escape_html(wa)}\n"
                f"📄 SPM: {escape_html(no_spm)}\n"
                f"🧾 Invoice: {escape_html(no_invoice)}\n"
                f"📝 Keluhan: {escape_html(isi_keluhan)}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan format:\n/reply {no_tiket} isi_balasan</code>"
            )
            kirim_telegram(pesan_telegram)
            st.success(f"✅ Keluhan dikirim. Nomor Tiket: {no_tiket}")
            st.session_state["keluhan_dikirim"] = True
        else:
            st.warning("⚠️ Lengkapi semua kolom!")

# Step 2: Diskusi Tiket
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.markdown("---")
    st.subheader(f"💬 Diskusi Tiket {no_tiket}")
    tampilkan_diskusi(no_tiket)

    if st.button("🔄 Refresh"):
        st.rerun()

    tanggapan = st.text_area("🗨️ Tanggapan Anda", key="tanggapan")
    if st.button("📩 Kirim Tanggapan", disabled=st.session_state["tanggapan_dikirim"]):
        if tanggapan.strip():
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            simpan_csv(CSV_DISKUSI, {
                "timestamp": now,
                "no_tiket": no_tiket,
                "pengirim": "User",
                "isi": tanggapan.strip()
            })

            pesan_tanggapan = (
                f"<b>Tanggapan User</b>\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                f"💬 {escape_html(tanggapan.strip())}"
            )
            kirim_telegram(pesan_tanggapan)
            st.success("✅ Tanggapan dikirim.")
            st.session_state["tanggapan_dikirim"] = True
        else:
            st.warning("⚠️ Isi tanggapan tidak boleh kosong.")

    if st.button("✅ Tandai Selesai", disabled=st.session_state["selesai_dikirim"]):
        pesan_selesai = (
            f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah ditandai <b>SELESAI</b> oleh pelapor."
        )
        kirim_telegram(pesan_selesai)
        st.success("✅ Keluhan ditandai selesai.")
        st.session_state["selesai_dikirim"] = True
