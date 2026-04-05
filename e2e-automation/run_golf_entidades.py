"""
run_golf_entidades.py
---------------------
Automatización E2E para navegar la ruta:
  Inicio → (login si es necesario) → Menú hamburguesa → Golf → Maestros → Entidades → Entidades

Uso:
    python run_golf_entidades.py

Requiere:
    - Archivo .env (copia de .env.example) con las credenciales reales.
    - Playwright instalado: playwright install chromium
"""

import sys
from pathlib import Path
# Asegura que Python pueda importar módulos del mismo directorio que este script (config.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def screenshot(page: Page, name: str) -> None:
    """Guarda una captura de pantalla con marca de tiempo."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{name}.png"
    page.screenshot(path=str(filepath))
    print(f"  📸  Captura guardada: {filepath.name}")


def wait_and_click(page: Page, selectors: list[str], description: str, timeout: int | None = None) -> None:
    """
    Intenta hacer clic en el primer selector que se encuentre disponible.

    Args:
        page:        Instancia de Playwright Page.
        selectors:   Lista de selectores CSS/XPath/texto a probar en orden.
        description: Descripción legible del elemento (para logs).
        timeout:     Tiempo máximo de espera en ms (usa config.TIMEOUT_MS si es None).
    """
    t = timeout or config.TIMEOUT_MS
    last_error: Exception | None = None

    for sel in selectors:
        try:
            locator = page.locator(sel).first
            locator.wait_for(state="visible", timeout=t)
            locator.click()
            print(f"  ✅  Clic en '{description}' usando selector: {sel}")
            return
        except (PlaywrightTimeoutError, Exception) as exc:
            last_error = exc
            continue

    raise RuntimeError(
        f"No se pudo hacer clic en '{description}'. "
        f"Selectores probados: {selectors}. "
        f"Último error: {last_error}"
    )


def element_exists(page: Page, selector: str, timeout: int = 3000) -> bool:
    """Devuelve True si el selector está visible en la página dentro del timeout."""
    try:
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


# ---------------------------------------------------------------------------
# Pasos del flujo
# ---------------------------------------------------------------------------

def handle_login(page: Page) -> None:
    """
    Detecta si la página pide login y, en ese caso, ingresa las credenciales.

    Selectores de login: se prueban varias estrategias.  Ajustar si el HTML
    usa otros nombres de campo.  Los más comunes están cubiertos abajo.
    """
    login_selectors = [
        "input[name='username']",
        "input[name='user']",
        "input[name='login']",
        "input[id='username']",
        "input[id='user']",
        "input[type='text'][placeholder*='usu' i]",
        "input[type='text'][placeholder*='user' i]",
        "input[autocomplete='username']",
    ]

    password_selectors = [
        "input[name='password']",
        "input[name='pass']",
        "input[id='password']",
        "input[id='pass']",
        "input[type='password']",
        "input[autocomplete='current-password']",
    ]

    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Ingresar')",
        "button:has-text('Entrar')",
        "button:has-text('Login')",
        "button:has-text('Iniciar sesión')",
        "a:has-text('Ingresar')",
    ]

    # Verificar si hay un campo de usuario visible
    username_visible = any(element_exists(page, s, timeout=3000) for s in login_selectors)

    if not username_visible:
        print("  ℹ️   No se detectó pantalla de login – se continúa con la sesión activa.")
        return

    print("  🔐  Pantalla de login detectada. Ingresando credenciales…")

    if not config.APP_USERNAME or not config.APP_PASSWORD:
        raise ValueError(
            "APP_USERNAME o APP_PASSWORD no están definidos. "
            "Copia .env.example como .env y completa los valores."
        )

    # Completar usuario
    for sel in login_selectors:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_USERNAME)
            print(f"    Usuario ingresado en: {sel}")
            break

    # Completar contraseña
    for sel in password_selectors:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_PASSWORD)
            print("    Contraseña ingresada.")
            break

    screenshot(page, "01_before_login")

    # Enviar formulario
    wait_and_click(page, submit_selectors, "botón de login")

    # Esperar a que la página de login desaparezca o la URL cambie
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    print("  ✅  Login completado.")
    screenshot(page, "02_after_login")


def click_hamburger_menu(page: Page) -> None:
    """
    Hace clic en el botón de menú tipo 'hamburguesa' (tres rayas).
    """
    selectors = [
        # ✅ Selectores basados en tu DOM real (recomendado)
        "css=div.toggle.menu",  # contenedor del menú
        "css=div.toggle.menu svg",  # el ícono en sí

        # Si tu header tiene una estructura estable, puedes subir un nivel:
        "css=div.header div.toggle.menu",
        "css=app-ui-header div.toggle.menu",

        # (Deja tus fallbacks anteriores por si cambia el HTML)
        "[aria-label='menu' i]",
        "[aria-label='menú' i]",
        "[aria-label='toggle menu' i]",
        "[aria-label='open menu' i]",
        "[aria-label='hamburger' i]",
        ".hamburger",
        ".menu-toggle",
        ".navbar-toggle",
        ".burger",
        ".nav-toggle",
        "button:has(svg[data-icon='bars'])",
        "button:has(.fa-bars)",
        "button[title*='menu' i]",
        "button[title*='menú' i]",
        "button:has(span + span + span)",
        "header button",
        "nav button",
        ".navbar button",
    ]

    wait_and_click(page, selectors, "menú hamburguesa")

    page.locator(":text('Golf'), [aria-label='Golf'], [title='Golf']").first.wait_for(
        state="visible", timeout=config.TIMEOUT_MS
    )
    screenshot(page, "03_hamburger_opened")


def click_menu_option(page: Page, option_text: str, step_name: str) -> None:
    """
    Hace clic en una opción de menú usando su texto.

    Estrategia multi-selector: texto exacto, texto parcial, aria-label.
    """
    selectors = [
        f"text='{option_text}'",
        f"text=\"{option_text}\"",
        f":text-is('{option_text}')",
        f"a:has-text('{option_text}')",
        f"li:has-text('{option_text}')",
        f"button:has-text('{option_text}')",
        f"span:has-text('{option_text}')",
        f"[aria-label='{option_text}']",
        f"[title='{option_text}']",
    ]
    wait_and_click(page, selectors, option_text)
    # Esperar que la red se estabilice tras el clic (submenús / navegación)
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    screenshot(page, step_name)


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------

def run() -> None:
    print("\n" + "=" * 60)
    print("  Automatización E2E – Golf > Maestros > Entidades")
    print("=" * 60)
    print(f"  URL base : {config.BASE_URL}")
    print(f"  Headless : {config.HEADLESS}")
    print(f"  Timeout  : {config.TIMEOUT_MS} ms")
    print("=" * 60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=300,      # 300 ms entre acciones → el usuario puede ver cada paso
            args=["--start-maximized"],
        )

        context = browser.new_context(
            viewport=None,    # usa el tamaño máximo de la ventana
            ignore_https_errors=True,
        )
        context.set_default_timeout(config.TIMEOUT_MS)

        page = context.new_page()

        try:
            # ── Paso 1: Abrir la URL ──────────────────────────────────────
            print("▶ Paso 1: Abriendo la URL…")
            page.goto(config.BASE_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            screenshot(page, "00_home")
            print(f"  ✅  Página cargada: {page.url}\n")

            # ── Paso 2: Login si es necesario ─────────────────────────────
            print("▶ Paso 2: Verificando si se requiere login…")
            handle_login(page)
            print()

            # ── Paso 3: Clic en menú hamburguesa ─────────────────────────
            print("▶ Paso 3: Abriendo menú hamburguesa…")
            click_hamburger_menu(page)
            print()

            # ── Paso 4: Elegir Golf ───────────────────────────────────────
            print("▶ Paso 4: Haciendo clic en 'Golf'…")
            click_menu_option(page, "Golf", "04_golf_selected")
            print()

            # ── Paso 5: Elegir Maestros ───────────────────────────────────
            print("▶ Paso 5: Haciendo clic en 'Maestros'…")
            click_menu_option(page, "Maestros", "05_maestros_selected")
            print()

            # ── Paso 6: Elegir Entidades (primera vez) ────────────────────
            print("▶ Paso 6: Haciendo clic en 'Entidades'…")
            click_menu_option(page, "Entidades", "06_entidades_1_selected")
            print()

            # ── Paso 7: Elegir Entidades (segunda vez – pantalla final) ───
            print("▶ Paso 7: Haciendo clic en 'Entidades' (pantalla final)…")
            click_menu_option(page, "Entidades", "07_entidades_final")
            print()

            # ── Fin ───────────────────────────────────────────────────────
            print("=" * 60)
            print("  ✅  Flujo completado con éxito.")
            print(f"  📁  Capturas guardadas en: {config.SCREENSHOTS_DIR}")
            print("=" * 60 + "\n")

            # Pausa final para que el usuario vea la pantalla resultante
            print("  Presiona ENTER para cerrar el navegador…")
            input()

        except Exception as exc:
            screenshot(page, "ERROR")
            print(f"\n  ❌  Error durante la automatización: {exc}", file=sys.stderr)
            raise

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    run()
