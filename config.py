"""
LexNum - Configuración de la aplicación
========================================

Configuración centralizada para la aplicación Flask LexNum.
Utiliza variables de entorno cuando están disponibles con valores por defecto.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

import os
from pathlib import Path


# =========================================================
# CONFIGURACIÓN BASE
# =========================================================
class Config:
    """Configuración base para la aplicación LexNum."""

    # Directorio base del proyecto
    BASE_DIR = Path(__file__).resolve().parent

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "lexnum-ofs-tlaxcala-2025")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Servidor
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "4055"))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

    # Archivos permitidos
    ALLOWED_EXTENSIONS = frozenset(["xlsx", "xls"])
    MAX_FILE_SIZE_MB = 10

    # Nombres de archivos de salida
    OUTPUT_FILENAME = "resultado_lexnum.xlsx"

    # Mensajes de error
    ERROR_NO_FILE = "No se subió archivo."
    ERROR_INVALID_EXCEL = "No se pudo leer el Excel. Use .xlsx válido."
    ERROR_NO_COLUMN = "Columna no encontrada. Use: Número, Numero, numero, NUMERO o Num."
    ERROR_CONVERSION = "Error al convertir el número."
    ERROR_NETWORK = "Error de conexión."

    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# =========================================================
# CONFIGURACIONES POR ENTORNO
# =========================================================
class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")  # Debe estar definida en producción


class TestingConfig(Config):
    """Configuración para testing."""
    TESTING = True
    DEBUG = True
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB para tests


# =========================================================
# SELECCIÓN DE CONFIGURACIÓN
# =========================================================
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env_name: str = None) -> Config:
    """
    Obtiene la configuración según el entorno especificado.

    Args:
        env_name: Nombre del entorno ('development', 'production', 'testing')
                  Si es None, usa la variable FLASK_ENV o 'default'

    Returns:
        Config: Instancia de configuración correspondiente
    """
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", "default")

    return config_by_name.get(env_name, DevelopmentConfig)
