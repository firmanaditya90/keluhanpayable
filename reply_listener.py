import os
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

# Konfigurasi
BOT_TOKEN = "8361565236:AAFsh7asYAhLxhS5qDxDvsVJirVZMsU2pXo"
BALASAN_FILE = "balasan_data.csv"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fungsi handler /reply
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Format salah. Gunakan: /reply <no_tiket> <isi_balasan>")
            return

        no_tiket = context.args[0]
        isi_balasan = " ".join(context.args[1:])
        data_baru = pd.DataFrame([{"no_tiket": no_tiket, "balasan": isi_balasan}])

        if os.path.exists(BALASAN_FILE):
            df_lama = pd.read_csv(BALASAN_FILE)
            df = pd.concat([df_lama, data_baru], ignore_index=True)
        else:
            df = data_baru

        df.to_csv(BALASAN_FILE, index=False)
        await update.message.reply_text(f"✅ Balasan untuk {no_tiket} disimpan.")
    except Exception as e:
        await update.message.reply_text(f"❌ Terjadi error: {e}")

# Fungsi utama bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("reply", reply_handler))
    print("Bot reply_listener aktif... menunggu perintah /reply")

    app.run_polling()

if __name__ == "__main__":
    main()
