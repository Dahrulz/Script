#!/usr/bin/env python3
import os, sys, subprocess, shutil, json, time
import readchar

URL   = "https://github.com/Dahrulz/RDP/actions"
REPO  = "Dahrulz/RDP"
WF    = "main.yml"
TS_PKG = "com.tailscale.ipn"
PLAY   = "https://play.google.com/store/apps/details?id=com.tailscale.ipn"

# ---------- AUTO-INSTALL (CEK SEKALI SAJA, DENGAN FLAG FILE) ----------
import os
import subprocess
import sys
import shutil

# File flag untuk mencatat instalasi speedtest-cli
SPEEDTEST_FLAG = "~/.speedtest_installed"
# Pastikan path file flag bersih dari tilda (~)
SPEEDTEST_FLAG = os.path.expanduser(SPEEDTEST_FLAG)

def install(pkg):
    # Cek apakah paket OS sudah terinstal (tanpa instal ulang)
    if shutil.which(pkg) is None:
        print(f"\n📦 Installing system package: {pkg} …")
        subprocess.run(["pkg", "install", pkg, "-y"], check=True)
    # Jika sudah terinstal, tidak ada aksi

def pip_install(mod, flag_file):
    # Cek file flag: jika ada → skip instalasi
    if os.path.exists(flag_file):
        return
    # Jika tidak ada flag, cek apakah modul Python sudah terinstal
    try:
        __import__(mod)  # Coba import modul
    except ImportError:
        print(f"\n📦 Installing Python module: {mod} …")
        subprocess.run([sys.executable, "-m", "pip", "install", mod], check=True)
        # Buat file flag setelah instalasi berhasil
        with open(flag_file, "w") as f:
            f.write("installed")

# Jalankan auto-install untuk semua paket yang dibutuhkan
install("gh")
install("python")
pip_install("readchar", "~/.readchar_installed")
pip_install("speedtest-cli", SPEEDTEST_FLAG)
# ----------------------------------

def clear(): os.system("clear")

def banner(title="TERMUX MENU BROWSER v1.4"):
    bar = "┌" + "─"*30 + "┐"; print(bar)
    print(f"│{title:^30}│")
    print("└" + "─"*30 + "┘")

# ---------- KEY FILTER ----------
ALLOWED = {readchar.key.UP, readchar.key.DOWN, readchar.key.ENTER,
           "\r", "\n", "q", readchar.key.CTRL_C}
def read_key_safe():
    while True:
        k = readchar.readkey()
        if k in ALLOWED: return k
# --------------------------------

# WARNA: biru terang = pilihan, putih = lainnya
def show_menu(items, selected):
    clear(); banner()
    for idx, text in enumerate(items, 1):
        if idx == selected:
            print(f"\033[1;36m▶ {idx}. {text}\033[0m")   # CYAN BRIGHT
        else:
            print(f"  {idx}. {text}")                   # WHITE NORMAL
    print("\n[↑↓] Navigate   [Enter] Choose   [q] Quit")

def total_workflows():
    try:
        out = subprocess.check_output(["gh", "workflow", "list", "--repo", REPO, "--json", "id"],
                                      stderr=subprocess.DEVNULL)
        return len(json.loads(out))
    except Exception:
        return 0

# ---------- SUB-MENUS (ALL COLOURED) ----------
def run_workflow():
    clear(); banner("RUN WORKFLOWS")
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        print("\n🔑 Belum login GitHub. Ikuti prompt di bawah:")
        subprocess.run(["gh", "auth", "login", "--web", "--git-protocol", "https"])
    total = total_workflows()
    print(f"\n📊 Total workflows: {total}\n")
    sub = ["Run workflows", "View workflows", "Back"]
    sub_pos = 1
    while True:
        clear(); banner("RUN WORKFLOWS")
        print(f"📊 Total workflows: {total}\n")
        for idx, text in enumerate(sub, 1):
            if idx == sub_pos:
                print(f"\033[1;36m▶ {idx}. {text}\033[0m")
            else:
                print(f"  {idx}. {text}")
        print("\n[↑↓] Navigate   [Enter] Choose")
        key = read_key_safe()
        if key == readchar.key.UP: sub_pos = (sub_pos - 2) % len(sub) + 1
        elif key == readchar.key.DOWN: sub_pos = sub_pos % len(sub) + 1
        elif key in (readchar.key.ENTER, "\r", "\n"):
            if sub_pos == 1:
                clear(); banner("RUN WORKFLOWS")
                print("\n⏳ Memicu workflow …\n")
                rc = subprocess.run(["gh", "workflow", "run", WF, "--repo", REPO, "--ref", "main"],
                                    stderr=subprocess.STDOUT).returncode
                if rc == 0:
                    print("\n✅ Workflow berhasil dipicu!")
                    print("\n⏳ Buka halaman Actions dalam 10 detik …")
                    
                    # ---------- TEKAN ENTER UNTUK KEMBALI LANGSUNG ----------
                    print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                    
                    # Cek input Enter DALAM 10 DETIK
                    user_cancel = False
                    start_time = time.time()
                    while (time.time() - start_time) < 10:
                        if readchar.readkey() in (readchar.key.ENTER, "\r", "\n"):
                            user_cancel = True
                            break
                    
                    if not user_cancel:
                        print("\n✨ Membuka halaman Actions GitHub ...")
                        os.system(f"am start -a android.intent.action.VIEW -d {URL}")
                    
                    # ---------- KEMBALI KE MENU (TANPA PESAN ENTER LAGI) ----------
                    return  # Langsung kembali ke menu sebelumnya
                else:
                    print("\n❌ Gagal memicu workflow.")
                    print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                    while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            elif sub_pos == 2:
                clear(); banner("VIEW WORKFLOWS")
                print(f"\n📋 Daftar workflow (total {total}):\n")
                subprocess.run(["gh", "workflow", "list", "--repo", REPO, "--limit", "20"])
                print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            else:
                return

def tailscale_menu():
    clear(); banner("TAILSCALE")
    installed = False
    try:
        test = subprocess.run(["am", "start", "-n", f"{TS_PKG}/.ipn.MainActivity"],
                              capture_output=True, text=True, timeout=3)
        installed = (test.returncode == 0)
    except Exception:
        installed = False

    sub = ["Buka Tailscale" if installed else "Install Tailscale", "Back"]
    sub_pos = 1
    while True:
        clear(); banner("TAILSCALE")
        for idx, text in enumerate(sub, 1):
            if idx == sub_pos:
                print(f"\033[1;36m▶ {idx}. {text}\033[0m")
            else:
                print(f"  {idx}. {text}")
        print("\n[↑↓] Navigate   [Enter] Choose")
        key = read_key_safe()
        if key == readchar.key.UP: sub_pos = (sub_pos - 2) % len(sub) + 1
        elif key == readchar.key.DOWN: sub_pos = sub_pos % len(sub) + 1
        elif key in (readchar.key.ENTER, "\r", "\n"):
            if sub_pos == 1:
                if installed:
                    os.system(f"am start -n {TS_PKG}/.ipn.MainActivity")
                else:
                    os.system(f"am start -a android.intent.action.VIEW -d {PLAY}")
                return
            else:
                return

def edit_script():
    clear(); banner("EDIT SCRIPT")
    sub = ["Edit script", "Reset script", "Back"]; sub_pos = 1
    while True:
        clear(); banner("EDIT SCRIPT")
        for idx, text in enumerate(sub, 1):
            if idx == sub_pos:
                print(f"\033[1;36m▶ {idx}. {text}\033[0m")
            else:
                print(f"  {idx}. {text}")
        print("\n[↑↓] Navigate   [Enter] Choose")
        key = read_key_safe()
        if key == readchar.key.UP: sub_pos = (sub_pos - 2) % len(sub) + 1
        elif key == readchar.key.DOWN: sub_pos = sub_pos % len(sub) + 1
        elif key in (readchar.key.ENTER, "\r", "\n"):
            if sub_pos == 1:
                clear(); banner("EDIT SCRIPT")
                print("\n📂 Membuka nano …\n"); os.system("nano menu.py")
                print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            elif sub_pos == 2:
                reset_script()
            else:
                return

def reset_script():
    clear(); banner("RESET SCRIPT")
    print("\n⚠️  Kosongkan isi menu.py?\n")
    reset_menu = ["Ya", "Back"]; yakin = 1
    while True:
        for idx, txt in enumerate(reset_menu, 1):
            if idx == yakin:
                print(f"\033[1;36m▶ {idx}. {txt}\033[0m")
            else:
                print(f"  {idx}. {txt}")
        key = read_key_safe()
        if key in (readchar.key.UP, readchar.key.DOWN):
            yakin = 3 - yakin
            clear(); banner("RESET SCRIPT")
            print("\n⚠️  Kosongkan isi menu.py?\n")
        elif key in (readchar.key.ENTER, "\r", "\n"):
            break
    if yakin == 1:
        open("menu.py", "w").close()  # kosongkan (0 byte)
        clear(); banner("RESET SCRIPT")
        print("\n✅ File dikosongkan.")
        sys.exit(0)                   # langsung keluar total
    else:
        return                        # Back tanpa pesan Enter
        
def success_screen():
    clear(); banner("SUCCESS")
    print("\n✅ Browser telah dibuka.\n")
    print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
    while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
        
# ---------- TOOLS SUB-MENU (SCAN SYSTEM FULL: SAMPAI FREKUENSI CPU) ----------
# ---------- TOOLS SUB-MENU (SCAN SYSTEM FULL: HAPUS BATERAI, SAMPAI CPU) ----------
def tools_menu():
    clear(); banner("TOOLS")
    tools_sub = [
        "Buka browser Link", 
        "Cek IP", 
        "Test Speed Network", 
        "Scan System Full (HP + Termux)",  # Tools baru: Scan Full
        "Back"
    ]; tools_pos = 1
    
    while True:
        clear(); banner("TOOLS")
        for idx, text in enumerate(tools_sub, 1):
            if idx == tools_pos:
                print(f"\033[1;36m▶ {idx}. {text}\033[0m")
            else:
                print(f"  {idx}. {text}")
        print("\n[↑↓] Navigate   [Enter] Choose")
        key = read_key_safe()
        
        if key == readchar.key.UP:
            tools_pos = (tools_pos - 2) % len(tools_sub) + 1
        elif key == readchar.key.DOWN:
            tools_pos = tools_pos % len(tools_sub) + 1
        elif key in (readchar.key.ENTER, "\r", "\n"):
            # 1. Buka browser Link (lama)
            if tools_pos == 1:
                clear(); banner("TOOLS - BUKA LINK")
                link = input("\n🔗 Ketik link lengkap (https://…): ").strip()
                if not link:
                    print("\n❌ Link kosong, dibatalkan.")
                    print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                    while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
                    continue
                print("\n⏳ Membuka browser …")
                os.system(f"am start -a android.intent.action.VIEW -d {link}")
                success_screen()
            
            # 2. Cek IP (lama)
            elif tools_pos == 2:
                clear(); banner("TOOLS - CEK IP")
                try:
                    ipv4 = subprocess.check_output(
                        ["curl", "-4", "-s", "https://ifconfig.me"], 
                        text=True, 
                        stderr=subprocess.PIPE
                    ).strip()
                except Exception:
                    ipv4 = "Tidak terdeteksi"
                try:
                    ipv6 = subprocess.check_output(
                        ["curl", "-6", "-s", "https://ifconfig.me"], 
                        text=True, 
                        stderr=subprocess.PIPE
                    ).strip()
                except Exception:
                    ipv6 = "Tidak terdeteksi"
                print(f"\nIPv4 : {ipv4}")
                print(f"IPv6 : {ipv6}\n")
                print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            
            # 3. Test Speed Network (lama)
            elif tools_pos == 3:
                clear(); banner("TOOLS - TEST SPEED NETWORK")
                print("\n⏳ Menjalankan speedtest.net …\n")
                speed_bps = -1.0
                try:
                    out = subprocess.check_output(
                        ["speedtest-cli", "--simple"],
                        stderr=subprocess.STDOUT, 
                        text=True, 
                        timeout=60
                    )
                    for line in out.splitlines():
                        if line.startswith("Download:"):
                            parts = line.split()
                            speed_val = float(parts[1])
                            speed_unit_raw = parts[2]
                            if speed_unit_raw == "Kbit/s":
                                speed_bps = speed_val * 1000
                            elif speed_unit_raw == "Mbit/s":
                                speed_bps = speed_val * 1_000_000
                            elif speed_unit_raw == "Gbit/s":
                                speed_bps = speed_val * 1_000_000_000
                            else:
                                speed_bps = speed_val
                            break
                except Exception:
                    speed_bps = -1.0

                if speed_bps < 0:
                    col, txt, speed_display, unit = "\033[31m", "Gagal mengukur", 0.0, "-"
                elif speed_bps < 1000:
                    speed_display = speed_bps
                    unit = "bps"
                    col, txt = "\033[31m", "Sangat Lambat"
                elif speed_bps < 1_000_000:
                    speed_display = speed_bps / 1000
                    unit = "Kbps"
                    col, txt = "\033[31m" if speed_display < 100 else "\033[33m", "Lambat" if speed_display < 100 else "Sedang"
                elif speed_bps < 1_000_000_000:
                    speed_display = speed_bps / 1_000_000
                    unit = "Mbps"
                    col, txt = "\033[32m" if speed_display >= 25 else "\033[33m", "Bagus" if speed_display >= 25 else "Sedang"
                else:
                    speed_display = speed_bps / 1_000_000_000
                    unit = "Gbps"
                    col, txt = "\033[32m", "Sangat Bagus"

                print(f"{col}Kecepatan : {speed_display:.2f} {unit} ({txt})\033[0m\n")
                print("\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            
            # 4. SCAN SYSTEM FULL (HAPUS BATERAI, SAMPAI FREKUENSI CPU)
            elif tools_pos == 4:
                clear(); banner("TOOLS - SCAN SYSTEM FULL")
                print("\n🔍 Menscan informasi (HP + Termux) …\n")

                # --------------------------
                # 1. INFORMASI TERMUX DETAIL
                # --------------------------
                print("\033[1;33m📱 INFORMASI TERMUX\033[0m")
                print("-" * 30)
                # Versi Termux
                try:
                    if shutil.which("termux-info"):
                        termux_ver = subprocess.check_output(
                            ["termux-info", "-v"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        print(f"• Versi Termux    : \033[34m{termux_ver}\033[0m")
                    else:
                        print(f"• Versi Termux    : \033[31mtermux-info tidak ada\033[0m")
                except Exception as e:
                    print(f"• Versi Termux    : \033[31mError: {str(e)[:25]}...\033[0m")
                
                # Lokasi Home Termux
                try:
                    termux_home = os.path.expanduser("~")
                    print(f"• Lokasi Home     : \033[34m{termux_home}\033[0m")
                except:
                    print(f"• Lokasi Home     : \033[31mTidak terdeteksi\033[0m")
                
                # Shell Aktif (bash/zsh)
                try:
                    shell_ver = subprocess.check_output(
                        ["echo", "$SHELL"], text=True, stderr=subprocess.PIPE
                    ).strip()
                    print(f"• Shell Aktif     : \033[34m{shell_ver}\033[0m")
                except:
                    print(f"• Shell Aktif     : \033[31mTidak terdeteksi\033[0m")
                
                # Paket Terinstal di Termux
                try:
                    pkg_count = subprocess.check_output(
                        ["pkg list-installed | wc -l"], 
                        shell=True, text=True, stderr=subprocess.PIPE
                    ).strip()
                    print(f"• Paket Terinstal : \033[34m{pkg_count} paket\033[0m")
                except:
                    print(f"• Paket Terinstal : \033[31mTidak terdeteksi\033[0m")

                # --------------------------
                # 2. INFORMASI SISTEM HP FULL (HAPUS BATERAI)
                # --------------------------
                print("\n\n\033[1;33m📱 INFORMASI SISTEM HP\033[0m")
                print("-" * 30)
                # Model & Merek HP
                try:
                    if shutil.which("getprop"):
                        hp_brand = subprocess.check_output(
                            ["getprop", "ro.product.brand"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        hp_model = subprocess.check_output(
                            ["getprop", "ro.product.model"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        print(f"• Merek & Model   : \033[34m{hp_brand} {hp_model}\033[0m")
                    else:
                        print(f"• Merek & Model   : \033[31mgetprop tidak ada\033[0m")
                except:
                    print(f"• Merek & Model   : \033[31mTidak terdeteksi\033[0m")
                
                # Versi Android (angka + nama)
                try:
                    if shutil.which("getprop"):
                        android_ver = subprocess.check_output(
                            ["getprop", "ro.build.version.release"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        android_name = subprocess.check_output(
                            ["getprop", "ro.build.version.codename"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        print(f"• Versi Android   : \033[34m{android_ver} ({android_name})\033[0m")
                    else:
                        print(f"• Versi Android   : \033[31mgetprop tidak ada\033[0m")
                except:
                    print(f"• Versi Android   : \033[31mTidak terdeteksi\033[0m")
                
                # SDK Android
                try:
                    if shutil.which("getprop"):
                        sdk_ver = subprocess.check_output(
                            ["getprop", "ro.build.version.sdk"], text=True, stderr=subprocess.PIPE
                        ).strip()
                        print(f"• SDK Android     : \033[34m{sdk_ver}\033[0m")
                    else:
                        print(f"• SDK Android     : \033[31mgetprop tidak ada\033[0m")
                except:
                    print(f"• SDK Android     : \033[31mTidak terdeteksi\033[0m")
                
                # RAM HP (total + tersedia)
                try:
                    if shutil.which("free"):
                        ram_info = subprocess.check_output(
                            ["free", "-h", "-t"], text=True, stderr=subprocess.PIPE
                        ).splitlines()[-1]
                        ram_total = ram_info.split()[1]
                        ram_free = ram_info.split()[3]
                        print(f"• Total RAM       : \033[34m{ram_total}\033[0m")
                        print(f"• RAM Tersedia    : \033[34m{ram_free}\033[0m")
                    else:
                        print(f"• RAM             : \033[31mperintah free tidak ada\033[0m")
                except:
                    print(f"• RAM             : \033[31mTidak terdeteksi\033[0m")
                
                # Penyimpanan (Internal + Termux)
                print("\n\033[1;33m💾 INFORMASI PENYIMPANAN\033[0m")
                print("-" * 30)
                try:
                    # Penyimpanan Internal HP
                    internal = subprocess.check_output(
                        ["df", "-h", "/sdcard"], text=True, stderr=subprocess.PIPE
                    ).splitlines()[-1]
                    int_total = internal.split()[1]
                    int_free = internal.split()[3]
                    print(f"• Internal Storage: Total \033[34m{int_total}\033[0m, Bebas \033[34m{int_free}\033[0m")
                    
                    # Penyimpanan Termux
                    termux_storage = subprocess.check_output(
                        ["df", "-h", os.path.expanduser("~")], text=True, stderr=subprocess.PIPE
                    ).splitlines()[-1]
                    term_total = termux_storage.split()[1]
                    term_free = termux_storage.split()[3]
                    print(f"• Termux Storage  : Total \033[34m{term_total}\033[0m, Bebas \033[34m{term_free}\033[0m")
                except:
                    print(f"• Penyimpanan     : \033[31mTidak terdeteksi\033[0m")

                # --------------------------
                # 3. INFORMASI CPU (ARSITEKTUR + CORE + FREKUENSI)
                # --------------------------
                print("\n\n\033[1;33m⚙️ INFORMASI CPU\033[0m")
                print("-" * 30)
                try:
                    # Arsitektur CPU (misal: aarch64)
                    cpu_arch = subprocess.check_output(
                        ["uname", "-m"], text=True, stderr=subprocess.PIPE
                    ).strip()
                    
                    # Jumlah Core CPU
                    cpu_cores = os.cpu_count()
                    
                    # Frekuensi CPU Maksimum (dalam GHz)
                    try:
                        cpu_freq_hz = open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "r").read().strip()
                        cpu_freq_ghz = round(int(cpu_freq_hz) / 1_000_000, 2)  # Konversi Hz → GHz
                        print(f"• Arsitektur      : \033[34m{cpu_arch}\033[0m")
                        print(f"• Jumlah Core     : \033[34m{cpu_cores} core\033[0m")
                        print(f"• Frekuensi Maks  : \033[34m{cpu_freq_ghz} GHz\033[0m")
                    except:
                        # Jika frekuensi tidak bisa dideteksi
                        print(f"• Arsitektur      : \033[34m{cpu_arch}\033[0m")
                        print(f"• Jumlah Core     : \033[34m{cpu_cores} core\033[0m")
                        print(f"• Frekuensi Maks  : \033[31mTidak terdeteksi\033[0m")
                except:
                    print(f"• Semua info CPU  : \033[31mTidak terdeteksi\033[0m")
                
                # Tombol kembali
                print("\n\n\033[1;36mTekan Enter untuk kembali …\033[0m", end="", flush=True)
                while read_key_safe() not in (readchar.key.ENTER, "\r", "\n"): pass
            
            # 5. Back
            else:
                return
# ------------------------------------

def main():
    menu = ["Open browser GitHub", "Run workflows", "Edit script", "Tailscale", "Tools", "Exit"]
    pos = 1
    while True:
        show_menu(menu, pos)
        key = read_key_safe()
        if key == readchar.key.UP: pos = (pos - 2) % len(menu) + 1
        elif key == readchar.key.DOWN: pos = pos % len(menu) + 1
        elif key in (readchar.key.ENTER, "\r", "\n"):
            if   pos == 1: os.system(f"am start -a android.intent.action.VIEW -d {URL}"); success_screen()
            elif pos == 2: run_workflow()
            elif pos == 3: edit_script()
            elif pos == 4: tailscale_menu()
            elif pos == 5: tools_menu()
            else: clear(); banner("EXIT LIST"); break
        elif key in ("q", readchar.key.CTRL_C): clear(); banner("EXIT LIST"); break

if __name__ == "__main__":
    main()
