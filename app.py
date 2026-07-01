import os
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://sistemas.policia.gob.pe/lunasoscurecidas/solicitud_menu.aspx"

PNP_DNI = os.getenv("PNP_USERNAME")
PNP_PASSWORD = os.getenv("PNP_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))

last_alert = None


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }, timeout=20)


def check_once():
    global last_alert

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)

            page.get_by_label("Tipo Documento").select_option("1")
            page.get_by_role("textbox", name="Nro. Documento").fill(PNP_DNI)
            page.get_by_role("textbox", name="Clave").fill(PNP_PASSWORD)
            page.get_by_role("button", name="Ingresar").click()

            page.wait_for_selector("#MainContent_gvProgramacion_btnAccion_0", timeout=60000)
            page.locator("#MainContent_gvProgramacion_btnAccion_0").click()

            page.get_by_role("button", name="Reservar Cita").click()
            page.wait_for_selector("#MainContent_idUcitas_cbosede", timeout=30000)

            page.locator("#MainContent_idUcitas_cbosede").select_option("1")
            page.wait_for_timeout(5000)

            fecha = page.locator("#MainContent_idUcitas_cbofecha").inner_text(timeout=30000)
            hora = page.locator("#MainContent_idUcitas_cbohora").inner_text(timeout=30000)
            cupos = page.locator("#MainContent_idUcitas_txtcupos").input_value(timeout=30000)

            print("Fecha:", fecha)
            print("Hora:", hora)
            print("Cupos:", cupos)

            texto = f"{fecha} | {hora} | {cupos}"

            if "Sin Cupos" not in texto:
                if texto != last_alert:
                    last_alert = texto
                    send_telegram(
                        "🚨 ¡PUEDE HABER CUPOS DISPONIBLES!\n\n"
                        "📍 Sede: LIMA - LA VICTORIA\n"
                        f"📅 Fecha: {fecha}\n"
                        f"🕐 Hora: {hora}\n"
                        f"👥 Cupos: {cupos}\n\n"
                        "Entra al sistema de la PNP ahora."
                    )
            else:
                print("Sin cupos por ahora.")

        except PlaywrightTimeoutError as e:
            print("Timeout:", e)
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()


def main():
    send_telegram("✅ Bot de lunas polarizadas iniciado.")
    while True:
        check_once()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
