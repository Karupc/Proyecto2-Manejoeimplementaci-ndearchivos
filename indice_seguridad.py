import os
import json
import hashlib

# Rutas relativas a la carpeta del proyecto
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_DATOS = os.path.join(CARPETA, "contactos.dat")
RUTA_INDICE = os.path.join(CARPETA, "indice.json")
RUTA_HASH = os.path.join(CARPETA, "contactos.sha256")


def mensaje_error(error):
    """Convierte un error común en un mensaje comprensible para el usuario."""
    if isinstance(error, FileNotFoundError):
        return "No se encontró un archivo necesario (contactos.dat o indice.json)."
    if isinstance(error, PermissionError):
        return "No hay permisos de lectura o escritura sobre los archivos."
    return f"Ocurrió un error: {error}"