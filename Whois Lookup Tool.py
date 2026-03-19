#!/usr/bin/env python3
"""
WHOIS Lookup Tool
Author: Mr. Sabaz Ali Khan (inspired edition)
Last Update: 2025–2026 style

Features:
    • Colored & formatted output
    • Multiple domain support
    • Automatic whois server detection fallback
    • Basic parsing of important fields
    • Copy-friendly output mode (--raw)
"""

import socket
import sys
import argparse
import re
from datetime import datetime
from typing import Optional, List

try:
    import whois
    HAS_PYTHON_WHOIS = True
except ImportError:
    HAS_PYTHON_WHOIS = False
    print("→ Tip: For much better results install →  pip install python-whois", file=sys.stderr)

# ────────────────────────────────────────────────
#   ANSI COLORS
# ────────────────────────────────────────────────
C = {
    "reset": "\033[0m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
    "bold": "\033[1m",
}

def color(text: str, color_key: str) -> str:
    return f"{C[color_key]}{text}{C['reset']}"

def banner():
    print(f"""
{color("╔════════════════════════════════════════════╗", "cyan")}
{color("║", "cyan")}      WHOIS Lookup Tool 2025–2026 Edition      {color("║", "cyan")}
{color("║", "cyan")}      coded with passion by                    {color("║", "cyan")}
{color("║", "cyan")}         Mr. Sabaz Ali Khan                     {color("║", "cyan")}
{color("╚════════════════════════════════════════════╝", "cyan")}
""")

def get_whois_raw(domain: str) -> Optional[str]:
    """Low-level WHOIS query without python-whois"""
    domain = domain.strip().lower()
    
    # Most common whois servers
    tld = domain.split('.')[-1].lower()
    whois_server_map = {
        'com': 'whois.verisign-grs.com',
        'net': 'whois.verisign-grs.com',
        'org': 'whois.pir.org',
        'io': 'whois.nic.io',
        'co': 'whois.nic.co',
        'ai': 'whois.nic.ai',
        'app': 'whois.nic.google',
        'dev': 'whois.nic.google',
        'pk': 'whois.pknic.net.pk',
        'in': 'whois.registry.in',
        'uk': 'whois.nic.uk',
        'de': 'whois.denic.de',
        'ru': 'whois.tcinet.ru',
    }
    
    server = whois_server_map.get(tld, 'whois.iana.org')
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((server, 43))
        s.send((domain + "\r\n").encode())
        
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        
        s.close()
        return response.decode("utf-8", errors="replace").strip()
    
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        print(f"{color('Error', 'red')} connecting to {server}: {e}", file=sys.stderr)
        return None


def extract_important_fields(raw: str) -> dict:
    """Very simple regex-based field extraction"""
    data = {}
    
    patterns = {
        "Registrar":        r"(?mi)^Registrar:\s+(.+?)$",
        "Created":          r"(?mi)(?:Creation Date|Registered on|created):\s+(.+?)$",
        "Expires":          r"(?mi)(?:Registry Expiry Date|Expiry date|expires):\s+(.+?)$",
        "Updated":          r"(?mi)(?:Updated Date|Last updated):\s+(.+?)$",
        "Name Servers":     r"(?mi)^Name Server:\s+(.+?)$",
        "Status":           r"(?mi)^Status:\s+(.+?)$",
        "Registrant Org":   r"(?mi)(?:Registrant Organization|Organisation):\s+(.+?)$",
        "Registrant Country": r"(?mi)(?:Registrant Country):\s+(.+?)$",
    }
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, raw)
        if matches:
            if key == "Name Servers":
                data[key] = [ns.strip() for ns in matches if ns.strip()]
            else:
                # take first non-empty
                for m in matches:
                    cleaned = m.strip()
                    if cleaned:
                        data[key] = cleaned
                        break
    
    return data


def print_beautiful_whois(domain: str, raw: str, parsed: dict, raw_mode: bool = False):
    if raw_mode:
        print(f"\n{color('─'*68, 'gray')}")
        print(f"Raw WHOIS for {color(domain, 'yellow')}")
        print(f"{color('─'*68, 'gray')}\n")
        print(raw or "(no data received)")
        return

    print(f"\n{color('═'*60, 'blue')}")
    print(f" {color('DOMAIN', 'cyan')} → {color(domain.upper(), 'yellow bold')}")
    print(f"{color('═'*60, 'blue')}\n")

    if not parsed and not raw:
        print(f"  {color('× No WHOIS data received', 'red')}")
        return

    important_order = [
        "Registrar", "Created", "Updated", "Expires",
        "Status", "Registrant Org", "Registrant Country", "Name Servers"
    ]

    found_any = False
    for key in important_order:
        if key in parsed:
            found_any = True
            value = parsed[key]
            if isinstance(value, list):
                print(f"  {color(key+':', 'green')} ")
                for v in value:
                    print(f"      • {color(v, 'white')}")
            else:
                print(f"  {color(key+':', 'green')} {color(value, 'white')}")

    if not found_any and raw:
        print(f"  {color('(!) Basic fields not detected — showing first 15 lines of raw data', 'yellow')}")
        lines = raw.splitlines()[:15]
        for line in lines:
            if line.strip():
                print(f"    {color(line, 'gray')}")

    print()


def main():
    parser = argparse.ArgumentParser(description="WHOIS Lookup Tool by Mr. Sabaz Ali Khan")
    parser.add_argument("domains", nargs="+", help="One or more domain names")
    parser.add_argument("--raw", action="store_true", help="Show raw WHOIS output only")
    parser.add_argument("--no-python-whois", action="store_true", help="Force socket method (ignore python-whois)")
    
    args = parser.parse_args()

    banner()

    use_python_whois = HAS_PYTHON_WHOIS and not args.no_python_whois

    for i, domain in enumerate(args.domains, 1):
        if i > 1:
            print()

        print(f"{color('['+str(i)+'/'+str(len(args.domains))+']', 'gray')} Querying: {color(domain, 'cyan bold')}")

        try:
            if use_python_whois:
                w = whois.whois(domain)
                parsed = {
                    "Registrar": w.registrar,
                    "Created": w.creation_date,
                    "Expires": w.expiration_date,
                    "Updated": w.last_updated,
                    "Name Servers": w.name_servers,
                    "Status": w.status,
                    "Registrant Org": getattr(w, "org", None) or w.registrant_org,
                }
                raw = str(w)
            else:
                raw = get_whois_raw(domain)
                parsed = extract_important_fields(raw) if raw else {}

            print_beautiful_whois(domain, raw, parsed, raw_mode=args.raw)

        except Exception as e:
            print(f"  {color('Error:', 'red')} {str(e)}")
            if not args.raw:
                print(f"  Try again with {color('--raw', 'yellow')} or {color('--no-python-whois', 'yellow')} flag\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{color('Goodbye! ────────────────────────────────────────', 'gray')}")
        sys.exit(130)
