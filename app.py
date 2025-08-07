import streamlit as st
import pandas as pd
import datetime
import requests
import os
import html

CSV_KELUHAN = "keluhan_data.csv"
CSV_DISKUSI = "diskusi_data.csv"
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_CHAT_ID = "-1002346075387"

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

def tampilkan_chat(no_tiket):
    if os.path.exists(CSV_DISKUSI):
        df = pd.read_csv(CSV_DISKUSI)
        df = df[df['no_tiket'] == no_tiket]
        df = df.sort_values(by='timestamp')
        st.markdown("### 💬 Diskusi Tiket")
        for _, row in df.iterrows():
            pengirim = row.get("pengirim", "")
            pesan = row.get("isi", "")
            waktu = row.get("timestamp", "")
            if pengirim == "User":
                st.markdown(
                    f"""
                    <div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin:5px 0; text-align:right'>
                        <b>{pengirim}</b><br>{pesan}<br><small>{waktu}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(
                    f"""
                    <div style='background-color:#F1F0F0; padding:10px; border-radius:10px; margin:5px 0; text-align:left'>
                        <b>{pengirim}</b><br>{pesan}<br><small>{waktu}</small>
                    </div>
                    """, unsafe_allow_html=True)

# UI Start
st.set_page_config("💬 Keluhan SPM", layout="centered")
st.title("📨 Form Keluhan & Chat Interaktif")

# Session
if "no_tiket" not in st.session_state:
    st.session_state["no_tiket"] = None
if "keluhan_terkirim" not in st.session_state:
    st.session_state["keluhan_terkirim"] = False

# Form Keluhan
if not st.session_state["keluhan_terkirim"]:
    with st.form("kirim_keluhan"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email")
        no_wa = st.text_input("Nomor WhatsApp")
        no_spm = st.text_input("Nomor SPM")
        no_invoice = st.text_input("Nomor Invoice")
        isi_keluhan = st.text_area("Isi Keluhan")
        submit = st.form_submit_button("📤 Kirim Keluhan")

        if submit:
            if all([nama, email, no_wa, no_spm, no_invoice, isi_keluhan]):
                now = datetime.datetime.now()
                no_tiket = f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"
                st.session_state["no_tiket"] = no_tiket
                st.session_state["keluhan_terkirim"] = True

                # Simpan ke CSV
                simpan_csv(CSV_KELUHAN, {
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "no_tiket": no_tiket,
                    "nama": nama,
                    "email": email,
                    "no_wa": no_wa,
                    "no_spm": no_spm,
                    "no_invoice": no_invoice,
                    "keluhan": isi_keluhan
                })

                simpan_csv(CSV_DISKUSI, {
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "no_tiket": no_tiket,
                    "pengirim": "User",
                    "isi": isi_keluhan
                })

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
                st.success(f"✅ Keluhan berhasil dikirim. Tiket: {no_tiket}")
            else:
                st.warning("⚠️ Semua kolom wajib diisi.")
else:
    no_tiket = st.session_state["no_tiket"]
    st.subheader(f"🎟️ Tiket: `{no_tiket}`")
    if st.button("🔄 Refresh Chat"):
        tampilkan_chat(no_tiket)

    tampilkan_chat(no_tiket)

    with st.form("form_tanggapan"):
        user_reply = st.text_input("Ketik Tanggapan Anda:")
        send = st.form_submit_button("📨 Kirim")

        if send and user_reply.strip():
            now = datetime.datetime.now()
            simpan_csv(CSV_DISKUSI, {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "no_tiket": no_tiket,
                "pengirim": "User",
                "isi": user_reply.strip()
            })
            telegram_pesan = (
                f"<b>📨 Tanggapan User</b>\n"
                f"🎟️ Tiket: <b>{no_tiket}</b>\n"
                f"💬 {escape_html(user_reply.strip())}"
            )
            kirim_telegram(telegram_pesan)
            st.success("✅ Tanggapan terkirim!")

    if st.button("✅ Tandai Keluhan Selesai"):
        now = datetime.datetime.now()
        simpan_csv(CSV_DISKUSI, {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "no_tiket": no_tiket,
            "pengirim": "User",
            "isi": "Keluhan ditandai selesai oleh pelapor."
        })
        kirim_telegram(f"✅ Tiket <b>{no_tiket}</b> telah SELESAI oleh pelapor.")
        st.success("🎉 Keluhan ditandai selesai.")
