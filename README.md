# EvaluandoTestAut01

Repositorio de demostración para mostrar **vaciados de DOM** (*DOM snapshots*) de un sitio web y descubrir la mejor manera de **automatizar ejecución de pruebas** con [Playwright](https://playwright.dev/).

---

## 🎯 Objetivo

Mostrar cómo extraer el DOM de un sitio web — incluyendo el árbol de accesibilidad ARIA, el HTML completo y la lista de elementos interactivos — y usar esa información para escribir pruebas automatizadas precisas y mantenibles.

---

## 📁 Estructura del proyecto

```
EvaluandoTestAut01/
├── sample-site/               # Sitio web de muestra (HTML estático)
│   ├── index.html             #   Página de inicio con catálogo de productos
│   ├── login.html             #   Página de inicio de sesión
│   └── carrito.html           #   Página del carrito de compras
│
├── scripts/
│   ├── extract-dom.js         # Script principal de extracción de DOM
│   └── server.js              # Servidor HTTP estático (usado por Playwright)
│
├── tests/
│   ├── inicio.spec.js         # Pruebas automatizadas — Página de inicio
│   ├── login.spec.js          # Pruebas automatizadas — Login
│   └── carrito.spec.js        # Pruebas automatizadas — Carrito
│
├── dom-snapshots/             # Vaciados de DOM generados (ver abajo)
│
└── playwright.config.js       # Configuración de Playwright
```

---

## 🚀 Requisitos previos

- [Node.js](https://nodejs.org/) v18 o superior
- npm (incluido con Node.js)

---

## ⚙️ Instalación

```bash
# 1. Instalar dependencias
npm install

# 2. Instalar el navegador de Playwright
npx playwright install chromium
```

---

## 📸 Extracción de DOM (vaciados)

El script `scripts/extract-dom.js` navega cada página del sitio de muestra y genera tres archivos por página en el directorio `dom-snapshots/`:

| Archivo | Descripción |
|---|---|
| `<pagina>-aria-snapshot.yaml` | Árbol de accesibilidad ARIA — ideal para identificar selectores de prueba |
| `<pagina>-dom.html` | HTML completo tal como lo ve el navegador |
| `<pagina>-interactivos.json` | Lista de todos los elementos interactivos con sus atributos |

### Ejecutar la extracción

```bash
npm run extract-dom
```

### Ejemplo de salida — ARIA snapshot de Login (`dom-snapshots/login-aria-snapshot.yaml`)

```yaml
- banner:
  - heading "Tienda Demo" [level=1]
  - navigation:
    - link "Inicio"
    - link "Iniciar sesión"
    - link "Carrito (0)"
- heading "Iniciar sesión" [level=2]
- textbox "Usuario"
- textbox "Contraseña"
- button "Ingresar"
```

### Ejemplo — Elementos interactivos (`dom-snapshots/login-interactivos.json`)

```json
[
  { "tag": "input", "tipo": "text",     "id": "usuario",    "placeholder": "Tu nombre de usuario" },
  { "tag": "input", "tipo": "password", "id": "contrasena", "placeholder": "Tu contraseña" },
  { "tag": "button","tipo": "submit",   "id": "btn-ingresar","texto": "Ingresar" }
]
```

El snapshot ARIA y la lista de interactivos revelan directamente qué selectores usar en las pruebas: IDs (`#usuario`, `#btn-ingresar`), roles ARIA (`button`, `textbox`) y atributos accesibles.

---

## ✅ Ejecutar las pruebas automatizadas

Las pruebas están en el directorio `tests/` y fueron escritas **a partir de los vaciados de DOM** generados por el script de extracción.

```bash
# Ejecutar todas las pruebas (modo headless)
npm test

# Ejecutar con navegador visible
npm run test:headed

# Ver el reporte HTML
npm run test:report
```

### Resultado esperado

```
Running 27 tests using 1 worker

  ✓  Página de Carrito › muestra el título de la página
  ✓  Página de Carrito › muestra la tabla del carrito con encabezados correctos
  ✓  Página de Carrito › muestra dos productos en el carrito
  ...
  ✓  Página de Login › login exitoso con credenciales válidas
  ✓  Página de Login › login fallido con credenciales inválidas
  ...
  27 passed (4.5s)
```

---

## 🔎 De DOM a prueba: flujo de trabajo

```
1. npm run extract-dom
        ↓
   dom-snapshots/
   ├── login-aria-snapshot.yaml   ← identificar roles y textos
   ├── login-interactivos.json    ← descubrir IDs y tipos de input
   └── login-dom.html             ← explorar la estructura HTML

2. Analizar los snapshots para elegir selectores robustos:
   - Preferir IDs únicos (#usuario, #btn-ingresar)
   - Usar roles ARIA cuando no hay ID (role=button, role=textbox)
   - Evitar selectores CSS frágiles basados en clases de estilo

3. Escribir pruebas en tests/ usando los selectores identificados

4. npm test  ← validar que todo funciona
```

---

## 🧰 Tecnologías

- **[Playwright](https://playwright.dev/)** — automatización de navegador y extracción de snapshots ARIA
- **HTML/CSS** — sitio de muestra sin frameworks adicionales
- **Node.js** — entorno de ejecución
