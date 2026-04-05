"""
run_all_menus.py
----------------
Automatización E2E que recorre TODAS las opciones del menú de la aplicación.

Estrategia:
  1. Abre la URL y hace login si es necesario.
  2. Abre el menú hamburguesa.
  3. Descubre dinámicamente los ítems de primer nivel.
  4. Para cada ítem de primer nivel:
       a. Lo hace clic y espera a que aparezcan sub-ítems (o la vista cargue).
       b. Si aparecen sub-ítems, repite el proceso de forma recursiva.
       c. Toma captura en cada nivel.
  5. Al terminar cada rama vuelve al estado inicial (re-abre el menú).
  6. Genera un reporte en texto con el árbol de menú descubierto.

Uso:
    python run_all_menus.py

Requiere:
    - Archivo .env (copia de .env.example) con las credenciales reales.
    - Playwright instalado: playwright install chromium
"""

import sys
import datetime
from datetime import timezone
from pathlib import Path
import re  # <-- AGREGAR

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

import config

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Selector del contenedor donde aparecen los ítems del menú lateral/desplegable
# Ajustar si la app usa otra estructura (ej: "nav ul li", ".sidebar-menu li", etc.)
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

# Selectores de ítems clickeables dentro del menú
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

# Profundidad máxima de recursión para evitar bucles infinitos
MAX_DEPTH = 5

# Longitud máxima del nombre de archivo para capturas de pantalla
MAX__FILENAME_LENGTH = 80

# Pausa (ms) antes de re-abrir el menú tras navegar un ítem
MENU_REOPEN_DELAY_MS = 500

# Velocidad de slow_mo del navegador (ms entre acciones)
BROWSER_SLOW_MO_MS = 300

# ---------------------------------------------------------------------------
# Helpers compartidos con run_golf_entidades.py
# ---------------------------------------------------------------------------


def screenshot(page: Page, name: str) -> None:
    """Guarda una captura de pantalla con marca de tiempo."""
    ts = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{name}.png"
    page.screenshot(path=str(filepath))
    print(f"  📸  Captura guardada: {filepath.name}")

def dump_dom(page: Page, name: str = "dom-after-login") -> Path:
    """
    Guarda el DOM actual (HTML) en un archivo .html.
    """
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
    """Abre el menú hamburguesa y espera a que aparezca algún ítem."""
    wait_and_click(page, HAMBURGER_SELECTORS, "menú hamburguesa")
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)


# ---------------------------------------------------------------------------
# Descubrimiento dinámico del menú
# ---------------------------------------------------------------------------


def get_visible_menu_items(page: Page) -> list[str]:
    """
    Devuelve los textos de los ítems de menú actualmente visibles.

    Recorre varias estrategias de selector hasta encontrar elementos.
    Filtra textos vacíos y duplicados.
    """
    for sel in MENU_ITEM_SELECTORS:
        try:
            locators = page.locator(sel).all()
            texts = []
            for loc in locators:
                try:
                    if loc.is_visible():
                        text = loc.inner_text().strip()
                        if text and text not in texts:
                            texts.append(text)
                except Exception:
                    continue
            if texts:
                return texts
        except Exception:
            continue
    return []


def click_item_by_text(page: Page, text: str) -> bool:
    """
    Hace clic en el elemento del menú que contiene exactamente el texto dado.
    Devuelve True si tuvo éxito, False en caso contrario.
    """
    selectors = [
        f":text-is('{text}')",
        f"text='{text}'",
        f"a:has-text('{text}')",
        f"li:has-text('{text}')",
        f"button:has-text('{text}')",
        f"span:has-text('{text}')",
        f"[aria-label='{text}']",
        f"[title='{text}']",
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible():
                loc.click()
                page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
                return True
        except Exception:
            continue
    return False


# ---------------------------------------------------------------------------
# Recorrido recursivo del árbol de menú
# ---------------------------------------------------------------------------


def traverse_menu(
    page: Page,
    breadcrumb: list[str],
    discovered: list[str],
    depth: int = 0,
) -> None:
    """
    Recorre recursivamente las opciones del menú visible.

    Args:
        page:        Instancia de Playwright Page.
        breadcrumb:  Ruta actual (lista de textos de ítems ya visitados).
        discovered:  Lista acumulada de rutas completas descubiertas.
        depth:       Nivel de profundidad actual (para evitar recursión infinita).
    """
    if depth >= MAX_DEPTH:
        print(f"  ⚠️   Profundidad máxima ({MAX_DEPTH}) alcanzada en: {' > '.join(breadcrumb)}")
        return

    indent = "  " * depth
    items = get_visible_menu_items(page)

    if not items:
        path_str = " > ".join(breadcrumb) if breadcrumb else "(raíz)"
        print(f"{indent}ℹ️   Sin ítems de menú visibles en: {path_str}")
        return

    print(f"{indent}📋  Ítems encontrados en '{' > '.join(breadcrumb) or 'raíz'}': {items}")

    for item_text in items:
        current_path = breadcrumb + [item_text]
        path_str = " > ".join(current_path)

        # Guardar URL de retorno para poder volver después del clic
        url_before = page.url

        print(f"\n{indent}▶  Navegando a: {path_str}")
        success = click_item_by_text(page, item_text)

        if not success:
            print(f"{indent}  ⚠️   No se pudo hacer clic en '{item_text}' – se omite.")
            continue

        # Tomar captura del estado tras el clic
        safe_name = path_str.replace(" > ", "__").replace(" ", "_")[:MAX_SCREENSHOT_FILENAME_LENGTH]
        screenshot(page, f"menu__{safe_name}")
        dump_dom(page, f"dom__{safe_name}")  # <-- OPCIONAL: agrega esto
        discovered.append(path_str)

        # Revisar si aparecieron nuevos sub-ítems (sub-menú expandido)
        new_items = get_visible_menu_items(page)
        # Los sub-ítems son aquellos nuevos que no estaban en el nivel anterior
        sub_items = [i for i in new_items if i not in items]

        if sub_items and depth + 1 < MAX_DEPTH:
            print(f"{indent}  🔽  Sub-ítems detectados: {sub_items}")
            traverse_menu(page, current_path, discovered, depth + 1)

        # Volver al estado anterior para continuar con el siguiente ítem del mismo nivel
        if page.url != url_before:
            page.go_back(wait_until="networkidle", timeout=config.TIMEOUT_MS)

        # Re-abrir el menú si se cerró tras la navegación
        open_hamburger_menu(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)  # pequeña pausa estética


# ---------------------------------------------------------------------------
# Flujo principal
# ---------------------------------------------------------------------------


def run() -> None:
    print("\n" + "=" * 60)
    print("  Automatización E2E – Recorrido completo del menú")
    print("=" * 60)
    print(f"  URL base  : {config.BASE_URL}")
    print(f"  Headless  : {config.HEADLESS}")
    print(f"  Timeout   : {config.TIMEOUT_MS} ms")
    print(f"  Capturas  : {config.SCREENSHOTS_DIR}")
    print("=" * 60 + "\n")

    discovered_paths: list[str] = []

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
            # ── Paso 1: Cargar la URL ──────────────────────────────────────
            print("▶ Paso 1: Abriendo la URL…")
            page.goto(config.BASE_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            screenshot(page, "00_home")
            print(f"  ✅  Página cargada: {page.url}\n")

            # ── Paso 2: Login ─────────────────────────────────────────────
            print("▶ Paso 2: Verificando login…")
            handle_login(page)
            dump_dom(page, "dom-after-login")  # <-- AGREGAR
            print()

            # ── Paso 3: Abrir menú y recorrer ────────────────────────────
            print("▶ Paso 3: Abriendo menú hamburguesa…")
            open_hamburger_menu(page)
            screenshot(page, "03_menu_abierto")
            dump_dom(page, "dom-menu-abierto")  # <-- AGREGAR
            print()

            print("▶ Paso 4: Recorriendo todas las opciones del menú…\n")
            traverse_menu(page, [], discovered_paths, depth=0)

            # ── Reporte final ─────────────────────────────────────────────
            print("\n" + "=" * 60)
            print(f"  ✅  Recorrido completado. {len(discovered_paths)} ruta(s) visitadas.")
            print("=" * 60)
            print("\n  🗺️   Árbol de menú descubierto:")
            for path in discovered_paths:
                depth = path.count(" > ")
                indent = "    " + "  " * depth
                leaf = path.split(" > ")[-1]
                print(f"{indent}• {leaf}  ({path})")

            # Guardar reporte en texto
            report_path = config.SCREENSHOTS_DIR / "menu_report.txt"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"Reporte de menú – {datetime.datetime.now(timezone.utc).isoformat()}\n")
                f.write(f"URL: {config.BASE_URL}\n\n")
                for path in discovered_paths:
                    f.write(path + "\n")
            print(f"\n  📄  Reporte guardado en: {report_path}")
            print(f"  📁  Capturas guardadas en: {config.SCREENSHOTS_DIR}")
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
