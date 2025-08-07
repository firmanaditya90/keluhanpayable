import streamlit as st
import pandas as pd
import datetime
import requests
import os

# Konfigurasi
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # Supergroup ID

# Fungsi kirim pesan ke Telegram
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
            st.error(f"Gagal kirim ke Telegram: {r.text}")
    except Exception as e:
        st.error(f"Exception saat kirim Telegram: {e}")

# Fungsi simpan keluhan ke CSV
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_KELUHAN, index=False)

# Fungsi ambil balasan
def ambil_balasan(no_tiket):
    if os.path.exists(CSV_BALASAN):
        df = pd.read_csv(CSV_BALASAN)
        match = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not match.empty:
            return match.iloc[-1]["balasan"]
    return None

# Fungsi kirim tanggapan user
def kirim_tanggapan(no_tiket, isi_tanggapan):
    pesan = f"<b>Tanggapan dari Pelapor</b>\n🎟️ Tiket: <b>{no_tiket}</b>\n💬 {isi_tanggapan}"
    kirim_telegram(pesan)

# Fungsi kirim notifikasi selesai
def kirim_akhiri(no_tiket):
    pesan = f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah <b>SELESAI</b> oleh pelapor."
    kirim_telegram(pesan)

# ---------- UI Streamlit ---------- #

st.set_page_config(page_title="Keluhan SPM", layout="centered")
st.title("📨 Form Keluhan Verifikasi Pembayaran")

# Inisialisasi session
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None

# STEP 1: Isi Keluhan
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    submit = st.form_submit_button("Kirim Keluhan")
    if submit:
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
            simpan_keluhan(data)

            # Kirim ke Telegram
            pesan_telegram = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"📄 No SPM: {no_spm}\n"
                f"🧾 Invoice: {no_invoice}\n"
                f"🗒️ Keluhan: {keluhan}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n/reply {no_tiket} <isi_balasan>"
            )
            kirim_telegram(pesan_telegram)

            st.success(f"Keluhan berhasil dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi!")

# STEP 2: Tampilkan balasan jika tiket sudah dibuat
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.subheader(f"🎟️ Nomor Tiket: {no_tiket}")
    if st.button("🔄 Cek Balasan PIC"):
        balasan = ambil_balasan(no_tiket)
        if balasan:
            st.success(f"✅ Balasan dari Tim:\n\n{balasan}")
        else:
            st.info("❌ Belum ada balasan dari tim.")

    # STEP 3: Kirim tanggapan tambahan
    tanggapan = st.text_area("Tanggapan Anda terhadap Balasan")
    if st.button("📤 Kirim Tanggapan"):
        if tanggapan.strip():
            kirim_tanggapan(no_tiket, tanggapan.strip())
            st.success("Tanggapan berhasil dikirim ke Telegram.")
        else:
            st.warning("Isi tanggapan tidak boleh kosong.")

    # STEP 4: Akhiri
    if st.button("✅ Akhiri Keluhan"):
        kirim_akhiri(no_tiket)
        st.success("Keluhan ditandai selesai.")

