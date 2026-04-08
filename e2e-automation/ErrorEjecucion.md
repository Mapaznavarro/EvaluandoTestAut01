============================================================
  Automatización E2E – Click de 3 opciones de menú (sin recursividad)
============================================================
  URL base  : http://172.21.170.81/home
  Headless  : False
  Timeout   : 15000 ms
  Capturas  : B:\Users\gather\python\e2e-automation\screenshots
============================================================

▶ Paso 1: Abriendo la URL…
  📸  Captura guardada: 20260408_175604_00_home.png
  ✅  Página cargada: http://172.21.170.81/login

▶ Paso 2: Verificando login…
  🔐  Pantalla de login detectada. Ingresando credenciales…
  📸  Captura guardada: 20260408_175605_01_before_login.png
  ✅  Clic en 'botón de login' usando: button[type='submit']
  ✅  Login completado.
  📸  Captura guardada: 20260408_175605_02_after_login.png
  🧾  DOM guardado: 20260408_175606_dom-after-login.html

▶ Paso 3: Click en 3 opciones del menú (sin recursividad)…
  ✅  Clic en 'menú hamburguesa' usando: css=div.toggle.menu
  📸  Captura guardada: 20260408_175609_03_menu_abierto.png
  🧾  DOM guardado: 20260408_175609_dom-menu-abierto.html

▶ Opción 1/3: Golf
Traceback (most recent call last):
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 312, in run
    run_click_only_three_menu_options(page)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 257, in run_click_only_three_menu_options
    open_hamburger_menu(page)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 198, in open_hamburger_menu
    wait_and_click(page, HAMBURGER_SELECTORS, "menú hamburguesa")
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 107, in wait_and_click
    locator.wait_for(state="visible", timeout=t)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "B:\Users\gather\python\Lib\site-packages\playwright\sync_api\_generated.py", line 18074, in wait_for
    self._sync(self._impl_obj.wait_for(timeout=timeout, state=state))
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "B:\Users\gather\python\Lib\site-packages\playwright\_impl\_sync_base.py", line 113, in _sync
    self._dispatcher_fiber.switch()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "B:\Users\gather\python\Lib\site-packages\playwright\sync_api\_context_manager.py", line 56, in greenlet_main
    self._loop.run_until_complete(self._connection.run_as_sync())
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "asyncio\base_events.py", line 712, in run_until_complete
  File "asyncio\base_events.py", line 683, in run_forever
  File "asyncio\base_events.py", line 2012, in _run_once
  File "asyncio\windows_events.py", line 446, in select
  File "asyncio\windows_events.py", line 775, in _poll
KeyboardInterrupt

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 332, in <module>
    run()
    ~~~^^
  File "B:\Users\gather\python\e2e-automation\run_all_menusIncremental.py", line 327, in run
    context.close()
    ~~~~~~~~~~~~~^^
  File "B:\Users\gather\python\Lib\site-packages\playwright\sync_api\_generated.py", line 13552, in close
    return mapping.from_maybe_impl(self._sync(self._impl_obj.close(reason=reason)))
                                   ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "B:\Users\gather\python\Lib\site-packages\playwright\_impl\_sync_base.py", line 113, in _sync
    self._dispatcher_fiber.switch()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
KeyboardInterrupt
Future exception was never retrieved
future: <Future finished exception=TargetClosedError('Target page, context or browser has been closed')>
playwright._impl._errors.TargetClosedError: Target page, context or browser has been closed
Future exception was never retrieved
future: <Future finished exception=TargetClosedError('Target page, context or browser has been closed')>
playwright._impl._errors.TargetClosedError: Target page, context or browser has been closed
PS B:\Users\gather\python\e2e-automation> ^C
PS B:\Users\gather\python\e2e-automation>
