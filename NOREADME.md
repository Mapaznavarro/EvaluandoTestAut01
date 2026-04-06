await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);

VM97:1 Uncaught ReferenceError: page is not defined
    at <anonymous>:1:1

console.log(document.documentElement.outerHTML);

console.log(new XMLSerializer().serializeToString(document));

''''
============================================================
  Automatización E2E – Recorrido completo del menú
============================================================
  URL base  : http://172.21.170.81/home
  Headless  : False
  Timeout   : 15000 ms
  Capturas  : B:\Users\gather\python\e2e-automation\screenshots
============================================================

▶ Paso 1: Abriendo la URL…
  📸  Captura guardada: 20260406_013749_00_home.png
  ✅  Página cargada: http://172.21.170.81/login

▶ Paso 2: Verificando login…
  🔐  Pantalla de login detectada. Ingresando credenciales…
  📸  Captura guardada: 20260406_013750_01_before_login.png
  ✅  Clic en 'botón de login' usando: button[type='submit']
  ✅  Login completado.
  📸  Captura guardada: 20260406_013750_02_after_login.png
  📸  DOM guardado: 20260406_013751_dom-after-login.html

▶ Paso 3: Abriendo menú hamburguesa…
  ✅  Clic en 'menú hamburguesa' usando: css=div.toggle.menu
  📸  Captura guardada: 20260406_013753_03_menu_abierto.png
  📸  DOM guardado: 20260406_013753_dom-menu-abierto.html

▶ Paso 4: Clickeando las tres opciones objetivo del menú…


▶ Paso 4: Clickeando opción de menú → 'Golf'
