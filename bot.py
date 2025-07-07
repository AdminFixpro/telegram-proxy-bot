from telethon import TelegramClient, events
import re, json, time, socket
import requests
from scraper_github import scrape_proxies_from_all_github

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

api_id = config["API_ID"]
api_hash = config["API_HASH"]
channel_username = config["CHANNEL_USERNAME"]
group_id = config["GROUP_ID"]

client = TelegramClient('telethon_session', api_id, api_hash)

proxy_sources = [
    "https://mtpro.xyz/api/?type=mtproto",
    "https://proxymtproto.ru/api",
    "https://mtpro.pro/api?type=mtproto",
]

def log(message):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def parse_proxy_info(proxy_link):
    from urllib.parse import urlparse, parse_qs
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
    pattern_link = re.compile(r"(tg://proxy\\?[^ \"'\\n<]+)")
    matches = pattern_link.findall(text)
    if matches:
        return matches

    pattern_server = re.search(r"server[:= ]+([\w\.\-]+)", text, re.I)
    pattern_port = re.search(r"port[:= ]+(\d+)", text, re.I)
    pattern_secret = re.search(r"secret[:= ]+([a-fA-F0-9]+)", text, re.I)
    if pattern_server and pattern_port and pattern_secret:
        server = pattern_server.group(1)
        port = pattern_port.group(1)
        secret = pattern_secret.group(1)
        return [build_tg_link(server, port, secret)]

    return []

async def send_proxy(proxy_link):
    server, port, secret = parse_proxy_info(proxy_link)
    message = (
        f"🔥 New MTProto Proxy Found!\n\n"
        f"server: `{server}`\n"
        f"port: `{port}`\n"
        f"secret: `{secret}`"
    )
    await client.send_message(channel_username, message, parse_mode="markdown", buttons=[[
        {"text": "Connect 🔥", "url": proxy_link}
    ]])

async def process_proxies(proxy_list, min_count=300):
    sent = 0
    with open("sent_proxies.txt", "a+", encoding="utf-8") as f:
        f.seek(0)
        sent_before = set(line.strip() for line in f.readlines())

    for proxy in proxy_list:
        if proxy in sent_before:
            continue
        server, port, secret = parse_proxy_info(proxy)
        if server and port and secret and check_proxy_alive(server, port):
            await send_proxy(proxy)
            with open("sent_proxies.txt", "a", encoding="utf-8") as f:
                f.write(proxy + "\n")
            log(f"✅ Sent proxy: {server}:{port}")
            sent += 1
            time.sleep(1)
        if sent >= min_count:
            break
    log(f"✅ Cycle finished: Sent {sent}/{min_count}")

async def scraping_cycle():
    while True:
        log("🔍 Gathering proxies...")
        proxies_api = []
        for url in proxy_sources:
            try:
                resp = requests.get(url, timeout=10)
                data = resp.json()
                proxies = [item['link'] for item in data if 'link' in item]
                proxies_api.extend(proxies)
                log(f"✅ Fetched {len(proxies)} from {url}")
            except Exception as e:
                log(f"⚠️ Error fetching from {url}: {e}")
        proxies_github = scrape_proxies_from_all_github()
        all_proxies = list(set(proxies_api + proxies_github))
        await process_proxies(all_proxies, min_count=300)
        log("✅ Waiting 3 hours...")
        time.sleep(10800)

@client.on(events.NewMessage(chats=group_id))
async def handler(event):
    text = event.message.message
    proxies = extract_proxy_from_text(text)
    for proxy in proxies:
        server, port, secret = parse_proxy_info(proxy)
        if server and port and secret and check_proxy_alive(server, port):
            await send_proxy(proxy)
            with open("sent_proxies.txt", "a", encoding="utf-8") as f:
                f.write(proxy + "\n")
            log(f"✅ Sent proxy from group: {server}:{port}")

async def main():
    await client.start()
    client.loop.create_task(scraping_cycle())
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("🚀 Telethon bot started... listening and scraping.")
    import asyncio
    asyncio.run(main())
