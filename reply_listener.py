import requests
import time
import pandas as pd
import os

BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
BALASAN_FILE = "balasan_data.csv"

LAST_UPDATE_ID_FILE = "last_update_id.txt"

def simpan_balasan(no_tiket, balasan):
    data = {
        "no_tiket": no_tiket,
        "balasan": balasan,
        "waktu": pd.Timestamp.now()
    }
    df_baru = pd.DataFrame([data])
    if os.path.exists(BALASAN_FILE):
        df_lama = pd.read_csv(BALASAN_FILE)
        df = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df = df_baru
    df.to_csv(BALASAN_FILE, index=False)
    print(f"Balasan disimpan untuk {no_tiket}")

def get_last_update_id():
    if os.path.exists(LAST_UPDATE_ID_FILE):
        with open(LAST_UPDATE_ID_FILE, "r") as f:
            return int(f.read())
    return 0

def set_last_update_id(update_id):
    with open(LAST_UPDATE_ID_FILE, "w") as f:
        f.write(str(update_id))

def listen_for_replies():
    print("Mendengarkan balasan dari Telegram...")
    last_update_id = get_last_update_id()
    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}"
        try:
            response = requests.get(url)
            data = response.json()

            if data["ok"] and data["result"]:
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "")
                    if text.startswith("/reply "):
                        try:
                            bagian = text.split(" ", 2)
                            no_tiket = bagian[1]
                            isi_balasan = bagian[2]
                            simpan_balasan(no_tiket, isi_balasan)
                        except Exception as e:
                            print(f"Format balasan salah atau gagal proses: {e}")

                set_last_update_id(last_update_id)
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
        time.sleep(3)

if __name__ == "__main__":
    listen_for_replies()
