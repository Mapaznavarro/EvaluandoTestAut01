"""Parseo de respuestas de servicios RPC2 (XML), STORM (JSON) y GPL (JSON).

Extrae columnas y filas de datos para permitir comparación entre servicios.
"""
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

NS = {"ex": "http://ws.apache.org/xmlrpc/namespaces/extensions"}


@dataclass
class DatosTabla:
    """Representa datos tabulares extraídos de una respuesta de servicio."""
    columnas: list[str]
    filas: list[list[str]]
    es_error: bool = False
    mensaje_error: str = ""
    detalle_error: str = ""
    codigo_error: str = ""

    @property
    def tiene_datos(self) -> bool:
        return len(self.columnas) > 0 and not self.es_error


def _extraer_valor_xml(elem) -> str:
    """Extrae el valor de texto de un elemento <value> del XML RPC2."""
    if elem is None:
        return ""
    for child in elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag in ("i4", "int", "double", "boolean", "string",
                    "dateTime.iso8601", "base64"):
            return child.text or ""
        if tag == "value":
            return _extraer_valor_xml(child)
    return elem.text.strip() if elem.text else ""


def parsear_rpc2(xml_text: str) -> DatosTabla:
    """Parsea la respuesta XML del servicio RPC2.
    
    Estructura esperada:
    <methodResponse>
      <params><param><value><array><data>
        <value>  ← struct con MENSAJE_ERROR, DETALLE_ERROR, CODIGO_ERROR
        <value>  ← array con nombres de columnas
        <value>  ← cantidad de filas (i4)
        <value>  ← array de arrays con datos de filas
      </data></array></value></param></params>
    </methodResponse>
    """
    resultado = DatosTabla(columnas=[], filas=[])
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        resultado.es_error = True
        resultado.mensaje_error = f"Error parseando XML: {e}"
        return resultado

    fault = root.find(".//fault")
    if fault is not None:
        resultado.es_error = True
        resultado.mensaje_error = "SOAP Fault en respuesta RPC2"
        return resultado

    data_values = root.findall(".//params/param/value/array/data/value")
    if not data_values:
        resultado.es_error = True
        resultado.mensaje_error = "Estructura XML inesperada: no se encontró array/data/value"
        return resultado

    # Primer value: struct con errores
    struct_elem = data_values[0].find("struct")
    if struct_elem is not None:
        error_info = {}
        for member in struct_elem.findall("member"):
            name_elem = member.find("name")
            value_elem = member.find("value")
            if name_elem is not None and name_elem.text:
                error_info[name_elem.text] = _extraer_valor_xml(value_elem) if value_elem is not None else ""
        msg_err = error_info.get("MENSAJE_ERROR", "")
        det_err = error_info.get("DETALLE_ERROR", "")
        cod_err = error_info.get("CODIGO_ERROR", "0")
        if msg_err or (cod_err and cod_err != "0"):
            resultado.es_error = True
            resultado.mensaje_error = msg_err
            resultado.detalle_error = det_err
            resultado.codigo_error = cod_err
            return resultado

    # Segundo value: array con nombres de columnas
    if len(data_values) >= 2:
        col_array = data_values[1].find("array/data")
        if col_array is not None:
            resultado.columnas = [_extraer_valor_xml(v) for v in col_array.findall("value")]

    # Cuarto value (índice 3): array de arrays con datos
    if len(data_values) >= 4:
        rows_array = data_values[3].find("array/data")
        if rows_array is not None:
            for row_val in rows_array.findall("value"):
                row_data_elem = row_val.find("array/data")
                if row_data_elem is not None:
                    fila = [_extraer_valor_xml(v) for v in row_data_elem.findall("value")]
                    resultado.filas.append(fila)

    return resultado


def parsear_json_gpl(json_text: str) -> DatosTabla:
    """Parsea la respuesta JSON del servicio GPL.
    
    Error: {"MENSAJE_ERROR": "...", "DETALLE_ERROR": "...", "CODIGO_ERROR": ...}
    Éxito: arreglo de objetos [{...}, {...}] o un objeto simple {...}
    """
    resultado = DatosTabla(columnas=[], filas=[])
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        resultado.es_error = True
        resultado.mensaje_error = f"Error parseando JSON GPL: {e}"
        return resultado

    if isinstance(data, dict):
        if "MENSAJE_ERROR" in data:
            resultado.es_error = True
            resultado.mensaje_error = str(data.get("MENSAJE_ERROR", ""))
            resultado.detalle_error = str(data.get("DETALLE_ERROR", ""))
            resultado.codigo_error = str(data.get("CODIGO_ERROR", ""))
            return resultado
        resultado.columnas = list(data.keys())
        resultado.filas = [[str(data.get(c, "")) for c in resultado.columnas]]
    elif isinstance(data, list):
        if not data:
            return resultado
        all_keys = []
        seen = set()
        for obj in data:
            if isinstance(obj, dict):
                for k in obj.keys():
                    if k not in seen:
                        all_keys.append(k)
                        seen.add(k)
        resultado.columnas = all_keys
        for obj in data:
            if isinstance(obj, dict):
                resultado.filas.append([str(obj.get(c, "")) for c in all_keys])
    return resultado


def parsear_json_storm(json_text: str) -> DatosTabla:
    """Parsea la respuesta JSON del servicio STORM.
    
    Error: {"title": "Errores", "errores": [{"errorCode":..., "errorType":..., ...}]}
    Éxito: arreglo de objetos o un objeto simple.
    """
    resultado = DatosTabla(columnas=[], filas=[])
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        resultado.es_error = True
        resultado.mensaje_error = f"Error parseando JSON STORM: {e}"
        return resultado

    if isinstance(data, dict):
        if (data.get("title") or "").lower() == "errores" or "errores" in data:
            resultado.es_error = True
            errores = data.get("errores", [])
            if errores and isinstance(errores, list):
                primer_error = errores[0] if isinstance(errores[0], dict) else {}
                resultado.mensaje_error = str(primer_error.get("errorDescription", ""))
                resultado.codigo_error = str(primer_error.get("errorCode", ""))
                resultado.detalle_error = json.dumps(errores, ensure_ascii=False)
            else:
                resultado.mensaje_error = str(data)
            return resultado
        resultado.columnas = list(data.keys())
        resultado.filas = [[str(data.get(c, "")) for c in resultado.columnas]]
    elif isinstance(data, list):
        if not data:
            return resultado
        all_keys = []
        seen = set()
        for obj in data:
            if isinstance(obj, dict):
                for k in obj.keys():
                    if k not in seen:
                        all_keys.append(k)
                        seen.add(k)
        resultado.columnas = all_keys
        for obj in data:
            if isinstance(obj, dict):
                resultado.filas.append([str(obj.get(c, "")) for c in all_keys])
    return resultado
