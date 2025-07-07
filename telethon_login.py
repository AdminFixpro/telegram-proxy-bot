from telethon.sync import TelegramClient

api_id = '24014199'    # << اینو با api_id خودت عوض کن
api_hash = "915cd861a86b04242ad1cad614e82e31"

with TelegramClient("telethon_session", api_id, api_hash) as client:
    print("✅ Logged in successfully. Session file saved.")
