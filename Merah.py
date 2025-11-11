import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
import time
import re
from dotenv import load_dotenv 

# --- Muat Variabel dari File .env (Wajib ada!) ---
load_dotenv() 

# --- Warna ANSI dan Utility ---
BOLD = '\033[1m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
BLUE = '\033[36m' 
RESET = '\033[0m'

# --- Ambil Kredensial dari .env ---
SENDER_EMAIL = os.getenv('EMAIL_USER')
SENDER_PASSWORD = os.getenv('EMAIL_PASS')
RECEIVER_EMAIL = "support@support.whatsapp.com"

DELAY_SECONDS = 20 

# --- BANNER ASCII Sederhana ---
BANNER_TEXT = f"""
{BLUE}{BOLD}
   .-------------------.
   | {YELLOW}S E R E N A - W A{BLUE} |
   '-------------------'
{RESET}
   {GREEN}Massal WhatsApp Appeal Sender (Termux Edition){RESET}
"""

def buat_panel(judul, konten, warna):
    """Fungsi untuk membuat panel berwarna dengan garis border."""
    garis = f"{warna}═{'═' * (len(judul) + 4)}═{RESET}"
    panel = (
        f"{garis}\n"
        f"{warna}║ {BOLD}{judul}{RESET}{warna} ║{RESET}\n"
        f"{garis}\n"
        f"{konten}\n"
        f"{warna}═{'═' * (len(judul) + 4)}═{RESET}"
    )
    return panel

def proses_jeda_20_detik(nomor_saat_ini, total_nomor):
    """
    Menampilkan hitungan mundur 20 detik yang stabil.
    Tampilan: [00:XX] Menunggu nomor berikutnya... |/-\
    """
    
    spinner = ['-', '\\', '|', '/']
    
    # Tampilkan pesan status jeda (tidak ditimpa)
    print(f"\n{YELLOW}⏳ JEDA {DELAY_SECONDS} DETIK:{RESET} Proses: {nomor_saat_ini} dari {total_nomor}.")
    
    for s in range(DELAY_SECONDS, 0, -1):
        indicator = spinner[s % 4] 
        
        # Hitungan menit dan detik
        menit = s // 60
        detik = s % 60
        
        # Teks yang akan ditimpa (\r)
        countdown_text = f"    {BOLD}[{menit:02d}:{detik:02d}]{RESET} Menunggu nomor berikutnya... {YELLOW}{indicator}{RESET}"
        
        # sys.stdout.write dan \r menimpa baris sebelumnya
        sys.stdout.write(f"\r{countdown_text}") 
        sys.stdout.flush() 

        time.sleep(1)
        
    # Membersihkan baris hitungan setelah selesai
    sys.stdout.write("\r" + " " * 60 + "\r") 
    print(f"{GREEN}   ☑️ Jeda selesai! Lanjut ke nomor berikutnya.{RESET}")

def kirim_email_banding(nomor_telepon, email_ke):
    """Fungsi untuk mengirim email banding ke alamat tertentu."""

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"{RED}🚨 ERROR:{RESET} Variabel EMAIL_USER atau EMAIL_PASS {BOLD}tidak ditemukan di file .env.{RESET}")
        print(f"   Pastikan file .env ada dan isinya benar.{RESET}")
        return False

    subjek = f"Permintaan Peninjauan Akun Ditangguhkan: {nomor_telepon}"
    isi_email = f"""
Halo Tim Dukungan WhatsApp,

Saya ingin melaporkan masalah terkait nomor WhatsApp saya. Saat mencoba melakukan pendaftaran, setiap kali saya ingin masuk selalu muncul pesan "Login Tidak Tersedia Untuk Saat Ini".

Nomor WhatsApp saya adalah: {nomor_telepon}.

Saya sangat berharap pihak WhatsApp dapat membantu agar saya bisa menggunakan kembali nomor saya tanpa muncul kendala tersebut. Terima kasih atas perhatian dan bantuannya.
    """

    try:
        # Konfigurasi Pesan
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_ke
        msg['Subject'] = subjek
        msg.attach(MIMEText(isi_email, 'plain'))

        # Koneksi dan Login
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Kirim Email
        server.sendmail(SENDER_EMAIL, email_ke, msg.as_string())
        server.close()

        print(f"{GREEN}✅ SUKSES:{RESET} Email banding berhasil dikirim untuk nomor {BOLD}{nomor_telepon}{RESET}!")
        return True

    except Exception as e:
        print(f"{RED}❌ GAGAL:{RESET} Gagal mengirim email untuk nomor {BOLD}{nomor_telepon}{RESET}. ERROR: {e}")
        return False

if __name__ == "__main__":
    
    # --- Perintah CLEAR SCREEN ---
    os.system('clear')
    
    # --- Tampilkan BANNER ---
    print(BANNER_TEXT)
    
    # Cek kredensial segera setelah banner
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"{RED}{BOLD}!!! GAGAL MEMUAT KREDENSIAL !!!{RESET}")
        print("Pastikan file .env ada dan terisi dengan EMAIL_USER dan EMAIL_PASS.")
        sys.exit(1)
        
    # --- Tampilkan Panel Kredensial (untuk konfirmasi pengguna) ---
    kredensial_info = (
        f"   Email Pengirim: {SENDER_EMAIL}\n"
        f"   Email Tujuan: {RECEIVER_EMAIL}"
    )
    print(buat_panel("INFO KONEKSI", kredensial_info, YELLOW))
    print("\n" + BOLD + "──────────────────────────────────────────" + RESET)

    try:
        # Minta input jumlah banding
        jumlah_banding = int(input(f"{BOLD}Masukkan berapa nomor yang ingin di banding (Angka): {RESET}"))
    except ValueError:
        print(f"{RED}❌ Masukan tidak valid. Harap masukkan angka bulat.{RESET}")
        sys.exit(1)
        
    print(f"\n{BOLD}Persiapan:{RESET} Anda akan mengirim banding untuk {GREEN}{jumlah_banding}{RESET} nomor dengan jeda {RED}{DELAY_SECONDS} detik{RESET} antar nomor.")
    
    # Loop sebanyak jumlah_banding
    for i in range(1, jumlah_banding + 1):
        print(f"\n{BOLD}──────────────────────────────────────────{RESET}")
        print(f"{BOLD}   [ PROSES NOMOR ke-{i} dari {jumlah_banding} ]{RESET}")
        print(f"{BOLD}──────────────────────────────────────────{RESET}")
        
        # Minta input nomor telepon dengan validasi
        while True:
            nomor = input(f"   {BOLD}Masukkan Nomor WhatsApp ke-{i} (cth: +62812xxxx):{RESET} ").strip()
            if re.match(r'^\+\d{5,}$', nomor):
                break
            else:
                print(f"{RED}❌ Format salah.{RESET} Harap masukkan format internasional yang valid (diawali '+' dan hanya angka).")

        # Kirim Email
        status_kirim = kirim_email_banding(nomor, RECEIVER_EMAIL)

        # Jeda 20 Detik DENGAN DISPLAY
        # Jeda hanya terjadi jika pengiriman sukses dan BUKAN nomor terakhir
        if status_kirim and i < jumlah_banding:
            proses_jeda_20_detik(i, jumlah_banding)
            
        elif status_kirim and i == jumlah_banding:
             print(f"\n{GREEN}🎉 SEMUA PROSES SELESAI!{RESET}")
             print(f"➡️ Harap cek kotak masuk email {BOLD}{SENDER_EMAIL}{RESET} secara {BOLD}MANUAL{RESET} untuk balasan dari WhatsApp.")