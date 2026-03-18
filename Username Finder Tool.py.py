import requests
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ====================== BANNER ======================
print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗██████╗  █████╗ ███████╗    ███████╗██╗   ██╗║
║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝    ██╔════╝██║   ██║║
║   ██████╔╝█████╗  ██████╔╝███████║█████╗      █████╗  ██║   ██║║
║   ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══╝      ██╔══╝  ██║   ██║║
║   ██║  ██║███████╗██████╔╝██║  ██║██║         ██║     ╚██████╔╝║
║   ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝         ╚═╝      ╚═════╝ ║
║                                                              ║
║               USERNAME FINDER TOOL v1.0                      ║
║                                                              ║
║              Coded by Mr Sabaz Ali Khan                      ║
║         (Multi-Platform Username Availability Checker)       ║
╚══════════════════════════════════════════════════════════════╝
""")

# ====================== CONFIG ======================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# List of platforms (you can add more!)
PLATFORMS = [
    {
        "name": "GitHub",
        "url": "https://github.com/{}",
        "available_if": lambda r: r.status_code == 404
    },
    {
        "name": "Twitter / X",
        "url": "https://x.com/{}",
        "available_if": lambda r: r.status_code == 404 or "This account doesn’t exist" in r.text
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{}/",
        "available_if": lambda r: "Sorry, this page isn't available" in r.text or r.status_code == 404
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}/",
        "available_if": lambda r: r.status_code == 404
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@{}",
        "available_if": lambda r: r.status_code == 404 or "Couldn't find this account" in r.text
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{}",
        "available_if": lambda r: r.status_code == 404
    },
    {
        "name": "Twitch",
        "url": "https://www.twitch.tv/{}",
        "available_if": lambda r: r.status_code == 404 or "Sorry. Unless you’ve got a time machine" in r.text
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}",
        "available_if": lambda r: r.status_code == 404
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "available_if": lambda r: r.status_code == 404
    },
    {
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{}",
        "available_if": lambda r: "The specified profile could not be found" in r.text or r.status_code == 404
    },
]

# ====================== FUNCTIONS ======================
def check_username(platform, username):
    url = platform["url"].format(username)
    try:
        response = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        is_available = platform["available_if"](response)
        
        status = "✅ AVAILABLE" if is_available else "❌ TAKEN"
        color = "\033[92m" if is_available else "\033[91m"
        reset = "\033[0m"
        
        return f"{color}[{platform['name']:12}] {status}{reset} → {url}"
        
    except requests.exceptions.RequestException:
        return f"\033[93m[{platform['name']:12}] ⚠️  ERROR (Timeout/Connection)\033[0m"
    except Exception:
        return f"\033[93m[{platform['name']:12}] ⚠️  UNKNOWN ERROR\033[0m"


def main():
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    else:
        username = input("\nEnter username to check: ").strip()

    if not username:
        print("\033[91m❌ Username cannot be empty!\033[0m")
        sys.exit(1)

    print(f"\n🔍 Checking username: \033[96m{username}\033[0m")
    print("─" * 70)
    start_time = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_platform = {executor.submit(check_username, platform, username): platform for platform in PLATFORMS}
        
        for future in as_completed(future_to_platform):
            result = future.result()
            print(result)
            results.append(result)

    elapsed = time.time() - start_time
    print("─" * 70)
    print(f"✅ Scan completed in {elapsed:.2f} seconds")
    print(f"\033[96mCoded by Mr Sabaz Ali Khan - Happy Hunting! 🚀\033[0m\n")

    # Optional: Save results
    save = input("Save results to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"{username}_results.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Username Finder Tool Report\n")
            f.write(f"Username: {username}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            for line in results:
                # Remove ANSI colors for file
                clean_line = line.replace("\033[92m", "").replace("\033[91m", "").replace("\033[93m", "").replace("\033[96m", "").replace("\033[0m", "")
                f.write(clean_line + "\n")
        print(f"💾 Results saved to {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m⛔ Scan cancelled by user\033[0m")
        sys.exit(0)