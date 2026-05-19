En esta ruta ponemos los errores y como se van resolviendo con IA


ERROR:
 ERROR_CONFIG: Tipo Pantalla '=VLOOKUP(A4,'OpcionesThunder 2.5'!$B$2:$C$362,2,FALSE)' no válido. Usar: Consulta / CRUD / Transacciones
SOLUCION: 
Se correige el programa, al parecer abrira dos veces el Excel.

 Celda B4 tiene fórmula pero Excel aún no la calculó. Abre el Excel, guárdalo en Excel (no LibreOffice) y reintenta.
 SOLUCION:pidió a python evaluar la f+ormula

  File "B:\Users\gather\python\e2e-automationFaseIII\run_casos_prueba.py", line 1274
    tipo_raw = leer_celda(ws, ws_valores, fila, col_tipo, wb=wb)

    
