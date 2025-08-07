import streamlit as st
import pandas as pd
import datetime
import requests
import os
import html

# ---------- Konfigurasi ---------- #
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"

TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # ID Grup Telegram

# ---------- Fungsi Utama ---------- #
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
            st.error(f"❌ Gagal kirim ke Telegram: {res.text}")
    except Exception as e:
        st.error(f"❌ Exception Telegram: {e}")

def escape_html(text):
    return html.escape(text)

def simpan_keluhan(data):
    df_new = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CSV_KELUHAN, index=False)

def simpan_diskusi(no_tiket, pengirim, isi):
    df_new = pd.DataFrame([{
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "no_tiket": no_tiket,
        "pengirim": pengirim,
        "isi": isi
    }])
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CSV_DISKUSI, index=False)

def tampilkan_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df_tiket = df[df["no_tiket"] == no_tiket]
        for _, row in df_tiket.iterrows():
            st.markdown(f"<i>{row['timestamp']}</i>  \n<b>{row['pengirim']}:</b> {row['isi']}", unsafe_allow_html=True)

# ---------- Konfigurasi Streamlit ---------- #
st.set_page_config(page_title="Keluhan Pembayaran", layout="centered")
st.title("📨 Form Pengaduan Verifikasi Pembayaran")

if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_dikirim" not in st.session_state:
    st.session_state["keluhan_dikirim"] = False
if "tanggapan_dikirim" not in st.session_state:
    st.session_state["tanggapan_dikirim"] = False
if "selesai_dikirim" not in st.session_state:
    st.session_state["selesai_dikirim"] = False

# ---------- STEP 1: Form Keluhan ---------- #
with st.form("form_keluhan"):
    st.subheader("Isi Keluhan")
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    isi_keluhan = st.text_area("Detail Keluhan")

    submit = st.form_submit_button("📤 Kirim Keluhan")
    if submit and not st.session_state["keluhan_dikirim"]:
        if all([nama, email, wa, no_spm, no_invoice, isi_keluhan]):
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
                "no_invoice": no_invoice,
                "keluhan": isi_keluhan
            }
            simpan_keluhan(data)
            simpan_diskusi(no_tiket, "User", isi_keluhan)

            pesan = (
                f"<b>📩 Keluhan Baru</b>\n"
                f"🧑 Nama: {escape_html(nama)}\n"
                f"📧 Email: {escape_html(email)}\n"
                f"📱 WA: {escape_html(wa)}\n"
                f"📄 SPM: {escape_html(no_spm)}\n"
                f"🧾 Invoice: {escape_html(no_invoice)}\n"
                f"🗒️ Keluhan: {escape_html(isi_keluhan)}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n/reply {no_tiket} <isi>"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan terkirim. Nomor Tiket: {no_tiket}")
            st.session_state["keluhan_dikirim"] = True
        else:
            st.warning("⚠️ Lengkapi semua kolom terlebih dahulu!")

# ---------- STEP 2: Riwayat Diskusi ---------- #
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.markdown("---")
    st.subheader(f"💬 Riwayat Diskusi - {no_tiket}")
    tampilkan_diskusi(no_tiket)

    if st.button("🔄 Refresh"):
        st.rerun()

    st.markdown("### ✏️ Tanggapan Anda")
    isi_tanggapan = st.text_area("Isi tanggapan", key="tanggapan_text")

    if st.button("📩 Kirim Tanggapan", disabled=st.session_state["tanggapan_dikirim"]):
        if isi_tanggapan.strip():
            simpan_diskusi(no_tiket, "User", isi_tanggapan.strip())

            pesan = (
                f"<b>🗨️ Tanggapan User</b>\n"
                f"🎟️ <b>{no_tiket}</b>\n"
                f"💬 {escape_html(isi_tanggapan.strip())}"
            )
            kirim_telegram(pesan)
            st.success("✅ Tanggapan dikirim ke Telegram.")
            st.session_state["tanggapan_dikirim"] = True
        else:
            st.warning("⚠️ Isi tanggapan tidak boleh kosong.")

    if st.button("✅ Tandai Selesai", disabled=st.session_state["selesai_dikirim"]):
        kirim_telegram(
            f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah ditandai <b>SELESAI</b> oleh pelapor."
        )
        st.success("✅ Keluhan telah ditandai selesai.")
        st.session_state["selesai_dikirim"] = True
