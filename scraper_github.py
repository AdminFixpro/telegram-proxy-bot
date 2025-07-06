import requests
import re
from datetime import datetime

def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

def scrape_proxies_from_github_repo(repo):
    proxies = []
    urls = [
        f"https://raw.githubusercontent.com/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{repo}/master/README.md",
    ]

    pattern = re.compile(r"(tg://proxy\?[^ \"'\n<]+)")

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                matches = pattern.findall(response.text)
                if matches:
                    log(f"✅ Found {len(matches)} proxies in {url}")
                    proxies.extend(matches)
                else:
                    log(f"❌ No proxies found in {url}")
            else:
                log(f"❌ Failed to fetch {url}, status {response.status_code}")
        except Exception as e:
            log(f"⚠️ Error scraping {url}: {e}")

    return list(set(proxies))

def scrape_proxies_from_all_github():
    all_proxies = []
    try:
        with open("github_repos.txt", "r", encoding="utf-8") as f:
            repos = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log("⚠️ github_repos.txt not found.")
        return []

    for repo in repos:
        proxies = scrape_proxies_from_github_repo(repo)
        all_proxies.extend(proxies)

    return list(set(all_proxies))
