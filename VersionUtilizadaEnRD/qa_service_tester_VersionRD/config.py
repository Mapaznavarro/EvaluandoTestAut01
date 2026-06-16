"""Lectura de configuración desde config.ini."""
import configparser
import os

def cargar_config(ruta_ini=None):
    if ruta_ini is None:
        ruta_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    cfg = configparser.ConfigParser()
    cfg.read(ruta_ini, encoding="utf-8")
    return {
        "URL_Servicio_RPC2": cfg.get("SERVICIOS", "URL_Servicio_RPC2"),
        "URL_Servicio_STORM": cfg.get("SERVICIOS", "URL_Servicio_STORM"),
        "URL_Servicio_GPL": cfg.get("SERVICIOS", "URL_Servicio_GPL"),
        "TIEMPO_ESPERA_RPC": cfg.getint("TIMEOUTS", "TIEMPO_ESPERA_RPC"),
        "TIEMPO_ESPERA_STORM": cfg.getint("TIMEOUTS", "TIEMPO_ESPERA_STORM"),
        "TIEMPO_ESPERA_GPL": cfg.getint("TIMEOUTS", "TIEMPO_ESPERA_GPL"),
        "USUARIO_GPL": cfg.get("CREDENCIALES", "USUARIO_GPL"),
        "PASSWORD_GPL": cfg.get("CREDENCIALES", "PASSWORD_GPL"),
        "USUARIO_STORM": cfg.get("CREDENCIALES", "USUARIO_STORM"),
        "PASSWORD_STORM": cfg.get("CREDENCIALES", "PASSWORD_STORM"),
        "RUTA_RESULTADOS": cfg.get("RUTAS", "RUTA_RESULTADOS"),
        "ARCHIVO_EXCEL_ENTRADA": cfg.get("RUTAS", "ARCHIVO_EXCEL_ENTRADA"),
    }
