"""
run_casos_prueba.py
-------------------
Ejecuta los Casos de Prueba con Datos de Entrada definidos en un Excel.

PRIMERA SOLICITUD (este programa):
    1. Abre la URL y hace login.
    2. Lee el Excel definido por EXCEL_CASOS en .env.
    3. Para cada fila:
         a) Lee la columna "Camino a la Pantalla".
         b) Navega por el menú hasta la pantalla.
         c) Si ACTIVA_VENTANA=Si, abre una ventana con un botón "Avanzar"
            que se autocierra después de VENTANA_TIMEOUT_SEG segundos
            (default 20).
         d) Si la pantalla muestra una notificación de error, escribe
            ese mensaje en la columna "Resultado".
            Si todo OK, escribe "OK".
         e) Cierra la pantalla y pasa al siguiente caso (siempre partiendo
            de nuevo desde el menú hamburguesa).
    4. Al terminar guarda y cierra el Excel.

PASOS FUTUROS (NO implementados aquí, pero sí considerados en el diseño):
    - Usar las columnas Dato1..Dato20 con formato [Frame].Field.Valor
      para rellenar la pantalla y grabar.
    - Si los datos son rechazados → registrar mensaje + cancelar.
    - Si OK → registrar "EXITO".
    El gancho está en la función `procesar_caso()` → ver TODO marcado.

Uso:
    python run_casos_prueba.py

Requiere:
    - .env con APP_USERNAME, APP_PASSWORD, BASE_URL,
      ACTIVA_VENTANA, EXCEL_CASOS, VENTANA_TIMEOUT_SEG.
    - Playwright instalado:  playwright install chromium
    - openpyxl:              pip install openpyxl python-dotenv playwright
"""

from __future__ import annotations

import csv
import datetime
import re
import sys
import threading
import time
from datetime import timezone
from pathlib import Path
from typing import Optional

# tkinter es opcional: si la instalación de Python no lo incluye
# (suele pasar con Python del Microsoft Store o instalaciones minimal),
# usamos un fallback en consola.  Por eso NO se importa a nivel de módulo.
# El import se hace dentro de ventana_avanzar() de forma diferida.

from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


# ===========================================================================
# CONSTANTES
# ===========================================================================

NOTIFICATION_TYPE_SELECTORS = [
    "div.notification-type", "div.type", "div.title",
    "div.notification-title", ".notification-header",
]
NOTIFICATION_MESSAGE_SELECTORS = [
    "div.notification-message", "div.message", "div.body",
    "div.notification-body", "div.text", "p.message",
]
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

HAMBURGER_SELECTORS = [
    "css=div.toggle.menu",
    "css=div.toggle.menu svg",
    "css=div.header div.toggle.menu",
    "css=app-ui-header div.toggle.menu",
    "[aria-label='menu' i]", "[aria-label='menú' i]",
    ".hamburger", ".menu-toggle", ".navbar-toggle", ".burger", ".nav-toggle",
    "header button", "nav button", ".navbar button",
]

LOGIN_SELECTORS = [
    "input[name='username']", "input[name='user']", "input[name='login']",
    "input[id='username']", "input[id='user']",
    "input[type='text'][placeholder*='usu' i]",
    "input[type='text'][placeholder*='user' i]",
    "input[autocomplete='username']",
]
PASSWORD_SELECTORS = [
    "input[name='password']", "input[name='pass']",
    "input[id='password']", "input[id='pass']",
    "input[type='password']", "input[autocomplete='current-password']",
]
SUBMIT_SELECTORS = [
    "button[type='submit']", "input[type='submit']",
    "button:has-text('Ingresar')", "button:has-text('Entrar')",
    "button:has-text('Login')", "button:has-text('Iniciar sesión')",
    "a:has-text('Ingresar')",
]

MAX_FILENAME_LENGTH = 80
MENU_NAVIGATION_DELAY_MS = 600
MENU_REOPEN_DELAY_MS = 500
BROWSER_SLOW_MO_MS = 300
ENTRE_CASOS_PAUSA_MS = 400  # pausa breve entre el cierre de un caso y el siguiente


# ===========================================================================
# HELPERS — capturas, DOM, clic genérico
# ===========================================================================


def screenshot(page: Page, name: str) -> None:
    ts = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name).strip("_")[:MAX_FILENAME_LENGTH]
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{safe}.png"
    page.screenshot(path=str(filepath))
    print(f"  📸  Captura guardada: {filepath.name}")


def dump_dom(page: Page, name: str = "dom") -> Path:
    ts = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name).strip("_")[:MAX_FILENAME_LENGTH]
    filepath = config.SCREENSHOTS_DIR / f"{ts}_{safe}.html"
    filepath.write_text(page.content(), encoding="utf-8")
    print(f"  🧾  DOM guardado: {filepath.name}")
    return filepath


def element_exists(page: Page, selector: str, timeout: int = 3000) -> bool:
    try:
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


def wait_and_click(page: Page, selectors: list[str], description: str,
                   timeout: Optional[int] = None) -> None:
    t = timeout or config.TIMEOUT_MS
    last_error: Optional[Exception] = None
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=t)
            loc.click()
            print(f"  ✅  Clic en '{description}' usando: {sel}")
            return
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(
        f"No se pudo hacer clic en '{description}'. "
        f"Último error: {last_error}"
    )


# ===========================================================================
# LOGIN
# ===========================================================================


def handle_login(page: Page) -> None:
    username_visible = any(element_exists(page, s, timeout=3000) for s in LOGIN_SELECTORS)
    if not username_visible:
        print("  ℹ️   No se detectó pantalla de login – sesión activa.")
        return

    print("  🔐  Pantalla de login detectada. Ingresando credenciales…")
    if not config.APP_USERNAME or not config.APP_PASSWORD:
        raise ValueError(
            "APP_USERNAME o APP_PASSWORD no están definidos en .env"
        )

    for sel in LOGIN_SELECTORS:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_USERNAME)
            break
    for sel in PASSWORD_SELECTORS:
        if element_exists(page, sel, timeout=2000):
            page.fill(sel, config.APP_PASSWORD)
            break

    screenshot(page, "01_before_login")
    wait_and_click(page, SUBMIT_SELECTORS, "botón de login")
    page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
    print("  ✅  Login completado.")
    screenshot(page, "02_after_login")


# ===========================================================================
# MENÚ — apertura / cierre
# ===========================================================================


def abrir_menu_hamburguesa(page: Page) -> None:
    """
    SIEMPRE hace clic en el hamburguesa ≡ y espera a que div.ui-menu-item
    sea visible. Esta función NO chequea si el menú "ya está abierto" —
    entre casos consecutivos esa detección puede dar falso positivo y
    romper la navegación. Cada caso parte desde el hamburguesa.
    """
    ultimo_error: Optional[Exception] = None
    for sel in ["css=div.toggle.menu", "css=app-ui-header div.toggle.menu"]:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=3000)
            loc.click()
            print("  🍔  Hamburguesa ≡ clickeado.")
            page.locator("div.ui-menu-item").first.wait_for(state="visible", timeout=5000)
            return
        except Exception as exc:
            ultimo_error = exc
            continue
    # Último recurso: probar todos los selectores genéricos
    try:
        wait_and_click(page, HAMBURGER_SELECTORS, "menú hamburguesa")
        page.locator("div.ui-menu-item").first.wait_for(state="visible", timeout=5000)
    except Exception:
        raise RuntimeError(
            f"No se pudo hacer clic en el hamburguesa ≡. "
            f"Último error: {ultimo_error}"
        )


def cerrar_menu_si_abierto(page: Page) -> None:
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

    print("  🔒  Cerrando menú con clic fuera…")
    try:
        page.mouse.click(800, 400)
        page.wait_for_timeout(500)
    except Exception:
        pass

    try:
        page.locator("div.ui-menu-item").first.wait_for(state="hidden", timeout=2000)
    except PlaywrightTimeoutError:
        # Fallback: botón X del panel raíz
        try:
            page.locator("div.menu-title.main div.close").first.click(timeout=2000)
            page.wait_for_timeout(400)
        except Exception:
            pass


# ===========================================================================
# NAVEGACIÓN POR RUTA
# ===========================================================================


def parse_camino(camino: str) -> list[str]:
    """
    'Golf > Consultas > Contabilidad > Asientos manuales'
      → ['Golf', 'Consultas', 'Contabilidad', 'Asientos manuales']
    """
    if not camino:
        return []
    partes = re.split(r"\s*>\s*", camino.strip())
    return [p for p in partes if p]


def navegar_ruta_completa(page: Page, ruta: list[str]) -> bool:
    """
    Navega toda la ruta desde el menú ya abierto:
      ruta[0]    → div.ui-menu-item
      ruta[1:-1] → div.menu-options (ramas)
      ruta[-1]   → div.menu-options (hoja)
    """
    try:
        loc = page.locator("div.ui-menu-item", has_text=ruta[0]).first
        loc.wait_for(state="visible", timeout=5000)
        loc.click()
        page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        for rama in ruta[1:-1]:
            loc = page.locator("div.menu-options", has_text=rama).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        if len(ruta) > 1:
            loc = page.locator("div.menu-options", has_text=ruta[-1]).first
            loc.wait_for(state="visible", timeout=5000)
            loc.click()
            page.wait_for_timeout(MENU_NAVIGATION_DELAY_MS)

        return True
    except Exception as exc:
        print(f"  ❌  Error navegando ruta {ruta}: {exc}")
        return False


# ===========================================================================
# NOTIFICACIONES Y CIERRE DE PANTALLA
# ===========================================================================


def is_notification_modal_visible(page: Page):
    """
    Detecta la ventana unimodal de notificación buscando un div.title
    cuyo innerText sea exactamente ' Notificaciones '.
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


def handle_notification_modal(page: Page, ruta_str: str) -> Optional[str]:
    """
    Si hay notificación visible: extrae tipo + mensaje, registra en CSV,
    cierra el modal y retorna "{tipo}: {mensaje}". Si no hay, retorna None.
    """
    modal_loc = is_notification_modal_visible(page)
    if modal_loc is None:
        return None

    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", ruta_str)[:MAX_FILENAME_LENGTH]
    screenshot(page, f"NOTIF__{safe}")
    dump_dom(page, f"NOTIF_DOM__{safe}")

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

    if not tipo and not mensaje:
        try:
            mensaje = modal_loc.inner_text().strip()
        except Exception:
            mensaje = "(texto no disponible)"

    texto_notif = f"{tipo}: {mensaje}" if tipo else mensaje

    # Log a CSV
    log_path = config.SCREENSHOTS_DIR / "notificaciones_log.csv"
    ts_iso = datetime.datetime.now(timezone.utc).isoformat()
    escribir_cabecera = not log_path.exists()
    try:
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if escribir_cabecera:
                w.writerow(["timestamp", "ruta_menu", "tipo", "mensaje"])
            w.writerow([ts_iso, ruta_str, tipo, mensaje])
    except Exception as exc:
        print(f"  ⚠️   No se pudo escribir el log: {exc}")

    # Cerrar
    for sel in NOTIFICATION_CLOSE_SELECTORS:
        try:
            btn = page.locator(sel).first
            btn.wait_for(state="visible", timeout=2000)
            btn.click()
            page.wait_for_timeout(400)
            print(f"  ✅  Notificación cerrada.")
            break
        except Exception:
            continue

    return texto_notif


def _cerrar_app_modal_si_existe(page: Page) -> bool:
    try:
        page.locator("app-modal div.modal-background").first.wait_for(
            state="visible", timeout=2000
        )
    except Exception:
        return False

    print("  🪟  app-modal detectado.")
    try:
        page.locator("app-modal div.option.close").first.click(timeout=2000)
        page.wait_for_timeout(400)
        return True
    except Exception:
        pass
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
        return True
    except Exception:
        return False


def cerrar_pantalla_layout(page: Page) -> bool:
    _cerrar_app_modal_si_existe(page)
    try:
        close_btn = page.locator("div.tab.activable.active div.close").first
        close_btn.wait_for(state="visible", timeout=5000)
        close_btn.click()
        page.locator("div.tab.activable.active").first.wait_for(state="hidden", timeout=5000)
        page.locator("div.toggle.menu").first.wait_for(state="visible", timeout=5000)
        print("  ✖️   Pantalla cerrada.")
        return True
    except Exception:
        try:
            page.locator("div.tab.activable.active div.close").first.dispatch_event("click")
            page.locator("div.tab.activable.active").first.wait_for(state="hidden", timeout=5000)
            return True
        except Exception:
            return False


# ===========================================================================
# VENTANA "AVANZAR"  (Tkinter con fallback a consola)
# ===========================================================================


def _ventana_avanzar_tkinter(timeout_seg: int, titulo_caso: str) -> str:
    """
    Implementación con Tkinter (ventana gráfica).
    Lanza ImportError si tkinter no está disponible.
    """
    import tkinter as tk  # diferido

    motivo = {"valor": "timeout"}

    root = tk.Tk()
    root.title("Automatización QA — Avanzar")
    root.attributes("-topmost", True)
    root.geometry("420x180+200+200")
    root.resizable(False, False)

    titulo = titulo_caso[:80] if titulo_caso else "Caso de prueba"
    tk.Label(
        root, text=titulo, font=("Segoe UI", 10, "bold"),
        wraplength=380, justify="center",
    ).pack(pady=(15, 5))

    restante = {"seg": timeout_seg}
    lbl_timer = tk.Label(
        root, text=f"Auto-avanza en {restante['seg']} s",
        font=("Segoe UI", 9), fg="#555",
    )
    lbl_timer.pack(pady=(0, 10))

    def on_avanzar():
        motivo["valor"] = "avanzar"
        root.destroy()

    def on_cerrar():
        motivo["valor"] = "cerrada"
        root.destroy()

    btn = tk.Button(
        root, text="Avanzar", width=14, height=2,
        font=("Segoe UI", 10, "bold"), command=on_avanzar,
    )
    btn.pack(pady=10)

    def tick():
        if not root.winfo_exists():
            return
        restante["seg"] -= 1
        if restante["seg"] <= 0:
            try:
                root.destroy()
            except Exception:
                pass
            return
        lbl_timer.config(text=f"Auto-avanza en {restante['seg']} s")
        root.after(1000, tick)

    root.protocol("WM_DELETE_WINDOW", on_cerrar)
    root.after(1000, tick)
    root.after(timeout_seg * 1000 + 50,
              lambda: root.winfo_exists() and root.destroy())

    try:
        btn.focus_set()
    except Exception:
        pass

    root.mainloop()
    return motivo["valor"]


def _ventana_avanzar_consola(timeout_seg: int, titulo_caso: str) -> str:
    """
    Fallback en consola cuando tkinter no está disponible.
    """
    print("\n" + "─" * 60)
    print(f"  ⏸   Pausa — {titulo_caso[:80]}")
    print(f"        Presiona ENTER para avanzar  (auto-avanza en {timeout_seg}s)")
    print("─" * 60)

    # Variante Windows
    try:
        import msvcrt
        inicio = time.time()
        ultimo_print = -1
        while True:
            restante = timeout_seg - int(time.time() - inicio)
            if restante <= 0:
                print("\r  ⏱   Tiempo agotado — avanzando…              ")
                return "timeout"
            if restante != ultimo_print:
                sys.stdout.write(f"\r  ⏱   Auto-avanza en {restante:2d}s  (ENTER para continuar)  ")
                sys.stdout.flush()
                ultimo_print = restante
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b"\r", b"\n", b" "):
                    print("\r  ▶   ENTER recibido — avanzando…              ")
                    return "avanzar"
            time.sleep(0.1)
    except ImportError:
        pass

    # Variante Linux/Mac
    try:
        import select
        inicio = time.time()
        ultimo_print = -1
        while True:
            restante = timeout_seg - int(time.time() - inicio)
            if restante <= 0:
                print("\r  ⏱   Tiempo agotado — avanzando…              ")
                return "timeout"
            if restante != ultimo_print:
                sys.stdout.write(f"\r  ⏱   Auto-avanza en {restante:2d}s  (ENTER para continuar)  ")
                sys.stdout.flush()
                ultimo_print = restante
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                sys.stdin.readline()
                print("\r  ▶   ENTER recibido — avanzando…              ")
                return "avanzar"
    except Exception:
        pass

    # Último recurso
    print(f"  (Sin detección de teclado disponible — espera {timeout_seg}s)")
    time.sleep(timeout_seg)
    return "timeout"


_TKINTER_AVISADO = {"flag": False}


def ventana_avanzar(timeout_seg: int = 20, titulo_caso: str = "") -> str:
    """
    Pausa con botón "Avanzar". Intenta Tkinter; si no está, fallback a consola.
    """
    if timeout_seg <= 0:
        timeout_seg = 20
    try:
        return _ventana_avanzar_tkinter(timeout_seg, titulo_caso)
    except ImportError:
        if not _TKINTER_AVISADO["flag"]:
            print(
                "\n  ⚠️   Tkinter no está disponible en esta instalación de Python.\n"
                "        Usando ventana de consola como alternativa.\n"
                "        (Para tener la ventana gráfica: reinstalar Python\n"
                "         marcando la opción 'tcl/tk and IDLE')."
            )
            _TKINTER_AVISADO["flag"] = True
        return _ventana_avanzar_consola(timeout_seg, titulo_caso)
    except Exception as exc:
        print(f"  ⚠️   Tkinter falló ({exc}). Usando fallback de consola.")
        return _ventana_avanzar_consola(timeout_seg, titulo_caso)


# ===========================================================================
# EXCEL
# ===========================================================================

COL_CAMINO_HEADER = "Camino a la Pantalla"
COL_TIPO_HEADER = "Tipo Pantalla"
COL_ACCION_HEADER = "Acción"
COL_RESULTADO_HEADER = "Resultado"
COL_DATO_PREFIX = "Dato"

# Tipos de pantalla soportados
TIPO_CONSULTA = "Consulta"
TIPO_CRUD = "CRUD"
TIPO_TRANSACCIONES = "Transacciones"
TIPOS_VALIDOS = {TIPO_CONSULTA, TIPO_CRUD, TIPO_TRANSACCIONES}
TIPO_DEFAULT = TIPO_CONSULTA  # Si la columna queda vacía → se asume Consulta

# Acciones soportadas
ACCION_CREATE = "Create"
ACCION_READ = "Read"
ACCION_UPDATE = "Update"
ACCION_DELETE = "Delete"
ACCIONES_VALIDAS = {ACCION_CREATE, ACCION_READ, ACCION_UPDATE, ACCION_DELETE}

# Tipos que REQUIEREN acción (en Consulta es opcional/ignorado)
TIPOS_REQUIEREN_ACCION = {TIPO_CRUD, TIPO_TRANSACCIONES}

FILL_OK = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
FILL_ERROR = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")


def localizar_columnas(ws) -> dict[str, int]:
    cols: dict[str, int] = {}
    for cell in ws[1]:
        if cell.value is None:
            continue
        cols[str(cell.value).strip()] = cell.column

    faltan = []
    if COL_CAMINO_HEADER not in cols:
        faltan.append(COL_CAMINO_HEADER)
    if COL_RESULTADO_HEADER not in cols:
        faltan.append(COL_RESULTADO_HEADER)
    if faltan:
        raise ValueError(
            f"El Excel no contiene la(s) columna(s): {faltan}. "
            f"Headers detectados: {list(cols.keys())}"
        )
    # COL_TIPO_HEADER y COL_ACCION_HEADER son opcionales
    if COL_TIPO_HEADER not in cols:
        print(f"  ⚠️   Columna '{COL_TIPO_HEADER}' no encontrada — se asumirá '{TIPO_DEFAULT}' para todos los casos.")
    if COL_ACCION_HEADER not in cols:
        print(f"  ⚠️   Columna '{COL_ACCION_HEADER}' no encontrada — los casos CRUD/Transacciones requerirán acción.")
    return cols


def normalizar_accion(valor) -> Optional[str]:
    """
    Acepta variantes (mayúsculas, espacios, abreviaturas en español/inglés)
    y retorna una de ACCIONES_VALIDAS, None si está vacía, o el string
    original si es inválido (para que el dispatch lo marque como ERROR_CONFIG).
    """
    if valor is None:
        return None
    s = str(valor).strip()
    if s == "":
        return None
    s_lower = s.lower()
    if s_lower in ("create", "crear", "nuevo", "agregar", "add", "alta", "c", "n"):
        return ACCION_CREATE
    if s_lower in ("read", "leer", "consultar", "buscar", "ver", "query", "r", "q"):
        return ACCION_READ
    if s_lower in ("update", "actualizar", "modificar", "editar", "edit", "u", "m", "e"):
        return ACCION_UPDATE
    if s_lower in ("delete", "eliminar", "borrar", "baja", "del", "d", "b"):
        return ACCION_DELETE
    return s  # inválido — retorna tal cual


def normalizar_tipo(valor) -> str:
    """
    Acepta variantes (mayúsculas, espacios, abreviaturas) y retorna uno de:
    TIPO_CONSULTA, TIPO_CRUD, TIPO_TRANSACCIONES, o TIPO_DEFAULT si está vacío.
    Si el valor es inválido retorna el string original (para que el dispatch lo marque como error).
    """
    if valor is None:
        return TIPO_DEFAULT
    s = str(valor).strip()
    if s == "":
        return TIPO_DEFAULT
    s_lower = s.lower()
    if s_lower in ("consulta", "consultas", "consult", "c"):
        return TIPO_CONSULTA
    if s_lower in ("crud", "mantenedor", "mantenedores", "abm"):
        return TIPO_CRUD
    if s_lower in ("transacciones", "transaccion", "transacción", "operacion",
                   "operación", "operaciones", "trx", "t"):
        return TIPO_TRANSACCIONES
    return s  # valor inválido — lo retorna tal cual para reportar el error


def _resolver_referencia_celda(ref: str, wb, ws_actual):
    """
    Resuelve una referencia tipo A4, $B$2 o 'Hoja'!C5 al valor literal de esa celda.
    """
    # Literal entre comillas: "texto"  o  'texto'
    if (ref.startswith('"') and ref.endswith('"')) or \
       (ref.startswith("'") and ref.endswith("'") and "!" not in ref):
        return ref[1:-1]

    # Referencia con hoja: 'Hoja'!A4   o   Hoja!A4
    m = re.match(r"^(?:('[^']+'|[A-Za-z_][A-Za-z0-9_.]*)!)?\$?([A-Z]+)\$?(\d+)$", ref)
    if not m:
        return None
    sheet_name = m.group(1)
    if sheet_name and sheet_name.startswith("'") and sheet_name.endswith("'"):
        sheet_name = sheet_name[1:-1]
    target_ws = wb[sheet_name] if sheet_name else ws_actual

    from openpyxl.utils import column_index_from_string
    col = column_index_from_string(m.group(2))
    row = int(m.group(3))
    return target_ws.cell(row=row, column=col).value


_VLOOKUP_RE = re.compile(
    r"^=VLOOKUP\(\s*"
    r"(.+?)"                                   # lookup_value
    r"\s*,\s*"
    r"(.+?)"                                   # table_array
    r"\s*,\s*"
    r"(\d+)"                                   # col_index
    r"(?:\s*,\s*(?:TRUE|FALSE|0|1|VERDADERO|FALSO))?"  # opcional 4to param
    r"\s*\)\s*$",
    re.IGNORECASE,
)

_RANGO_RE = re.compile(
    r"^(?:('[^']+'|[A-Za-z_][A-Za-z0-9_.]*)!)?"  # hoja opcional
    r"\$?([A-Z]+)\$?(\d+)?"                       # col-fila inicio
    r"\s*:\s*"
    r"\$?([A-Z]+)\$?(\d+)?$"                      # col-fila fin
)


def _evaluar_vlookup(formula: str, wb, ws_actual):
    """
    Evalúa una fórmula VLOOKUP simple en Python sin necesidad del caché de Excel.

    Soporta:
        =VLOOKUP(A4, 'Hoja con espacios'!$B$2:$C$362, 2, FALSE)
        =VLOOKUP(A4, Mapeo!A:B, 2, 0)
        =VLOOKUP("literal", Hoja!A:B, 2, FALSE)

    Solo coincidencia exacta (asume el 4to parámetro = FALSE).
    Retorna el valor encontrado o None si no se pudo evaluar / no encontró.
    """
    m = _VLOOKUP_RE.match(formula.strip())
    if not m:
        return None

    lookup_ref, range_ref, col_idx_str = (
        m.group(1).strip(), m.group(2).strip(), m.group(3)
    )
    col_idx = int(col_idx_str)

    # 1. Resolver el valor a buscar
    lookup_value = _resolver_referencia_celda(lookup_ref, wb, ws_actual)
    if lookup_value is None:
        return None

    # 2. Parsear el rango
    range_m = _RANGO_RE.match(range_ref)
    if not range_m:
        return None

    sheet_name = range_m.group(1)
    if sheet_name and sheet_name.startswith("'") and sheet_name.endswith("'"):
        sheet_name = sheet_name[1:-1]

    from openpyxl.utils import column_index_from_string
    start_col = column_index_from_string(range_m.group(2))
    start_row = int(range_m.group(3)) if range_m.group(3) else 1
    end_col = column_index_from_string(range_m.group(4))
    end_row_str = range_m.group(5)

    target_ws = wb[sheet_name] if sheet_name else ws_actual
    end_row = int(end_row_str) if end_row_str else target_ws.max_row

    # 3. Buscar lookup_value en la primera columna del rango
    lookup_str = str(lookup_value).strip()
    for row in range(start_row, end_row + 1):
        cell_val = target_ws.cell(row=row, column=start_col).value
        if cell_val is None:
            continue
        if str(cell_val).strip() == lookup_str:
            # Encontrado — retornar valor de la columna col_idx
            return_col = start_col + col_idx - 1
            if return_col > end_col:
                return None
            return target_ws.cell(row=row, column=return_col).value
    return None  # No encontrado


def leer_celda(ws, ws_valores, fila: int, col: int, wb=None):
    """
    Lee el valor de una celda. Si es fórmula:
      1. Intenta leer el valor cacheado por Excel (ws_valores, data_only=True).
      2. Si no hay caché y la fórmula es VLOOKUP → la evalúa en Python.
      3. Si todo falla → warning + None.
    """
    valor = ws.cell(row=fila, column=col).value
    if not (isinstance(valor, str) and valor.startswith("=")):
        return valor  # No es fórmula, lectura directa

    coord = ws.cell(row=fila, column=col).coordinate

    # 1. Cache de Excel
    if ws_valores is not None:
        valor_calc = ws_valores.cell(row=fila, column=col).value
        if valor_calc is not None:
            return valor_calc

    # 2. Fallback: evaluar VLOOKUP en Python
    if wb is not None and "VLOOKUP" in valor.upper():
        valor_eval = _evaluar_vlookup(valor, wb, ws)
        if valor_eval is not None:
            print(f"  🧮  Celda {coord}: fórmula evaluada en Python → {valor_eval!r}")
            return valor_eval

    # 3. No se pudo resolver
    print(f"  ⚠️   Celda {coord} tiene fórmula sin valor calculable:")
    print(f"         {valor}")
    print(f"         Soluciones: (a) abrir Excel, F9, Ctrl+S")
    print(f"                     (b) verificar que la fórmula sea VLOOKUP exacto")
    return None


def leer_datos_fila(ws, fila: int, columnas: dict[str, int],
                    ws_valores=None, wb=None) -> list[str]:
    datos = []
    for n in range(1, 21):
        header = f"{COL_DATO_PREFIX}{n}"
        col = columnas.get(header)
        if col is None:
            continue
        valor = leer_celda(ws, ws_valores, fila, col, wb=wb)
        if valor is None or str(valor).strip() == "":
            continue
        datos.append(str(valor).strip())
    return datos


def escribir_resultado(ws, fila: int, col_resultado: int, texto: str, ok: bool) -> None:
    cell = ws.cell(row=fila, column=col_resultado, value=texto)
    cell.fill = FILL_OK if ok else FILL_ERROR


# ===========================================================================
# FLUJO POR CASO — SIEMPRE PARTE DESDE EL HAMBURGUESA
# ===========================================================================


def preparar_estado_limpio(page: Page) -> None:
    """
    Asegura que NO haya pantallas, menús o modales abiertos antes de
    intentar abrir el menú hamburguesa para el próximo caso.

    Esto es crítico para que cada caso pueda partir desde cero, incluso
    si el caso anterior terminó en un estado inesperado.
    """
    # a) Modal app-modal
    _cerrar_app_modal_si_existe(page)

    # b) Notificación residual
    try:
        if is_notification_modal_visible(page) is not None:
            print("  🧹  Notificación residual — cerrándola…")
            handle_notification_modal(page, "_residual_")
    except Exception:
        pass

    # c) Pantalla activa abierta
    try:
        page.locator("div.tab.activable.active").first.wait_for(
            state="visible", timeout=1000
        )
        print("  🧹  Pantalla previa aún abierta — cerrándola…")
        cerrar_pantalla_layout(page)
    except PlaywrightTimeoutError:
        pass
    except Exception:
        pass

    # d) Menú abierto
    cerrar_menu_si_abierto(page)

    # e) Pausa breve para que Angular termine de renderizar
    page.wait_for_timeout(ENTRE_CASOS_PAUSA_MS)


# ---------------------------------------------------------------------------
# MÓDULOS POR TIPO DE PANTALLA
# ---------------------------------------------------------------------------
# Cada módulo se ejecuta DESPUÉS de que procesar_caso ya navegó a la pantalla,
# verificó que cargó y descartó la primera notificación de error (si hubo).
# Recibe la página activa, la ruta navegada y la lista de datos parseados.
# Retorna (ok: bool, texto_resultado: str).
#
# Por ahora son stubs documentados — imprimen los pasos que ejecutarían y
# retornan OK. Cuando definamos cada tipo en detalle, reemplazamos la lógica.
# ---------------------------------------------------------------------------


def procesar_consulta(page: Page, ruta: list[str], datos: list[str],
                      accion: Optional[str] = None) -> tuple[bool, str]:
    """
    Pantalla de Consulta (solo lectura). La acción se ignora si viene definida.

    Pasos que se implementarán:
      1. Verificar que la pantalla cargó (ya lo hizo procesar_caso).
      2. Si hay datos en Dato1..Dato20 → aplicar filtros [Frame].Field.Valor.
      3. Disparar 'Consultar' / 'Buscar' si existe el botón.
      4. Capturar resultados y registrar en log.
    """
    if accion:
        print(f"  ℹ️   [CONSULTA] acción '{accion}' ignorada — Consulta es solo lectura.")
    print(f"  📖  [CONSULTA] pantalla cargada — {len(datos)} filtro(s) en Excel.")
    for d in datos:
        print(f"        filtro pendiente: {d}")
    # TODO: aplicar filtros y disparar consultar
    return True, "OK (Consulta)"


def procesar_crud(page: Page, ruta: list[str], datos: list[str],
                  accion: Optional[str] = None) -> tuple[bool, str]:
    """
    Pantalla de Mantenedor CRUD. La acción determina el flujo:
      - Create: clic en '+', llenar campos, grabar
      - Read:   localizar registro existente con los datos como filtros
      - Update: localizar, editar campos, grabar
      - Delete: localizar, clic en eliminar/papelera, confirmar
    """
    if accion is None:
        return False, "ERROR_CONFIG: Acción requerida para CRUD (Create/Read/Update/Delete)"
    if accion not in ACCIONES_VALIDAS:
        return False, f"ERROR_CONFIG: Acción '{accion}' no válida para CRUD"

    print(f"  🗂   [CRUD/{accion}] pantalla cargada — {len(datos)} dato(s).")
    if accion == ACCION_CREATE:
        print(f"        TODO: clic en '+', llenar campos y grabar.")
    elif accion == ACCION_READ:
        print(f"        TODO: localizar registro usando los datos como filtro.")
    elif accion == ACCION_UPDATE:
        print(f"        TODO: localizar registro, editar campos, grabar.")
    elif accion == ACCION_DELETE:
        print(f"        TODO: localizar registro, clic en eliminar, confirmar.")
    for d in datos:
        print(f"        dato pendiente: {d}")
    # TODO: implementar cada flujo
    return True, f"OK (CRUD/{accion} - stub)"


def procesar_transaccion(page: Page, ruta: list[str], datos: list[str],
                         accion: Optional[str] = None) -> tuple[bool, str]:
    """
    Pantalla de Transacciones (operaciones). La acción determina el flujo:
      - Create: clic '+', llenar frames, grabar/procesar
      - Read:   localizar transacción existente
      - Update: localizar y modificar
      - Delete: localizar y anular/eliminar
    """
    if accion is None:
        return False, "ERROR_CONFIG: Acción requerida para Transacciones (Create/Read/Update/Delete)"
    if accion not in ACCIONES_VALIDAS:
        return False, f"ERROR_CONFIG: Acción '{accion}' no válida para Transacciones"

    print(f"  💼  [TRANSACCION/{accion}] pantalla cargada — {len(datos)} dato(s).")
    if accion == ACCION_CREATE:
        print(f"        TODO: clic '+', llenar frames, grabar/procesar.")
    elif accion == ACCION_READ:
        print(f"        TODO: localizar transacción existente.")
    elif accion == ACCION_UPDATE:
        print(f"        TODO: localizar transacción, modificar campos, grabar.")
    elif accion == ACCION_DELETE:
        print(f"        TODO: localizar transacción, anular/eliminar.")
    for d in datos:
        print(f"        dato pendiente: {d}")
    # TODO: implementar cada flujo
    return True, f"OK (Transacción/{accion} - stub)"


# Tabla de dispatch: tipo → función
DISPATCH_POR_TIPO = {
    TIPO_CONSULTA: procesar_consulta,
    TIPO_CRUD: procesar_crud,
    TIPO_TRANSACCIONES: procesar_transaccion,
}


def procesar_caso(page: Page, ruta: list[str], datos: list[str],
                  tipo: str = TIPO_DEFAULT,
                  accion: Optional[str] = None) -> tuple[bool, str]:
    """
    Procesa un caso individual. Retorna (ok, texto_resultado).

    Flujo:
        1. Estado limpio (cierra cualquier pantalla/menú/modal previo).
        2. Verifica que el botón hamburguesa esté visible.
        3. Hace clic en el hamburguesa.
        4. Navega la ruta completa.
        5. Espera la vista.
        6. Captura notificación de error (si la hay) y reporta.
        7. (Futuro) Llena los datos.
        8. Cierra la pantalla.
    """
    ruta_str = " > ".join(ruta)

    # 1. Estado limpio entre casos
    preparar_estado_limpio(page)

    # 2. Verificar que el hamburguesa esté visible
    try:
        page.locator("div.toggle.menu").first.wait_for(state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        return False, "FALLO_NAVEGACION: hamburguesa ≡ no visible (¿quedó algo abierto?)"

    # 3. Abrir hamburguesa (SIEMPRE, sin cortocircuito)
    try:
        abrir_menu_hamburguesa(page)
    except Exception as exc:
        return False, f"FALLO_NAVEGACION: no se pudo abrir el menú ({exc})"

    # 4. Navegar la ruta
    if not navegar_ruta_completa(page, ruta):
        return False, "FALLO_NAVEGACION: no se pudo recorrer la ruta completa"

    # 5. Esperar la vista
    try:
        page.locator("div.tab.activable.active").first.wait_for(
            state="visible", timeout=8000
        )
    except PlaywrightTimeoutError:
        notif = handle_notification_modal(page, ruta_str)
        if notif:
            return False, f"ERROR: {notif}"
        return False, "FALLO_NAVEGACION: la pantalla nunca apareció"

    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", ruta_str)[:MAX_FILENAME_LENGTH]
    screenshot(page, f"caso__{safe}")

    # 6. ¿Hay notificación de error inicial?
    notif = handle_notification_modal(page, ruta_str)
    if notif:
        try:
            cerrar_pantalla_layout(page)
        except Exception:
            pass
        return False, f"ERROR: {notif}"

    # 7. Dispatch al módulo según el tipo de pantalla
    handler = DISPATCH_POR_TIPO.get(tipo)
    if handler is None:
        try:
            cerrar_pantalla_layout(page)
        except Exception:
            pass
        return False, (f"ERROR_CONFIG: Tipo Pantalla '{tipo}' no válido. "
                       f"Usar: Consulta / CRUD / Transacciones")

    accion_log = f"/{accion}" if accion else ""
    print(f"  ▶  Dispatch → módulo '{tipo}{accion_log}'")
    try:
        ok, resultado = handler(page, ruta, datos, accion=accion)
    except Exception as exc:
        ok, resultado = False, f"EXCEPCION en módulo {tipo}: {exc}"
        try:
            screenshot(page, f"EXC_{tipo}_{safe}")
        except Exception:
            pass

    # 8. Cerrar pantalla
    cerrar_pantalla_layout(page)
    return ok, resultado


# ===========================================================================
# FLUJO PRINCIPAL
# ===========================================================================


def run() -> None:
    print("\n" + "=" * 60)
    print("  Automatización QA — Ejecución de Casos de Prueba")
    print("=" * 60)
    print(f"  URL base       : {config.BASE_URL}")
    print(f"  Headless       : {config.HEADLESS}")
    print(f"  Timeout        : {config.TIMEOUT_MS} ms")
    print(f"  Capturas       : {config.SCREENSHOTS_DIR}")
    print(f"  Excel casos    : {config.EXCEL_CASOS}")
    print(f"  ACTIVA_VENTANA : {config.ACTIVA_VENTANA}")
    print(f"  Tiempo ventana : {config.VENTANA_TIMEOUT_SEG} s")
    print("=" * 60 + "\n")

    if not config.EXCEL_CASOS.exists():
        print(f"❌  No se encontró el Excel: {config.EXCEL_CASOS}")
        sys.exit(1)

    print(f"▶ Abriendo Excel: {config.EXCEL_CASOS.name}")
    # Workbook normal — conserva fórmulas, sirve para escribir resultados
    wb = load_workbook(config.EXCEL_CASOS)
    ws = wb.active
    # Workbook "valores" — data_only=True devuelve el resultado calculado de las fórmulas
    # (siempre que Excel haya guardado el caché de valores en el archivo)
    try:
        wb_valores = load_workbook(config.EXCEL_CASOS, data_only=True)
        ws_valores = wb_valores[ws.title]
        print(f"  ✅  Modo dual: lectura con data_only=True (fórmulas → valores calculados)")
    except Exception as exc:
        print(f"  ⚠️   No se pudo abrir el Excel en modo data_only: {exc}")
        wb_valores = None
        ws_valores = None

    columnas = localizar_columnas(ws)
    col_camino = columnas[COL_CAMINO_HEADER]
    col_resultado = columnas[COL_RESULTADO_HEADER]
    col_tipo = columnas.get(COL_TIPO_HEADER)      # opcional
    col_accion = columnas.get(COL_ACCION_HEADER)  # opcional
    total_filas = ws.max_row - 1
    print(f"  ✅  Hoja: '{ws.title}' — {total_filas} caso(s) detectado(s).\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=BROWSER_SLOW_MO_MS,
            args=["--start-maximized"],
        )
        context = browser.new_context(viewport=None, ignore_https_errors=True)
        context.set_default_timeout(config.TIMEOUT_MS)
        page = context.new_page()

        exitosos: list[str] = []
        fallidos: list[str] = []

        try:
            print("▶ Cargando URL y login…")
            page.goto(config.BASE_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_MS)
            handle_login(page)
            print()

            for fila in range(2, ws.max_row + 1):
                camino = leer_celda(ws, ws_valores, fila, col_camino, wb=wb)
                if camino is None or str(camino).strip() == "":
                    print(f"[Fila {fila}] (vacía) — se omite")
                    continue

                ruta = parse_camino(str(camino))
                ruta_str = " > ".join(ruta)

                if col_tipo is not None:
                    tipo_raw = leer_celda(ws, ws_valores, fila, col_tipo, wb=wb)
                    tipo = normalizar_tipo(tipo_raw)
                else:
                    tipo = TIPO_DEFAULT

                # Leer Acción (opcional). Solo se valida para tipos que la requieren.
                accion = None
                if col_accion is not None:
                    accion_raw = leer_celda(ws, ws_valores, fila, col_accion, wb=wb)
                    accion = normalizar_accion(accion_raw)

                etiqueta_accion = f"/{accion}" if accion else ""
                print(f"\n{'─'*60}")
                print(f"[Fila {fila}] [{tipo}{etiqueta_accion}] {ruta_str}")
                print(f"{'─'*60}")

                datos = leer_datos_fila(ws, fila, columnas,
                                        ws_valores=ws_valores, wb=wb)

                try:
                    ok, resultado = procesar_caso(page, ruta, datos,
                                                  tipo=tipo, accion=accion)
                except Exception as exc:
                    ok, resultado = False, f"EXCEPCION: {exc}"
                    try:
                        screenshot(page, f"EXC_fila{fila}")
                    except Exception:
                        pass
                    try:
                        preparar_estado_limpio(page)
                    except Exception:
                        pass

                print(f"  → {resultado}")
                escribir_resultado(ws, fila, col_resultado, resultado, ok)

                try:
                    wb.save(config.EXCEL_CASOS)
                except PermissionError:
                    print(
                        f"  ⚠️   No se pudo guardar el Excel "
                        f"(¿lo tienes abierto en Excel?). Continuando."
                    )

                (exitosos if ok else fallidos).append(ruta_str)

                if config.ACTIVA_VENTANA:
                    motivo = ventana_avanzar(
                        timeout_seg=config.VENTANA_TIMEOUT_SEG,
                        titulo_caso=ruta_str,
                    )
                    print(f"  ▶   Continuando ({motivo}).")

            print(f"\n{'='*60}")
            print(f"  ✅  Casos exitosos : {len(exitosos)}")
            print(f"  ❌  Casos fallidos : {len(fallidos)}")
            print(f"{'='*60}")

        except Exception as exc:
            print(f"\n❌  Error fatal: {exc}", file=sys.stderr)
            try:
                screenshot(page, "FATAL_ERROR")
            except Exception:
                pass
            raise
        finally:
            try:
                wb.save(config.EXCEL_CASOS)
                print(f"\n💾  Excel guardado: {config.EXCEL_CASOS}")
            except Exception as exc:
                print(f"\n⚠️   No se pudo guardar el Excel al cerrar: {exc}")
            wb.close()
            if wb_valores is not None:
                wb_valores.close()

            context.close()
            browser.close()


if __name__ == "__main__":
    run()
   tipo_raw = leer_celda(ws, ws_valores, fila, col_tipo, wb=wb)
                    tipo = normalizar_tipo(tipo_raw)
                else:
                    tipo = TIPO_DEFAULT

                accion = None
                if col_accion is not None:
                    accion_raw = leer_celda(ws, ws_valores, fila, col_accion, wb=wb)
                    accion = normalizar_accion(accion_raw)

                etiqueta_accion = f"/{accion}" if accion else ""
                print(f"\n{'─'*60}")
                print(f"[Fila {fila}] [{tipo}{etiqueta_accion}] {ruta_str}")
                print(f"{'─'*60}")

                datos = leer_datos_fila(ws, fila, columnas,
                                        ws_valores=ws_valores, wb=wb)

                try:
                    ok, resultado = procesar_caso(page, ruta, datos,
                                                  tipo=tipo, accion=accion)
                except Exception as exc:
                    ok, resultado = False, f"EXCEPCION: {exc}"
                    try:
                        screenshot(page, f"EXC_fila{fila}")
                    except Exception:
                        pass
                    try:
                        preparar_estado_limpio(page)
                    except Exception:
                        pass

                print(f"  → {resultado}")
                escribir_resultado(ws, fila, col_resultado, resultado, ok)

                try:
                    wb.save(config.EXCEL_CASOS)
                except PermissionError:
                    print(f"  ⚠️   No se pudo guardar el Excel (¿lo tienes abierto?).")

                (exitosos if ok else fallidos).append(ruta_str)

                if config.ACTIVA_VENTANA:
                    motivo = ventana_avanzar(
                        timeout_seg=config.VENTANA_TIMEOUT_SEG,
                        titulo_caso=ruta_str,
                    )
                    print(f"  ▶   Continuando ({motivo}).")

            print(f"\n{'='*60}")
            print(f"  ✅  Casos exitosos : {len(exitosos)}")
            print(f"  ❌  Casos fallidos : {len(fallidos)}")
            print(f"{'='*60}")

        except Exception as exc:
            print(f"\n❌  Error fatal: {exc}", file=sys.stderr)
            try:
                screenshot(page, "FATAL_ERROR")
            except Exception:
                pass
            raise
        finally:
            try:
                wb.save(config.EXCEL_CASOS)
                print(f"\n💾  Excel guardado: {config.EXCEL_CASOS}")
            except Exception as exc:
                print(f"\n⚠️   No se pudo guardar el Excel al cerrar: {exc}")
            wb.close()
            if wb_valores is not None:
                wb_valores.close()

            context.close()
            browser.close()


if __name__ == "__main__":
    run()
