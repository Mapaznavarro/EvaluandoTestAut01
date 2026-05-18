"""
config.py
---------
Carga la configuración desde el archivo .env (o variables de entorno del sistema).
Crear el archivo .env copiando .env.example y completando los valores reales.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carga el archivo .env desde el mismo directorio que este script
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key, str(default)).strip().lower()
    return val not in ("false", "0", "no", "off")


def _get_si(key: str, default: bool = False) -> bool:
    """
    Variante estricta: retorna True SOLO si el valor es 'si' / 'sí' / 'yes' / 'true' / '1'.
    Útil para variables como ACTIVA_VENTANA donde 'Si' debe activarla y cualquier
    otro texto (No, vacío, mayúsculas raras) debe desactivarla.
    """
    val = os.getenv(key, "").strip().lower()
    if val == "":
        return default
    return val in ("si", "sí", "yes", "true", "1", "y", "s")


# URL base del sitio
BASE_URL: str = os.getenv("BASE_URL", "http://172.21.170.81/home")

# Credenciales
APP_USERNAME: str = os.getenv("APP_USERNAME", "")
APP_PASSWORD: str = os.getenv("APP_PASSWORD", "")

# Modo headless: False → ventana visible para el usuario
HEADLESS: bool = _get_bool("HEADLESS", False)

# Timeout por defecto para esperar elementos (ms)
TIMEOUT_MS: int = int(os.getenv("TIMEOUT_MS", "15000"))

# Directorio donde se guardan capturas de pantalla
SCREENSHOTS_DIR: Path = Path(__file__).parent / os.getenv("SCREENSHOTS_DIR", "screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Pausa (ms) para observar cada vista del PASO 2 antes de continuar
PASO2_VISTA_PAUSA_MS: int = int(os.getenv("PASO2_VISTA_PAUSA_MS", "2000"))

PAUSE_PANTALLA_MS: int = int(os.getenv("PAUSE_PANTALLA_MS", "3000"))

# ---------------------------------------------------------------------------
# Configuración — Ejecución de Casos de Prueba con Datos de Entrada
# ---------------------------------------------------------------------------

# Excel con los casos de prueba
_EXCEL_CASOS_RAW: str = os.getenv("EXCEL_CASOS", "casos_prueba.xlsx")
_excel_path = Path(_EXCEL_CASOS_RAW)
if not _excel_path.is_absolute():
    _excel_path = Path(__file__).parent / _excel_path
EXCEL_CASOS: Path = _excel_path

# ¿Mostrar la ventana "Avanzar" entre cada caso?
ACTIVA_VENTANA: bool = _get_si("ACTIVA_VENTANA", default=False)

# Tiempo (segundos) que la ventana espera antes de auto-cerrarse
VENTANA_TIMEOUT_SEG: int = int(os.getenv("VENTANA_TIMEOUT_SEG", "20"))
