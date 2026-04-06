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
    "app-ui-menu-item",                        # componente Angular del ítem
    "app-ui-menu-item span",                   # texto dentro del componente
    "app-ui-menu-item .menu-item-label",       # label si existe
    ".menu-list app-ui-menu-item",
    ".nav-menu li",
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

def is_menu_open(page: Page) -> bool:
    """Devuelve True si el menú ya está desplegado (div.ui-menu-item visible)."""
    try:
        page.locator("div.ui-menu-item").first.wait_for(state="visible", timeout=2000)
        return True
    except PlaywrightTimeoutError:
        return False


def ensure_menu_open(page: Page) -> None:
    """
    Abre el menú hamburguesa SOLO si no está ya abierto.
    Evita el efecto toggle (doble clic = cierra el menú).
    """
    if is_menu_open(page):
        print("  ℹ️   Menú ya está abierto – no se vuelve a clickear hamburguesa.")
        return
    print("  🍔  Abriendo menú hamburguesa…")
    wait_and_click(page, HAMBURGER_SELECTORS, "menú hamburguesa")
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    try:
        page.locator("div.ui-menu-item").first.wait_for(state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        print("  ⚠️   Menú abierto pero div.ui-menu-item no apareció.")




TARGET_MENU_ITEMS = ["Golf", "Participes LATAM", "FrontOn Gestión"]


def click_target_menu_items(page: Page) -> None:
    """
    Hace clic en cada opción específica del menú.

    Estructura DOM confirmada:
        DIV.ui-menu-item   ← clickeable (cursor:pointer, pointer-events:auto)
          DIV.label
            DIV.text.xl
              "Golf" | "Participes LATAM" | "FrontOn Gestión"
    """
    for item_text in TARGET_MENU_ITEMS:
        print(f"\n▶ Clickeando opción de menú → '{item_text}'")

        # Abrir menú solo si no está ya abierto
        ensure_menu_open(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

        # Selector: div.ui-menu-item que contenga el texto en su div.text.xl hijo
        # has_text es tolerante a espacios — perfecto para este DOM Angular
        loc = page.locator("div.ui-menu-item", has_text=item_text).first

        try:
            loc.wait_for(state="visible", timeout=5000)
            screenshot(page, f"menu_antes__{item_text.replace(' ', '_')}")
            loc.click()
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            print(f"  ✅  Clic exitoso en '{item_text}'")
        except Exception as exc:
            print(f"  ❌  No se pudo hacer clic en '{item_text}': {exc}")
            screenshot(page, f"ERROR__{item_text.replace(' ', '_')}")
            continue

        # Captura + DOM tras el clic
        safe = item_text.replace(" ", "_")
        screenshot(page, f"menu_clic__{safe}")
        dump_dom(page, f"dom_clic__{safe}")

        # Volver atrás para el siguiente ítem
        print(f"  ↩️   Volviendo atrás desde '{item_text}'…")
        page.go_back(wait_until="networkidle", timeout=config.TIMEOUT_MS)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

# ---------------------------------------------------------------------------
# Captura de submenús de primer nivel (con X para cerrar)
# ---------------------------------------------------------------------------

ITEMS_NIVEL1 = ["Golf", "Participes LATAM", "FrontOn Gestión"]


def capturar_submenus_nivel1(page: Page) -> None:
    """
    Para cada opción del menú principal:
      1. Abre el menú principal con ensure_menu_open()
      2. Hace clic en el ítem (Golf / Participes LATAM / FrontOn Gestión)
      3. Espera a que aparezca el submenú
      4. Toma screenshot + dump DOM
      5. Cierra el submenú con la X (vuelve al menú principal)
    """
    for item_text in ITEMS_NIVEL1:
        print(f"\n{'='*50}")
        print(f"▶ Abriendo submenú de: '{item_text}'")
        print(f"{'='*50}")

        # 1. Asegurar que el menú principal está abierto
        ensure_menu_open(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

        # 2. Clic en el ítem del menú principal
        loc = page.locator("div.ui-menu-item", has_text=item_text).first
        try:
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            print(f"  ✅  Clic en '{item_text}'")
        except Exception as exc:
            print(f"  ❌  No se pudo hacer clic en '{item_text}': {exc}")
            screenshot(page, f"ERROR_nivel1_{item_text.replace(' ', '_')}")
            continue

        # 3. Esperar a que aparezca el submenú
        #    (aún no sabemos el selector exacto — esperamos networkidle + pausa)
        page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
        page.wait_for_timeout(800)  # pausa para que Angular termine de renderizar

        # 4. Capturar screenshot + DOM del submenú
        safe = item_text.replace(" ", "_")
        screenshot(page, f"submenu_nivel1__{safe}")
        dump_dom(page, f"dom_submenu_nivel1__{safe}")
        print(f"  📸  Submenú de '{item_text}' capturado.")

        # 5. Cerrar con la X — aún no sabemos el selector exacto
        #    Intentamos selectores comunes para un botón de cerrar
        close_selectors = [
            "button.close", "button[aria-label='close' i]",
            "button[aria-label='cerrar' i]", ".close-button",
            "span.close", "div.close", "i.fa-times", "i.fa-xmark",
            "svg[data-icon='xmark']", "svg[data-icon='times']",
            ".menu-back", "[class*='close']", "[class*='back']",
        ]
        closed = False
        for sel in close_selectors:
            try:
                btn = page.locator(sel).first
                btn.wait_for(state="visible", timeout=2000)
                btn.click()
                page.wait_for_timeout(500)
                print(f"  ✖️   Submenú cerrado con selector: {sel}")
                closed = True
                break
            except Exception:
                continue

        if not closed:
            print(f"  ⚠️   No se encontró la X para cerrar — revisar DOM capturado.")
            print(f"        Buscar en: dom_submenu_nivel1__{safe}.html")
            # Forzar recarga para volver al estado inicial
            page.goto(config.BASE_URL, wait_until="networkidle")
            handle_login(page)

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
        safe_name = path_str.replace(" > ", "__").replace(" ", "_")[:MAX__FILENAME_LENGTH]
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

            #print("▶ Paso 4: Clickeando las tres opciones objetivo del menú…\n")
            #click_target_menu_items(page)

            print("▶ Paso 4: Capturando submenús de primer nivel…\n")
            capturar_submenus_nivel1(page)

            # Opcional: mantener el recorrido dinámico completo también
            # print("▶ Paso 5: Recorrido dinámico completo del menú…\n")
            # open_hamburger_menu(page)
            # traverse_menu(page, [], discovered_paths, depth=0)

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
