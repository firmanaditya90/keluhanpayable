import streamlit as st
import pandas as pd
import datetime
import requests
import os

# === Konfigurasi ===
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # Ganti dengan ID grup kamu

# === Fungsi Telegram ===
def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        st.error(f"❌ Gagal kirim ke Telegram: {r.text}")

# === Simpan keluhan ke CSV ===
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_KELUHAN, index=False)

# === Ambil balasan terakhir ===
def ambil_balasan(no_tiket):
    if os.path.exists(CSV_BALASAN):
        df = pd.read_csv(CSV_BALASAN)
        df = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not df.empty:
            return df.iloc[-1]["balasan"]
    return None

# === Ambil diskusi lengkap ===
def ambil_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        if not df.empty:
            return df.sort_values("timestamp")
    return pd.DataFrame()

# === Kirim tanggapan dari user ===
def kirim_tanggapan(no_tiket, isi):
    pesan = f"<b>Tanggapan dari Pelapor</b>\n🎟️ Tiket: <b>{no_tiket}</b>\n💬 {isi}\n\nBalas dengan:\n/tanggapan {no_tiket} <balasan PIC>"
    kirim_telegram(pesan)

# === Tandai keluhan selesai ===
def kirim_akhiri(no_tiket):
    pesan = f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah <b>SELESAI</b> oleh pelapor."
    kirim_telegram(pesan)

# === Konfigurasi Streamlit ===
st.set_page_config(page_title="Keluhan Verifikasi Pembayaran", layout="centered")
st.title("📨 Form Keluhan Verifikasi Pembayaran")

# Inisialisasi Session
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "tanggapan_sent" not in st.session_state:
    st.session_state["tanggapan_sent"] = False
if "selesai_sent" not in st.session_state:
    st.session_state["selesai_sent"] = False

# === Form Input ===
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    submitted = st.form_submit_button("📤 Kirim Keluhan")
    if submitted and not st.session_state["submitted"]:
        if all([nama, email, no_wa, no_spm, no_invoice, keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket
            st.session_state["submitted"] = True

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

            pesan = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"📄 No SPM: {no_spm}\n"
                f"🧾 Invoice: {no_invoice}\n"
                f"🗒️ Keluhan: {keluhan}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n/reply {no_tiket} <isi balasan>"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi.")

# === Lihat Balasan dan Diskusi ===
no_tiket = st.session_state.get("no_tiket")
if no_tiket:
    st.divider()
    st.subheader(f"🎫 Tiket Aktif: {no_tiket}")

    if st.button("🔄 Cek Balasan dan Diskusi"):
        balasan = ambil_balasan(no_tiket)
        if balasan:
            st.success(f"📩 Balasan Terakhir:\n\n{balasan}")
        else:
            st.info("Belum ada balasan dari tim.")

        diskusi_df = ambil_diskusi(no_tiket)
        if not diskusi_df.empty:
            st.subheader("💬 Riwayat Diskusi")
            for _, row in diskusi_df.iterrows():
                waktu = pd.to_datetime(row["timestamp"]).strftime("%d-%m-%Y %H:%M")
                pengirim = row["pengirim"]
                isi = row["isi"]
                st.markdown(f"**{pengirim}** ({waktu}): {isi}")
        else:
            st.info("💬 Belum ada diskusi tambahan.")

    st.divider()

    # === Tanggapan User ===
    tanggapan = st.text_area("Tanggapan Anda")
    if st.button("📨 Kirim Tanggapan", disabled=st.session_state["tanggapan_sent"]):
        if tanggapan.strip():
            kirim_tanggapan(no_tiket, tanggapan)
            st.session_state["tanggapan_sent"] = True
            st.success("Tanggapan dikirim ke Telegram.")
        else:
            st.warning("⚠️ Tanggapan tidak boleh kosong.")

    # === Tandai Selesai ===
    if st.button("✅ Tandai Selesai", disabled=st.session_state["selesai_sent"]):
        kirim_akhiri(no_tiket)
        st.session_state["selesai_sent"] = True
        st.success("✅ Keluhan ditandai selesai.")
