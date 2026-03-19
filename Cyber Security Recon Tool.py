#!/usr/bin/env python3
"""
=================================================================
CYBER SECURITY RECON TOOL
Coded by: Mr. Sabaz Ali Khan
Pakistani Ethical Hacker | Certified White Hat Hacker
GitHub: https://github.com/whoami592
=================================================================
FOR EDUCATIONAL PURPOSES ONLY!
I am not responsible for any misuse of this tool.
Use only on targets you have explicit permission to test.
=================================================================
"""

import argparse
import socket
import requests
import whois
from datetime import datetime
import sys
import time

# ====================== BANNER ======================
def show_banner():
    banner = r"""
    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗    ████████╗ ██████╗  ██████╗ ██╗
    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║       ██║   ██║   ██║██║   ██║██║
    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║       ██║   ██║   ██║██║   ██║██║
    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║       ██║   ╚██████╔╝╚██████╔╝███████╗
    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    
    Cyber Security Recon Tool v1.0
    Coded by Mr. Sabaz Ali Khan (Pakistan)
    ================================================
    """
    print(banner)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Tool Started...\n")

# ====================== WHOIS LOOKUP ======================
def whois_lookup(domain):
    print(f"[+] Fetching WHOIS information for {domain}...")
    try:
        w = whois.whois(domain)
        print("\n" + "="*60)
        print("WHOIS RESULT")
        print("="*60)
        print(f"Domain Name     : {w.domain_name}")
        print(f"Registrar       : {w.registrar}")
        print(f"Creation Date   : {w.creation_date}")
        print(f"Expiration Date : {w.expiration_date}")
        print(f"Name Servers    : {w.name_servers}")
        print(f"Emails          : {w.emails}")
        print(f"Org             : {w.org}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"[-] WHOIS Error: {e}")

# ====================== SUBDOMAIN ENUMERATION ======================
def subdomain_enum(domain, wordlist_file=None):
    print(f"[+] Starting Subdomain Enumeration for {domain}...")
    # Default common subdomains (you can add more or use a big wordlist)
    common_subs = [
        "www", "admin", "api", "dev", "test", "staging", "mail", "ftp", "webmail",
        "portal", "blog", "shop", "app", "cdn", "static", "backup", "beta", "demo"
    ]
    
    found = 0
    if wordlist_file:
        try:
            with open(wordlist_file, "r") as f:
                common_subs = [line.strip() for line in f if line.strip()]
        except:
            print("[-] Wordlist not found, using built-in list.")

    for sub in common_subs:
        subdomain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            print(f"[+] Found: {subdomain} → {ip}")
            found += 1
        except socket.gaierror:
            pass  # subdomain not resolved
        time.sleep(0.1)  # avoid rate limiting
    
    print(f"[+] Subdomain scan complete. {found} subdomains discovered.\n")

# ====================== PORT SCANNING ======================
def port_scan(target, ports=[21, 22, 23, 25, 53, 80, 443, 3306, 3389, 8080]):
    print(f"[+] Starting Port Scan on {target} (Top 10 ports)...")
    print(f"{'Port':<6} {'Status':<10} {'Service'}")
    print("-" * 30)
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        result = sock.connect_ex((target, port))
        if result == 0:
            service = socket.getservbyport(port, "tcp") if port in [21,22,23,25,53,80,443] else "Unknown"
            print(f"{port:<6} Open      {service}")
        else:
            print(f"{port:<6} Closed")
        sock.close()
        time.sleep(0.2)
    print("\n")

# ====================== HTTP HEADER & TITLE GRAB ======================
def http_info(url):
    if not url.startswith("http"):
        url = "http://" + url
    print(f"[+] Fetching HTTP headers & title for {url}...")
    try:
        r = requests.get(url, timeout=5, allow_redirects=True)
        print(f"Status Code : {r.status_code}")
        print(f"Server      : {r.headers.get('Server', 'Not found')}")
        print(f"Title       : {r.text.split('<title>')[1].split('</title>')[0] if '<title>' in r.text else 'No title'}")
        print("Headers:")
        for key, value in r.headers.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"[-] HTTP Error: {e}")

# ====================== MAIN MENU ======================
def main():
    show_banner()
    
    parser = argparse.ArgumentParser(description="Cyber Security Recon Tool by Mr. Sabaz Ali Khan")
    parser.add_argument("target", help="Target domain or IP (example: example.com)")
    parser.add_argument("-w", "--whois", action="store_true", help="Perform WHOIS lookup")
    parser.add_argument("-s", "--subdomains", action="store_true", help="Enumerate subdomains")
    parser.add_argument("-p", "--ports", action="store_true", help="Scan common ports")
    parser.add_argument("-H", "--http", action="store_true", help="Grab HTTP headers & title")
    parser.add_argument("--wordlist", help="Path to custom subdomain wordlist file")
    
    args = parser.parse_args()
    
    target = args.target
    ip = None
    
    try:
        ip = socket.gethostbyname(target)
        print(f"[+] Target: {target} → Resolved IP: {ip}\n")
    except:
        print(f"[!] Could not resolve {target}. Using domain directly.\n")
    
    if args.whois:
        whois_lookup(target)
    
    if args.subdomains:
        subdomain_enum(target, args.wordlist)
    
    if args.ports:
        scan_target = ip if ip else target
        port_scan(scan_target)
    
    if args.http:
        http_info(target)
    
    if not (args.whois or args.subdomains or args.ports or args.http):
        # Run all if no flags
        print("[*] No options selected → Running Full Recon\n")
        whois_lookup(target)
        subdomain_enum(target, args.wordlist)
        scan_target = ip if ip else target
        port_scan(scan_target)
        http_info(target)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Recon Complete! Stay Safe & Hack Responsibly 🔥")

if __name__ == "__main__":
    # Install requirements: pip install python-whois requests
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Tool stopped by user. Coded by Mr. Sabaz Ali Khan")
        sys.exit(0)
