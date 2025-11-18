"""
LexNum - Aplicación Web para Conversión Numérica a Texto Monetario
====================================================================

Aplicación Flask que convierte números a su representación en texto
en formato monetario mexicano oficial para uso institucional.

Autor: Omar Gabriel Salvatierra Garcia
Organización: Órgano de Fiscalización Superior del Estado de Tlaxcala
"""

import logging
from io import BytesIO
from typing import Tuple, Dict, Any

import pandas as pd
from flask import Flask, render_template, request, send_file, jsonify, Response
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import RequestEntityTooLarge

from config import get_config
from utils import numero_a_texto, find_num_column


# =========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================
def create_app(config_name: str = None) -> Flask:
    """
    Factory function para crear y configurar la aplicación Flask.

    Args:
        config_name: Nombre del entorno de configuración

    Returns:
        Flask: Instancia configurada de la aplicación
    """
    app = Flask(__name__)

    # Cargar configuración
    config = get_config(config_name)
    app.config.from_object(config)

    # Configurar logging
    setup_logging(app)

    # Registrar rutas
    register_routes(app)

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Registrar hooks de respuesta
    register_response_hooks(app)

    return app


def setup_logging(app: Flask) -> None:
    """
    Configura el sistema de logging de la aplicación.

    Args:
        app: Instancia de la aplicación Flask
    """
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    log_format = app.config.get("LOG_FORMAT")

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )

    app.logger.setLevel(log_level)
    app.logger.info("LexNum iniciado correctamente")


# =========================================================
# VALIDACIONES
# =========================================================
def validate_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Valida que el archivo subido sea válido.

    Args:
        file: Archivo subido por el usuario

    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
    """
    if not file or file.filename == "":
        return False, "No se proporcionó ningún archivo."

    # Validar extensión
    if not file.filename or "." not in file.filename:
        return False, "El archivo debe tener una extensión válida."

    extension = file.filename.rsplit(".", 1)[1].lower()
    if extension not in {"xlsx", "xls"}:
        return False, "Solo se permiten archivos Excel (.xlsx, .xls)."

    return True, ""


# =========================================================
# RUTAS PRINCIPALES
# =========================================================
def register_routes(app: Flask) -> None:
    """
    Registra todas las rutas de la aplicación.

    Args:
        app: Instancia de la aplicación Flask
    """

    @app.route("/")
    def index() -> str:
        """Renderiza la página principal."""
        return render_template("index.html")

    @app.route("/health")
    def health() -> Tuple[Dict[str, str], int]:
        """Endpoint de salud para monitoreo."""
        return jsonify({"status": "healthy", "service": "LexNum"}), 200

    @app.route("/convertir_texto", methods=["POST"])
    def convertir_texto() -> Tuple[Dict[str, Any], int]:
        """
        Convierte un número individual a texto monetario.

        Returns:
            JSON con el texto convertido o error
        """
        try:
            data = request.get_json(silent=True) or {}
            numero = data.get("numero", "")

            if not numero:
                return jsonify({"texto": ""}), 200

            texto = numero_a_texto(numero)
            app.logger.debug(f"Conversión: {numero} -> {texto}")

            return jsonify({"texto": texto}), 200

        except Exception as e:
            app.logger.error(f"Error en convertir_texto: {e}")
            return jsonify({
                "error": app.config["ERROR_CONVERSION"]
            }), 500

    @app.route("/convertir_excel", methods=["POST"])
    def convertir_excel() -> Tuple[Response, int]:
        """
        Procesa un archivo Excel y retorna el resultado con conversiones.

        Returns:
            Archivo Excel con columna de texto agregada o error JSON
        """
        try:
            # Validar que se subió un archivo
            archivo = request.files.get("archivo")
            if not archivo:
                return jsonify({
                    "error": app.config["ERROR_NO_FILE"]
                }), 400

            # Validar el archivo
            is_valid, error_message = validate_file(archivo)
            if not is_valid:
                return jsonify({"error": error_message}), 400

            # Leer Excel
            try:
                df = pd.read_excel(archivo)
                app.logger.info(f"Excel leído: {len(df)} filas")
            except Exception as e:
                app.logger.error(f"Error leyendo Excel: {e}")
                return jsonify({
                    "error": app.config["ERROR_INVALID_EXCEL"]
                }), 400

            # Encontrar columna de números
            col = find_num_column(df)
            if not col:
                return jsonify({
                    "error": app.config["ERROR_NO_COLUMN"]
                }), 400

            # Aplicar conversión
            df["Texto"] = df[col].apply(numero_a_texto)
            app.logger.info(f"Conversiones aplicadas en columna: {col}")

            # Generar archivo Excel en memoria
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            buf.seek(0)

            # Enviar archivo
            return send_file(
                buf,
                as_attachment=True,
                download_name=app.config["OUTPUT_FILENAME"],
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ), 200

        except Exception as e:
            app.logger.error(f"Error en convertir_excel: {e}")
            return jsonify({
                "error": "Error interno del servidor."
            }), 500


# =========================================================
# MANEJADORES DE ERRORES
# =========================================================
def register_error_handlers(app: Flask) -> None:
    """
    Registra manejadores de errores personalizados.

    Args:
        app: Instancia de la aplicación Flask
    """

    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        """Maneja archivos que exceden el tamaño máximo."""
        max_size = app.config["MAX_FILE_SIZE_MB"]
        return jsonify({
            "error": f"El archivo excede el tamaño máximo permitido de {max_size} MB."
        }), 413

    @app.errorhandler(404)
    def handle_not_found(e):
        """Maneja rutas no encontradas."""
        return jsonify({"error": "Ruta no encontrada."}), 404

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Maneja errores internos del servidor."""
        app.logger.error(f"Error interno: {e}")
        return jsonify({"error": "Error interno del servidor."}), 500


# =========================================================
# HOOKS DE RESPUESTA
# =========================================================
def register_response_hooks(app: Flask) -> None:
    """
    Registra hooks que se ejecutan después de cada petición.

    Args:
        app: Instancia de la aplicación Flask
    """

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        """Agrega encabezados de seguridad a todas las respuestas."""
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


# =========================================================
# PUNTO DE ENTRADA
# =========================================================
app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )

