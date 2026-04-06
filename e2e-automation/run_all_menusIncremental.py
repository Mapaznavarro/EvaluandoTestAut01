"""
run_all_menus.py
----------------
Automatización E2E que recorre TODAS las opciones del menú de la aplicación.

(Actualización solicitada)
- NO recursividad.
- Hace clic SOLO en 3 opciones visibles: "Golf", "Participes LATAM", "FrontOn Gestión".
- Después de cada clic toma captura (PNG) y guarda el DOM (HTML).
"""

import sys
import datetime
from datetime import timezone
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

import config

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

MENU_CONTAINER_SELECTORS = [
    "css=div.toggle.menu",
    "css=app-ui-header div.toggle.menu",
    "nav",
    ".sidebar",
    ".menu",
    "[role='navigation']",
    "[role='menu']",
    "[role='menubar']",
]

MENU_ITEM_SELECTORS = [
    "[role='menuitem']",
    "[role='option']",
    "nav a",
    "nav li > a",
    "nav li > button",
    "nav li > span",
    "ul.menu li",
    ".sidebar-item",
    ".menu-item",
    "li.nav-item a",
]

# Longitud máxima del nombre de archivo para capturas de pantalla
MAX_SCREENSHOT_FILENAME_LENGTH = 80  # <-- FIX: antes estaba mal nombrada en el script

# Pausa (ms) antes de re-abrir el menú tras navegar un ítem
MENU_REOPEN_DELAY_MS = 500

# Velocidad de slow_mo del navegador (ms entre acciones)
BROWSER_SLOW_MO_MS = 300

# Opciones EXACTAS a clicar (en orden)
MENU_OPTIONS_TO_CLICK = ["Golf", "Participes LATAM", "FrontOn Gestión"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def screenshot(page: Page, name: str) -> None:
    """Guarda una captura de pantalla con marca de tiempo."""
    ts = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{name}.png"
    page.screenshot(path=str(filepath))
    print(f"  📸  Captura guardada: {filepath.name}")


def dump_dom(page: Page, name: str = "dom") -> Path:
    """Guarda el DOM actual (HTML) en un archivo .html."""
    ts = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name).strip("_")
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{safe}.html"

    html = page.content()
    filepath.write_text(html, encoding="utf-8")

    print(f"  🧾  DOM guardado: {filepath.name}")
    return filepath


def element_exists(page: Page, selector: str, timeout: int = 3000) -> bool:
    """Devuelve True si el selector está visible dentro del timeout."""
    try:
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


def wait_and_click(page: Page, selectors: list[str], description: str, timeout: int | None = None) -> None:
    """Intenta hacer clic en el primer selector disponible de la lista."""
    t = timeout or config.TIMEOUT_MS
    last_error: Exception | None = None

    for sel in selectors:
        try:
            locator = page.locator(sel).first
            locator.wait_for(state="visible", timeout=t)
            locator.click()
            print(f"  ✅  Clic en '{description}' usando: {sel}")
            return
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(
        f"No se pudo hacer clic en '{description}'. "
        f"Selectores probados: {selectors}. "
        f"Último error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def handle_login(page: Page) -> None:
    """Detecta y maneja la pantalla de login si es necesario."""
    login_selectors = [
        "input[name='username']", "input[name='user']", "input[name='login']",
        "input[id='username']", "input[id='user']",
        "input[type='text'][placeholder*='usu' i]",
        "input[type='text'][placeholder*='user' i]",
        "input[autocomplete='username']",
    ]
    password_selectors = [
        "input[name='password']", "input[name='pass']",
        "input[id='password']", "input[id='pass']",
        "input[type='password']", "input[autocomplete='current-password']",
    ]
    submit_selectors = [
        "button[type='submit']", "input[type='submit']",
        "button:has-text('Ingresar')", "button:has-text('Entrar')",
        "button:has-text('Login')", "button:has-text('Iniciar sesión')",
        "a:has-text('Ingresar')",
    ]

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

    for sel in login_selectors:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_USERNAME)
            break

    for sel in password_selectors:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_PASSWORD)
            break

    screenshot(page, "01_before_login")
    wait_and_click(page, submit_selectors, "botón de login")
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    print("  ✅  Login completado.")
    screenshot(page, "02_after_login")


# ---------------------------------------------------------------------------
# Apertura del menú hamburguesa
# ---------------------------------------------------------------------------

HAMBURGER_SELECTORS = [
    "css=div.toggle.menu",
    "css=div.toggle.menu svg",
    "css=div.header div.toggle.menu",
    "css=app-ui-header div.toggle.menu",
    "[aria-label='menu' i]", "[aria-label='menú' i]",
    "[aria-label='toggle menu' i]", "[aria-label='open menu' i]",
    "[aria-label='hamburger' i]",
    ".hamburger", ".menu-toggle", ".navbar-toggle", ".burger", ".nav-toggle",
    "button:has(svg[data-icon='bars'])", "button:has(.fa-bars)",
    "button[title*='menu' i]", "button[title*='menú' i]",
    "header button", "nav button", ".navbar button",
]


def open_hamburger_menu(page: Page) -> None:
    """Abre el menú hamburguesa y espera estado estable."""
    wait_and_click(page, HAMBURGER_SELECTORS, "menú hamburguesa")
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)


# ---------------------------------------------------------------------------
# Click por texto (opciones específicas)
# ---------------------------------------------------------------------------


def click_item_by_text(page: Page, text: str) -> None:
    """
    Hace clic en el elemento del menú que contiene el texto dado.
    Lanza excepción si no lo puede clicar (para cumplir el flujo exacto).
    """
    selectors = [
        f":text-is('{text}')",
        f"text='{text}'",
        f"[role='menuitem']:has-text('{text}')",
        f"a:has-text('{text}')",
        f"li:has-text('{text}')",
        f"button:has-text('{text}')",
        f"span:has-text('{text}')",
        f"[aria-label='{text}']",
        f"[title='{text}']",
    ]

    last_error: Exception | None = None
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=config.TIMEOUT_MS)
            loc.click()
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            print(f"  ✅  Clic en opción de menú: {text} (selector: {sel})")
            return
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"No se pudo hacer clic en la opción '{text}'. Último error: {last_error}")


def run_click_only_three_menu_options(page: Page) -> None:
    """
    NO recursivo.
    Abre el menú y hace clic en: Golf, Participes LATAM, FrontOn Gestión.
    Después de cada clic: screenshot + dump_dom.
    """
    # Asegura que el menú esté abierto antes de empezar
    open_hamburger_menu(page)
    screenshot(page, "03_menu_abierto")
    dump_dom(page, "dom-menu-abierto")

    for idx, label in enumerate(MENU_OPTIONS_TO_CLICK, start=1):
        print(f"\n▶ Opción {idx}/{len(MENU_OPTIONS_TO_CLICK)}: {label}")

        url_before = page.url

        # (re)abrir menú por si se cerró
        open_hamburger_menu(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

        click_item_by_text(page, label)

        safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", label).strip("_")[:MAX_SCREENSHOT_FILENAME_LENGTH]
        screenshot(page, f"menu_click_{idx:02d}__{safe}")
        dump_dom(page, f"dom_click_{idx:02d}__{safe}")

        # volver si navegó a otra URL (para que las siguientes opciones sigan disponibles)
        if page.url != url_before:
            page.go_back(wait_until="networkidle", timeout=config.TIMEOUT_MS)


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------


def run() -> None:
    print("\n" + "=" * 60)
    print("  Automatización E2E – Click de 3 opciones de menú (sin recursividad)")
    print("=" * 60)
    print(f"  URL base  : {config.BASE_URL}")
    print(f"  Headless  : {config.HEADLESS}")
    print(f"  Timeout   : {config.TIMEOUT_MS} ms")
    print(f"  Capturas  : {config.SCREENSHOTS_DIR}")
    print("=" * 60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=BROWSER_SLOW_MO_MS,
            args=["--start-maximized"],
        )
        context = browser.new_context(
            viewport=None,
            ignore_https_errors=True,
        )
        context.set_default_timeout(config.TIMEOUT_MS)
        page = context.new_page()

        try:
            print("▶ Paso 1: Abriendo la URL…")
            page.goto(config.BASE_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            screenshot(page, "00_home")
            print(f"  ✅  Página cargada: {page.url}\n")

            print("▶ Paso 2: Verificando login…")
            handle_login(page)
            dump_dom(page, "dom-after-login")
            print()

            print("▶ Paso 3: Click en 3 opciones del menú (sin recursividad)…")
            run_click_only_three_menu_options(page)

            print("\n" + "=" * 60)
            print("  ✅  Finalizado: se hizo clic en Golf, Participes LATAM y FrontOn Gestión.")
            print("=" * 60)

            print("\n  Presiona ENTER para cerrar el navegador…")
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
