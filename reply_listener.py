
import os
import time
import pandas as pd
import requests
import re

# Konfigurasi
TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
BALASAN_FILE = "balasan_data.csv"
LAST_UPDATE_FILE = "last_update_id.txt"
POLL_INTERVAL = 3  # detik

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    try:
        res = requests.get(url, params=params)
        return res.json()
    except Exception as e:
        print("Gagal ambil update:", e)
        return {"ok": False, "result": []}

def simpan_balasan(no_tiket, balasan):
    data_baru = pd.DataFrame([{"no_tiket": no_tiket, "balasan": balasan}])
    if os.path.exists(BALASAN_FILE):
        df_lama = pd.read_csv(BALASAN_FILE)
        df = pd.concat([df_lama, data_baru], ignore_index=True)
    else:
        df = data_baru
    df.to_csv(BALASAN_FILE, index=False)
    print(f"✅ Balasan untuk {no_tiket} disimpan.")

def muat_last_update_id():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read().strip())
    return None

def simpan_last_update_id(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))

def proses_pesan(pesan):
    if "text" in pesan.get("message", {}):
        text = pesan["message"]["text"]
        match = re.match(r'^/reply\s+(TIKET-\d{14})\s+(.+)', text, re.IGNORECASE)
        if match:
            no_tiket = match.group(1).strip()
            balasan = match.group(2).strip()
            simpan_balasan(no_tiket, balasan)

def main():
    print("📡 Memulai reply listener...")
    last_update_id = muat_last_update_id()

    while True:
        hasil = get_updates(offset=last_update_id + 1 if last_update_id else None)
        if hasil.get("ok"):
            for pesan in hasil["result"]:
                proses_pesan(pesan)
                last_update_id = pesan["update_id"]
                simpan_last_update_id(last_update_id)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
