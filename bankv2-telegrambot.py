import logging
import requests
import colorama
from flask import Flask, request
from colorama import Fore, Style
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Inisialisasi colorama untuk warna terminal
colorama.init(autoreset=True)

# 🔹 Konfigurasi Bot Telegram
TELEGRAM_BOT_TOKEN = "7152068354:AAFW23XAfk5Ghc38E3-KzysoaI7ReEcTzE8"  # Ganti dengan token bot baru Anda
WEBHOOK_URL = "https://aaaaa-bzdl.onrender.com/"  # Ganti dengan URL Webhook dari Render

# 🔹 API Bank (Validasi Rekening)
API_BANK_URL = "https://cek-nomor-rekening-bank-indonesia1.p.rapidapi.com/cekRekening"
API_BANK_HEADERS = {
    "x-rapidapi-key": "347c3d28d8msh5b5bbb8fcfdf9eap1b3295jsn7f44586c582f",
    "x-rapidapi-host": "cek-nomor-rekening-bank-indonesia1.p.rapidapi.com"
}

# 🔹 Daftar kode bank di Indonesia
KODE_BANKS = {
    "bca": "014",
    "mandiri": "008",
    "bni": "009",
    "bri": "002",
    "cimb": "022",
    "danamon": "011",
    "maybank": "016",
    "permata": "013",
    "panin": "019",
    "btn": "200",
    "mega": "426",
    "bsi": "451",
    "btpn": "213",
    "jenius": "213",
    "ocbc": "028",
    "dbs": "046",
    "uob": "023",
    "hsbc": "041",
    "citibank": "031",
    "standard": "050",
    "muamalat": "147",
    "sea": "535"
}

# 🔹 Logging untuk debugging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Inisialisasi Flask
app = Flask(__name__)

# 🔹 Inisialisasi Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# 🔹 Inisialisasi Application untuk Telegram Bot
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 🔹 Fungsi Webhook untuk menerima pesan dari Telegram
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    logging.info("📩 Webhook menerima permintaan!")

    try:
        update = Update.de_json(request.get_json(), bot)
        logging.info(f"✅ Update diterima: {update}")

        # Memproses update ke dalam bot
        application.process_update(update)

    except Exception as e:
        logging.error(f"❌ Error dalam webhook: {e}")

    return "OK", 200

# 🔹 Fungsi untuk menangani perintah /start
async def start(update: Update, context: CallbackContext):
    logging.info(f"📩 Fungsi /start dipanggil oleh {update.message.chat.username}")

    try:
        await update.message.reply_text(
            "✅ Selamat datang di *BANK CHECK BOT*!\n\n"
            "🔹 Ketik `<nama_bank> <nomor_rekening>` atau `<nomor_rekening> <nama_bank>` untuk validasi rekening.\n"
            "*Contoh:* `bca 8060127426` atau `8060127426 bca`",
            parse_mode="Markdown"
        )
        logging.info("✅ Pesan /start berhasil dikirim.")
    except Exception as e:
        logging.error(f"❌ Error mengirim pesan /start: {e}")

# 🔹 Fungsi untuk menangani semua pesan masuk
async def handle_message(update: Update, context: CallbackContext):
    logging.info(f"📩 Pesan diterima dari {update.message.chat.username}: {update.message.text}")

    try:
        text = update.message.text.strip().lower()
        words = text.split()

        if len(words) != 2:
            await update.message.reply_text("⚠️ Format salah. Gunakan `<nama_bank> <nomor_rekening>`.")
            return

        layanan_1, layanan_2 = words

        if layanan_1 in KODE_BANKS and layanan_2.isdigit():
            kode_bank = KODE_BANKS[layanan_1]
            nomor = layanan_2
        elif layanan_2 in KODE_BANKS and layanan_1.isdigit():
            kode_bank = KODE_BANKS[layanan_2]
            nomor = layanan_1
        else:
            kode_bank = None

        if kode_bank:
            nama_pemilik = cek_rekening(kode_bank, nomor)
            if nama_pemilik:
                await update.message.reply_text(
                    f"✅ *BANK CHECK*\n\n"
                    f"🔢 Nomor Rekening: `{nomor}`\n"
                    f"👤 Nama Pemilik: *{nama_pemilik}*",
                    parse_mode="Markdown"
                )
                logging.info("✅ Cek rekening berhasil.")
            else:
                await update.message.reply_text("⚠️ Rekening tidak ditemukan.", parse_mode="Markdown")
                logging.info("⚠️ Rekening tidak ditemukan.")
    except Exception as e:
        logging.error(f"❌ Error saat memproses pesan: {e}")

# 🔹 Fungsi untuk mengecek rekening bank via API
def cek_rekening(kode_bank, nomor_rekening):
    params = {"kodeBank": kode_bank, "noRekening": nomor_rekening}
    try:
        response = requests.get(API_BANK_URL, headers=API_BANK_HEADERS, params=params, timeout=10)
        data = response.json()
        if response.status_code == 200 and "data" in data and "nama" in data["data"]:
            return data["data"]["nama"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API Error: {e}")
        return None

# 🔹 Menambahkan handler ke application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🔹 Jalankan Flask untuk menerima Webhook
if __name__ == "__main__":
    print(Fore.GREEN + "🚀 BOT TELEGRAM SIAP MENERIMA WEBHOOK...")
    app.run(host="0.0.0.0", port=5000)
