# Automatización E2E – Golf > Maestros > Entidades

Automatización de navegación sobre el sitio interno usando **Python + Playwright**.

El script abre el navegador de forma **visible** (no headless), detecta si se
requiere login, ingresa credenciales desde variables de entorno y recorre la ruta:

> Inicio → Menú hamburguesa → **Golf** → **Maestros** → **Entidades** → **Entidades**

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python      | 3.10           |
| pip         | cualquiera     |

> **Windows**: asegúrate de que `python` y `pip` estén en el PATH del sistema.  
> **macOS/Linux**: puede ser necesario usar `python3` / `pip3`.

---

## Instalación

```bash
# 1. Entrar al directorio de la automatización
cd e2e-automation

# 2. (Opcional pero recomendado) Crear entorno virtual
..\python -m venv .venv

# Activar en Windows:
.venv\Scripts\activate

# Activar en macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Instalar el navegador Chromium de Playwright
playwright install chromium
```

---

## Configuración

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Editar `.env` con los valores reales:

```dotenv
BASE_URL=http://172.21.170.81/home
APP_USERNAME=your_username_here
APP_PASSWORD=your_password_here
HEADLESS=False
TIMEOUT_MS=15000
SCREENSHOTS_DIR=screenshots
```

> ⚠️ **El archivo `.env` está en `.gitignore` y NUNCA debe subirse al repositorio.**

---

## Ejecución

### Script 1 – Ruta fija: Golf > Maestros > Entidades

```bash
python run_golf_entidades.py
```

El script:

1. Abre Chromium de forma visible (ventana maximizada).  
2. Navega a `BASE_URL`.  
3. Si detecta pantalla de login, ingresa las credenciales del `.env`.  
4. Hace clic en el menú hamburguesa.  
5. Selecciona **Golf**.  
6. Selecciona **Maestros**.  
7. Selecciona **Entidades** (primera vez).  
8. Selecciona **Entidades** (segunda vez – pantalla final).  
9. Guarda capturas de pantalla en `screenshots/` a lo largo del flujo.  
10. Espera que el usuario presione **ENTER** antes de cerrar el navegador.

---

### Script 2 – Recorrido completo de todas las opciones del menú

```bash
python run_all_menus.py
```

El script:

1. Abre Chromium de forma visible (ventana maximizada).
2. Navega a `BASE_URL` y hace login si es necesario.
3. Abre el menú hamburguesa.
4. **Descubre dinámicamente** todos los ítems de menú visibles.
5. Hace clic en cada ítem, detecta sub-menús y los recorre de forma recursiva.
6. Toma una captura de pantalla en cada nodo del árbol de menú.
7. Al finalizar, imprime el árbol completo de rutas descubiertas y guarda un reporte en texto (`screenshots/menu_report.txt`).
8. Espera que el usuario presione **ENTER** antes de cerrar el navegador.

#### Parámetros ajustables

| Constante en `run_all_menus.py` | Por defecto | Descripción |
|---------------------------------|-------------|-------------|
| `MAX_DEPTH`                     | `5`         | Profundidad máxima de recursión del árbol de menú |
| `MENU_ITEM_SELECTORS`           | varios      | Selectores CSS para detectar ítems de menú; ajustar si la app usa otra estructura |
| `HAMBURGER_SELECTORS`           | varios      | Selectores del botón hamburguesa |

#### Salida generada

| Archivo                        | Contenido                                              |
|--------------------------------|--------------------------------------------------------|
| `screenshots/menu__<ruta>.png` | Captura por cada opción de menú visitada               |
| `screenshots/menu_report.txt`  | Lista de todas las rutas de menú descubiertas          |
| `screenshots/ERROR.png`        | Captura del estado de la página si el script falla     |

---

## Estructura del proyecto

```
e2e-automation/
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Excluye .env, screenshots/, traces/, etc.
├── requirements.txt          # Dependencias Python
├── config.py                 # Carga configuración desde .env
├── run_golf_entidades.py     # Script: ruta fija Golf > Maestros > Entidades
├── run_all_menus.py          # Script: recorrido dinámico de todo el menú
├── README.md                 # Este archivo
└── screenshots/              # Capturas generadas (ignoradas por git)
```

---

## Capturas de pantalla

Se guardan automáticamente en `screenshots/` con nombre:
`YYYYMMDD_HHMMSS_<paso>.png`

| Archivo                   | Momento                                      |
|---------------------------|----------------------------------------------|
| `00_home.png`             | Al cargar la URL inicial                     |
| `01_before_login.png`     | Antes de enviar credenciales (si aplica)     |
| `02_after_login.png`      | Tras el login exitoso                        |
| `03_hamburger_opened.png` | Menú hamburguesa abierto                     |
| `04_golf_selected.png`    | Tras hacer clic en Golf                      |
| `05_maestros_selected.png`| Tras hacer clic en Maestros                  |
| `06_entidades_1_selected.png` | Tras el primer clic en Entidades         |
| `07_entidades_final.png`  | Pantalla final de Entidades                  |
| `ERROR.png`               | Captura de error si el script falla          |

---

## Ajuste de selectores

Si el script no encuentra algún elemento, el mensaje de error indicará los
selectores que se intentaron. Los lugares clave donde ajustar son:

| Función                  | Archivo                   | Qué ajustar                              |
|--------------------------|---------------------------|------------------------------------------|
| `handle_login`           | `run_golf_entidades.py`   | Selectores del campo usuario/contraseña  |
| `click_hamburger_menu`   | `run_golf_entidades.py`   | Selector del botón hamburguesa           |
| `click_menu_option`      | `run_golf_entidades.py`   | Texto exacto de las opciones de menú     |

Para inspeccionar el HTML real del sitio, abre las DevTools del navegador
(F12 → pestaña Elements) y busca el elemento que falla.

---

## Solución de problemas

| Síntoma                                     | Solución                                           |
|---------------------------------------------|----------------------------------------------------|
| `APP_USERNAME o APP_PASSWORD no definidos`  | Verifica que `.env` existe y tiene los valores     |
| `No se pudo hacer clic en 'menú hamburguesa'` | Inspecciona el HTML y ajusta `click_hamburger_menu` |
| Timeout en algún paso                       | Aumenta `TIMEOUT_MS` en `.env` (p.ej. `30000`)    |
| El navegador se abre pero cierra inmediatamente | Ejecuta en modo debug con `HEADLESS=False`      |
| Error de instalación de Playwright          | Ejecuta `playwright install chromium` de nuevo     |
