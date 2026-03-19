#!/usr/bin/env python3
"""
    Domain Information Scanner
    ───────────────────────────
    Coded by: Mr Sabaz Ali Khan   (as requested 😄)
    Purpose: Quick reconnaissance / OSINT gathering for domains
    
    Last updated: March 2025 style
"""

import socket
import ssl
import whois
import dns.resolver
import requests
import argparse
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional, List, Dict
import warnings

# Silence some noisy warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

BANNER = r"""
   ▄████████    ▄████████  ▄█    █▄     ▄████████    ▄████████ 
  ███    ███   ███    ███ ███    ███   ███    ███   ███    ███ 
  ███    █▀    ███    █▀  ███    ███   ███    █▀    ███    █▀  
 ▄███▄▄▄      ▄███▄▄▄     ███    ███  ▄███▄▄▄      ▄███▄▄▄     
▀▀███▀▀▀     ▀▀███▀▀▀     ███    ███ ▀▀███▀▀▀     ▀▀███▀▀▀     
  ███    █▄    ███    █▄  ███    ███   ███    █▄    ███    █▄  
  ███    ███   ███    ███ ███    ███   ███    ███   ███    ███ 
  ██████████   ██████████  ▀██████▀    ██████████   ██████████ 
                     Domain Information Scanner
                     coded by Mr Sabaz Ali Khan
"""


class DomainScanner:
    def __init__(self, domain: str):
        self.domain = domain.strip().lower()
        self.results: Dict[str, any] = {}

    def run_all(self) -> None:
        """Run all available checks"""
        print(f"\n[+] Scanning domain: {self.domain}\n")
        
        self.get_whois()
        self.get_dns_records()
        self.get_ip_addresses()
        self.get_http_headers()
        self.get_ssl_certificate_info()
        self.show_summary()

    def get_whois(self) -> None:
        print("[*] Fetching WHOIS information...")
        try:
            w = whois.whois(self.domain)
            self.results["whois"] = {
                "registrar": w.registrar,
                "org": w.org or w.organization,
                "registrant_name": w.name,
                "creation_date": self._normalize_date(w.creation_date),
                "expiration_date": self._normalize_date(w.expiration_date),
                "name_servers": w.name_servers,
                "emails": w.emails,
            }
            print("    ✓ WHOIS collected")
        except Exception as e:
            print(f"    ✗ WHOIS failed: {e}")
            self.results["whois"] = {"error": str(e)}

    def get_dns_records(self) -> None:
        print("[*] Collecting DNS records...")
        records = {}
        
        for rtype in ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]:
            try:
                answers = dns.resolver.resolve(self.domain, rtype, raise_on_no_answer=False)
                if answers:
                    records[rtype] = [str(rdata) for rdata in answers]
            except Exception:
                pass

        self.results["dns"] = records
        print(f"    ✓ Found {len(records)} record types")

    def get_ip_addresses(self) -> None:
        print("[*] Resolving IP address(es)...")
        try:
            ips_v4 = socket.gethostbyname_ex(self.domain)[2]
            self.results["ipv4"] = ips_v4
            
            # Try IPv6 (may fail silently)
            try:
                ips_v6 = [info[4][0] for info in socket.getaddrinfo(self.domain, None, socket.AF_INET6)]
                if ips_v6:
                    self.results["ipv6"] = ips_v6
            except:
                pass
                
            print(f"    ✓ Resolved {len(ips_v4)} IPv4 address(es)")
        except Exception as e:
            print(f"    ✗ Resolution failed: {e}")

    def get_http_headers(self) -> None:
        print("[*] Checking HTTP/HTTPS headers...")
        urls = [f"http://{self.domain}", f"https://{self.domain}"]
        headers_found = {}

        for url in urls:
            try:
                r = requests.get(url, timeout=8, allow_redirects=True, verify=False)
                h = dict(r.headers)
                headers_found[urlparse(url).scheme] = {
                    "status": r.status_code,
                    "server": h.get("Server"),
                    "x-powered-by": h.get("X-Powered-By"),
                    "content-security-policy": h.get("Content-Security-Policy"),
                    "strict-transport-security": h.get("Strict-Transport-Security"),
                    "x-frame-options": h.get("X-Frame-Options"),
                    "final_url": r.url,
                }
            except Exception as e:
                headers_found[urlparse(url).scheme] = {"error": str(e)}

        self.results["http_headers"] = headers_found
        print("    ✓ Headers collected")

    def get_ssl_certificate_info(self) -> None:
        print("[*] Checking SSL certificate...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=8) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    self.results["ssl"] = {
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "notBefore": cert.get("notBefore"),
                        "notAfter": cert.get("notAfter"),
                        "version": cert.get("version"),
                        "serialNumber": cert.get("serialNumber"),
                    }
                    print("    ✓ SSL certificate info collected")
        except Exception as e:
            self.results["ssl"] = {"error": str(e)}
            print(f"    ✗ SSL check failed: {e}")

    def show_summary(self):
        print("\n" + "═" * 70)
        print("  DOMAIN SCAN SUMMARY")
        print("═" * 70)

        if "ipv4" in self.results and self.results["ipv4"]:
            print(f"IPv4 Addresses : {', '.join(self.results['ipv4'])}")
        if "ipv6" in self.results and self.results["ipv6"]:
            print(f"IPv6 Addresses : {', '.join(self.results['ipv6'][:3])} ...")

        if "whois" in self.results and "error" not in self.results["whois"]:
            w = self.results["whois"]
            print(f"Registrar      : {w.get('registrar','—')}")
            print(f"Created        : {w.get('creation_date','—')}")
            print(f"Expires        : {w.get('expiration_date','—')}")
            if w.get("org"):
                print(f"Organization   : {w['org']}")

        if "dns" in self.results:
            for rtype, values in self.results["dns"].items():
                if values:
                    print(f"{rtype:<6} → {', '.join(values[:3])}" + (" ..." if len(values)>3 else ""))

        print("═" * 70 + "\n")

    @staticmethod
    def _normalize_date(date_obj) -> str:
        if isinstance(date_obj, list):
            date_obj = date_obj[0]
        if hasattr(date_obj, "strftime"):
            return date_obj.strftime("%Y-%m-%d")
        return str(date_obj)


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="Domain Information Scanner by Mr Sabaz Ali Khan")
    parser.add_argument("domain", help="Domain name (example.com)")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output (not implemented yet)")
    
    args = parser.parse_args()

    scanner = DomainScanner(args.domain)
    scanner.run_all()


if __name__ == "__main__":
    main()
