import telebot
from telebot import types
import requests
import socket
import time
import re
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from scraper_github import scrape_proxies_from_all_github

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TOKEN"]
CHANNEL_USERNAME = config["CHANNEL_USERNAME"]
GROUP_ID = config["GROUP_ID"]

bot = telebot.TeleBot(TOKEN)

def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")

def parse_proxy_info(proxy_link):
    url = proxy_link.replace("tg://", "https://")
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    server = query.get("server", [""])[0]
    port = query.get("port", [""])[0]
    secret = query.get("secret", [""])[0]
    return server, port, secret

def build_tg_link(server, port, secret):
    return f"tg://proxy?server={server}&port={port}&secret={secret}"

def check_proxy_alive(server, port, timeout=5):
    try:
        with socket.create_connection((server, int(port)), timeout=timeout):
            return True
    except:
        return False

def extract_proxy_from_text(text):
    # پیدا کردن لینک tg://proxy
    pattern_link = re.compile(r"(tg://proxy\?[^ \"'\n<]+)")
    matches = pattern_link.findall(text)
    if matches:
        return matches

    # پیدا کردن server / port / secret جدا
    pattern_server = re.search(r"server[:= ]+([\w\.\-]+)", text, re.I)
    pattern_port = re.search(r"port[:= ]+(\d+)", text, re.I)
    pattern_secret = re.search(r"secret[:= ]+([a-fA-F0-9]+)", text, re.I)
    if pattern_server and pattern_port and pattern_secret:
        server = pattern_server.group(1)
        port = pattern_port.group(1)
        secret = pattern_secret.group(1)
        return [build_tg_link(server, port, secret)]

    return []

def post_proxy(proxy_link):
    server, port, secret = parse_proxy_info(proxy_link)
    caption = (
        f"🔥 New MTProto Proxy Found!\n\n"
        f"server: `{server}`\n"
        f"port: `{port}`\n"
        f"secret: `{secret}`\n\n"
        f"Join our channel: {CHANNEL_USERNAME}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Connect 🔥", url=proxy_link))
    try:
        bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown", reply_markup=markup)
        log(f"✅ Sent proxy: {server}:{port}")
    except Exception as e:
        log(f"⚠️ Failed to send proxy: {e}")

def send_min_proxies_from_source(proxy_list, min_count=300):
    sent = 0
    for proxy_link in proxy_list:
        server, port, secret = parse_proxy_info(proxy_link)
        if server and port and secret:
            if check_proxy_alive(server, port):
                post_proxy(proxy_link)
                sent += 1
                time.sleep(1)
            else:
                log(f"❌ Dead proxy skipped: {server}:{port}")
        if sent >= min_count:
            break
    if sent < min_count:
        log(f"⚠️ Only sent {sent}/{min_count} proxies in this cycle.")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_group_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        proxies = extract_proxy_from_text(message.text)
        for proxy in proxies:
            server, port, secret = parse_proxy_info(proxy)
            if server and port and secret and check_proxy_alive(server, port):
                post_proxy(proxy)

def main():
    while True:
        log("🔍 Gathering proxies...")

        # از github
        github_list = scrape_proxies_from_all_github()

        # میتونی scraper های دیگه هم اینجا اضافه کنی
        all_proxies = github_list

        # remove duplicates
        all_proxies = list(set(all_proxies))
        send_min_proxies_from_source(all_proxies, min_count=300)

        log("✅ Finished this cycle. Waiting 3 hours...")
        time.sleep(10800)  # 3 hours

if __name__ == "__main__":
    print("🚀 Bot started...")
    from threading import Thread
    Thread(target=main).start()
    bot.polling(none_stop=True)
