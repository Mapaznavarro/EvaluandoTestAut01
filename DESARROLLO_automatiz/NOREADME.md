// Snippet 10b — Ver qué requests se dispararon y el estado del DOM
(() => {
    window._snippet10_observer?.disconnect();
    return {
        // ¿Hubo requests de red? (indica si Angular hizo fetch)
        requests_disparados: window._snippet10_requests?.length ?? 0,
        requests_urls: (window._snippet10_requests ?? []).slice(0, 10),
        // Estado del tab activo
        tab_activo: document.querySelector('div.tab.activable.active')?.textContent.trim().substring(0, 60) ?? 'NINGUNO',
        // ¿Cuánto tardó en aparecer? (ver si es síncrono o asíncrono)
        menu_cerrado: !document.querySelector('div.menu-content')?.offsetParent,
        // Componente cargado
        componente_principal: document.querySelector('div.tab-content app-generic-form, div.tab-content app-dynamic-loader')?.tagName ?? 'NO ENCONTRADO'
    };
})();
Respuesta
{
    "requests_disparados": 32,
    "requests_urls": [
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h8419t74&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h8nbudia&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h8nbxwqs&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h96mi7zl&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h96mknzc&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h9px5xld&sid=2LlqOmfz50Y",
        "http://172.21.170.81/api/thunder/form-loader/get/golf/consultas/asientosdiariosCtb/asientosdiariosCtb",
        "http://172.21.170.81/api/thunder/client_conf/save-tabs",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=h9px8thi&sid=2LlqOmfz50Y",
        "http://172.21.170.81/socket/?session-id=2ab213b2-5711-4591-bb1d-39a52cee55e9&agent-type=THUNDER&agent-id=THUNDER-e41cde44-2079-4a39-a925-5bea26407e7f&EIO=4&transport=polling&t=ha97tjlo&sid=2LlqOmfz50Y"
    ],
    "tab_activo": "Asientos diarios",
    "menu_cerrado": false,
    "componente_principal": "APP-DYNAMIC-LOADER"
}


// Snippet 10 — Capturar qué evento dispara el clic en una hoja
// Ejecutar ANTES de hacer clic en "Asientos diarios"
(() => {
    const requests = [];
    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach(e => requests.push(e.name));
    });
    observer.observe({ entryTypes: ['resource'] });
    window._snippet10_requests = requests;
    window._snippet10_observer = observer;
    console.log('✅ Observer instalado — ahora haz clic en "Asientos diarios"');
})();
Respuesta
fragmentoComand1:11 ✅ Observer instalado — ahora haz clic en "Asientos diarios"
VM106 fragmentoComand1:1 undefined




Snippet en python
with open("run_all_menus_Pantalla.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines[990:1020], start=991):
    print(f"{i:4}: {line}", end="")
Respuesta
 991:             print()
 992:
 993:             # ── Paso 3: Abrir menú y recorrer ────────────────────────────
 994:             print("▶ Paso 3: Abriendo menú hamburguesa…")
 995:             open_hamburger_menu(page)
 996:             screenshot(page, "03_menu_abierto")
 997:             dump_dom(page, "dom-menu-abierto")  # <-- AGREGAR
 998:             print()
 999:
1000:             #print("▶ Paso 4: Clickeando las tres opciones objetivo del menú…\n")
1001:             #click_target_menu_items(page)
1002:
1003:             #print("▶ Paso 4: Capturando submenús de primer nivel…\n")
1004:             #capturar_submenus_nivel1(page)
1005:
1006:             #print("▶ Paso 4: Recorrido completo del menú…\n")
1007:             #recorrer_menu_completo(page)
1008:
1009:             # 4. Captura + DOM
1010:             screenshot(page, f"paso2__{safe}")
1011:             dump_dom(page, f"dom_paso2__{safe}")
1012:
1013:             exitosas += 1
1014:
1015:             # 4b. Pausa para observar la vista antes de continuar
1016:             page.wait_for_timeout(config.PASO2_VISTA_PAUSA_MS)
1017:
1018:             # 5. Cerrar pestaña y volver al estado inicial
1019:             volver_desde_hoja(page, ruta)
1020:
  
  
  
  
  
  ❌  Error durante la automatización: name 'safe' is not defined
Traceback (most recent call last):
  File "B:\Users\gather\python\e2e-automation\run_all_menus_Pantalla.py", line 1061, in <module>
    run()
    ~~~^^
  File "B:\Users\gather\python\e2e-automation\run_all_menus_Pantalla.py", line 1010, in run
    screenshot(page, f"paso2__{safe}")
                               ^^^^
NameError: name


// pestaña Asientos diarios abierta
// Snippet 9 — Cómo cerrar la pestaña activa
Array.from(document.querySelectorAll('div.tab.activable'))
  .filter(el => el.offsetParent !== null)
  .map(el => ({
    texto:        el.textContent.trim().substring(0, 60),
    clases:       el.className,
    tiene_close:  !!el.querySelector('div.close, button.close, span.close, [class*="close"]'),
    close_html:   el.querySelector('div.close, button.close, span.close, [class*="close"]')
                    ?.outerHTML.substring(0, 200) ?? 'N/A',
    html_tab:     el.outerHTML.substring(0, 300)
  }));
  Respuesta:
[
    {
        "texto": "Asientos diarios",
        "clases": "tab activable active",
        "tiene_close": true,
        "close_html": "<div _ngcontent-ng-c2920271696=\"\" class=\"close\"><svg _ngcontent-ng-c2920271696=\"\" class=\"svg-inline--fa fa-xmark fa-fw fa-sm\" aria-hidden=\"true\" focusable=\"false\" data-prefix=\"fal\" data-icon=\"xmark\" r",
        "html_tab": "<div _ngcontent-ng-c2920271696=\"\" draggable-item=\"\" class=\"tab activable active\" draggable=\"true\"><div _ngcontent-ng-c2920271696=\"\" draggable=\"false\" class=\"label not-selectable\"><div _ngcontent-ng-c2920271696=\"\" class=\"icon\"><svg _ngcontent-ng-c2920271696=\"\" class=\"svg-inline--fa fa-money-check fa-"
    }
]


// Snippet 8 — Contenido de la pestaña activa después de clic en hoja final
(() => {
  const tabContent = document.querySelector('div.tab-content');
  return {
    // Estructura interna del tab-content
    tab_content_html: tabContent?.innerHTML.substring(0, 500) ?? 'NO ENCONTRADO',
    // ¿Qué componente Angular cargó dentro?
    componentes_angular: Array.from(document.querySelectorAll(
      'div.tab-content *'
    ))
    .filter(el => el.tagName.includes('-') && el.offsetParent !== null)
    .map(el => ({
      tag:    el.tagName,
      clases: el.className,
      id:     el.id ?? '',
    })),
    // Pestañas abiertas (puede haber más de una)
    todas_las_tabs: Array.from(document.querySelectorAll(
      '.tab, app-ui-tab, [role="tab"]'
    ))
    .filter(el => el.offsetParent !== null)
    .map(el => ({
      texto:  el.textContent.trim().substring(0, 80),
      clases: el.className,
      tag:    el.tagName
    }))
  };
})();
Respuesta:
{
    "tab_content_html": "<div _ngcontent-ng-c135740549=\"\" class=\"content-block\"><app-dynamic-loader _ngcontent-ng-c135740549=\"\"><app-layout-tab _nghost-ng-c3180408634=\"\"><div _ngcontent-ng-c3180408634=\"\" class=\"container\"><app-layout-container _ngcontent-ng-c3180408634=\"\" _nghost-ng-c198808079=\"\"><div _ngcontent-ng-c198808079=\"\" class=\"container\"><app-rdlayout _ngcontent-ng-c198808079=\"\" _nghost-ng-c3588374777=\"\"><div _ngcontent-ng-c3588374777=\"\" class=\"container\"><div _ngcontent-ng-c3588374777=\"\" class=\"hover-block hid",
    "componentes_angular": [
        {
            "tag": "APP-DYNAMIC-LOADER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-LAYOUT-TAB",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-LAYOUT-CONTAINER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-RDLAYOUT",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-BOX",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-MODAL-CONTAINER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "OVERLAY-SCROLLBARS",
            "clases": "tabs",
            "id": ""
        },
        {
            "tag": "DND-DROP",
            "clases": "",
            "id": ""
        },
        {
            "tag": "DND-DROP-HOVER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "DND-DROP",
            "clases": "",
            "id": ""
        },
        {
            "tag": "DND-DROP-HOVER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-DYNAMIC-INIT-CONTAINER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-DYNAMIC-LOADER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-GENERIC-FORM",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-BLOCK-TEMPLATE",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-MODAL-CONTAINER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-RESIZER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-RESIZER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-RESIZER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-DYNAMIC-LIST-LOADER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-DYNAMIC-LIST",
            "clases": "",
            "id": ""
        },
        {
            "tag": "OVERLAY-SCROLLBARS",
            "clases": "menu-content",
            "id": ""
        },
        {
            "tag": "APP-LOADER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FABRIC",
            "clases": "",
            "id": ""
        },
        {
            "tag": "OVERLAY-SCROLLBARS",
            "clases": "form-content",
            "id": ""
        },
        {
            "tag": "APP-FORM-TYPE",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-ACCORDION",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-GROUP",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-MULTIPLE",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-DATE",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-DATE",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-SELECT",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-CHECKBOX",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-RADIO",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-RADIO",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-CHECKBOX",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-SELECT",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-NUMBER",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-CHECKBOX",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-RADIO",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-FIELD",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-RADIO",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-FORM-BUTTON",
            "clases": "",
            "id": ""
        },
        {
            "tag": "APP-SEPARATOR",
            "clases": "",
            "id": ""
        }
    ],
    "todas_las_tabs": [
        {
            "texto": "Asientos diarios",
            "clases": "tab activable active",
            "tag": "DIV"
        },
        {
            "texto": "Layout",
            "clases": "tab active",
            "tag": "DIV"
        }
    ]
}

// Snippet 7 — Estado del DOM y URL después de clic en una hoja final
(() => {
  return {
    url_actual: window.location.href,
    // ¿Se cerró el menú o sigue visible?
    menu_visible: !!document.querySelector('div.menu-content')?.offsetParent,
    // ¿Qué componente/vista cargó? Buscar el contenedor principal de contenido
    main_content: Array.from(document.querySelectorAll(
      'app-ui-tab, app-tab, .tab-content, .main-content, .workspace, router-outlet + *, main > *'
    ))
    .filter(el => el.offsetParent !== null)
    .map(el => ({
      tag:    el.tagName,
      clases: el.className,
      id:     el.id ?? '',
      hijos:  el.children.length
    })),
    // ¿Apareció alguna pestaña nueva?
    tabs: Array.from(document.querySelectorAll(
      '.tab, .tab-item, [role="tab"], app-ui-tab-item, .activable'
    ))
    .filter(el => el.offsetParent !== null)
    .map(el => ({
      texto:  el.textContent.trim().substring(0, 60),
      clases: el.className,
      activo: el.classList.contains('active')
    }))
  };
})();
Respuesta:
{
    "url_actual": "http://172.21.170.81/home",
    "menu_visible": false,
    "main_content": [
        {
            "tag": "CORE-HOME",
            "clases": "",
            "id": "",
            "hijos": 1
        },
        {
            "tag": "DIV",
            "clases": "tab-content",
            "id": "",
            "hijos": 1
        }
    ],
    "tabs": [
        {
            "texto": "Layout",
            "clases": "tab active",
            "activo": true
        }
    ]
}






Ejecuta el programa hasta que esté parado en el panel que muestra las hojas de Golf > Consultas > Contabilidad (donde están Asientos diarios, Asientos manuales, etc.) y ejecuta este snippet:

// Snippet 6 — Estructura de una hoja final (div.menu-options sin div.next)
Array.from(document.querySelectorAll('div.menu-options'))
  .filter(el => el.offsetParent !== null)
  .map(el => ({
    texto:        el.querySelector('div.text')?.textContent.trim() ?? '',
    tiene_next:   !!el.querySelector('div.next'),
    clases:       el.className,
    padre:        el.parentElement?.className ?? '',
    abuelo:       el.parentElement?.parentElement?.className ?? '',
    html:         el.outerHTML.substring(0, 300)
  }));
Respuesta:
[
    {
        "texto": "Asientos diarios",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-money-check fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false"
    },
    {
        "texto": "Asientos manuales",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-calendar-week fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"fal"
    },
    {
        "texto": "Comparativa de cuentas",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-file-pdf fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false\" d"
    },
    {
        "texto": "Comparativa de saldos a fecha",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-calendar-week fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"fal"
    },
    {
        "texto": "Consulta informe",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-clipboard fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false\" "
    },
    {
        "texto": "Consulta signo girado",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-file-pdf fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false\" d"
    },
    {
        "texto": "Cuadre contabilidad cartera",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-coins fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false\" data"
    },
    {
        "texto": "Saldos contables entidad",
        "tiene_next": false,
        "clases": "menu-options",
        "padre": "",
        "abuelo": "menu-content",
        "html": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-id-card fa-fw fw-sm\" aria-hidden=\"true\" focusable=\"false\" da"
    }
]
