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

ya_aviso = False


def avisar(mensaje):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje},
            timeout=20,
        )
        print("Telegram:", r.status_code, r.text, flush=True)
    except Exception as e:
        print("Error Telegram:", e, flush=True)


def revisar_cupos():
    global ya_aviso

    print("Abriendo navegador...", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )

        page = browser.new_page()

        try:
            print("Abriendo PNP...", flush=True)

            response = page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=120000,
            )

            print("URL final:", page.url, flush=True)
            print("Título:", page.title(), flush=True)

            if response:
                print("Status PNP:", response.status, flush=True)
            else:
                print("Sin response PNP", flush=True)

            print("Página cargada. Intentando login...", flush=True)

            page.get_by_label("Tipo Documento").select_option("1")
            page.get_by_role("textbox", name="Nro. Documento").fill(PNP_USERNAME)
            page.get_by_role("textbox", name="Clave").fill(PNP_PASSWORD)
            page.get_by_role("button", name="Ingresar").click()

            print("Esperando expediente...", flush=True)

            page.wait_for_selector(
                "#MainContent_gvProgramacion_btnAccion_0",
                timeout=90000,
            )

            page.locator("#MainContent_gvProgramacion_btnAccion_0").click()

            print("Entrando a Reservar Cita...", flush=True)

            page.get_by_role("button", name="Reservar Cita").click()

            page.wait_for_selector(
                "#MainContent_idUcitas_cbosede",
                timeout=60000,
            )

            page.locator("#MainContent_idUcitas_cbosede").select_option("1")

            print("Sede seleccionada. Esperando fechas...", flush=True)

            page.wait_for_timeout(8000)

            texto = page.inner_text("body")

            print("Texto detectado:", texto[:1500], flush=True)

            if "Sin Cupos" in texto:
                print("Sin cupos por ahora.", flush=True)
                ya_aviso = False
            else:
                print("POSIBLE CUPO DETECTADO", flush=True)
                if not ya_aviso:
                    ya_aviso = True
                    avisar(
                        "🚨 ¡POSIBLE CUPO DISPONIBLE!\n\n"
                        "📍 Lunas polarizadas - LIMA LA VICTORIA\n"
                        "Entra ahora al sistema de la PNP para revisar y reservar."
                    )

        except PlaywrightTimeoutError as e:
            print("TIMEOUT:", e, flush=True)

        except Exception as e:
            print("ERROR GENERAL:", e, flush=True)

        finally:
            browser.close()
            print("Navegador cerrado.", flush=True)


def main():
    print("Bot PNP iniciado", flush=True)
    avisar("✅ Bot PNP iniciado. Revisaré cupos cada 2 minutos.")

    while True:
        revisar_cupos()
        print(f"Esperando {CHECK_INTERVAL} segundos...", flush=True)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
