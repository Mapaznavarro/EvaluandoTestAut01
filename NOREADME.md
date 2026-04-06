await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);

VM97:1 Uncaught ReferenceError: page is not defined
    at <anonymous>:1:1

console.log(document.documentElement.outerHTML);

console.log(new XMLSerializer().serializeToString(document));

'Buscando los selectores
<div _ngcontent-ng-c4036937797="" class="text xl"> Golf </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Participes LATAM </div>
<div _ngcontent-ng-c4036937797="" class="text xl">  FrontOn Gestión </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Ajustes </div>

'Buscando los receptores de click's pegar esto en console
// 1. Encontrar todos los div.text.xl y mostrar su info completa
document.querySelectorAll('div.text.xl').forEach((el, i) => {
  console.log(`--- Ítem ${i} ---`);
  console.log('texto:', JSON.stringify(el.textContent));
  console.log('tag padre:', el.parentElement?.tagName, el.parentElement?.className);
  console.log('tag abuelo:', el.parentElement?.parentElement?.tagName, el.parentElement?.parentElement?.className);
  console.log('es clickeable (pointer-events):', getComputedStyle(el).pointerEvents);
  console.log('outerHTML del padre:', el.parentElement?.outerHTML?.substring(0, 300));
  console.log('');
});

=========================================
// Pega esto y presiona Enter
console.log("Total div.text.xl encontrados:", document.querySelectorAll('div.text.xl').length)
R =======================================
Total div.text.xl encontrados: 0

==========================================
// Buscar en todos los shadow roots
function queryAllShadow(selector, root = document) {
  let results = [...root.querySelectorAll(selector)];
  root.querySelectorAll('*').forEach(el => {
    if (el.shadowRoot) results = results.concat(queryAllShadow(selector, el.shadowRoot));
  });
  return results;
}

let items = queryAllShadow('div.text.xl');
console.log("Encontrados en Shadow DOM:", items.length);
items.forEach((el, i) => console.log(i, JSON.stringify(el.textContent.trim()), el.parentElement?.tagName, el.parentElement?.className));
R =======================================

=========================================
Array.from(document.querySelectorAll('div.text.xl')).map((el, i) => {
  let node = el;
  let path = [];
  for (let j = 0; j < 5; j++) {
    if (!node) break;
    path.push(node.tagName + (node.className ? '.' + node.className.trim().replace(/\s+/g, '.') : '') + (node.id ? '#' + node.id : ''));
    node = node.parentElement;
  }
  return { indice: i, texto: el.textContent.trim(), ruta_hacia_arriba: path };
});
R =========================================
[
    {
        "indice": 0,
        "texto": "Golf",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.first",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 1,
        "texto": "Participes LATAM",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 2,
        "texto": "FrontOn Gestión",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.last",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 3,
        "texto": "Ajustes",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.first.last",
            "DIV.bottom",
            "DIV.menu.xl"
        ]
    }
]

===============================================================
// Verificar que ui-menu-item es clickeable
Array.from(document.querySelectorAll('div.ui-menu-item')).map(el => ({
  texto: el.querySelector('div.text.xl')?.textContent.trim(),
  clase: el.className,
  cursor: getComputedStyle(el).cursor,
  pointer_events: getComputedStyle(el).pointerEvents
}));

Respuesta
[
    {
        "texto": "Golf",
        "clase": "ui-menu-item first",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "Participes LATAM",
        "clase": "ui-menu-item",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "FrontOn Gestión",
        "clase": "ui-menu-item last",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "Ajustes",
        "clase": "ui-menu-item first last",
        "cursor": "pointer",
        "pointer_events": "auto"
    }
]

===========================================================
COnfirmar que funcionan en consola
// Probar clic en Golf (debe navegar o cambiar la vista)
document.querySelector('div.ui-menu-item.first')?.click();

// Después de volver al menú, probar Participes LATAM
Array.from(document.querySelectorAll('div.ui-menu-item'))
  .find(el => el.querySelector('div.text.xl')?.textContent.trim() === 'Participes LATAM')
  ?.click();

// Después de volver al menú, probar FrontOn Gestión
document.querySelector('div.ui-menu-item.last')?.click();


