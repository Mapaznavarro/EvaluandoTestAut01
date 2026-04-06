// Con el sub-submenú de Consultas abierto
(() => {
  // Opciones del nivel 2
  const opts = Array.from(document.querySelectorAll('div.menu-options'));
  
  // Botón de retroceso (el "<" que mencionaste)
  const backs = Array.from(document.querySelectorAll('*')).filter(el =>
    el.offsetParent !== null &&
    getComputedStyle(el).cursor === 'pointer' &&
    (el.className?.toString().includes('back') || 
     el.className?.toString().includes('prev') ||
     el.className?.toString().includes('return') ||
     el.className?.toString().includes('header') ||
     el.className?.toString().includes('title'))
  ).map(el => ({
    tag: el.tagName,
    clases: el.className,
    texto: el.textContent.trim().substring(0, 40),
    padre_clases: el.parentElement?.className,
    abuelo_clases: el.parentElement?.parentElement?.className
  }));

  return {
    total_menu_options: opts.length,
    opciones: opts.map(el => ({
      texto: el.querySelector('div.text')?.textContent.trim(),
      tiene_next: !!el.querySelector('div.next'),
      visible: el.offsetParent !== null
    })),
    posibles_botones_back: backs.slice(0, 8)
  };
})();

Respuesta:
{
    "total_menu_options": 11,
    "opciones": [
        {
            "texto": "Contabilidad",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Estados de cartera",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Ficha instrumentos",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Históricos",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Informe comisiones",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Operaciones",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Precios",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Resumen patrimonial",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Saldos",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Tareas",
            "tiene_next": true,
            "visible": true
        },
        {
            "texto": "Valor Liquidativo",
            "tiene_next": true,
            "visible": true
        }
    ],
    "posibles_botones_back": [
        {
            "tag": "DIV",
            "clases": "back",
            "texto": "",
            "padre_clases": "menu-title",
            "abuelo_clases": "menu"
        }
    ]
}


// Ver todos los div.menu-options visibles y su texto
Array.from(document.querySelectorAll('div.menu-options')).map(el => ({
  texto: el.querySelector('div.text')?.textContent.trim(),
  cursor: getComputedStyle(el).cursor,
  visible: el.offsetParent !== null,
  draggable: el.getAttribute('draggable'),
  padre_clases: el.parentElement?.className,
  tiene_next: !!el.querySelector('div.next')
}));
Respuesta:
[
    {
        "texto": "Consultas",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Contabilidad",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Entradas",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Incorporaciones",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Maestros",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Procesos",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    },
    {
        "texto": "Tareas",
        "cursor": "pointer",
        "visible": true,
        "draggable": "true",
        "padre_clases": "",
        "tiene_next": true
    }
]



// Verificar el div.close
(() => {
  const close = document.querySelector('div.close');
  if (!close) return 'No encontrado';
  return {
    tag: close.tagName,
    clases: close.className,
    cursor: getComputedStyle(close).cursor,
    pointer_events: getComputedStyle(close).pointerEvents,
    padre_clases: close.parentElement?.className,
    outerHTML: close.outerHTML.substring(0, 300)
  };
})();
Respuesta:
{
    "tag": "DIV",
    "clases": "close",
    "cursor": "pointer",
    "pointer_events": "auto",
    "padre_clases": "menu-title main",
    "outerHTML": "<div _ngcontent-ng-c638813965=\"\" class=\"close\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-xmark fa-fw\" aria-hidden=\"true\" focusable=\"false\" data-prefix=\"fal\" data-icon=\"xmark\" role=\"img\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" data-fa-i2svg=\"\"><path fill=\"currentColor"
}


// Cuántos div.close hay visibles
Array.from(document.querySelectorAll('div.close')).map(el => ({
  clases: el.className,
  cursor: getComputedStyle(el).cursor,
  visible: el.offsetParent !== null,
  padre_clases: el.parentElement?.className,
  abuelo_clases: el.parentElement?.parentElement?.className
}));
Respuesta:
[
    {
        "clases": "close",
        "cursor": "pointer",
        "visible": true,
        "padre_clases": "menu-title main",
        "abuelo_clases": "menu"
    },
    {
        "clases": "close",
        "cursor": "pointer",
        "visible": true,
        "padre_clases": "option",
        "abuelo_clases": "options"
    }
]

// Ver la estructura completa alrededor de "Consultas"
(() => {
  const textos = Array.from(document.querySelectorAll('div.menu-options div.text'));
  const consultas = textos.find(el => el.textContent.trim() === 'Consultas');
  if (!consultas) return 'No encontrado';
  
  let node = consultas;
  let niveles = [];
  for (let i = 0; i < 5; i++) {
    if (!node) break;
    niveles.push({
      nivel: i,
      tag: node.tagName,
      clases: node.className,
      cursor: getComputedStyle(node).cursor,
      pointer_events: getComputedStyle(node).pointerEvents,
      outerHTML: node.outerHTML.substring(0, 200)
    });
    node = node.parentElement;
  }
  return niveles;
})();
Respuesta
[
    {
        "nivel": 0,
        "tag": "DIV",
        "clases": "text",
        "cursor": "pointer",
        "pointer_events": "auto",
        "outerHTML": "<div _ngcontent-ng-c638813965=\"\" class=\"text\"> Consultas </div>"
    },
    {
        "nivel": 1,
        "tag": "DIV",
        "clases": "label",
        "cursor": "pointer",
        "pointer_events": "auto",
        "outerHTML": "<div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng-c638813965=\"\" class=\"svg-inline--fa fa-table-cells fa-fw fw-sm\" aria-hidden=\"true\" focus"
    },
    {
        "nivel": 2,
        "tag": "DIV",
        "clases": "menu-options",
        "cursor": "pointer",
        "pointer_events": "auto",
        "outerHTML": "<div _ngcontent-ng-c638813965=\"\" draggable-item=\"\" class=\"menu-options\" draggable=\"true\"><div _ngcontent-ng-c638813965=\"\" class=\"label\"><div _ngcontent-ng-c638813965=\"\" class=\"icon\"><svg _ngcontent-ng"
    },
    {
        "nivel": 3,
        "tag": "DIV",
        "clases": "",
        "cursor": "auto",
        "pointer_events": "auto",
        "outerHTML": "<div overlayscrollbars=\"\" data-overlayscrollbars-contents=\"\" data-overlayscrollbars-viewport=\"scrollbarHidden overflowXHidden overflowYHidden\" tabindex=\"-1\" style=\"margin-right: 0px; margin-bottom: 0p"
    },
    {
        "nivel": 4,
        "tag": "OVERLAY-SCROLLBARS",
        "clases": "menu-content",
        "cursor": "auto",
        "pointer_events": "auto",
        "outerHTML": "<overlay-scrollbars _ngcontent-ng-c638813965=\"\" data-overlayscrollbars-initialize=\"\" class=\"menu-content\" data-overlayscrollbars=\"host\"><div overlayscrollbars=\"\" data-overlayscrollbars-contents=\"\" dat"
    }
]


// Ver todas las subopciones del submenú Golf
(() => {
  const options = Array.from(document.querySelectorAll('div.menu-options'));
  return options.map((container, i) => ({
    contenedor: i,
    padre_clases: container.parentElement?.className ?? '',
    subopciones: Array.from(container.querySelectorAll('div.text')).map(el => ({
      texto: el.textContent.trim(),
      clases: el.className,
      tiene_next: !!el.parentElement?.querySelector('div.next'),
      padre_clases: el.parentElement?.className ?? ''
    }))
  }));
})();
Responde
[
    {
        "contenedor": 0,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Consultas",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 1,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Contabilidad",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 2,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Entradas",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 3,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Incorporaciones",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 4,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Maestros",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 5,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Procesos",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    },
    {
        "contenedor": 6,
        "padre_clases": "",
        "subopciones": [
            {
                "texto": "Tareas",
                "clases": "text",
                "tiene_next": false,
                "padre_clases": "label"
            }
        ]
    }
]


// Buscar el contenedor del submenú activo (el que tiene Golf como cabecera)
(() => {
  const items = Array.from(document.querySelectorAll('div.ui-menu-item'));
  const result = items.map((el, i) => ({
    indice: i,
    texto: el.querySelector('div.text.xl')?.textContent.trim() ?? '',
    clases: el.className,
    padre_clases: el.parentElement?.className ?? '',
    abuelo_clases: el.parentElement?.parentElement?.className ?? '',
    bisabuelo_tag: el.parentElement?.parentElement?.parentElement?.tagName ?? '',
    bisabuelo_clases: el.parentElement?.parentElement?.parentElement?.className ?? ''
  }));
  console.log(JSON.stringify(result, null, 2));
  return result;
})();
Responde
[
    {
        "indice": 0,
        "texto": "",
        "clases": "ui-menu-item first active",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 1,
        "texto": "",
        "clases": "ui-menu-item",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 2,
        "texto": "",
        "clases": "ui-menu-item last",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 3,
        "texto": "",
        "clases": "ui-menu-item first last",
        "padre_clases": "bottom",
        "abuelo_clases": "menu lg",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "ui-menu"
    }
]
// Buscar el botón X o elemento de cierre del submenú
(() => {
  const candidates = Array.from(document.querySelectorAll('*')).filter(el => {
    const txt = el.textContent.trim();
    const cls = el.className?.toString() ?? '';
    return (
      el.offsetParent !== null &&
      getComputedStyle(el).cursor === 'pointer' &&
      (cls.includes('close') || cls.includes('back') || cls.includes('header') || 
       cls.includes('title') || cls.includes('return') || cls.includes('x') ||
       el.tagName === 'BUTTON')
    );
  });
  return candidates.slice(0, 15).map(el => ({
    tag: el.tagName,
    clases: el.className,
    texto: el.textContent.trim().substring(0, 40),
    padre_clases: el.parentElement?.className ?? ''
  }));
})();
Responde
[
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Golf",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item first active"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Participes LATAM",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "FrontOn Gestión",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item last"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Ajustes",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item first last"
    },
    {
        "tag": "DIV",
        "clases": "close",
        "texto": "",
        "padre_clases": "menu-title main"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Consultas",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Contabilidad",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Entradas",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    }
]

Respuesta snippet1
[
  {
    "indice": 0,
    "texto": "",
    "clases": "ui-menu-item first active",
    "padre_clases": "",
    "abuelo_clases": "top",
    "bisabuelo_tag": "DIV",
    "bisabuelo_clases": "menu lg"
  },
  {
    "indice": 1,
    "texto": "",
    "clases": "ui-menu-item",
    "padre_clases": "",
    "abuelo_clases": "top",
    "bisabuelo_tag": "DIV",
    "bisabuelo_clases": "menu lg"
  },
  {
    "indice": 2,
    "texto": "",
    "clases": "ui-menu-item last",
    "padre_clases": "",
    "abuelo_clases": "top",
    "bisabuelo_tag": "DIV",
    "bisabuelo_clases": "menu lg"
  },
  {
    "indice": 3,
    "texto": "",
    "clases": "ui-menu-item first last",
    "padre_clases": "bottom",
    "abuelo_clases": "menu lg",
    "bisabuelo_tag": "DIV",
    "bisabuelo_clases": "ui-menu"
  }
]
[
    {
        "indice": 0,
        "texto": "",
        "clases": "ui-menu-item first active",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 1,
        "texto": "",
        "clases": "ui-menu-item",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 2,
        "texto": "",
        "clases": "ui-menu-item last",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 3,
        "texto": "",
        "clases": "ui-menu-item first last",
        "padre_clases": "bottom",
        "abuelo_clases": "menu lg",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "ui-menu"
    }
]
Objeto
[
    {
        "indice": 0,
        "texto": "",
        "clases": "ui-menu-item first active",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 1,
        "texto": "",
        "clases": "ui-menu-item",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 2,
        "texto": "",
        "clases": "ui-menu-item last",
        "padre_clases": "",
        "abuelo_clases": "top",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "menu lg"
    },
    {
        "indice": 3,
        "texto": "",
        "clases": "ui-menu-item first last",
        "padre_clases": "bottom",
        "abuelo_clases": "menu lg",
        "bisabuelo_tag": "DIV",
        "bisabuelo_clases": "ui-menu"
    }
]
Resultado del snippets 2
Objeto
[
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Golf",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item first active"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Participes LATAM",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "FrontOn Gestión",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item last"
    },
    {
        "tag": "DIV",
        "clases": "text lg",
        "texto": "Ajustes",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next lg",
        "texto": "",
        "padre_clases": "ui-menu-item first last"
    },
    {
        "tag": "DIV",
        "clases": "close",
        "texto": "",
        "padre_clases": "menu-title main"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Consultas",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Contabilidad",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    },
    {
        "tag": "DIV",
        "clases": "text",
        "texto": "Entradas",
        "padre_clases": "label"
    },
    {
        "tag": "DIV",
        "clases": "next",
        "texto": "",
        "padre_clases": "menu-options"
    }
]















await page.waitForLoadState('networkidle'); // o 'domcontentloaded' según tu app
const dom = await page.content();           // HTML completo del documento actual
console.log(dom);

VM97:1 Uncaught ReferenceError: page is not defined
    at <anonymous>:1:1

console.log(document.documentElement.outerHTML);

console.log(new XMLSerializer().serializeToString(document));

'Buscando los selectores
<div _ngcontent-ng-c4036937797="" class="text xl"> Golf </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Participes LATAM </div>
<div _ngcontent-ng-c4036937797="" class="text xl">  FrontOn Gestión </div>
<div _ngcontent-ng-c4036937797="" class="text xl"> Ajustes </div>

'Buscando los receptores de click's pegar esto en console
// 1. Encontrar todos los div.text.xl y mostrar su info completa
document.querySelectorAll('div.text.xl').forEach((el, i) => {
  console.log(`--- Ítem ${i} ---`);
  console.log('texto:', JSON.stringify(el.textContent));
  console.log('tag padre:', el.parentElement?.tagName, el.parentElement?.className);
  console.log('tag abuelo:', el.parentElement?.parentElement?.tagName, el.parentElement?.parentElement?.className);
  console.log('es clickeable (pointer-events):', getComputedStyle(el).pointerEvents);
  console.log('outerHTML del padre:', el.parentElement?.outerHTML?.substring(0, 300));
  console.log('');
});

=========================================
// Pega esto y presiona Enter
console.log("Total div.text.xl encontrados:", document.querySelectorAll('div.text.xl').length)
R =======================================
Total div.text.xl encontrados: 0

==========================================
// Buscar en todos los shadow roots
function queryAllShadow(selector, root = document) {
  let results = [...root.querySelectorAll(selector)];
  root.querySelectorAll('*').forEach(el => {
    if (el.shadowRoot) results = results.concat(queryAllShadow(selector, el.shadowRoot));
  });
  return results;
}

let items = queryAllShadow('div.text.xl');
console.log("Encontrados en Shadow DOM:", items.length);
items.forEach((el, i) => console.log(i, JSON.stringify(el.textContent.trim()), el.parentElement?.tagName, el.parentElement?.className));
R =======================================

=========================================
Array.from(document.querySelectorAll('div.text.xl')).map((el, i) => {
  let node = el;
  let path = [];
  for (let j = 0; j < 5; j++) {
    if (!node) break;
    path.push(node.tagName + (node.className ? '.' + node.className.trim().replace(/\s+/g, '.') : '') + (node.id ? '#' + node.id : ''));
    node = node.parentElement;
  }
  return { indice: i, texto: el.textContent.trim(), ruta_hacia_arriba: path };
});
R =========================================
[
    {
        "indice": 0,
        "texto": "Golf",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.first",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 1,
        "texto": "Participes LATAM",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 2,
        "texto": "FrontOn Gestión",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.last",
            "DIV",
            "OVERLAY-SCROLLBARS.top"
        ]
    },
    {
        "indice": 3,
        "texto": "Ajustes",
        "ruta_hacia_arriba": [
            "DIV.text.xl",
            "DIV.label",
            "DIV.ui-menu-item.first.last",
            "DIV.bottom",
            "DIV.menu.xl"
        ]
    }
]

===============================================================
// Verificar que ui-menu-item es clickeable
Array.from(document.querySelectorAll('div.ui-menu-item')).map(el => ({
  texto: el.querySelector('div.text.xl')?.textContent.trim(),
  clase: el.className,
  cursor: getComputedStyle(el).cursor,
  pointer_events: getComputedStyle(el).pointerEvents
}));

Respuesta
[
    {
        "texto": "Golf",
        "clase": "ui-menu-item first",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "Participes LATAM",
        "clase": "ui-menu-item",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "FrontOn Gestión",
        "clase": "ui-menu-item last",
        "cursor": "pointer",
        "pointer_events": "auto"
    },
    {
        "texto": "Ajustes",
        "clase": "ui-menu-item first last",
        "cursor": "pointer",
        "pointer_events": "auto"
    }
]

===========================================================
COnfirmar que funcionan en consola
// Probar clic en Golf (debe navegar o cambiar la vista)
document.querySelector('div.ui-menu-item.first')?.click();

// Después de volver al menú, probar Participes LATAM
Array.from(document.querySelectorAll('div.ui-menu-item'))
  .find(el => el.querySelector('div.text.xl')?.textContent.trim() === 'Participes LATAM')
  ?.click();
// Después de volver al menú, probar FrontOn Gestión
document.querySelector('div.ui-menu-item.last')?.click();


  =========================================================
  Array.from(document.querySelectorAll('div.ui-menu-item')).map((el, i) => {
  let node = el;
  let path = [];
  for (let j = 0; j < 6; j++) {
    if (!node) break;
    path.push(node.tagName + (node.className ? '.' + node.className.trim().replace(/\s+/g, '.') : '') + (node.id ? '#' + node.id : ''));
    node = node.parentElement;
  }
  return {
    indice: i,
    texto: el.querySelector('div.text.xl')?.textContent.trim() ?? el.textContent.trim().substring(0, 50),
    clase_item: el.className,
    ruta_hacia_arriba: path
  };
});





