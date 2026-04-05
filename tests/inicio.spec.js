// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Pruebas de la página de inicio (index.html)
 *
 * Estos tests fueron escritos a partir del vaciado de DOM obtenido con:
 *   node scripts/extract-dom.js
 *
 * Los selectores utilizados reflejan directamente los ids, roles y
 * atributos aria encontrados en el snapshot de accesibilidad.
 */

test.describe('Página de Inicio', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('index.html');
  });

  test('muestra el título principal de la tienda', async ({ page }) => {
    await expect(page).toHaveTitle('Tienda Demo - EvaluandoTestAut01');
    await expect(page.locator('header h1')).toHaveText('Tienda Demo');
  });

  test('muestra los enlaces de navegación', async ({ page }) => {
    await expect(page.locator('#nav-inicio')).toBeVisible();
    await expect(page.locator('#nav-login')).toBeVisible();
    await expect(page.locator('#nav-carrito')).toBeVisible();
  });

  test('muestra la barra de búsqueda con su botón', async ({ page }) => {
    const campoBusqueda = page.locator('#busqueda');
    const btnBuscar = page.locator('#btn-buscar');

    await expect(campoBusqueda).toBeVisible();
    await expect(btnBuscar).toBeVisible();
    await expect(btnBuscar).toHaveText('Buscar');
  });

  test('permite escribir en el campo de búsqueda', async ({ page }) => {
    const campoBusqueda = page.locator('#busqueda');
    await campoBusqueda.fill('Producto A');
    await expect(campoBusqueda).toHaveValue('Producto A');
  });

  test('muestra tres tarjetas de producto', async ({ page }) => {
    const tarjetas = page.locator('.product-card');
    await expect(tarjetas).toHaveCount(3);
  });

  test('cada tarjeta de producto tiene botón Agregar al carrito', async ({ page }) => {
    const botones = page.locator('.btn-agregar');
    await expect(botones).toHaveCount(3);
    for (const boton of await botones.all()) {
      await expect(boton).toHaveText('Agregar al carrito');
    }
  });

  test('los precios de los productos están visibles', async ({ page }) => {
    const precios = page.locator('.product-card .price');
    await expect(precios).toHaveCount(3);
    for (const precio of await precios.all()) {
      await expect(precio).toBeVisible();
    }
  });

  test('muestra el pie de página', async ({ page }) => {
    await expect(page.locator('#pie-pagina')).toBeVisible();
  });

  test('el enlace de Inicio navega a index.html', async ({ page }) => {
    await page.locator('#nav-inicio').click();
    await expect(page).toHaveURL(/index\.html/);
  });

  test('el enlace de Iniciar sesión navega a login.html', async ({ page }) => {
    await page.locator('#nav-login').click();
    await expect(page).toHaveURL(/login\.html/);
  });
});
