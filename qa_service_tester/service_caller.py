"""Módulo para invocar servicios web SOAP (RPC2) y REST (STORM, GPL)."""
import requests
from requests.auth import HTTPBasicAuth
from dataclasses import dataclass, field
from typing import Optional

BALANCER_504_KEYWORDS = ["504 Gateway Time-out", "504 Gateway", "gateway time-out"]


@dataclass
class RespuestaServicio:
    """Resultado de una llamada a un servicio web."""
    codigo_respuesta: int = 0
    cuerpo_respuesta: str = ""
    headers: dict = field(default_factory=dict)
    error: str = ""
    disponible: bool = True

    @property
    def es_exitosa(self) -> bool:
        return self.disponible and not self.error and 200 <= self.codigo_respuesta < 300

    @property
    def es_error_balanceador(self) -> bool:
        return any(kw.lower() in self.cuerpo_respuesta.lower() for kw in BALANCER_504_KEYWORDS)


def _verificar_balanceador(resp: RespuestaServicio) -> RespuestaServicio:
    """Si la respuesta proviene del balanceador (504), marcar como error."""
    if resp.es_error_balanceador:
        resp.error = "Error 504 Gateway Time-out del balanceador (no del servicio)"
    return resp


def llamar_rpc2(url: str, body_xml: str, timeout: int) -> RespuestaServicio:
    """Llama al servicio SOAP RPC2.
    
    Args:
        url: URL base del servicio RPC2 (ej: http://host:8081/RPC2/RPC)
        body_xml: Cuerpo XML SOAP completo (columna LlamadaRPC2)
        timeout: Tiempo de espera en segundos
    """
    resultado = RespuestaServicio()
    if not body_xml or not body_xml.strip():
        resultado.disponible = False
        resultado.error = "Sin body XML para RPC2"
        return resultado
    body_xml_limpio = body_xml.replace("_x000D_\n", "\n").replace("_x000D_", "")
    headers = {
        "Content-Type": "text/xml; charset=iso-8859-1",
        "SOAPAction": "",
    }
    try:
        resp = requests.post(url, data=body_xml_limpio.encode("iso-8859-1"),
                             headers=headers, timeout=timeout)
        resultado.codigo_respuesta = resp.status_code
        resultado.cuerpo_respuesta = resp.text
        resultado.headers = dict(resp.headers)
        _verificar_balanceador(resultado)
    except requests.exceptions.Timeout:
        resultado.error = f"Timeout ({timeout}s) al llamar RPC2"
        resultado.disponible = True
    except requests.exceptions.ConnectionError:
        resultado.error = "Servicio RPC2 no disponible (error de conexión)"
        resultado.disponible = False
    except Exception as e:
        resultado.error = f"Error inesperado RPC2: {type(e).__name__}: {e}"
        resultado.disponible = False
    return resultado


def llamar_rest(url: str, body: str, timeout: int,
                content_type: str = "application/json",
                accept: str = "application/json",
                usuario: str = "", password: str = "") -> RespuestaServicio:
    """Llama a un servicio REST (STORM o GPL).
    
    Args:
        url: URL completa del endpoint (base + nombre método)
        body: Cuerpo de la solicitud (JSON o XML según content_type)
        timeout: Tiempo de espera en segundos
        content_type: Tipo MIME del cuerpo (application/json o application/xml)
        accept: Tipo MIME esperado en la respuesta
        usuario: Usuario para autenticación básica
        password: Password para autenticación básica
    """
    resultado = RespuestaServicio()
    if not body or not body.strip():
        resultado.disponible = False
        resultado.error = "Sin body para servicio REST"
        return resultado
    headers = {
        "Content-Type": content_type,
        "Accept": accept,
    }
    auth = HTTPBasicAuth(usuario, password) if usuario else None
    try:
        resp = requests.post(url, data=body.encode("utf-8"),
                             headers=headers, timeout=timeout, auth=auth)
        resultado.codigo_respuesta = resp.status_code
        resultado.cuerpo_respuesta = resp.text
        resultado.headers = dict(resp.headers)
        _verificar_balanceador(resultado)
    except requests.exceptions.Timeout:
        resultado.error = f"Timeout ({timeout}s) al llamar servicio REST"
        resultado.disponible = True
    except requests.exceptions.ConnectionError:
        resultado.error = "Servicio REST no disponible (error de conexión)"
        resultado.disponible = False
    except Exception as e:
        resultado.error = f"Error inesperado REST: {type(e).__name__}: {e}"
        resultado.disponible = False
    return resultado


def llamar_storm(url_base: str, nombre_metodo: str, body: str, timeout: int,
                 content_type: str = "application/json",
                 accept: str = "application/json",
                 usuario: str = "", password: str = "") -> RespuestaServicio:
    """Llama al servicio STORM (REST)."""
    url = f"{url_base.rstrip('/')}/{nombre_metodo}"
    return llamar_rest(url, body, timeout, content_type, accept, usuario, password)


def llamar_gpl(url_base: str, nombre_metodo: str, body: str, timeout: int,
               content_type: str = "application/json",
               accept: str = "application/json",
               usuario: str = "", password: str = "") -> RespuestaServicio:
    """Llama al servicio GPL (REST)."""
    url = f"{url_base.rstrip('/')}/{nombre_metodo}"
    return llamar_rest(url, body, timeout, content_type, accept, usuario, password)
