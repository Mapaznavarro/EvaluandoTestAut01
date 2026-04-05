// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Pruebas de la página de Carrito (carrito.html)
 *
 * Estos tests fueron escritos a partir del vaciado de DOM obtenido con:
 *   node scripts/extract-dom.js
 *
 * Demuestra cómo el snapshot de elementos interactivos identifica
 * los botones y la tabla que deben validarse.
 */

test.describe('Página de Carrito', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('carrito.html');
  });

  test('muestra el título de la página', async ({ page }) => {
    await expect(page).toHaveTitle('Carrito - Tienda Demo');
    await expect(page.locator('main h2')).toHaveText('Tu carrito');
  });

  test('muestra la tabla del carrito con encabezados correctos', async ({ page }) => {
    const encabezados = page.locator('#tabla-carrito thead th');
    await expect(encabezados).toHaveCount(4);
    await expect(encabezados.nth(0)).toHaveText('Producto');
    await expect(encabezados.nth(1)).toHaveText('Precio');
    await expect(encabezados.nth(2)).toHaveText('Cantidad');
    await expect(encabezados.nth(3)).toHaveText('Acciones');
  });

  test('muestra dos productos en el carrito', async ({ page }) => {
    const filas = page.locator('#filas-carrito tr');
    await expect(filas).toHaveCount(2);
  });

  test('muestra el total del carrito', async ({ page }) => {
    await expect(page.locator('#total-carrito')).toBeVisible();
    await expect(page.locator('#total-carrito')).toHaveText('$88.99');
  });

  test('muestra el botón de Finalizar compra', async ({ page }) => {
    const btnComprar = page.locator('#btn-comprar');
    await expect(btnComprar).toBeVisible();
    await expect(btnComprar).toHaveText('Finalizar compra');
  });

  test('cada fila tiene un botón Eliminar', async ({ page }) => {
    const botones = page.locator('#filas-carrito .acciones button');
    await expect(botones).toHaveCount(2);
    for (const boton of await botones.all()) {
      await expect(boton).toHaveText('Eliminar');
    }
  });

  test('la tabla tiene el atributo aria-label correcto', async ({ page }) => {
    await expect(page.locator('#tabla-carrito')).toHaveAttribute('aria-label', 'Productos en el carrito');
  });

  test('los precios de los productos están presentes', async ({ page }) => {
    const precios = page.locator('#filas-carrito .precio');
    await expect(precios).toHaveCount(2);
    await expect(precios.nth(0)).toHaveText('$19.99');
    await expect(precios.nth(1)).toHaveText('$34.50');
  });
});
