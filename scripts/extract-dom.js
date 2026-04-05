/**
 * extract-dom.js
 *
 * Script para extraer vaciados (dumps) del DOM de las páginas del sitio de muestra.
 * Genera:
 *  - Snapshot de accesibilidad (ARIA) → útil para identificar selectores en pruebas
 *  - HTML completo del DOM → útil para análisis estructural
 *  - Lista de elementos interactivos → útil para planificar casos de prueba
 *
 * Uso:
 *   node scripts/extract-dom.js
 *
 * Los archivos se guardan en dom-snapshots/
 */

'use strict';

const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const PAGES = [
  { nombre: 'inicio',  archivo: 'index.html' },
  { nombre: 'login',   archivo: 'login.html' },
  { nombre: 'carrito', archivo: 'carrito.html' },
];

const SITE_BASE = path.resolve(__dirname, '..', 'sample-site');
const OUTPUT_DIR = path.resolve(__dirname, '..', 'dom-snapshots');

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined,
    headless: true,
  });

  try {
    for (const pagina of PAGES) {
      const url = `file://${SITE_BASE}/${pagina.archivo}`;
      console.log(`\n📄 Procesando: ${url}`);

      const page = await browser.newPage();
      await page.goto(url, { waitUntil: 'domcontentloaded' });

      // 1. Snapshot de accesibilidad (ARIA tree) ─────────────────────────────
      const ariaSnapshot = await page.ariaSnapshot();
      const ariaFile = path.join(OUTPUT_DIR, `${pagina.nombre}-aria-snapshot.yaml`);
      fs.writeFileSync(ariaFile, ariaSnapshot, 'utf8');
      console.log(`  ✅ ARIA snapshot → ${path.relative(process.cwd(), ariaFile)}`);

      // 2. HTML completo del DOM ──────────────────────────────────────────────
      const htmlContent = await page.content();
      const htmlFile = path.join(OUTPUT_DIR, `${pagina.nombre}-dom.html`);
      fs.writeFileSync(htmlFile, htmlContent, 'utf8');
      console.log(`  ✅ HTML DOM       → ${path.relative(process.cwd(), htmlFile)}`);

      // 3. Lista de elementos interactivos ───────────────────────────────────
      const interactivos = await page.evaluate(() => {
        const SELECTORES = [
          'a', 'button', 'input', 'select', 'textarea',
          '[role="button"]', '[role="link"]', '[role="checkbox"]',
          '[role="radio"]', '[role="textbox"]', '[tabindex]',
        ];

        const elementos = [];
        const vistos = new WeakSet();

        for (const selector of SELECTORES) {
          document.querySelectorAll(selector).forEach((el) => {
            if (vistos.has(el)) return;
            vistos.add(el);

            const rect = el.getBoundingClientRect();
            elementos.push({
              tag: el.tagName.toLowerCase(),
              tipo: el.getAttribute('type') || null,
              id: el.id || null,
              nombre: el.getAttribute('name') || null,
              clases: el.className || null,
              ariaLabel: el.getAttribute('aria-label') || null,
              rol: el.getAttribute('role') || null,
              texto: (el.textContent || '').trim().substring(0, 80) || null,
              placeholder: el.getAttribute('placeholder') || null,
              href: el.getAttribute('href') || null,
              visible: rect.width > 0 && rect.height > 0,
            });
          });
        }

        return elementos;
      });

      const interactivosFile = path.join(OUTPUT_DIR, `${pagina.nombre}-interactivos.json`);
      fs.writeFileSync(interactivosFile, JSON.stringify(interactivos, null, 2), 'utf8');
      console.log(`  ✅ Interactivos   → ${path.relative(process.cwd(), interactivosFile)} (${interactivos.length} elementos)`);

      await page.close();
    }

    // 4. Índice de resumen ────────────────────────────────────────────────────
    const resumen = {
      generadoEn: new Date().toISOString(),
      paginas: PAGES.map((p) => ({
        nombre: p.nombre,
        archivos: {
          ariaSnapshot: `${p.nombre}-aria-snapshot.yaml`,
          domHtml: `${p.nombre}-dom.html`,
          interactivos: `${p.nombre}-interactivos.json`,
        },
      })),
    };

    const resumenFile = path.join(OUTPUT_DIR, 'resumen.json');
    fs.writeFileSync(resumenFile, JSON.stringify(resumen, null, 2), 'utf8');
    console.log(`\n📋 Resumen → ${path.relative(process.cwd(), resumenFile)}`);

  } finally {
    await browser.close();
  }

  console.log('\n✨ Extracción de DOM completada. Revisa el directorio dom-snapshots/\n');
}

main().catch((err) => {
  console.error('❌ Error durante la extracción:', err);
  process.exit(1);
});
