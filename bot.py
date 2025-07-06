
import telebot
import requests
import time
import random
import socket
import json
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from scraper import scrape_proxies_from_channels
from scraper_telethon import scrape_proxies_from_telegram
from scraper_github import scrape_proxies_from_github_repo

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
CHANNEL_USERNAME = config["CHANNEL_USERNAME"]

bot = telebot.TeleBot(TOKEN)

proxy_sources = [
    "https://mtpro.xyz/api/?type=mtproto",
    "https://proxymtproto.ru/api",
    "https://mtpro.pro/api?type=mtproto",
    "https://telegrampx.com/api",
    "https://tgproxies.io/api",
    "https://hypermtproto.com/api",
    "https://newapi.com/api?type=mtproto"
]

def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

def fetch_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            proxies = [item['link'] for item in data if 'link' in item]
            log(f"Fetched {len(proxies)} proxies from {url}")
            return proxies
        else:
            log(f"Failed from {url}, status {response.status_code}")
            return []
    except Exception as e:
        log(f"Error fetching from {url}: {e}")
        return []

def get_all_proxies_from_apis():
    all_proxies = []
    for url in proxy_sources:
        all_proxies.extend(fetch_proxies_from_url(url))
    return all_proxies

def get_proxies_from_file():
    try:
        with open("proxies.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            log(f"Loaded {len(lines)} proxies from file")
            return lines
    except FileNotFoundError:
        log("proxies.txt not found")
        return []

def parse_proxy_info(proxy_link):
    url = proxy_link.replace("tg://", "https://")
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    server = query.get("server", [""])[0]
    port = query.get("port", [""])[0]
    secret = query.get("secret", [""])[0]
    return server, port, secret

def check_proxy_alive(server, port, timeout=5):
    try:
        with socket.create_connection((server, port), timeout=timeout):
            return True
    except Exception:
        return False

def already_sent(proxy_link):
    if not os.path.exists("sent_proxies.txt"):
        return False
    with open("sent_proxies.txt", "r") as f:
        return proxy_link in f.read()

def mark_as_sent(proxy_link):
    with open("sent_proxies.txt", "a") as f:
        f.write(proxy_link + "\n")

def post_proxy(proxy_link):
    server, port, secret = parse_proxy_info(proxy_link)
    caption = (
        f"🔥 New MTProto Proxy Found!\n\n"
        f"server: `{server}`\n"
        f"port: `{port}`\n"
        f"secret: `{secret}`\n\n"
        f"Join our channel: {CHANNEL_USERNAME}"
    )
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Connect 🔥", url=proxy_link))
    try:
        bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown", reply_markup=markup)
        log(f"✅ Sent proxy: {server}:{port}")
        mark_as_sent(proxy_link)
        print(f"✅ Sent: {server}:{port}")
    except Exception as e:
        log(f"⚠️ Failed to send: {e}")
        print(f"⚠️ Failed to send: {e}")

def send_min_proxies_from_source(source_list, min_count=100):
    random.shuffle(source_list)
    sent = 0
    for proxy_link in source_list:
        if sent >= min_count:
            break
        if already_sent(proxy_link):
            continue
        server, port = parse_proxy(proxy_link)
        if server and port and check_proxy_alive(server, port):
            post_proxy(proxy_link)
        else:
           log(f"❌ Dead proxy skipped: {proxy_link}")
           print(f"❌ Dead proxy skipped: {proxy_link}")
    if sent < min_count:
        log(f"Only sent {sent}/{min_count} from this source")
    return sent

def main():
    while True:
        print("🔍 Gathering proxies...")

        api_list = get_all_proxies_from_apis()
        send_min_proxies_from_source(api_list, min_count=300)

        file_list = get_proxies_from_file()
        send_min_proxies_from_source(file_list, min_count=300)

        scraped_list = scrape_proxies_from_channels()
        send_min_proxies_from_source(scraped_list, min_count=300)

        scraped_telegram_list = scrape_proxies_from_telegram()
        send_min_proxies_from_source(scraped_telegram_list, min_count=300)
        
        github_list = scrape_proxies_from_github_repo("TelegramMessenger/MTProxy")
        send_min_proxies_from_source(github_list, min_count=300)

        print("✅ Finished this cycle. Waiting 180 minutes...")
        time.sleep(10800)

if __name__ == "__main__":
    print("🚀 Bot started...")
    log("Bot started.")
    main()
