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
TELEGRAM_CHAT_ID = "-1002346075387"  # Supergroup ID

# Fungsi aman kirim ke Telegram
def escape_html(text):
    return html.escape(str(text))

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
        df = df[df['no_tiket'] == no_tiket]
        df = df.sort_values(by='timestamp')
        for _, row in df.iterrows():
            waktu = row.get("timestamp", "")
            pengirim = row.get("pengirim", "")
            isi = row.get("isi", "")
            st.markdown(f"📌 _{waktu}_\n**{pengirim}**: {isi}")

# Streamlit UI
st.set_page_config(page_title="📨 Form Keluhan SPM", layout="centered")
st.title("📨 Form Pengaduan Verifikasi Pembayaran")

# Inisialisasi session
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_terkirim" not in st.session_state:
    st.session_state["keluhan_terkirim"] = False
if "tanggapan_terkirim" not in st.session_state:
    st.session_state["tanggapan_terkirim"] = False
if "ditutup" not in st.session_state:
    st.session_state["ditutup"] = False

# STEP 1: Form keluhan
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    submit = st.form_submit_button("📤 Kirim Keluhan")
    if submit and not st.session_state["keluhan_terkirim"]:
        if all([nama, email, no_wa, no_spm, no_invoice, keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket
            data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": no_wa,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": keluhan
            }
            simpan_csv(CSV_KELUHAN, data)
            simpan_csv(CSV_DISKUSI, {
                "timestamp": data["timestamp"],
                "no_tiket": no_tiket,
                "pengirim": nama,
                "isi": keluhan
            })

            # Kirim ke Telegram
            pesan = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🎟️ Tiket: <b>{escape_html(no_tiket)}</b>\n"
                f"🧑 Nama: {escape_html(nama)}\n"
                f"📧 Email: {escape_html(email)}\n"
                f"📱 WA: {escape_html(no_wa)}\n"
                f"📄 SPM: {escape_html(no_spm)}\n"
                f"🧾 Invoice: {escape_html(no_invoice)}\n"
                f"🗒️ Keluhan: {escape_html(keluhan)}\n\n"
                f"Balas dengan:\n/reply {no_tiket} ISI_BALASAN"
            )
            kirim_telegram(pesan)
            st.session_state["keluhan_terkirim"] = True
            st.success(f"Keluhan dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Harap lengkapi semua kolom.")

# STEP 2: Diskusi jika ada tiket
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.subheader(f"🎟️ Tiket: {no_tiket}")

    if st.button("🔄 Refresh Balasan"):
        st.rerun()

    tampilkan_diskusi(no_tiket)

    # Tanggapan user
    if not st.session_state["ditutup"]:
        tanggapan = st.text_area("Tanggapan Anda:")
        if st.button("📤 Kirim Tanggapan", disabled=st.session_state["tanggapan_terkirim"]):
            if tanggapan.strip():
                now = datetime.datetime.now()
                simpan_csv(CSV_DISKUSI, {
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "no_tiket": no_tiket,
                    "pengirim": nama,
                    "isi": tanggapan.strip()
                })
                pesan = (
                    f"<b>Tanggapan Pelapor</b>\n"
                    f"🎟️ Tiket: <b>{escape_html(no_tiket)}</b>\n"
                    f"🧑 {escape_html(nama)}: {escape_html(tanggapan)}"
                )
                kirim_telegram(pesan)
                st.success("✅ Tanggapan dikirim.")
                st.session_state["tanggapan_terkirim"] = True
            else:
                st.warning("⚠️ Tanggapan tidak boleh kosong.")

        if st.button("✅ Tandai Selesai"):
            now = datetime.datetime.now()
            simpan_csv(CSV_DISKUSI, {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "pengirim": nama,
                "isi": "[SELESAI]"
            })
            kirim_telegram(f"✅ Keluhan dengan tiket <b>{escape_html(no_tiket)}</b> telah SELESAI oleh pelapor.")
            st.success("✅ Keluhan ditandai selesai.")
            st.session_state["ditutup"] = True
