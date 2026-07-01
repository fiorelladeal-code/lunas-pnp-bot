import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("TOKEN:", TOKEN[:10] + "..." if TOKEN else "NO TOKEN", flush=True)
print("CHAT_ID:", CHAT_ID, flush=True)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "🚀 Prueba desde Railway"
    }
)

print("STATUS:", r.status_code, flush=True)
print("RESPUESTA:", r.text, flush=True)
