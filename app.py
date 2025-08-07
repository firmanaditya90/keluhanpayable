import streamlit as st
import pandas as pd
import datetime
import requests
import os

# ---------- Konfigurasi ----------
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"

TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"

# ---------- Fungsi Kirim Telegram ----------
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

# ---------- Fungsi Simpan & Ambil Data ----------
def simpan_csv(data, csv_file):
    df_baru = pd.DataFrame([data])
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df = pd.concat([df, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(csv_file, index=False)

def ambil_balasan(no_tiket):
    if os.path.exists(CSV_BALASAN):
        df = pd.read_csv(CSV_BALASAN)
        match = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not match.empty:
            return match.iloc[-1]["balasan"]
    return None

def ambil_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        return df[df["no_tiket"].str.upper() == no_tiket.upper()]
    return pd.DataFrame()

# ---------- Streamlit UI ----------
st.set_page_config(page_title="SPM Helpdesk", layout="centered")
st.title("📨 Formulir Keluhan Verifikasi Pembayaran")

# Inisialisasi session state
for key in ["no_tiket", "kirim_disabled", "tanggapan_disabled", "akhiri_disabled"]:
    if key not in st.session_state:
        st.session_state[key] = False if "disabled" in key else None

# ---------- STEP 1: Form Keluhan ----------
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    kirim = st.form_submit_button("📤 Kirim Keluhan", disabled=st.session_state.kirim_disabled)
    if kirim:
        if all([nama, email, no_wa, no_spm, no_invoice, keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state.no_tiket = no_tiket
            st.session_state.kirim_disabled = True

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
            simpan_csv(data, CSV_KELUHAN)

            pesan = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"📄 No SPM: {no_spm}\n"
                f"🧾 Invoice: {no_invoice}\n"
                f"🗒️ Keluhan: {keluhan}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n<code>/reply {no_tiket} isi_balasan</code>"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan berhasil dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi.")

# ---------- STEP 2: Cek Balasan ----------
no_tiket = st.session_state.no_tiket
if no_tiket:
    st.markdown("---")
    st.subheader(f"🎟️ Tiket Anda: {no_tiket}")

    if st.button("🔄 Cek Balasan PIC"):
        balasan = ambil_balasan(no_tiket)
        if balasan:
            st.success(f"📩 Balasan:\n\n{balasan}")
        else:
            st.info("⏳ Belum ada balasan dari PIC.")

    # ---------- STEP 3: Diskusi Lanjutan ----------
    st.markdown("### 💬 Diskusi")
    diskusi_df = ambil_diskusi(no_tiket)
    if not diskusi_df.empty:
        for _, row in diskusi_df.iterrows():
            if row["pengirim"] == "user":
                st.markdown(f"👤 <b>Anda:</b> {row['pesan']}", unsafe_allow_html=True)
            else:
                st.markdown(f"🛠️ <b>PIC:</b> {row['pesan']}", unsafe_allow_html=True)

    tanggapan = st.text_area("✏️ Kirim Tanggapan")
    if st.button("📨 Kirim Tanggapan", disabled=st.session_state.tanggapan_disabled):
        if tanggapan.strip():
            st.session_state.tanggapan_disabled = True
            pesan = f"<b>Tanggapan dari Pelapor</b>\n🎟️ Tiket: <b>{no_tiket}</b>\n💬 {tanggapan}"
            kirim_telegram(pesan)
            simpan_csv({"no_tiket": no_tiket, "pengirim": "user", "pesan": tanggapan}, CSV_DISKUSI)
            st.success("✅ Tanggapan terkirim.")
        else:
            st.warning("⚠️ Tanggapan tidak boleh kosong.")

    # ---------- STEP 4: Selesaikan Keluhan ----------
    if st.button("✅ Tandai Keluhan Selesai", disabled=st.session_state.akhiri_disabled):
        st.session_state.akhiri_disabled = True
        pesan = f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah <b>SELESAI</b> oleh pelapor."
        kirim_telegram(pesan)
        st.success("✅ Keluhan ditandai selesai.")
