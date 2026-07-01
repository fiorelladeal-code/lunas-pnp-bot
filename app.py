import os
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://sistemas.policia.gob.pe/lunasoscurecidas/solicitud_menu.aspx"

PNP_USERNAME = os.getenv("PNP_USERNAME")
PNP_PASSWORD = os.getenv("PNP_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))


def avisar(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=20)


def revisar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)

            page.get_by_label("Tipo Documento").select_option("1")
            page.get_by_role("textbox", name="Nro. Documento").fill(PNP_USERNAME)
            page.get_by_role("textbox", name="Clave").fill(PNP_PASSWORD)
            page.get_by_role("button", name="Ingresar").click()

            page.wait_for_selector("#MainContent_gvProgramacion_btnAccion_0", timeout=60000)
            page.locator("#MainContent_gvProgramacion_btnAccion_0").click()

            page.get_by_role("button", name="Reservar Cita").click()
            page.wait_for_selector("#MainContent_idUcitas_cbosede", timeout=30000)

            page.locator("#MainContent_idUcitas_cbosede").select_option("1")
            page.wait_for_timeout(5000)

            contenido = page.inner_text("body")

            print(contenido)

            if "Sin Cupos" not in contenido:
                avisar("🚨 ¡Puede haber cupos para lunas polarizadas en LIMA - LA VICTORIA! Entra al sistema ahora.")
            else:
                print("Sin cupos.")

        except Exception as e:
            print("ERROR:", e)

        finally:
            browser.close()


def main():
    avisar("✅ Bot iniciado. Revisando cupos cada 2 minutos.")
    while True:
        revisar()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
