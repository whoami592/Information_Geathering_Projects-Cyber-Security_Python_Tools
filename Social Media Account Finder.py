"""
============================================================
SOCIAL MEDIA ACCOUNT FINDER
============================================================
Coded by: Mr Sabaz Ali Khan
Pakistani Ethical Hacker | whoami592
GitHub: https://github.com/whoami592

For Educational & OSINT Purposes Only
Do NOT use for illegal activities, stalking, or harassment.
This tool checks usernames across popular platforms using public profiles.

Python 3.x Required
Install dependencies: pip install requests
"""

import requests
import sys
from time import sleep
from datetime import datetime

# ====================== CONFIG ======================
TIMEOUT = 8
DELAY = 0.8          # Be respectful to websites
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

# List of platforms (you can add more)
PLATFORMS = {
    "Instagram": "https://www.instagram.com/{username}/",
    "Twitter / X": "https://twitter.com/{username}",
    "Facebook": "https://www.facebook.com/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "YouTube": "https://www.youtube.com/@{username}",
    "GitHub": "https://github.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "LinkedIn": "https://www.linkedin.com/in/{username}/",
    "Pinterest": "https://www.pinterest.com/{username}/",
    "Tumblr": "https://{username}.tumblr.com",
    "Twitch": "https://www.twitch.tv/{username}",
    "Snapchat": "https://www.snapchat.com/add/{username}",
    "Medium": "https://medium.com/@{username}",
    "DeviantArt": "https://{username}.deviantart.com",
    "Vimeo": "https://vimeo.com/{username}",
    "SoundCloud": "https://soundcloud.com/{username}",
    "Behance": "https://www.behance.net/{username}",
    "Dribbble": "https://dribbble.com/{username}",
    "Flickr": "https://www.flickr.com/people/{username}",
    "VK": "https://vk.com/{username}",
    "Telegram": "https://t.me/{username}",          # Public channel or user
    "Discord": "https://discord.com/users/{username}", # Not very reliable but added
}

# Some sites need special status code or text check
SPECIAL_CHECKS = {
    "Instagram": lambda r: r.status_code == 200 and "Page not found" not in r.text and "Sorry, this page isn't available" not in r.text,
    "Twitter / X": lambda r: r.status_code == 200 and "This account doesn’t exist" not in r.text,
    "TikTok": lambda r: r.status_code == 200 and "Couldn't find this account" not in r.text,
    "YouTube": lambda r: r.status_code == 200 and "This channel does not exist" not in r.text,
    "Facebook": lambda r: r.status_code == 200 and "This content isn't available" not in r.text,
}

# ===================================================

def banner():
    print("=" * 60)
    print("SOCIAL MEDIA ACCOUNT FINDER".center(60))
    print("Coded by Mr Sabaz Ali Khan".center(60))
    print("Pakistani Ethical Hacker".center(60))
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def check_account(platform, username):
    url = PLATFORMS[platform].format(username=username)
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
        
        # Default check
        if response.status_code == 200:
            # Apply special check if available
            if platform in SPECIAL_CHECKS:
                if SPECIAL_CHECKS[platform](response):
                    return True, url
                else:
                    return False, None
            else:
                # Generic check: if status 200 and page is not too small (not error page)
                if len(response.text) > 500:  # rough filter
                    return True, url
                else:
                    return False, None
        else:
            return False, None
            
    except requests.exceptions.RequestException:
        return False, None
    except Exception as e:
        return False, None

def main():
    banner()
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter username to search: ").strip()
    
    if not username:
        print("❌ Username cannot be empty!")
        sys.exit(1)
    
    print(f"🔍 Searching for @{username} across {len(PLATFORMS)} platforms...\n")
    sleep(1)
    
    found = 0
    results = []
    
    for idx, (platform, _) in enumerate(PLATFORMS.items(), 1):
        print(f"[{idx:02d}/{len(PLATFORMS)}] Checking {platform}...", end=" ")
        
        exists, link = check_account(platform, username)
        
        if exists:
            print("✅ FOUND")
            found += 1
            results.append(f"✅ {platform}: {link}")
        else:
            print("❌ Not found")
        
        sleep(DELAY)  # Be gentle with rate limits
    
    print("\n" + "=" * 60)
    print(f"SEARCH COMPLETE - @{username}")
    print(f"Total platforms checked : {len(PLATFORMS)}")
    print(f"Accounts found         : {found}")
    print("=" * 60)
    
    if found > 0:
        print("\n📍 FOUND ACCOUNTS:")
        for result in results:
            print(result)
    else:
        print("\n❌ No accounts found with this username.")
    
    print(f"\nThank you for using the tool!")
    print("Coded with ❤️ by Mr Sabaz Ali Khan")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Search stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
