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
import csv
import datetime
import json
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

# Pausa (ms) entre clics durante la navegación del menú en PASO 2
MENU_NAVIGATION_DELAY_MS = 600

# Velocidad de slow_mo del navegador (ms entre acciones)
BROWSER_SLOW_MO_MS = 300

# ---------------------------------------------------------------------------
# Selectores para detección y cierre del modal de notificación
# ---------------------------------------------------------------------------

# Contenedores del modal de notificación (en orden de prioridad)
NOTIFICATION_MODAL_SELECTORS = [
    "app-notification-container",
    "div.notification-container",
    "app-notification-slider",
    "div.notification-slider",
    "app-ui-notifications",
    "div.notifications-container",
    "div.notification-panel",
    "div.notifications",
    "div[class*='notification']",
    "[role='alertdialog']",
    "[role='dialog'][class*='notification']",
    "[role='dialog']",
]

# Selectores para leer el tipo de notificación (ej. "Errores", "TypeError")
NOTIFICATION_TYPE_SELECTORS = [
    "div.notification-type", "div.type", "div.title",
    "div.notification-title", ".notification-header",
]

# Selectores para leer el mensaje de la notificación
NOTIFICATION_MESSAGE_SELECTORS = [
    "div.notification-message", "div.message", "div.body",
    "div.notification-body", "div.text", "p.message",
]

# Selectores para cerrar/aceptar la notificación
NOTIFICATION_CLOSE_SELECTORS = [
    "app-notification-container div.close",
    "app-notification-container button",
    "div.notification-slider div.close",
    "div.notification-slider button",
    "app-notification-slider div.close",
    "app-notification-slider button",
    "app-ui-notifications div.close",
    "app-ui-notifications button",
    "app-ui-notifications div.accept",
    "app-ui-notifications div.ok",
    "div.notifications div.close",
    "div.notifications button",
    "div.notification-panel div.close",
    "button:has-text('Aceptar')",
    "button:has-text('OK')",
    "button:has-text('Cerrar')",
    "div.modal div.close",
    "[role='dialog'] div.close",
    "[role='dialog'] button",
    "[role='alertdialog'] button",
]

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


def cerrar_menu_si_abierto(page: Page) -> None:
    """
    Cierra el panel de menú lateral si está abierto haciendo clic fuera del área.
    Esto simula el comportamiento del usuario: clic fuera del menú para cerrarlo.
    """
    # Verificar si el menú está abierto
    menu_abierto = False
    for sel in ["div.ui-menu-item", "div.menu-options"]:
        try:
            page.locator(sel).first.wait_for(state="visible", timeout=1000)
            menu_abierto = True
            break
        except PlaywrightTimeoutError:
            continue

    if not menu_abierto:
        return

    print("  🔒  Menú abierto detectado — haciendo clic fuera para cerrarlo…")

    # Intento 1: clic fuera del área del menú (centro de la pantalla)
    try:
        page.mouse.click(800, 400)
        page.wait_for_timeout(500)
    except Exception as exc:
        print(f"  ⚠️   Error al hacer clic fuera: {exc}")

    # Verificar si se cerró
    try:
        page.locator("div.ui-menu-item").first.wait_for(state="hidden", timeout=2000)
        print("  ✅  Menú cerrado con clic fuera.")
    except PlaywrightTimeoutError:
        # Intento 2: botón X del panel raíz
        print("  ⚠️   Clic fuera no cerró el menú — intentando botón X…")
        try:
            close_btn = page.locator("div.menu-title.main div.close").first
            close_btn.wait_for(state="visible", timeout=2000)
            close_btn.click()
            page.wait_for_timeout(400)
            print("  ✅  Menú cerrado con botón X.")
        except Exception as exc2:
            print(f"  ⚠️   No se pudo cerrar el menú con botón X: {exc2}")

    # Esperar a que el hamburguesa sea visible
    try:
        page.locator("div.toggle.menu").first.wait_for(state="visible", timeout=3000)
    except PlaywrightTimeoutError:
        print("  ⚠️   div.toggle.menu no apareció después de cerrar el menú.")




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



def volver_nivel(page: Page, usar_close: bool = False) -> None:
    """
    Vuelve al nivel anterior:
      usar_close=True  → div.menu-title.main div.close  (X) — cierra el panel raíz
      usar_close=False → div.menu-title:not(.main) div.back  (<) — sube un nivel
    """
    if usar_close:
        sel = "div.menu-title.main div.close"
        descripcion = "X (cerrar panel raíz)"
    else:
        sel = "div.menu-title:not(.main) div.back"
        descripcion = "< (volver nivel anterior)"

    try:
        btn = page.locator(sel).first
        btn.wait_for(state="visible", timeout=3000)
        btn.click()
        page.wait_for_timeout(400)
        print(f"  ↩️   {descripcion}")
    except Exception as exc:
        print(f"  ⚠️   No se pudo hacer clic en '{descripcion}': {exc}")


def recorrer_submenu(
    page: Page,
    breadcrumb: list[str],
    nivel: int = 1,
) -> None:
    """
    Recorre recursivamente todos los div.menu-options visibles.

    Args:
        page:       Instancia Playwright.
        breadcrumb: Ruta acumulada (ej: ["Golf", "Consultas"]).
        nivel:      Nivel actual (1 = primer submenú, 2 = sub-submenú, etc.).
    """
    indent = "  " * nivel
    opciones = get_menu_options(page)

    if not opciones:
        print(f"{indent}ℹ️   Sin opciones visibles en: {' > '.join(breadcrumb)}")
        return

    print(f"{indent}📋  Nivel {nivel} — '{' > '.join(breadcrumb)}': "
          f"{[o['texto'] for o in opciones]}")

    for opcion in opciones:
        texto = opcion["texto"]
        tiene_next = opcion["tiene_next"]
        ruta = breadcrumb + [texto]
        ruta_str = " > ".join(ruta)
        safe = ruta_str.replace(" > ", "__").replace(" ", "_")[:MAX__FILENAME_LENGTH]

        print(f"\n{indent}▶  {'[hoja]' if not tiene_next else '[rama]'} {ruta_str}")

        # Clic en la opción
        try:
            click_menu_option(page, texto)
        except Exception as exc:
            print(f"{indent}  ❌  No se pudo hacer clic en '{texto}': {exc}")
            screenshot(page, f"ERROR__{safe}")
            continue

        # Captura + DOM siempre
        screenshot(page, f"menu__{safe}")
        dump_dom(page, f"dom__{safe}")

        if tiene_next:
            # Tiene sub-submenú → recursión
            recorrer_submenu(page, ruta, nivel + 1)
        else:
            # Hoja final → ya estamos en la vista final, solo capturamos
            print(f"{indent}  🍃  Hoja final capturada: '{ruta_str}'")

        # Volver al nivel anterior
        volver_nivel(page, usar_close=(nivel == 1))


def recorrer_menu_completo(page: Page) -> None:
    """
    Punto de entrada: recorre Golf, Participes LATAM y FrontOn Gestión completos.
    """
    for item_text in TARGET_MENU_ITEMS:
        print(f"\n{'='*60}")
        print(f"▶ MENÚ PRINCIPAL → '{item_text}'")
        print(f"{'='*60}")

        # Abrir menú principal
        ensure_menu_open(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

        # Clic en el ítem del menú principal
        try:
            loc = page.locator("div.ui-menu-item", has_text=item_text).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            page.wait_for_timeout(500)
            print(f"  ✅  Submenú de '{item_text}' abierto.")
        except Exception as exc:
            print(f"  ❌  No se pudo abrir '{item_text}': {exc}")
            screenshot(page, f"ERROR__nivel0_{item_text.replace(' ', '_')}")
            continue

        # Captura del submenú de nivel 1
        safe0 = item_text.replace(" ", "_")
        screenshot(page, f"submenu_nivel1__{safe0}")

        # Recorrido recursivo desde nivel 1
        recorrer_submenu(page, breadcrumb=[item_text], nivel=1)

        # Al terminar todo el árbol de este ítem, cerrar con X
        volver_nivel(page, usar_close=True)

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
# PASO 1 — Navegación recursiva del árbol de menú (sin tocar hojas finales)
# ---------------------------------------------------------------------------

# Arreglo global donde se registran las hojas finales descubiertas
# Cada entrada: {"ruta": ["Golf", "Consultas", "Contabilidad", "Asientos diarios"]}
HOJAS_FINALES: list[dict] = []


def get_menu_options(page: Page) -> list[dict]:
    """Devuelve div.menu-options visibles con texto y tiene_next."""
    return page.evaluate("""
        () => Array.from(document.querySelectorAll('div.menu-options'))
            .filter(el => el.offsetParent !== null)
            .map(el => ({
                texto: el.querySelector('div.text')?.textContent.trim() ?? '',
                tiene_next: !!el.querySelector('div.next')
            }))
    """)


def click_menu_option(page: Page, texto: str) -> None:
    """Clic en el div.menu-options cuyo div.text contiene el texto dado."""
    loc = page.locator("div.menu-options", has_text=texto).first
    loc.wait_for(state="visible", timeout=5000)
    loc.click()
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    page.wait_for_timeout(400)


def recorrer_submenu_paso1(
    page: Page,
    breadcrumb: list[str],
    nivel: int = 1,
) -> None:
    """
    PASO 1: Navega recursivamente los nodos con tiene_next=True.
    Al encontrar una hoja (tiene_next=False) la registra en HOJAS_FINALES
    SIN hacer clic en ella.
    """
    indent = "  " * nivel
    opciones = get_menu_options(page)

    if not opciones:
        print(f"{indent}ℹ️   Sin opciones en: {' > '.join(breadcrumb)}")
        return

    print(f"{indent}📋  Nivel {nivel} — '{' > '.join(breadcrumb)}': "
          f"{[o['texto'] for o in opciones]}")

    for opcion in opciones:
        texto = opcion["texto"]
        tiene_next = opcion["tiene_next"]
        ruta = breadcrumb + [texto]
        ruta_str = " > ".join(ruta)
        indent2 = "  " * (nivel + 1)

        if not tiene_next:
            # ── Hoja final → registrar y NO hacer clic ──────────────────
            HOJAS_FINALES.append({"indice": len(HOJAS_FINALES) + 1, "ruta": ruta})
            print(f"{indent2}🍃  [HOJA] registrada: '{ruta_str}'")
            continue

        # ── Nodo rama → entrar, recorrer, volver ────────────────────────
        print(f"{indent2}▶  [RAMA] entrando en: '{ruta_str}'")
        safe = ruta_str.replace(" > ", "__").replace(" ", "_")[:MAX__FILENAME_LENGTH]

        try:
            click_menu_option(page, texto)
        except Exception as exc:
            print(f"{indent2}❌  No se pudo hacer clic en '{texto}': {exc}")
            screenshot(page, f"ERROR__{safe}")
            continue

        screenshot(page, f"menu__{safe}")

        # Recursión en el siguiente nivel
        recorrer_submenu_paso1(page, ruta, nivel + 1)

        # Volver al nivel actual — siempre con < (back), nunca con X
        volver_nivel(page, usar_close=False) 


def recorrer_menu_completo_paso1(page: Page) -> None:
    """
    PASO 1 — Punto de entrada.
    Recorre Golf, Participes LATAM y FrontOn Gestión registrando hojas finales.
    """
    global HOJAS_FINALES
    HOJAS_FINALES = []  # reiniciar por si se llama más de una vez

    for item_text in TARGET_MENU_ITEMS:
        print(f"\n{'='*60}")
        print(f"▶ MENÚ PRINCIPAL → '{item_text}'")
        print(f"{'='*60}")

        ensure_menu_open(page)
        page.wait_for_timeout(MENU_REOPEN_DELAY_MS)

        try:
            loc = page.locator("div.ui-menu-item", has_text=item_text).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            page.wait_for_timeout(500)
            print(f"  ✅  Submenú de '{item_text}' abierto.")
        except Exception as exc:
            print(f"  ❌  No se pudo abrir '{item_text}': {exc}")
            continue

        screenshot(page, f"submenu_nivel1__{item_text.replace(' ', '_')}")

        # Recorrido recursivo
        recorrer_submenu_paso1(page, breadcrumb=[item_text], nivel=1)

        # Cerrar el panel raíz con X al terminar TODO el árbol de este ítem
        volver_nivel(page, usar_close=True)
        #cerrar_menu_si_abierto(page)

    # ── Reporte de hojas finales descubiertas ───────────────────────────
    print(f"\n{'='*60}")
    print(f"  🗺️   HOJAS FINALES DESCUBIERTAS: {len(HOJAS_FINALES)}")
    print(f"{'='*60}")
    for i, hoja in enumerate(HOJAS_FINALES, 1):
        print(f"  {i:3}. {' > '.join(hoja['ruta'])}")

    # Guardar en archivo JSON para usar en PASO 2
    report_path = config.SCREENSHOTS_DIR / "hojas_finales.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(HOJAS_FINALES, f, ensure_ascii=False, indent=2)
    print(f"\n  💾  Hojas guardadas en: {report_path}")

# ---------------------------------------------------------------------------
# PASO 2 — Ejecución de hojas por índice (re-navega menú completo cada vez)
# ---------------------------------------------------------------------------


def abrir_menu_hamburguesa(page: Page) -> None:
    """
    Hace clic en el hamburguesa ≡ y espera a que div.ui-menu-item sea visible.
    Selectores del hamburguesa (en orden de prioridad):
      "css=div.toggle.menu"
      "css=app-ui-header div.toggle.menu"
    """
    for sel in ["css=div.toggle.menu", "css=app-ui-header div.toggle.menu"]:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=3000)
            loc.click()
            print("  🍔  Hamburguesa ≡ clickeado.")
            page.locator("div.ui-menu-item").first.wait_for(state="visible", timeout=5000)
            return
        except Exception:
            continue
    raise RuntimeError("No se pudo hacer clic en el hamburguesa ≡.")


def navegar_ruta_completa(page: Page, ruta: list[str]) -> bool:
    """
    Navega toda la ruta desde cero (menú ya abierto):
      - ruta[0]: clic en div.ui-menu-item (has_text=ruta[0])
      - ruta[1:-1]: clic en div.menu-options (has_text) para cada rama
      - ruta[-1]: clic en div.menu-options (has_text) para la hoja
    Devuelve True si llegó a la hoja, False si falló.
    Usa page.wait_for_timeout(600) entre clics (no networkidle).
    """
    try:
        # ruta[0] → raíz: div.ui-menu-item
        loc = page.locator("div.ui-menu-item", has_text=ruta[0]).first
        loc.wait_for(state="visible", timeout=5000)
        loc.click()
        page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        # ruta[1:-1] → ramas intermedias: div.menu-options
        for rama in ruta[1:-1]:
            loc = page.locator("div.menu-options", has_text=rama).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        # ruta[-1] → hoja final: div.menu-options (puede coincidir con ruta[0] si len==1)
        if len(ruta) > 1:
            loc = page.locator("div.menu-options", has_text=ruta[-1]).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        return True
    except Exception as exc:
        print(f"  ❌  Error navegando ruta {ruta}: {exc}")
        return False


def cerrar_pantalla_layout(page: Page) -> bool:
    """
    Cierra la pantalla activa haciendo clic en div.tab.activable.active div.close
    Espera a que div.tab.activable.active desaparezca (state="hidden", timeout=5000).
    Luego espera a que div.toggle.menu sea visible (hamburguesa ≡ disponible).
    Devuelve True si se cerró correctamente.
    """
    try:
        close_btn = page.locator("div.tab.activable.active div.close").first
        close_btn.wait_for(state="visible", timeout=5000)
        close_btn.click()
        page.locator("div.tab.activable.active").first.wait_for(state="hidden", timeout=5000)
        page.locator("div.toggle.menu").first.wait_for(state="visible", timeout=5000)
        print("  ✖️   Pantalla cerrada.")
        return True
    except Exception as exc:
        print(f"  ⚠️   No se pudo cerrar la pantalla: {exc}")
        return False


def is_notification_modal_visible(page: Page):
    """
    Detecta la ventana unimodal de notificación buscando:
        <div class="title"> Notificaciones </div>
    El innerText es exactamente ' Notificaciones ' (espacio + texto + espacio).
    Devuelve el locator del div.title si es visible, None en caso contrario.
    """
    try:
        index = page.evaluate("""
            () => {
                const divs = document.querySelectorAll('div.title');
                for (let i = 0; i < divs.length; i++) {
                    if (divs[i].innerText === ' Notificaciones ') return i;
                }
                return -1;
            }
        """)
        if index >= 0:
            return page.locator("div.title").nth(index)
    except Exception:
        pass
    return None


def handle_notification_modal(page: Page, ruta_str: str) -> str | None:
    """
    Detecta, registra y cierra el modal de notificación si está visible.

    1. Detecta si hay un modal de notificación visible (timeout corto 2000ms).
    2. Extrae tipo y mensaje de la notificación.
    3. Registra en notificaciones_log.csv (timestamp, ruta_menu, tipo, mensaje).
    4. Cierra el modal haciendo clic en el botón de aceptar/cerrar.
    5. Retorna el texto "{tipo}: {mensaje}" o None si no había modal.
    """
    # ── 1. Detectar si hay notificación visible ─────────────────────────
    modal_loc = is_notification_modal_visible(page)
    if modal_loc is None:
        return None
    safe = ruta_str.replace(" > ", "__").replace(" ", "_")[:MAX__FILENAME_LENGTH]
    screenshot(page, f"NOTIF__{safe}")
    dump_dom(page, f"NOTIF_DOM__{safe}")

    # ── 2. Extraer tipo y mensaje ────────────────────────────────────────
    tipo = ""
    for sel in NOTIFICATION_TYPE_SELECTORS:
        try:
            t = modal_loc.locator(sel).first.inner_text().strip()
            if t:
                tipo = t
                break
        except Exception:
            continue

    mensaje = ""
    for sel in NOTIFICATION_MESSAGE_SELECTORS:
        try:
            m = modal_loc.locator(sel).first.inner_text().strip()
            if m:
                mensaje = m
                break
        except Exception:
            continue

    # Si no se pudo distinguir tipo/mensaje, usar el texto completo
    if not tipo and not mensaje:
        try:
            texto_completo = modal_loc.inner_text().strip()
            mensaje = texto_completo
        except Exception:
            mensaje = "(texto no disponible)"

    texto_notif = f"{tipo}: {mensaje}" if tipo else mensaje

    # ── 3. Registrar en CSV ──────────────────────────────────────────────
    log_path = config.SCREENSHOTS_DIR / "notificaciones_log.csv"
    ts_iso = datetime.datetime.now(timezone.utc).isoformat()
    escribir_cabecera = not log_path.exists()
    try:
        with open(log_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if escribir_cabecera:
                writer.writerow(["timestamp", "ruta_menu", "tipo", "mensaje"])
            writer.writerow([ts_iso, ruta_str, tipo, mensaje])
        print(f"  📝  Notificación registrada en log: {log_path.name}")
    except Exception as exc:
        print(f"  ⚠️   No se pudo escribir en el log de notificaciones: {exc}")

    # ── 4. Cerrar el modal ───────────────────────────────────────────────
    cerrado = False
    for sel in NOTIFICATION_CLOSE_SELECTORS:
        try:
            btn = page.locator(sel).first
            btn.wait_for(state="visible", timeout=2000)
            btn.click()
            page.wait_for_timeout(400)
            print(f"  ✅  Modal de notificación cerrado con selector: {sel}")
            cerrado = True
            break
        except Exception:
            continue

    if not cerrado:
        screenshot(page, f"NOTIF_NO_CERRADA__{safe}")
        # Registrar el intento fallido en el CSV
        ts_iso2 = datetime.datetime.now(timezone.utc).isoformat()
        try:
            with open(log_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([ts_iso2, ruta_str, tipo, f"[NO SE PUDO CERRAR] {mensaje}"])
        except Exception:
            pass
        print(f"  ⚠️   No se pudo cerrar el modal de notificación. Screenshot guardado.")

    return texto_notif


def ejecutar_paso2(page: Page) -> None:
    """
    Lee hojas_finales.json.
    Para cada hoja por índice:
      1. abrir_menu_hamburguesa()
      2. navegar_ruta_completa()  → incluye clic en la hoja
      3. esperar div.tab.activable.active + screenshot + dump_dom
      4. cerrar_pantalla_layout()
    Genera paso2_report.txt al finalizar.
    """
    json_path = config.SCREENSHOTS_DIR / "hojas_finales.json"
    if not json_path.exists():
        print("  ❌  No se encontró hojas_finales.json. Ejecutar PASO 1 primero.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        hojas = json.load(f)

    total = len(hojas)
    print(f"\n  📋  Total de hojas a recorrer: {total}\n")

    exitosas: list[str] = []
    fallidas: list[dict] = []

    for hoja in hojas:
        indice = hoja.get("indice", "?")
        ruta = hoja["ruta"]
        ruta_str = " > ".join(ruta)
        safe = ruta_str.replace(" > ", "__").replace(" ", "_")[:MAX__FILENAME_LENGTH]

        print(f"\n[{indice:>3}/{total}] {ruta_str}")

        try:
            # PASO A — Asegurar estado limpio: cerrar cualquier menú o panel abierto
            cerrar_menu_si_abierto(page)
            # PASO A2 — Abrir menú desde cero
            abrir_menu_hamburguesa(page)

            # PASO B — Navegar ruta completa (raíz → ramas → hoja)
            ok = navegar_ruta_completa(page, ruta)
            if not ok:
                raise RuntimeError("navegar_ruta_completa retornó False")

            print(f"  ✅  Clic en hoja '{ruta[-1]}'")

            # PASO C — Captura
            page.locator("div.tab.activable.active").first.wait_for(
                state="visible", timeout=8000
            )
            print(f"  ✅  Vista cargada: '{ruta[-1]}'")
            screenshot(page, f"paso2__{safe}")
            dump_dom(page, f"dom_paso2__{safe}")

            # PASO C2 — Atender notificación modal si aparece
            notification_msg = handle_notification_modal(page, ruta_str)
            if notification_msg:
                print(f"  🔔  Notificación atendida: {notification_msg}")

            # Pausa para que el usuario reconozca la pantalla abierta
            page.wait_for_timeout(config.PAUSE_PANTALLA_MS)
          
            # PASO D — Cerrar pantalla
            cerrado = cerrar_pantalla_layout(page)
            if not cerrado:
                print(f"  ⚠️   No se pudo cerrar pantalla para '{ruta_str}'")

            exitosas.append(ruta_str)

        except Exception as exc:
            print(f"  ❌  Error en '{ruta_str}': {exc}")
            screenshot(page, f"ERROR_paso2__{safe}")
            fallidas.append({"ruta": ruta_str, "error": str(exc)})

            # Atender notificación modal si es la causa del error
            try:
                notification_msg = handle_notification_modal(page, ruta_str)
                if notification_msg:
                    print(f"  🔔  Notificación atendida en recuperación: {notification_msg}")
            except Exception:
                pass

            # Intentar recuperación: cerrar pantalla si quedó abierta
            try:
                if page.locator("div.tab.activable.active").first.is_visible(timeout=2000):
                    cerrar_pantalla_layout(page)
            except Exception:
                pass

            # Cerrar cualquier menú que haya quedado abierto (clic fuera del área)
            cerrar_menu_si_abierto(page)

    # Reporte final
    print(f"\n{'='*60}")
    print(f"  ✅  PASO 2 completado.")
    print(f"  ✅  Exitosas : {len(exitosas)}")
    print(f"  ❌  Fallidas : {len(fallidas)}")
    print(f"{'='*60}")

    report_path = config.SCREENSHOTS_DIR / "paso2_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"PASO 2 — Reporte – {datetime.datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"URL: {config.BASE_URL}\n\n")
        f.write(f"Exitosas: {len(exitosas)}\n")
        for r in exitosas:
            f.write(f"  ✅  {r}\n")
        f.write(f"\nFallidas: {len(fallidas)}\n")
        for item in fallidas:
            f.write(f"  ❌  {item['ruta']} → {item['error']}\n")
    print(f"\n  📄  Reporte PASO 2 guardado en: {report_path}")


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

            #print("▶ Paso 4: Capturando submenús de primer nivel…\n")
            #capturar_submenus_nivel1(page)

            #print("▶ Paso 4: Recorrido completo del menú…\n")
            #recorrer_menu_completo(page)

            print("▶ Paso 4: PASO 1 — Recorrido recursivo del árbol de menú…\n")
            recorrer_menu_completo_paso1(page)

            print("\n▶ Paso 5: PASO 2 — Clic en hojas finales y captura de vistas…\n")
            ejecutar_paso2(page)

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
