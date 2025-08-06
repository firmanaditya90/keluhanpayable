import requests
import time
import csv
import os

BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
BALASAN_FILE = "balasan_data.csv"
OFFSET_FILE = "last_update_id.txt"

def get_last_update_id():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_last_update_id(update_id):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(update_id))

def simpan_balasan(no_tiket, balasan):
    file_exists = os.path.exists(BALASAN_FILE)
    with open(BALASAN_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["no_tiket", "balasan"])
        writer.writerow([no_tiket, balasan])

def run_listener():
    print("🟢 Listener aktif...")
    while True:
        offset = get_last_update_id()
        resp = requests.get(URL, params={"offset": offset + 1})
        data = resp.json()

        if "result" in data:
            for update in data["result"]:
                update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "")

                if text.lower().startswith("/reply"):
                    parts = text.split(maxsplit=2)
                    if len(parts) == 3:
                        _, no_tiket, isi_balasan = parts
                        print(f"🔔 Balasan terdeteksi untuk {no_tiket}")
                        simpan_balasan(no_tiket, isi_balasan)

                save_last_update_id(update_id)

        time.sleep(2)

if __name__ == "__main__":
    if not os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "w") as f:
            f.write("0")
    run_listener()
