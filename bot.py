# ========================================================
# SCRIPT INI TIDAK GRATIS, JADI JANGAN MENJUAL ATAU MEMBERI SCRIPT INI SECARA GRATIS
# AUTHOR: Gamz
# TELEGRAM: @Gamzbr
# ========================================================

import telebot
import datetime
import smtplib
import json
import time
import random
import os
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telebot import types
import openpyxl

# ========================================================
# CONFIG LOADER / SAVER
# ========================================================

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def save_config(new_config):
    with open("config.json", "w") as f:
        json.dump(new_config, f, indent=4)

config = load_config()

BOT_TOKEN       = config.get("BOT_TOKEN")
LEGACY_EMAIL_USER = config.get("EMAIL_USER")
LEGACY_EMAIL_PASS = config.get("EMAIL_PASS")
EMAIL_TO        = config.get("EMAIL_TO")
PHOTO_URL       = config.get("PHOTO_URL")
admins          = config.get("admins", [])

bot = telebot.TeleBot(BOT_TOKEN)

# ========================================================
# DATABASE
# ========================================================

db = {"premium": []}

def save_db():
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

def load_db():
    global db
    try:
        with open("database.json", "r") as f:
            db = json.load(f)
    except:
        save_db()

load_db()

# ========================================================
# HELPERS
# ========================================================

def is_admin(user_id):
    return user_id in admins

def is_premium(user_id):
    return str(user_id) in db.get("premium", [])

# ========================================================
# MULTI-SENDER
# ========================================================

def get_all_senders():
    cfg = load_config()
    senders = cfg.get("senders")
    if senders and isinstance(senders, list):
        return senders
    if LEGACY_EMAIL_USER and LEGACY_EMAIL_PASS:
        return [{"email": LEGACY_EMAIL_USER, "app_password": LEGACY_EMAIL_PASS}]
    return []

def get_random_sender():
    senders = get_all_senders()
    if not senders:
        return None
    return random.choice(senders)

def send_email_via_sender(sender_email, sender_pass, nomor):
    try:
        subject = "WhatsApp Support Appeal"
        body = f"""Hello WhatsApp team,

I'm having trouble registering my phone number ({nomor}). I keep getting a 'login unavailable' error. Please help me resolve this issue.

Thank you."""
        email_text = f"From: {sender_email}\nTo: {EMAIL_TO}\nSubject: {subject}\n\n{body}"
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_pass)
            server.sendmail(sender_email, EMAIL_TO, email_text)
        return True, None
    except Exception as e:
        return False, str(e)

# ========================================================
# /start handler
# ========================================================

@bot.message_handler(commands=["start"])
def start(message):
    # Simpan user
    try:
        uid = message.from_user.id
        if str(uid) not in db.get("users", []):
            db_users = db.get("users", [])
            db_users.append(str(uid))
            db["users"] = db_users
            save_db()
    except:
        pass

    caption = (
        "🤖 *BOT BANDING MERAH WHATSAPP*\n\n"
        "Developer: ℌ𝔞𝔫𝔵𝔵𝔠𝔬𝔬𝔩\n\n"
        "ℹ️ Informasi Bot: Bot ini digunakan untuk membantu proses banding WhatsApp Merah secara otomatis. "
        "Bot akan mengirim email banding ke WhatsApp Support menggunakan Gmail yang terhubung. "
        "Dilengkapi fitur admin, premium, dan pengaturan Gmail.\n\n"
        "📌 Daftar Command\n"
        "⛧ /fix <nomor> └──► Banding Merah Wa\n"
        "⛧ /tambahgmail └──► Tambahkan Gmail + App Password\n"
        "⛧ /convert <reply> └──► Mengubah File Xlsx Menjadi Txt\n"
        "⛧ /listemail └──► Melihat semua sender email\n"
        "⛧ /delemail <email> └──► Menghapus email sender\n"
        "⛧ /addprem <id> └──► Tambah user premium\n"
        "⛧ /delprem <id> └──► Hapus user premium\n"
        "⛧ /addadmin <id> └──► Tambah admin bot\n"
        "⛧ /deladmin <id> └──► Hapus admin bot\n\n"
        "🔥 Bot khusus membantu proses banding WhatsApp."
    )

    bot.send_photo(
        message.chat.id,
        PHOTO_URL,
        caption=caption,
        parse_mode="Markdown"
    )

# ========================================================
# /fix command (Admin & Premium)
# ========================================================

@bot.message_handler(commands=["fix"])
def fix_number(message):
    try:
        uid = message.from_user.id
        if not (is_admin(uid) or is_premium(uid)):
            bot.reply_to(message, "❌ Fitur ini hanya untuk Admin & Premium!")
            return

        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Contoh: /fix 6285123456789")
            return

        nomor = parts[1].strip()
        if not nomor.isdigit() or len(nomor) < 8:
            bot.reply_to(message, "⚠️ Nomor tidak valid!")
            return

        sender = get_random_sender()
        if not sender:
            bot.reply_to(message, "⚠️ Tidak ada sender tersimpan. Tambah dengan /tambahgmail (admin).")
            return

        sender_email = sender.get("email")
        sender_pass  = sender.get("app_password")

        info_msg = bot.reply_to(message, f"📤 Menggunakan sender: `{sender_email}`", parse_mode="Markdown")
        msg = bot.reply_to(message, f"🔧 Memulai proses banding untuk *{nomor}*...\n\n⏳ Loading: 10%", parse_mode="Markdown")

        for i in range(10, 101, 10):
            bar = "█" * (i // 5) + "░" * (20 - (i // 5))
            try:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    text=f"🔧 Memproses Banding... 📱 Nomor: {nomor}\n\n[{bar}] {i}%",
                    parse_mode="Markdown"
                )
            except:
                pass
            time.sleep(0.12)

        ok, err = send_email_via_sender(sender_email, sender_pass, nomor)
        if ok:
            bot.send_message(message.chat.id, "📩 Banding terkirim ke WhatsApp Support!")
        else:
            bot.reply_to(message, f"❌ Gagal mengirim: {err}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ========================================================
# /tambahgmail (Admin only)
# ========================================================

@bot.message_handler(commands=["tambahgmail"])
def tambahgmail(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin!")
        return

    msg = bot.reply_to(message, "📧 Kirim Email Gmail baru (contoh: sender@gmail.com):")
    bot.register_next_step_handler(msg, step_tambahgmail_email)

def step_tambahgmail_email(message):
    email = message.text.strip()
    msg = bot.reply_to(message, "🔐 Kirim App Password untuk email tersebut:")
    bot.register_next_step_handler(msg, lambda m: step_tambahgmail_save(m, email))

def step_tambahgmail_save(message, email):
    app_pwd = message.text.strip()
    cfg = load_config()
    senders = cfg.get("senders", [])
    for s in senders:
        if s.get("email") == email:
            bot.reply_to(message, "⚠️ Email sudah ada di daftar.")
            return
    senders.append({"email": email, "app_password": app_pwd})
    cfg["senders"] = senders
    save_config(cfg)
    bot.reply_to(message, f"✅ Sender {email} berhasil ditambahkan.", parse_mode="Markdown")

# ========================================================
# /listemail (Admin only)
# ========================================================

@bot.message_handler(commands=["listemail"])
def list_email(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin!")
        return
    cfg = load_config()
    senders = cfg.get("senders", [])
    if not senders:
        bot.reply_to(message, "📭 Belum ada Gmail yang tersimpan.")
        return
    text = "📧 DAFTAR EMAIL SENDER\n\n"
    for i, s in enumerate(senders, start=1):
        text += f"{i}. {s.get('email')}\n"
    bot.reply_to(message, text, parse_mode="Markdown")

# ========================================================
# /delemail <email> (Admin only)
# ========================================================

@bot.message_handler(commands=["delemail"])
def delete_email(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Contoh: /delemail sender@gmail.com")
        return
    target = parts[1].strip()
    cfg = load_config()
    senders = cfg.get("senders", [])
    new_list = [s for s in senders if s.get("email") != target]
    if len(new_list) == len(senders):
        bot.reply_to(message, "⚠️ Email tidak ditemukan.")
        return
    cfg["senders"] = new_list
    save_config(cfg)
    bot.reply_to(message, f"🗑 Email {target} berhasil dihapus.", parse_mode="Markdown")

# ========================================================
# /convert (Reply XLSX/XLSM/XLT/CSV -> TXT)
# ========================================================

@bot.message_handler(commands=['convert'])
def cmd_convert(message):
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "Reply ke file XLSX / XLS / ODS nya sambil pake perintah /convert.")
        return

    doc = message.reply_to_message.document
    file_id = doc.file_id
    file_name = doc.file_name

    if not (file_name.endswith((".xlsx", ".xlsm", ".xltx", ".csv"))):
        bot.reply_to(message, "File harus berformat .xlsx / .xlsm / .xltx / .csv")
        return

    msg = bot.reply_to(message, "Downloading file...")
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    os.makedirs("tmp", exist_ok=True)
    input_path = os.path.join("tmp", file_name)
    output_path = input_path + ".txt"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    bot.edit_message_text("Membaca file...", chat_id=message.chat.id, message_id=msg.message_id)

    try:
        if file_name.endswith('.csv'):
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as rf, \
                 open(output_path, 'w', encoding='utf-8') as wf:
                for line in rf:
                    wf.write(line)
        else:
            wb = openpyxl.load_workbook(input_path, data_only=True)
            sheet = wb.active
            with open(output_path, "w", encoding="utf-8") as out:
                for row in sheet.iter_rows(values_only=True):
                    row_text = "\t".join([str(cell) if cell is not None else "" for cell in row])
                    out.write(row_text + "\n")

        bot.edit_message_text("Konversi selesai! Mengirim file...", chat_id=message.chat.id, message_id=msg.message_id)
        with open(output_path, "rb") as out:
            bot.send_document(message.chat.id, out, caption="Berhasil dikonversi.")

    except Exception as e:
        bot.edit_message_text(f"Gagal: {e}", chat_id=message.chat.id, message_id=msg.message_id)

    finally:
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass

# ========================================================
# PREMIUM MANAGEMENT
# ========================================================

@bot.message_handler(commands=["addprem"])
def add_premium(message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "❌ Kamu bukan admin!")
            return
        uid = message.text.split(" ")[1]
        if str(uid) in db.get("premium", []):
            bot.reply_to(message, "⚠️ User sudah premium.")
            return
        db.setdefault("premium", []).append(str(uid))
        save_db()
        bot.reply_to(message, f"✅ User {uid} ditambahkan ke premium!")
    except Exception:
        bot.reply_to(message, "⚠️ Contoh: /addprem 123456789")

@bot.message_handler(commands=["delprem"])
def del_premium(message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "❌ Kamu bukan admin!")
            return
        uid = message.text.split(" ")[1]
        if uid in db.get("premium", []):
            db.get("premium", []).remove(uid)
            save_db()
            bot.reply_to(message, f"🗑️ User {uid} dihapus dari premium!")
        else:
            bot.reply_to(message, "⚠️ User tidak ada di premium.")
    except Exception:
        bot.reply_to(message, "⚠️ Contoh: /delprem 123456789")

# ========================================================
# ADMIN MANAGEMENT
# ========================================================

@bot.message_handler(commands=["addadmin"])
def addadmin(message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "❌ Kamu bukan admin!")
            return
        uid = int(message.text.split(" ")[1])
        cfg = load_config()
        admins_list = cfg.get("admins", [])
        if uid in admins_list:
            bot.reply_to(message, "⚠️ User sudah admin.")
            return
        admins_list.append(uid)
        cfg["admins"] = admins_list
        save_config(cfg)
        global admins
        admins = cfg.get("admins", [])
        bot.reply_to(message, f"✅ {uid} ditambahkan sebagai admin!")
    except Exception:
        bot.reply_to(message, "⚠️ Contoh: /addadmin 123456789")

@bot.message_handler(commands=["deladmin"])
def deladmin(message):
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "❌ Kamu bukan admin!")
            return
        uid = int(message.text.split(" ")[1])
        cfg = load_config()
        admins_list = cfg.get("admins", [])
        if uid in admins_list:
            admins_list.remove(uid)
            cfg["admins"] = admins_list
            save_config(cfg)
            global admins
            admins = cfg.get("admins", [])
            bot.reply_to(message, f"🗑️ {uid} dihapus dari admin!")
        else:
            bot.reply_to(message, "⚠️ User bukan admin.")
    except Exception:
        bot.reply_to(message, "⚠️ Contoh: /deladmin 123456789")

# ========================================================
# START LOGO
# ========================================================
import time
import os

# ============================
# WARNA RAINBOW ANSI
# ============================
rainbow_colors = [
    "\033[91m",  # merah
    "\033[93m",  # kuning
    "\033[92m",  # hijau
    "\033[96m",  # cyan
    "\033[94m",  # biru
    "\033[95m",  # magenta
]

RESET = "\033[0m"

# ============================
# LOGO BOT
# ============================
logo_lines = [
"  /$$$$$$                                   ",
" /$$__  $$                                  ",
"| $$  \\__/  /$$$$$$  /$$$$$$/$$$$  /$$$$$$$$",
"| $$ /$$$$ |____  $$| $$_  $$_  $$|____ /$$/",
"| $$|_  $$  /$$$$$$$| $$ \\ $$ \\ $$   /$$$$/ ",
"| $$  \\ $$ /$$__  $$| $$ | $$ | $$  /$$__/  ",
"|  $$$$$$/|  $$$$$$$| $$ | $$ | $$ /$$$$$$$$",
" \\______/  \\_______/|__/ |__/ |__/|________/"
]

# ============================
# PRINT RAINBOW LOGO
# ============================
os.system("clear")
for i, line in enumerate(logo_lines):
    color = rainbow_colors[i % len(rainbow_colors)]
    print(f"{color}{line}{RESET}")
    time.sleep(0.05)  # efek sedikit delay biar lebih kerasa

# ============================
# Info box biasa
# ============================
info_box = f"""
\033[94m╔═══════════════════════════════════════════╗
║        BOT BANDING MERAH WHATSAPP          ║
║                                             ║
║ Developer : GamzOfficial                    ║
║ Fungsi    : Mengirim banding WA Merah       ║
║ Gmail     : Auto-send via SMTP              ║
║ Premium   : Support + Admin Tools           ║
╚═══════════════════════════════════════════╝{RESET}
"""
print(info_box)
bot.infinity_polling()