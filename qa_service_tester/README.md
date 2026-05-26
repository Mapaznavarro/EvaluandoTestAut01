# QA Service Tester - Comparador de Servicios RPC2, STORM y GPL

Programa Python que reemplaza el flujo de Power Automate para la comparación
de servicios web en el proceso de QA de la migración de RPC2 a GPL.

## Requisitos

- Python 3.9+
- Librerías: `openpyxl`, `requests`

```bash
pip install openpyxl requests
```

## Estructura del Proyecto

```
qa_service_tester/
├── config.ini          ← Configuración de URLs, credenciales, timeouts
├── config.py           ← Lectura de configuración
├── service_caller.py   ← Invocación de servicios SOAP y REST
├── response_parser.py  ← Parseo de respuestas XML (RPC2) y JSON (STORM/GPL)
├── comparator.py       ← Comparación de columnas y datos entre servicios
├── excel_handler.py    ← Lectura/escritura del Excel
├── main.py             ← Programa principal (punto de entrada)
└── README.md           ← Este archivo
```

## Configuración

Editar `config.ini` con los valores reales antes de ejecutar:

```ini
[SERVICIOS]
URL_Servicio_RPC2 = http://host:8081/RPC2/RPC
URL_Servicio_STORM = http://host:80/gather-rest-api/api/v1.0/
URL_Servicio_GPL = http://host/storm/bcibank/v1/

[TIMEOUTS]
TIEMPO_ESPERA_RPC = 40
TIEMPO_ESPERA_STORM = 40
TIEMPO_ESPERA_GPL = 40

[CREDENCIALES]
USUARIO_GPL = usuario
PASSWORD_GPL = clave
USUARIO_STORM = golfadmin
PASSWORD_STORM =

[RUTAS]
RUTA_RESULTADOS = ResultadosPythonServicios
ARCHIVO_EXCEL_ENTRADA = ListaMetodosServicioQA.xlsm
```

## Uso

```bash
cd qa_service_tester
python main.py
```

O especificando una ruta de configuración distinta:

```bash
python main.py /ruta/a/mi_config.ini
```

## Flujo de Ejecución

1. **Paso 1**: Abre el Excel de entrada (hoja activa)
2. **Paso 2**: Crea un Excel de salida `ListaMetodosServicioQAEjecutadosAAAAMMDD.xlsx`
3. **Paso 3-4**: Para cada fila con `Ejecuta = S`:
   - **4.1** Llama al servicio SOAP RPC2
   - **4.2** Llama al servicio REST STORM
   - **4.3** Llama al servicio REST GPL
   - **4.4** Compara columnas GPL vs RPC2 y GPL vs STORM
   - **4.5** Si las columnas coinciden, compara el contenido (genera CSVs)
   - **4.6** Registra la hora de ejecución
4. **Paso 4.8**: Guarda el Excel de resultados

## Manejo de Servicios No Disponibles

Si un servicio no está accesible (error de conexión), el programa:
- Registra el error en la columna correspondiente del Excel
- Continúa con los demás servicios de la misma fila
- Avanza a la siguiente fila sin detenerse

## Columnas del Excel de Salida

| Columna | Descripción |
|---------|-------------|
| Código Respuesta RPC2 | HTTP status code o mensaje de error |
| Respuesta RPC2 | Cuerpo de la respuesta (desborde en ContRespRPC2) |
| Codigo Resp GPL | HTTP status code o mensaje de error |
| Respuesta GPL | Cuerpo de la respuesta (desborde en ContRespGPL) |
| Codigo Resp Storm | HTTP status code o mensaje de error |
| Respuesta Storm | Cuerpo de la respuesta (desborde en ContRespSTORM) |
| Hora Ejecución | Timestamp de procesamiento |
| GPL Incluye col RPC2? | SI/NO si GPL tiene todas las columnas de RPC2 |
| GPL = RPC2? | SI o nombres de CSVs a comparar manualmente |
| GPL Incluye col STORM? | SI/NO si GPL tiene todas las columnas de STORM |
| GPL=STORM? | SI o nombres de CSVs a comparar manualmente |

## Archivos Generados

En la carpeta `RUTA_RESULTADOS`:
- **Respuestas individuales**: `NombreMetodo_Comentario.xml` o `.json`
- **CSVs de comparación**: cuando las columnas coinciden entre servicios
- **Excel de resultados**: con todas las respuestas y comparaciones
