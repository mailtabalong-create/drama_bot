# =========================================================
# BOT TELEGRAM VIP SHORT DRAMA ID
# Versi dasar - by GPT Asisten
# =========================================================

import telebot
import sqlite3
from datetime import datetime, timedelta

# === KONFIGURASI DASAR ===
BOT_TOKEN = "8041066937:AAGu5GPDEdszAnbWNaTfkapkenUEHNJxfgA"  # Token dari BotFather
GROUP_ID = -1002431177986  # ID grup VIP kamu
ADMIN_ID = 7993836617  # ID admin utama (kamu sendiri)

bot = telebot.TeleBot(BOT_TOKEN)

# === BUAT DATABASE UNTUK MENYIMPAN DATA LANGGANAN ===
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    paket TEXT,
    expired DATE
)
""")
conn.commit()

# =========================================================
# 1️⃣ /start - Pesan pembuka untuk pengguna baru
# =========================================================
@bot.message_handler(commands=['start'])
def start(message):
    teks = (
        "💎 Selamat datang di *Short Drama ID!* 💎\n\n"
        "🌸 PILIH PAKET LANGGANAN 🌸\n"
        "💠 1 Minggu – Rp15.000 (Saweria)\n"
        "💠 1 Bulan – Rp35.000 (1 Unit Trakteer)\n"
        "💠 1 Tahun – Rp105.000 (3 Unit Trakteer)\n"
        "💠 Selamanya – Rp245.000 (7 Unit Trakteer)\n\n"
        "📍 Pilih metode pembayaran:\n"
        "🔹 Trakteer: https://trakteer.id/anak-merch-tlwkw/tip\n"
        "🔹 Saweria: https://saweria.co/anakmerch\n\n"
        "📩 Setelah bayar, kirim bukti ke admin 👉 @Adm1nDracinESP"
    )
    bot.send_message(message.chat.id, teks, parse_mode="Markdown")


# =========================================================
# 2️⃣ /approve - Admin menambahkan langganan manual
# =========================================================
@bot.message_handler(commands=['approve'])
def approve_user(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Maaf, hanya admin yang bisa pakai perintah ini.")
        return

    try:
        # Format: /approve @username 1bulan
        command = message.text.split()
        if len(command) < 3:
            bot.reply_to(message, "❌ Format salah!\n\nContoh:\n`/approve @username 1bulan`", parse_mode="Markdown")
            return

        username = command[1].replace("@", "")
        paket = command[2].lower()

        # Tentukan tanggal expired berdasarkan paket
        if paket == "1minggu":
            expired = datetime.now() + timedelta(days=7)
        elif paket == "1bulan":
            expired = datetime.now() + timedelta(days=30)
        elif paket == "1tahun":
            expired = datetime.now() + timedelta(days=365)
        elif paket == "selamanya":
            expired = datetime.now() + timedelta(days=3650)
        else:
            bot.reply_to(message, "❌ Paket tidak dikenal. Gunakan: 1minggu / 1bulan / 1tahun / selamanya.")
            return

        # Dapatkan data user
        try:
            user = bot.get_chat(username)
        except Exception as e:
            bot.reply_to(message, f"❌ Gagal menemukan user @{username}. Pastikan user sudah pernah kirim /start ke bot dulu.")
            return

        # Simpan ke database
        c.execute("REPLACE INTO users (user_id, username, paket, expired) VALUES (?, ?, ?, ?)",
                  (user.id, username, paket, expired.strftime("%Y-%m-%d")))
        conn.commit()

        # Tambahkan user ke grup VIP
        try:
            bot.add_chat_members(GROUP_ID, user.id)
            bot.send_message(GROUP_ID, f"🎉 Selamat datang @{username}! Masa aktifmu sampai *{expired.strftime('%d-%m-%Y')}*.", parse_mode="Markdown")
        except:
            bot.reply_to(message, f"⚠️ Gagal menambahkan @{username} ke grup. Tambahkan manual jika grup bersifat private invite-only.")

        # Balasan ke admin
        bot.reply_to(message, f"✅ @{username} berhasil ditambahkan!\nPaket: {paket}\nBerlaku sampai: {expired.strftime('%d-%m-%Y')}")

    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan:\n{e}")


# =========================================================
# 3️⃣ /cek - Pengguna cek masa aktif mereka
# =========================================================
@bot.message_handler(commands=['cek'])
def cek_langganan(message):
    user_id = message.from_user.id
    c.execute("SELECT paket, expired FROM users WHERE user_id=?", (user_id,))
    data = c.fetchone()

    if not data:
        bot.reply_to(message, "❌ Kamu belum berlangganan. Ketik /start untuk melihat daftar paket.")
    else:
        paket, expired = data
        bot.reply_to(message, f"📅 Paket: {paket}\n🕒 Berlaku sampai: {expired}")


# =========================================================
# 4️⃣ Jalankan bot
# =========================================================
print("🤖 Bot Short Drama ID sedang berjalan...")
bot.polling(non_stop=True)
