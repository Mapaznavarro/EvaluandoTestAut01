await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);

VM97:1 Uncaught ReferenceError: page is not defined
    at <anonymous>:1:1

console.log(document.documentElement.outerHTML);

console.log(new XMLSerializer().serializeToString(document));

''''
<div _ngcontent-ng-c4036937797="" class="text xl"> Golf </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Participes LATAM </div>
<div _ngcontent-ng-c4036937797="" class="text xl">  FrontOn Gestión </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Ajustes </div>
