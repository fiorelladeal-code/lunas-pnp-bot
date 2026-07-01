import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("Bot arrancó correctamente", flush=True)
print("CHAT_ID configurado:", CHAT_ID, flush=True)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

try:
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": "✅ Prueba exitosa: Railway ya puede enviarte mensajes por Telegram."
    }, timeout=20)

    print("Telegram status:", r.status_code, flush=True)
    print("Telegram response:", r.text, flush=True)

except Exception as e:
    print("Error enviando Telegram:", e, flush=True)

while True:
    print("Bot vivo", flush=True)
    time.sleep(60)
