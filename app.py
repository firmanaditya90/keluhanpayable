
import streamlit as st
import pandas as pd
import datetime
import os

CSV_KELUHAN = "keluhan_data.csv"
CSV_BALASAN = "balasan_data.csv"

def simpan_keluhan(data):
    df_baru = pd.DataFrame([data])
    if os.path.exists(CSV_KELUHAN):
        df_lama = pd.read_csv(CSV_KELUHAN)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(CSV_KELUHAN, index=False)

def buat_no_tiket():
    now = datetime.datetime.now()
    return f"TIKET-{now.strftime('%Y%m%d%H%M%S')}"

st.title("📨 Form Keluhan Verifikasi Pembayaran")

menu = st.sidebar.selectbox("Menu", ["Isi Keluhan", "Cek Tiket"])

if menu == "Isi Keluhan":
    st.subheader("Form Pengisian Keluhan")

    nama = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    whatsapp = st.text_input("Nomor WhatsApp")
    no_spm = st.text_input("Nomor SPM")
    no_invoice = st.text_input("Nomor Invoice")
    keluhan = st.text_area("Isi Keluhan")

    if st.button("Kirim Keluhan"):
        if nama and email and no_spm and no_invoice and keluhan:
            no_tiket = buat_no_tiket()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "timestamp": timestamp,
                "no_tiket": no_tiket,
                "nama": nama,
                "email": email,
                "whatsapp": whatsapp,
                "no_spm": no_spm,
                "no_invoice": no_invoice,
                "keluhan": keluhan
            }
            simpan_keluhan(data)
            st.success(f"Keluhan berhasil dikirim ✅\nNo Tiket Anda: {no_tiket}")
            st.info("Mohon bersabar, keluhan Anda akan segera diproses oleh tim kami.")
        else:
            st.warning("Harap lengkapi semua isian.")

elif menu == "Cek Tiket":
    st.subheader("🔍 Cek Status Tiket")

    input_tiket = st.text_input("Masukkan No Tiket")
    if st.button("Cek Status"):
        if os.path.exists(CSV_KELUHAN):
            df_keluhan = pd.read_csv(CSV_KELUHAN)
            keluhan = df_keluhan[df_keluhan["no_tiket"] == input_tiket]
            if keluhan.empty:
                st.error("No Tiket tidak ditemukan.")
            else:
                st.write("### Keluhan Anda")
                st.write(keluhan[["timestamp", "nama", "no_spm", "no_invoice", "keluhan"]].iloc[0])

                if os.path.exists(CSV_BALASAN):
                    df_balasan = pd.read_csv(CSV_BALASAN)
                    balasan = df_balasan[df_balasan["no_tiket"] == input_tiket]
                    if not balasan.empty:
                        st.success("### Balasan dari Tim:\n" + balasan["balasan"].iloc[0])
                    else:
                        st.info("Keluhan Anda sedang diproses, mohon menunggu 🙏")
                else:
                    st.info("Belum ada balasan saat ini.")
        else:
            st.error("Belum ada data keluhan.")
