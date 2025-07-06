import requests
import re
import html

def scrape_proxies_from_channels():
    urls = [
        "https://t.me/s/mtpro_xyz",
        "https://t.me/s/Proxy_Daemi",
        "https://t.me/s/proxy_active",
        "https://t.me/s/ProxyMTProto",
        "https://mtpro.xyz",
        "https://github.com/TelegramMessenger/MTProxy",
        "https://raw.githubusercontent.com/ALIILAPRO/MTProtoProxy/main/mtproto.txt",
        "https://raw.githubusercontent.com/alexvarboffin/MTProto-List/master/proxy.json"
        "https://mtpro.xyz/mtproto"
    ]

    all_proxies = []
    pattern = re.compile(r"(tg://proxy\?[^\"\'\s<]+)")

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            text = response.text
            matches = pattern.findall(text)
            for m in matches:
                decoded = html.unescape(m)
                all_proxies.append(decoded)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return list(set(all_proxies))
