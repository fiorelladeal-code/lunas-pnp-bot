import os, time, requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = "https://sistemas.policia.gob.pe/lunasoscurecidas/solicitud_menu.aspx"

PNP_USERNAME = os.getenv("PNP_USERNAME")
PNP_PASSWORD = os.getenv("PNP_PASSWORD")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "120"))

ya_aviso = False


def avisar(texto):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": texto},
        timeout=20,
    )
    print("Telegram:", r.status_code, r.text, flush=True)


def revisar():
    global ya_aviso

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()

        try:
            print("Abriendo PNP...", flush=True)
         page.goto(
    URL,
    wait_until="load",
    timeout=120000
)

            page.get_by_label("Tipo Documento").select_option("1")
            page.get_by_role("textbox", name="Nro. Documento").fill(PNP_USERNAME)
            page.get_by_role("textbox", name="Clave").fill(PNP_PASSWORD)
            page.get_by_role("button", name="Ingresar").click()

            print("Esperando expediente...", flush=True)
            page.wait_for_selector("#MainContent_gvProgramacion_btnAccion_0", timeout=60000)
            page.locator("#MainContent_gvProgramacion_btnAccion_0").click()

            print("Entrando a reservar cita...", flush=True)
            page.get_by_role("button", name="Reservar Cita").click()

            page.wait_for_selector("#MainContent_idUcitas_cbosede", timeout=30000)
            page.locator("#MainContent_idUcitas_cbosede").select_option("1")

            time.sleep(5)

            body = page.inner_text("body")
            print("Texto detectado:", body[:1000], flush=True)

            if "Sin Cupos" in body:
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

        except PWTimeout as e:
            print("TIMEOUT:", e, flush=True)
        except Exception as e:
            print("ERROR:", e, flush=True)
        finally:
            browser.close()


def main():
    print("Bot PNP iniciado", flush=True)
    avisar("✅ Bot PNP iniciado. Revisaré cupos cada 2 minutos.")

    while True:
        revisar()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
