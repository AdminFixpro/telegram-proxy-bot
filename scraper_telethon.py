from telethon.sync import TelegramClient
import re
import html

api_id = 24014199  # << اینو با api_id خودت عوض کن
api_hash = "915cd861a86b04242ad1cad614e82e31"

channels = [
    "@mtpro_xyz",
    "@Proxy_Daemi",
    "@proxy_active",
    "@ProxyMTProto",
    "@mtproxyx",
    "@Mtproxys",
    "@mtprx",
    "@MTProxyStar",
    "@MTProtoProxyChannel",
    "@MTProtoProxyfree",
    "@BestMTProtoProxy",
    "@FreeMTProtoProxy",
    "@FastMTProtoProxy",
    "@MTProto_Proxy",
    "@MTProtoProxies"
]

def scrape_proxies_from_telegram():
    all_proxies = []
    pattern = re.compile(r"(tg://proxy\?[^\"\'\s]+)")

    with TelegramClient("telethon_session", api_id, api_hash, connection_retries=10, timeout=30, use_ipv6=False) as client:
        for channel in channels:
            try:
                for message in client.iter_messages(channel, limit=100):
                    if message.text:
                        matches = pattern.findall(message.text)
                        for m in matches:
                            decoded = html.unescape(m)
                            all_proxies.append(decoded)
                print(f"✅ Found {len(all_proxies)} proxies from {channel}")
            except Exception as e:
                print(f"❌ Error scraping {channel}: {e}")

    return list(set(all_proxies))