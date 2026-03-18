# ========================================================
#          WEBSITE INFORMATION COLLECTOR
# ========================================================
# Coded by: Mr. Sabaz Ali Khan
# Pakistani Ethical Hacker | Certified White Hat Hacker
# YouTube: Mr Sabaz Ali Khan Hacking Series
# GitHub: whoami592
# For Educational & Ethical Hacking Purposes ONLY
# Do NOT use this tool for illegal activities.
# I am not responsible for any misuse.
# ========================================================

import requests
from bs4 import BeautifulSoup
import socket
import whois
import re
import os
from datetime import datetime

def banner():
    print("""
    ========================================================
              WEBSITE INFORMATION COLLECTOR v1.0
    ========================================================
    Coded by Mr. Sabaz Ali Khan (Pakistani Ethical Hacker)
    ========================================================
    """)

def collect_website_info(target):
    banner()
    print(f"[+] Target: {target}")
    print(f"[+] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Add http/https if missing
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    
    try:
        # 1. Get IP Address
        domain = re.sub(r"https?://", "", target).split("/")[0]
        ip = socket.gethostbyname(domain)
        print(f"[+] IP Address          : {ip}")
        
        # 2. WHOIS Information
        print("\n[+] Fetching WHOIS Information...")
        w = whois.whois(domain)
        print(f"    Registrar           : {w.registrar}")
        print(f"    Creation Date       : {w.creation_date}")
        print(f"    Expiration Date     : {w.expiration_date}")
        print(f"    Name Servers        : {w.name_servers}")
        print(f"    Registrant Email    : {w.emails}")
        
        # 3. HTTP Request & Headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(target, headers=headers, timeout=10)
        
        print(f"\n[+] Status Code         : {response.status_code}")
        print("\n[+] HTTP Headers:")
        for key, value in response.headers.items():
            print(f"    {key}: {value}")
        
        # 4. Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"\n[+] Page Title          : {soup.title.string.strip() if soup.title else 'Not Found'}")
        
        # Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        print(f"[+] Meta Description    : {meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else 'Not Found'}")
        
        # Meta Keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        print(f"[+] Meta Keywords       : {meta_keywords['content'].strip() if meta_keywords and meta_keywords.get('content') else 'Not Found'}")
        
        # All Meta Tags (summary)
        print("\n[+] All Meta Tags Found:")
        for meta in soup.find_all("meta"):
            if meta.get("name") or meta.get("property"):
                name = meta.get("name") or meta.get("property")
                content = meta.get("content", "")
                print(f"    {name}: {content[:80]}...")
        
        # Links Count
        links = soup.find_all("a")
        internal = 0
        external = 0
        for link in links:
            href = link.get("href", "")
            if href.startswith(("http", "https")) and domain not in href:
                external += 1
            else:
                internal += 1
        print(f"\n[+] Total Links         : {len(links)}")
        print(f"    Internal Links      : {internal}")
        print(f"    External Links      : {external}")
        
        # 5. Check robots.txt
        robots_url = f"https://{domain}/robots.txt"
        try:
            robots = requests.get(robots_url, timeout=5)
            if robots.status_code == 200:
                print(f"\n[+] robots.txt Status   : Found")
                print("    First 5 lines of robots.txt:")
                print(robots.text.strip().split("\n")[:5])
            else:
                print(f"\n[+] robots.txt Status   : Not Found (Status: {robots.status_code})")
        except:
            print("\n[+] robots.txt Status   : Unable to fetch")
        
        # Save Report
        report_file = f"{domain}_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"Website Information Collector Report\n")
            f.write(f"Coded by Mr. Sabaz Ali Khan\n")
            f.write(f"Target: {target}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            f.write(f"IP Address: {ip}\n")
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Title: {soup.title.string if soup.title else 'N/A'}\n")
            f.write(f"Description: {meta_desc['content'] if meta_desc else 'N/A'}\n")
            f.write(f"Total Links: {len(links)}\n")
            f.write("\nFull WHOIS and Headers saved above.\n")
        
        print(f"\n[+] Report Saved As     : {report_file}")
        print("\n[+] Collection Complete! Thank you for using this tool.")
        
    except requests.exceptions.RequestException:
        print("[-] Error: Could not connect to the website. Check URL or internet.")
    except socket.gaierror:
        print("[-] Error: Could not resolve IP address.")
    except Exception as e:
        print(f"[-] Unexpected Error: {str(e)}")

# ===================== MAIN =====================
if __name__ == "__main__":
    banner()
    target = input("Enter Website URL or Domain (e.g. google.com): ").strip()
    if target:
        collect_website_info(target)
    else:
        print("[-] No target provided. Exiting...")