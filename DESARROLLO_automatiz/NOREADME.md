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
