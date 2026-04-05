// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Pruebas de la página de Login (login.html)
 *
 * Estos tests fueron escritos a partir del vaciado de DOM obtenido con:
 *   node scripts/extract-dom.js
 *
 * Demuestra cómo los snapshots ARIA e interactivos guían la escritura
 * de pruebas de autenticación.
 */

test.describe('Página de Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('login.html');
  });

  test('muestra el título del formulario de login', async ({ page }) => {
    await expect(page).toHaveTitle('Iniciar sesión - Tienda Demo');
    await expect(page.locator('.login-box h2')).toHaveText('Iniciar sesión');
  });

  test('el campo de usuario está visible y accesible', async ({ page }) => {
    const campoUsuario = page.locator('#usuario');
    await expect(campoUsuario).toBeVisible();
    await expect(campoUsuario).toHaveAttribute('placeholder', 'Tu nombre de usuario');
  });

  test('el campo de contraseña está visible y es tipo password', async ({ page }) => {
    const campoContrasena = page.locator('#contrasena');
    await expect(campoContrasena).toBeVisible();
    await expect(campoContrasena).toHaveAttribute('type', 'password');
  });

  test('el botón Ingresar está visible', async ({ page }) => {
    await expect(page.locator('#btn-ingresar')).toBeVisible();
    await expect(page.locator('#btn-ingresar')).toHaveText('Ingresar');
  });

  test('los mensajes de error y éxito están ocultos inicialmente', async ({ page }) => {
    await expect(page.locator('#mensaje-error')).toBeHidden();
    await expect(page.locator('#mensaje-exito')).toBeHidden();
  });

  test('login exitoso con credenciales válidas', async ({ page }) => {
    await page.locator('#usuario').fill('admin');
    await page.locator('#contrasena').fill('password123');
    await page.locator('#btn-ingresar').click();

    await expect(page.locator('#mensaje-exito')).toBeVisible();
    await expect(page.locator('#mensaje-error')).toBeHidden();
  });

  test('login fallido con credenciales inválidas', async ({ page }) => {
    await page.locator('#usuario').fill('usuario_incorrecto');
    await page.locator('#contrasena').fill('clave_incorrecta');
    await page.locator('#btn-ingresar').click();

    await expect(page.locator('#mensaje-error')).toBeVisible();
    await expect(page.locator('#mensaje-exito')).toBeHidden();
  });

  test('login fallido con contraseña vacía', async ({ page }) => {
    await page.locator('#usuario').fill('admin');
    await page.locator('#btn-ingresar').click();

    await expect(page.locator('#mensaje-error')).toBeVisible();
  });

  test('puede limpiar los campos y reintentar', async ({ page }) => {
    await page.locator('#usuario').fill('incorrecto');
    await page.locator('#contrasena').fill('mal');
    await page.locator('#btn-ingresar').click();

    await expect(page.locator('#mensaje-error')).toBeVisible();

    await page.locator('#usuario').clear();
    await page.locator('#contrasena').clear();
    await page.locator('#usuario').fill('admin');
    await page.locator('#contrasena').fill('password123');
    await page.locator('#btn-ingresar').click();

    await expect(page.locator('#mensaje-exito')).toBeVisible();
    await expect(page.locator('#mensaje-error')).toBeHidden();
  });
});
