import logging
import requests
import colorama
import time
from colorama import Fore, Style
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, CallbackContext

# 🔹 Inisialisasi colorama untuk warna terminal
colorama.init(autoreset=True)

# 🔹 Konfigurasi Bot Telegram
TELEGRAM_BOT_TOKEN = "7862379874:AAFsKAsU5jIbWxQOj6ITvtyFL6_f16hp99Q"  # Ganti dengan Token Bot Anda

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

# 🔹 Logging (Untuk Debugging)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Fungsi untuk mengecek rekening bank via API
def cek_rekening(kode_bank, nomor_rekening):
    params = {"kodeBank": kode_bank, "noRekening": nomor_rekening}
    try:
        response = requests.get(API_BANK_URL, headers=API_BANK_HEADERS, params=params, timeout=10)
        data = response.json()
        if response.status_code == 200 and "data" in data and "nama" in data["data"]:
            return data["data"]["nama"]
        else:
            return None  # Jika rekening tidak ditemukan
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ API Error: {e}")
        return None  # Jika terjadi kesalahan

# 🔹 Fungsi saat pengguna mengetik /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "✅ Selamat datang di *BANK CHECK BOT*!\n\n"
        "🔹 Ketik `<nama_bank> <nomor_rekening>` atau `<nomor_rekening> <nama_bank>` untuk validasi rekening.\n"
        "🔹 Cek Bank MDR | BRI | BNI | BCA | SEABANK | CIMB | BSI.\n\n"
        "*Contoh:* `bca 8060127426` atau `8060127426 bca`",
        parse_mode="Markdown"
    )

# 🔹 Fungsi untuk menangani semua pesan masuk
async def handle_message(update: Update, context: CallbackContext):
    try:
        text = update.message.text.strip().lower()  # Ambil teks dari pengguna
        words = text.split()  # Pecah pesan berdasarkan spasi

        # Memastikan format pesan valid (harus ada 2 kata)
        if len(words) != 2:
            return

        layanan_1, layanan_2 = words  # Ambil kedua kata input

        # **Cek Rekening Bank**
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
            else:
                await update.message.reply_text("⚠️ Rekening tidak ditemukan | bantu cek manual ya. 🔹 Berfungsi untuk Cek Bank MANDIRI | BRI | BNI | BCA | SEA | CIMB | BSI.", parse_mode="Markdown")
            return

    except Exception as e:
        logging.error(f"❌ Terjadi kesalahan: {e}")

# 🔹 Menjalankan bot Telegram dalam loop (agar otomatis restart jika crash)
def main():
    while True:
        try:
            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            print(Fore.GREEN + "🚀 BOT TELEGRAM SEDANG BERJALAN...")
            app.run_polling()
        except Exception as e:
            logging.error(f"❌ BOT TERHENTI: {e}")
            time.sleep(10)  # Tunggu 10 detik sebelum restart

# 🔹 Jalankan bot
if __name__ == "__main__":
    main()
