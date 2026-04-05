await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);

VM97:1 Uncaught ReferenceError: page is not defined
    at <anonymous>:1:1

console.log(document.documentElement.outerHTML);

console.log(new XMLSerializer().serializeToString(document));
