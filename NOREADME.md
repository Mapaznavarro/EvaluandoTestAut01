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
