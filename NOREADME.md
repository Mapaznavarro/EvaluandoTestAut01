await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);
