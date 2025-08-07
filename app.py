import streamlit as st
import pandas as pd
import datetime
import os
import requests

# --- Konfigurasi ---
CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"

TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"  # ID grup atau channel

# --- Fungsi kirim ke Telegram ---
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

# --- Simpan keluhan ke file ---
def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_KELUHAN, index=False)

# --- Simpan diskusi ke file ---
def simpan_diskusi(no_tiket, pengirim, isi):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"no_tiket": no_tiket, "pengirim": pengirim, "isi": isi, "timestamp": now}
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(CSV_DISKUSI, index=False)

# --- Tampilkan diskusi lengkap ---
def tampilkan_diskusi(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        if set(["no_tiket", "pengirim", "isi", "timestamp"]).issubset(df.columns):
            chat = df[df["no_tiket"] == no_tiket]
            for _, row in chat.iterrows():
                pengirim = row.get("pengirim", "???")
                isi = row.get("isi", "")
                waktu = row.get("timestamp", "")
                with st.chat_message("user" if pengirim == "User" else "assistant"):
                    st.markdown(f"_{waktu}_\n**{pengirim}**:\n{isi}")
        else:
            st.warning("⚠️ Format CSV tidak valid.")
    else:
        st.info("📭 Belum ada diskusi.")

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Keluhan SPM", layout="centered")
st.title("📨 Formulir Pengaduan Verifikasi Pembayaran")

# --- Session State ---
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_dikirim" not in st.session_state:
    st.session_state["keluhan_dikirim"] = False
if "tanggapan_dikirim" not in st.session_state:
    st.session_state["tanggapan_dikirim"] = False
if "keluhan_selesai" not in st.session_state:
    st.session_state["keluhan_selesai"] = False

# --- Form Pengaduan ---
with st.form("form_keluhan"):
    st.subheader("📝 Isi Keluhan")
    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    no_wa = st.text_input("No WhatsApp")
    no_spm = st.text_input("No SPM")
    no_invoice = st.text_input("No Invoice")
    keluhan = st.text_area("Isi Keluhan")

    submitted = st.form_submit_button("📤 Kirim Keluhan")
    if submitted and not st.session_state["keluhan_dikirim"]:
        if all([nama, email, no_wa, no_spm, no_invoice, keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state["no_tiket"] = no_tiket
            st.session_state["keluhan_dikirim"] = True

            data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": no_wa,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": keluhan,
            }
            simpan_keluhan(data)
            simpan_diskusi(no_tiket, "User", keluhan)

            pesan = (
                f"<b>📨 Keluhan Baru</b>\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                f"👤 Nama: {nama}\n"
                f"📧 Email: {email}\n"
                f"📞 WA: {no_wa}\n"
                f"🗂️ SPM: {no_spm}\n"
                f"📄 Invoice: {no_invoice}\n"
                f"📝 Keluhan:\n{keluhan}\n\n"
                f"Balas dengan:\n/reply {no_tiket} <isi>"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan berhasil dikirim.\nNomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom harus diisi.")

# --- Jika Tiket Ada ---
no_tiket = st.session_state["no_tiket"]
if no_tiket:
    st.divider()
    st.subheader(f"💬 Diskusi Tiket: {no_tiket}")

    if st.button("🔄 Refresh Diskusi"):
        st.rerun()

    tampilkan_diskusi(no_tiket)

    # --- Tanggapan User ---
    st.markdown("#### ✏️ Kirim Tanggapan")
    isi_tanggapan = st.text_area("Isi Tanggapan")
    if st.button("📩 Kirim Tanggapan", disabled=st.session_state["tanggapan_dikirim"]):
        if isi_tanggapan.strip():
            simpan_diskusi(no_tiket, "User", isi_tanggapan.strip())
            kirim_telegram(
                f"<b>🗨️ Tanggapan User</b>\n🎟️ <b>{no_tiket}</b>\n💬 {isi_tanggapan.strip()}"
            )
            st.success("✅ Tanggapan dikirim ke Telegram.")
            st.session_state["tanggapan_dikirim"] = True
        else:
            st.warning("Tanggapan tidak boleh kosong.")

    # --- Akhiri Keluhan ---
    if st.button("✅ Tandai Keluhan Selesai", disabled=st.session_state["keluhan_selesai"]):
        kirim_telegram(f"✅ Keluhan dengan tiket <b>{no_tiket}</b> telah SELESAI.")
        simpan_diskusi(no_tiket, "User", "[Keluhan ditandai selesai oleh pelapor]")
        st.success("Keluhan ditandai selesai.")
        st.session_state["keluhan_selesai"] = True
