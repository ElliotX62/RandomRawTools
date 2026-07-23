import os
import re
import sys
import shutil
from datetime import datetime
from pyfiglet import Figlet
from database import Database

def get_terminal_width():
    """Mendapatkan lebar terminal saat ini"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_time():
    """Mendapatkan waktu saat ini dalam format HH:MM:SS"""
    return datetime.now().strftime('%H:%M:%S')

def get_current_path():
    """Mendapatkan path direktori saat ini"""
    return os.getcwd()

def get_username():
    """Mendapatkan username dengan aman"""
    try:
        if os.name == 'nt':  # Windows
            return os.environ.get('USERNAME', 'user')
        else:  # Linux/Mac
            return os.environ.get('USER', os.environ.get('LOGNAME', 'user'))
    except:
        return 'user'

def get_hostname():
    """Mendapatkan hostname dengan aman"""
    try:
        import socket
        return socket.gethostname()
    except:
        return 'botscrapy'

def print_banner():
    """Mencetak banner botscrapy dengan warna merah"""
    width = get_terminal_width()
    
    # Buat banner dengan pyfiglet - font 'big' untuk tebal
    f = Figlet(font='big', width=width)
    banner_text = f.renderText('botscrapy')
    
    # Cetak dengan warna merah cerah dan tebal
    print("\033[1;31m" + banner_text + "\033[0m")
    print()  # Spasi setelah banner

def print_status_bar(message, status_type='info'):
    """Mencetak status bar dengan warna sesuai tipe"""
    width = get_terminal_width()
    bar_width = min(width - 2, 70)
    
    # Pilih warna berdasarkan tipe
    if status_type == 'success':
        color = '\033[1;32m'  # Hijau
        icon = '✓'
    elif status_type == 'error':
        color = '\033[1;31m'  # Merah
        icon = '✗'
    elif status_type == 'warning':
        color = '\033[1;33m'  # Kuning
        icon = '⚠'
    else:
        color = '\033[1;36m'  # Cyan
        icon = 'ℹ'
    
    # Buat status bar
    print(color + "┌" + "─" * bar_width + "┐\033[0m")
    
    # Isi pesan dengan padding
    msg = f"{icon} {message}"
    padding = bar_width - len(msg) - 2
    if padding < 1:
        padding = 1
    
    print(color + "│" + "\033[0m " + msg + " " * padding + color + "│\033[0m")
    print(color + "└" + "─" * bar_width + "┘\033[0m")
    print()

def get_user_input():
    """Fungsi untuk mendapatkan input dengan kotak"""
    width = get_terminal_width()
    bar_width = min(width - 2, 70)
    current_time = get_current_time()
    
    # Dapatkan username dan hostname dengan aman
    username = get_username()
    hostname = get_hostname()
    
    # Dapatkan path saat ini (di-singkat)
    current_path = get_current_path()
    home = os.path.expanduser('~')
    if current_path.startswith(home):
        current_path = '~' + current_path[len(home):]
    
    # Format prompt
    prompt_display = f"({username}@{hostname})-[{current_path}]"
    
    # Buat kotak input
    print("\033[1;31m┌" + "─" * bar_width + "┐\033[0m")
    
    # Baris pertama: prompt dan waktu
    time_str = f"⏰ {current_time}"
    padding = bar_width - len(prompt_display) - len(time_str) - 4
    if padding < 1:
        padding = 1
    
    print(f"\033[1;31m│\033[0m \033[1;33m{prompt_display}\033[0m" + " " * padding + f"\033[1;37m{time_str}\033[0m \033[1;31m│\033[0m")
    
    # Baris kedua: garis pemisah
    print("\033[1;31m├" + "─" * bar_width + "┤\033[0m")
    
    # Baris ketiga: tempat input dengan arrow
    arrow_line = "└─$ "
    
    # Cetak baris dengan arrow di dalam kotak
    print(f"\033[1;31m│\033[0m \033[1;31m{arrow_line}\033[0m", end='')
    
    # Ambil input dari user (cursor akan berada setelah arrow di dalam kotak)
    user_input = input().strip()
    
    # Hitung sisa padding untuk menutup kotak
    remaining = bar_width - len(arrow_line) - len(user_input) - 2
    if remaining < 1:
        remaining = 1
    
    # Cetak sisa padding dan tutup kotak
    print(" " * remaining + "\033[1;31m│\033[0m")
    
    # Garis bawah kotak
    print("\033[1;31m└" + "─" * bar_width + "┘\033[0m")
    print()
    
    return user_input

def display_database_content(db):
    """Menampilkan isi database dalam format tabel"""
    clear_screen()
    print_banner()
    
    print_status_bar("📊 ISI DATABASE TARGETS", 'info')
    
    targets = db.get_all_targets()
    total = db.get_total_count()
    
    if not targets:
        print_status_bar("Database kosong! Belum ada target tersimpan.", 'warning')
        input("\n\033[1;37mTekan Enter untuk kembali...\033[0m")
        return
    
    # Buat header tabel
    width = get_terminal_width()
    table_width = min(width - 4, 80)
    
    print("\033[1;31m┌" + "─" * table_width + "┐\033[0m")
    
    # Header
    header = f"│ ID │ URL {' ' * 40} │ STATUS    │ CREATED AT         │"
    print(f"\033[1;31m{header[:table_width+1]}\033[0m")
    
    print("\033[1;31m├" + "─" * table_width + "┤\033[0m")
    
    # Data
    for target in targets:
        id_val = str(target[0])
        url = target[1][:45]
        status = target[3]
        created_at = target[2]
        
        # Warna status
        if status == 'pending':
            status_display = f"\033[1;33m{status:<10}\033[0m"
        elif status == 'success':
            status_display = f"\033[1;32m{status:<10}\033[0m"
        elif status == 'failed':
            status_display = f"\033[1;31m{status:<10}\033[0m"
        else:
            status_display = f"\033[1;37m{status:<10}\033[0m"
        
        # Format baris
        row = f"│ {id_val:<2} │ {url:<45} │ {status_display} │ {created_at} │"
        print(row[:table_width+1])
    
    print("\033[1;31m└" + "─" * table_width + "┘\033[0m")
    
    # Info total
    print(f"\n\033[1;37mTotal target: \033[1;32m{total}\033[0m")
    print(f"\033[1;36mDatabase: \033[1;33m{db.db_name}\033[0m")
    print()
    
    # Opsi tambahan
    print("\033[1;33mOpsi:\033[0m")
    print("  \033[1;36m[1]\033[0m Hapus semua data")
    print("  \033[1;36m[2]\033[0m Hapus berdasarkan ID")
    print("  \033[1;36m[Enter]\033[0m Kembali")
    print()
    
    choice = input("\033[1;31m└─$ \033[0m").strip()
    
    if choice == '1':
        # Hapus semua data
        confirm = input("\033[1;31mYakin ingin menghapus semua data? (y/n): \033[0m").strip().lower()
        if confirm == 'y':
            db.delete_all_targets()
            print_status_bar("Semua data berhasil dihapus!", 'success')
            input("\n\033[1;37mTekan Enter untuk melanjutkan...\033[0m")
    elif choice == '2':
        # Hapus berdasarkan ID
        try:
            target_id = int(input("\033[1;33mMasukkan ID target yang akan dihapus: \033[0m").strip())
            target = db.get_target_by_id(target_id)
            if target:
                confirm = input(f"\033[1;31mYakin ingin menghapus target ID {target_id}? (y/n): \033[0m").strip().lower()
                if confirm == 'y':
                    db.delete_target(target_id)
                    print_status_bar(f"Target ID {target_id} berhasil dihapus!", 'success')
            else:
                print_status_bar(f"Target dengan ID {target_id} tidak ditemukan!", 'error')
        except ValueError:
            print_status_bar("ID harus berupa angka!", 'error')
        input("\n\033[1;37mTekan Enter untuk melanjutkan...\033[0m")

def validate_url(url):
    """Memvalidasi apakah URL memiliki awalan http:// atau https://"""
    pattern = re.compile(r'^https?://.+', re.IGNORECASE)
    return bool(pattern.match(url.strip()))

def exit_program():
    """Fungsi untuk keluar dari program"""
    clear_screen()
    print("\033[1;31m")
    f = Figlet(font='small')
    print(f.renderText('Goodbye!'))
    print("\033[1;36mTerima kasih telah menggunakan botscrapy! 👋\033[0m\n")
    sys.exit(0)

def main():
    """Fungsi utama program"""
    # Inisialisasi database
    db = Database()
    box = None
    
    while True:
        clear_screen()
        print_banner()
        
        # Tampilkan status jika ada URL tersimpan
        if box:
            print_status_bar(f"URL tersimpan: {box}", 'success')
        
        # Tampilkan kotak input dan ambil input dari user
        user_input = get_user_input()
        
        # Cek perintah khusus
        if user_input.lower() == '/showsql':
            display_database_content(db)
            continue
        
        if user_input.lower() == '/exit':
            exit_program()
        
        # Validasi input
        if not user_input:
            print_status_bar("ERROR: Input tidak boleh kosong!", 'error')
            input("\n\033[1;37mTekan Enter untuk mencoba lagi...\033[0m")
            continue
            
        if validate_url(user_input):
            # Simpan ke database
            target_id = db.insert_target(user_input)
            
            if target_id:
                box = user_input
                clear_screen()
                print_banner()
                print_status_bar(f"BERHASIL! URL berhasil disimpan", 'success')
                print_status_bar(f"URL: {box}", 'success')
                print_status_bar(f"ID Database: {target_id}", 'info')
                print()
                print("\033[1;36mTekan Ctrl+C atau ketik /exit untuk keluar\033[0m")
                print("\033[1;33mKetik /showsql untuk melihat isi database\033[0m")
                print("\033[1;33mKetik /exit untuk keluar\033[0m")
                input("\n\033[1;37mTekan Enter untuk melanjutkan...\033[0m")
            else:
                print_status_bar("Gagal menyimpan ke database!", 'error')
                input("\n\033[1;37mTekan Enter untuk mencoba lagi...\033[0m")
        else:
            # Input tidak valid
            clear_screen()
            print_banner()
            print_status_bar(f"ERROR: URL harus diawali dengan http:// atau https://", 'error')
            print_status_bar(f"Input Anda: {user_input}", 'error')
            print()
            print("\033[1;33mContoh URL yang benar:\033[0m")
            print("  \033[1;32m•\033[0m https://www.example.com")
            print("  \033[1;32m•\033[0m http://localhost:8000")
            print("  \033[1;32m•\033[0m https://google.com")
            print()
            input("\033[1;37mTekan Enter untuk mencoba lagi...\033[0m")

if __name__ == "__main__":
    try:
        # Cek apakah pyfiglet terinstall
        try:
            import pyfiglet
        except ImportError:
            print("\033[1;31mError: Library 'pyfiglet' tidak terinstall!\033[0m")
            print("\033[1;33mInstall dengan: pip install pyfiglet\033[0m")
            sys.exit(1)
            
        main()
    except KeyboardInterrupt:
        # Tangani Ctrl+C
        exit_program()
