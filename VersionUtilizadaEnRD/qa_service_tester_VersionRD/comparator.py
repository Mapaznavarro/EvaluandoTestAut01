"""Comparación de resultados entre servicios (GPL vs RPC2, GPL vs STORM).

Genera archivos CSV y compara columnas y contenido.
"""
import csv
import os
from response_parser import DatosTabla


def columnas_incluidas(tabla_referencia: DatosTabla, tabla_verificar: DatosTabla) -> bool:
    """Verifica si todas las columnas de tabla_referencia están incluidas en tabla_verificar."""
    if not tabla_referencia.tiene_datos or not tabla_verificar.tiene_datos:
        return False
    cols_ref = {c.lower().strip() for c in tabla_referencia.columnas}
    cols_ver = {c.lower().strip() for c in tabla_verificar.columnas}
    return cols_ref.issubset(cols_ver)


def generar_csv(tabla: DatosTabla, ruta_archivo: str) -> str:
    """Genera un archivo CSV a partir de DatosTabla. Retorna la ruta del archivo creado."""
    os.makedirs(os.path.dirname(ruta_archivo) or ".", exist_ok=True)
    with open(ruta_archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(tabla.columnas)
        for fila in tabla.filas:
            writer.writerow(fila)
    return ruta_archivo


def comparar_tablas(tabla_a: DatosTabla, tabla_b: DatosTabla,
                    ruta_csv_a: str, ruta_csv_b: str) -> str:
    """Compara contenido y orden entre dos tablas.
    
    Genera archivos CSV y compara. Retorna "SI" si son iguales,
    o los nombres de los archivos CSV si hay diferencias.
    """
    if not tabla_a.tiene_datos or not tabla_b.tiene_datos:
        return "N/A"

    generar_csv(tabla_a, ruta_csv_a)
    generar_csv(tabla_b, ruta_csv_b)

    # Comparar columnas comunes (las de tabla_a que estén en tabla_b)
    cols_a_lower = [c.lower().strip() for c in tabla_a.columnas]
    cols_b_lower = [c.lower().strip() for c in tabla_b.columnas]

    # Mapeo: para cada columna de A, encontrar su índice en B
    mapeo = {}
    for i, ca in enumerate(cols_a_lower):
        for j, cb in enumerate(cols_b_lower):
            if ca == cb:
                mapeo[i] = j
                break

    if not mapeo:
        return f"Sin columnas comunes: {os.path.basename(ruta_csv_a)} vs {os.path.basename(ruta_csv_b)}"

    # Comparar filas: misma cantidad
    if len(tabla_a.filas) != len(tabla_b.filas):
        return (f"Distinta cant. filas ({len(tabla_a.filas)} vs {len(tabla_b.filas)}): "
                f"{os.path.basename(ruta_csv_a)} vs {os.path.basename(ruta_csv_b)}")

    # Comparar contenido celda por celda en columnas comunes
    diferencias = []
    for row_idx in range(len(tabla_a.filas)):
        fila_a = tabla_a.filas[row_idx]
        fila_b = tabla_b.filas[row_idx]
        for idx_a, idx_b in mapeo.items():
            val_a = fila_a[idx_a] if idx_a < len(fila_a) else ""
            val_b = fila_b[idx_b] if idx_b < len(fila_b) else ""
            if val_a.strip() != val_b.strip():
                diferencias.append(
                    f"Fila {row_idx+1}, Col '{tabla_a.columnas[idx_a]}': "
                    f"'{val_a[:50]}' != '{val_b[:50]}'"
                )
        if len(diferencias) > 10:
            diferencias.append("... (más diferencias omitidas)")
            break

    if not diferencias:
        return "SI"
    return f"{os.path.basename(ruta_csv_a)} vs {os.path.basename(ruta_csv_b)}"
