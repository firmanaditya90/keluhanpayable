import requests
import time
import os
import pandas as pd

# Konfigurasi
TELEGRAM_BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
BALASAN_FILE = "balasan_data.csv"
UPDATE_ID_FILE = "last_update_id.txt"

def get_last_update_id():
    if os.path.exists(UPDATE_ID_FILE):
        with open(UPDATE_ID_FILE, "r") as f:
            return int(f.read())
    return None

def save_last_update_id(update_id):
    with open(UPDATE_ID_FILE, "w") as f:
        f.write(str(update_id))

def simpan_balasan(no_tiket, balasan):
    data = {
        "no_tiket": no_tiket,
        "balasan": balasan,
        "timestamp": pd.Timestamp.now()
    }

    df_baru = pd.DataFrame([data])
    if os.path.exists(BALASAN_FILE):
        df_lama = pd.read_csv(BALASAN_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru

    df.to_csv(BALASAN_FILE, index=False)
    print(f"✅ Balasan untuk {no_tiket} disimpan!")

def proses_pesan(pesan):
    if "text" in pesan["message"]:
        teks = pesan["message"]["text"]
        if teks.startswith("/reply"):
            bagian = teks.split(" ", 2)
            if len(bagian) >= 3:
                no_tiket = bagian[1].strip()
                balasan = bagian[2].strip()
                simpan_balasan(no_tiket, balasan)
                return True
    return False

def jalankan_listener():
    print("📡 Mendengarkan balasan dari Telegram...")
    last_update_id = get_last_update_id()

    while True:
        try:
            params = {"timeout": 10, "offset": last_update_id + 1 if last_update_id else None}
            response = requests.get(f"{TELEGRAM_API_URL}/getUpdates", params=params, timeout=15)
            result = response.json()

            if result["ok"]:
                for update in result["result"]:
                    last_update_id = update["update_id"]
                    save_last_update_id(last_update_id)

                    if "message" in update:
                        berhasil = proses_pesan(update)
                        if berhasil:
                            print(f"📨 Balasan diproses dari: {update['message']['from']['first_name']}")

        except Exception as e:
            print(f"❌ Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    jalankan_listener()
