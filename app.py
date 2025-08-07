import streamlit as st
import pandas as pd
import datetime
import requests
import os
import html

# Konfigurasi file dan token
CSV_KELUHAN = "keluhan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"

# Escape karakter HTML agar aman dikirim ke Telegram
def escape_html(text):
    return html.escape(str(text))

# Fungsi kirim ke Telegram
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

# Simpan ke file CSV
def simpan_csv(filepath, new_row):
    df_new = pd.DataFrame([new_row])
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filepath, index=False)

# Tampilkan diskusi
def tampilkan_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)

        if 'timestamp' not in df.columns:
            st.warning("⚠️ File diskusi_data.csv belum lengkap.")
            return

        df = df[df['no_tiket'] == no_tiket]
        df = df.sort_values(by='timestamp')
        st.markdown("### 💬 Riwayat Diskusi")
        for _, row in df.iterrows():
            waktu = row.get("timestamp", "")
            pengirim = row.get("pengirim", "")
            isi = row.get("isi", "")
            st.markdown(f"🕒 _{waktu}_\n**{pengirim}**: {isi}")

# ================================
# UI STREAMLIT
# ================================

st.set_page_config(page_title="💬 Keluhan SPM", layout="centered")
st.title("📨 Form Keluhan Verifikasi Pembayaran")

if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_terkirim" not in st.session_state:
    st.session_state["keluhan_terkirim"] = False
if "tanggapan_terkirim" not in st.session_state:
    st.session_state["tanggapan_terkirim"] = False
if "keluhan_selesai" not in st.session_state:
    st.session_state["keluhan_selesai"] = False

# Step 1: Kirim keluhan
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    isi_keluhan = st.text_area("Isi Keluhan")
    submit = st.form_submit_button("📤 Kirim Keluhan")

    if submit and not st.session_state["keluhan_terkirim"]:
        if all([nama, email, no_wa, no_spm, no_invoice, isi_keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket
            st.session_state["keluhan_terkirim"] = True

            # Simpan data ke keluhan_data.csv
            data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": no_wa,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": isi_keluhan
            }
            simpan_csv(CSV_KELUHAN, data)

            # Kirim ke Telegram
            pesan = (
                f"<b>📩 Keluhan Baru Masuk</b>\n"
                f"🧑 Nama: {escape_html(nama)}\n"
                f"📧 Email: {escape_html(email)}\n"
                f"📞 WA: {escape_html(no_wa)}\n"
                f"📄 No SPM: {escape_html(no_spm)}\n"
                f"🧾 Invoice: {escape_html(no_invoice)}\n"
                f"🗒️ Keluhan: {escape_html(isi_keluhan)}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Untuk membalas:\n/reply {no_tiket} balasan Anda"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan berhasil dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi.")

# Step 2: Cek balasan dan diskusi
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.markdown("---")
    st.subheader(f"🎟️ Nomor Tiket: `{no_tiket}`")

    if st.button("🔄 Refresh Balasan & Diskusi"):
        tampilkan_diskusi(no_tiket)

    tampilkan_diskusi(no_tiket)

    # Step 3: Tanggapan user
    with st.form("form_tanggapan"):
        isi_tanggapan = st.text_area("Tanggapan Anda:")
        submit_tanggapan = st.form_submit_button("📩 Kirim Tanggapan")

        if submit_tanggapan and not st.session_state["tanggapan_terkirim"]:
            if isi_tanggapan.strip():
                now = datetime.datetime.now()
                simpan_csv(CSV_DISKUSI, {
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "no_tiket": no_tiket,
                    "pengirim": "User",
                    "isi": isi_tanggapan.strip()
                })
                st.session_state["tanggapan_terkirim"] = True
                pesan = (
                    f"<b>✉️ Tanggapan dari Pelapor</b>\n"
                    f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                    f"💬 {escape_html(isi_tanggapan.strip())}"
                )
                kirim_telegram(pesan)
                st.success("✅ Tanggapan berhasil dikirim.")
            else:
                st.warning("⚠️ Tanggapan tidak boleh kosong.")

    # Step 4: Akhiri keluhan
    if st.button("✅ Tandai Keluhan Selesai") and not st.session_state["keluhan_selesai"]:
        now = datetime.datetime.now()
        simpan_csv(CSV_DISKUSI, {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "no_tiket": no_tiket,
            "pengirim": "User",
            "isi": "Keluhan telah diselesaikan oleh pelapor."
        })
        pesan = f"✅ Keluhan dengan Tiket <b>{no_tiket}</b> telah <b>SELESAI</b> oleh pelapor."
        kirim_telegram(pesan)
        st.session_state["keluhan_selesai"] = True
        st.success("✅ Keluhan ditandai selesai.")
