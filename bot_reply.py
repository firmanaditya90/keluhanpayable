
import time
import requests
import pandas as pd
import os
from datetime import datetime

# Konfigurasi bot Telegram
BOT_TOKEN = "8445782873:AAEG901iWnWl8lBXEUTb69bl_qpj76t7OgE"
BALASAN_FILE = "balasan_data.csv"

# URL dasar API Telegram
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Ambil offset terakhir
last_update_id = None

def simpan_balasan(no_tiket, balasan):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"timestamp": now, "no_tiket": no_tiket, "balasan": balasan}
    df_baru = pd.DataFrame([data])
    if os.path.exists(BALASAN_FILE):
        df_lama = pd.read_csv(BALASAN_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(BALASAN_FILE, index=False)
    print(f"[✓] Balasan untuk {no_tiket} disimpan.")

def proses_pesan(pesan):
    text = pesan.get("text", "")
    if text.startswith("/reply "):
        parts = text.split(" ", 2)
        if len(parts) >= 3:
            _, no_tiket, balasan = parts
            simpan_balasan(no_tiket.strip().upper(), balasan.strip())

def run_bot():
    global last_update_id
    print("Bot balasan aktif... tekan Ctrl+C untuk berhenti.")
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?timeout=30"
            if last_update_id:
                url += f"&offset={last_update_id + 1}"
            res = requests.get(url)
            data = res.json()

            for update in data.get("result", []):
                last_update_id = update["update_id"]
                pesan = update.get("message")
                if pesan:
                    proses_pesan(pesan)
        except Exception as e:
            print("Error:", e)
        time.sleep(2)

if __name__ == "__main__":
    run_bot()
