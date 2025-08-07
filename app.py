import streamlit as st
import pandas as pd
import datetime
import requests
import os

# ---------- Konfigurasi ----------
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # Ganti dengan ID grup Telegram kamu

# ---------- Fungsi Kirim Telegram ----------
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
            st.error(f"Gagal kirim ke Telegram: {res.text}")
    except Exception as e:
        st.error(f"Exception saat kirim Telegram: {e}")

# ---------- Simpan Keluhan ke CSV ----------
def simpan_keluhan(data):
    df_new = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CSV_KELUHAN, index=False)

# ---------- Ambil Semua Balasan Tiket ----------
def ambil_semua_balasan(no_tiket):
    if os.path.exists(CSV_BALASAN):
        df = pd.read_csv(CSV_BALASAN)
        match = df[df["no_tiket"].str.upper() == no_tiket.upper()]
        return match["balasan"].tolist()
    return []

# ---------- Kirim Tanggapan dari Pelapor ----------
def kirim_tanggapan(no_tiket, tanggapan):
    pesan = (
        f"<b>Tanggapan dari Pelapor</b>\n"
        f"🎟️ Tiket: <b>{no_tiket}</b>\n"
        f"💬 {tanggapan}"
    )
    kirim_telegram(pesan)

# ---------- Tandai Keluhan Selesai ----------
def kirim_selesai(no_tiket):
    pesan = f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah ditandai <b>SELESAI</b> oleh pelapor."
    kirim_telegram(pesan)

# ---------- STREAMLIT UI ----------
st.set_page_config("Form Keluhan SPM", layout="centered")
st.title("📨 Form Keluhan Verifikasi Pembayaran")

# Init session state
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "replied" not in st.session_state:
    st.session_state["replied"] = False
if "closed" not in st.session_state:
    st.session_state["closed"] = False

# ---------- STEP 1: Form Keluhan ----------
with st.form("form_keluhan"):
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    isi_keluhan = st.text_area("Isi Keluhan")
    tombol_submit = st.form_submit_button("📤 Kirim Keluhan")

    if tombol_submit and not st.session_state["submitted"]:
        if all([nama, email, no_wa, no_spm, no_invoice, isi_keluhan]):
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
                "keluhan": isi_keluhan
            }
            simpan_keluhan(data)

            pesan = (
                f"<b>Keluhan Baru Masuk</b>\n"
                f"🧑 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"📄 No SPM: {no_spm}\n"
                f"🧾 Invoice: {no_invoice}\n"
                f"🗒️ Keluhan: {isi_keluhan}\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n/reply {no_tiket} isi_balasan"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan berhasil dikirim. Tiket Anda: {no_tiket}")
            st.session_state["submitted"] = True
        else:
            st.warning("⚠️ Semua kolom wajib diisi!")

# ---------- STEP 2: Balasan Tiket ----------
no_tiket = st.session_state["no_tiket"]
if no_tiket:
    st.divider()
    st.subheader(f"🎟️ Tiket Anda: {no_tiket}")
    if st.button("🔄 Cek Balasan"):
        balasans = ambil_semua_balasan(no_tiket)
        if balasans:
            for idx, b in enumerate(balasans, start=1):
                st.info(f"✉️ Balasan #{idx}: {b}")
        else:
            st.warning("Belum ada balasan dari tim.")
    st.caption("Klik 'Cek Balasan' untuk update terbaru.")

    # ---------- STEP 3: Kirim Tanggapan ----------
    tanggapan = st.text_area("💬 Tanggapan Anda (opsional)")
    if st.button("📩 Kirim Tanggapan", disabled=st.session_state["replied"]):
        if tanggapan.strip():
            kirim_tanggapan(no_tiket, tanggapan.strip())
            st.success("✅ Tanggapan berhasil dikirim.")
            st.session_state["replied"] = True
        else:
            st.warning("Isi tanggapan tidak boleh kosong.")

    # ---------- STEP 4: Akhiri Keluhan ----------
    if st.button("✅ Tandai Keluhan Selesai", disabled=st.session_state["closed"]):
        kirim_selesai(no_tiket)
        st.success("🎉 Keluhan telah ditandai selesai.")
        st.session_state["closed"] = True

# Reset session (opsional)
if st.button("🔁 Reset Form"):
    st.session_state.clear()
    st.rerun()
