import streamlit as st
import pandas as pd
import datetime
import requests
import os
import html
import io

# ================= CONFIG =================
CSV_KELUHAN = "keluhan_data.csv"
DISKUSI_CSV_URL = "https://raw.githubusercontent.com/firmanaditya90/keluhanpayable/main/diskusi_data.csv"
BALASAN_CSV_URL = "https://raw.githubusercontent.com/firmanaditya90/keluhanpayable/main/balasan_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"
# =========================================

# Escape HTML untuk keamanan pesan Telegram
def escape_html(text):
    return html.escape(str(text))

# Kirim pesan ke Telegram
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

# Simpan keluhan ke CSV lokal
def simpan_keluhan(data):
    df_new = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CSV_KELUHAN, index=False)

# Ambil CSV dari GitHub
def fetch_csv_from_github(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return pd.read_csv(io.StringIO(res.text))
    except:
        pass
    return pd.DataFrame()

# Tampilkan chat / diskusi
def tampilkan_chat(no_tiket):
    df = fetch_csv_from_github(DISKUSI_CSV_URL)
    if df.empty or 'timestamp' not in df.columns:
        st.warning("⚠️ Tidak bisa menampilkan diskusi. File kosong atau rusak.")
        return

    df = df[df['no_tiket'] == no_tiket].sort_values(by="timestamp")
    for _, row in df.iterrows():
        pengirim = row.get("pengirim", "")
        isi = row.get("isi", "")
        waktu = row.get("timestamp", "")
        with st.chat_message("assistant" if pengirim != "User" else "user"):
            st.markdown(f"**_{pengirim}_** • {waktu}")
            st.write(isi)

# ================= STREAMLIT =================
st.set_page_config(page_title="Keluhan SPM", layout="centered")
st.title("💬 Form Keluhan & Chat Diskusi")

if "no_tiket" not in st.session_state:
    st.session_state.no_tiket = None
if "keluhan_terkirim" not in st.session_state:
    st.session_state.keluhan_terkirim = False
if "tanggapan_terkirim" not in st.session_state:
    st.session_state.tanggapan_terkirim = False
if "keluhan_selesai" not in st.session_state:
    st.session_state.keluhan_selesai = False

# ======== FORM KELUHAN ========
with st.form("form_keluhan"):
    st.subheader("📨 Kirim Keluhan Baru")
    nama = st.text_input("Nama")
    email = st.text_input("Email")
    wa = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("No. SPM")
    invoice = st.text_input("No. Invoice")
    keluhan = st.text_area("Isi Keluhan")
    submit = st.form_submit_button("📤 Kirim")

    if submit and not st.session_state.keluhan_terkirim:
        if all([nama, email, wa, no_spm, invoice, keluhan]):
            now = datetime.datetime.now()
            no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
            st.session_state.no_tiket = no_tiket
            st.session_state.keluhan_terkirim = True

            data = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "no_wa": wa,
                "no_spm": no_spm,
                "no_invoice": invoice,
                "keluhan": keluhan
            }
            simpan_keluhan(data)

            pesan = (
                f"<b>📩 Keluhan Baru</b>\n"
                f"🧑 {escape_html(nama)}\n📧 {escape_html(email)}\n📞 {escape_html(wa)}\n"
                f"📄 SPM: {escape_html(no_spm)}\n🧾 Invoice: {escape_html(invoice)}\n"
                f"📝 {escape_html(keluhan)}\n🎟️ Tiket: <b>{no_tiket}</b>\n\n"
                f"Balas dengan:\n/reply {no_tiket} isi_balasan"
            )
            kirim_telegram(pesan)
            st.success(f"✅ Keluhan dikirim. Nomor Tiket: {no_tiket}")
        else:
            st.warning("⚠️ Semua kolom wajib diisi!")

# ======== DISKUSI / CHAT ========
no_tiket = st.session_state.no_tiket
if no_tiket:
    st.divider()
    st.subheader(f"🎟️ Tiket Aktif: `{no_tiket}`")

    if st.button("🔄 Refresh Chat"):
        tampilkan_chat(no_tiket)

    tampilkan_chat(no_tiket)

    # ======== Kirim Tanggapan User ========
    with st.form("form_tanggapan"):
        tanggapan = st.text_area("💬 Balasan Anda")
        send = st.form_submit_button("📩 Kirim Tanggapan")
        if send and not st.session_state.tanggapan_terkirim:
            if tanggapan.strip():
                now = datetime.datetime.now()
                pesan = (
                    f"<b>📨 Tanggapan dari Pelapor</b>\n"
                    f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                    f"💬 {escape_html(tanggapan.strip())}"
                )
                kirim_telegram(pesan)
                st.session_state.tanggapan_terkirim = True
                st.success("✅ Tanggapan dikirim.")
            else:
                st.warning("❗ Kolom tanggapan kosong.")

    # ======== Akhiri ========
    if st.button("✅ Tandai Keluhan Selesai") and not st.session_state.keluhan_selesai:
        pesan = f"✅ Keluhan Tiket <b>{no_tiket}</b> telah SELESAI oleh pelapor."
        kirim_telegram(pesan)
        st.session_state.keluhan_selesai = True
        st.success("✅ Keluhan ditandai selesai.")
