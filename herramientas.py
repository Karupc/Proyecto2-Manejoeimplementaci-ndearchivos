import os
import json
import zipfile
from datetime import datetime
from pathlib import Path

import gestor_archivos
from indice_seguridad import CARPETA, RUTA_DATOS, RUTA_INDICE, mensaje_error

RUTA_JSON = os.path.join(CARPETA, "contactos_exportados.json")
RUTA_PDF = os.path.join(CARPETA, "reporte_contactos.pdf")
RUTA_ZIP = os.path.join(CARPETA, "respaldo.zip")

# Fuentes TTF comunes (con soporte para ñ y tildes) que se buscan en el sistema
RUTAS_FUENTES = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]

#JSON

def exportar_json():
    """Exporta todos los contactos de contactos.dat a contactos_exportados.json."""
    contactos, error = gestor_archivos.exportar_contactos()
    if contactos is None:
        return False, error
    try:
        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(contactos, archivo, ensure_ascii=False, indent=4)
        return True, f"Se exportaron {len(contactos)} contactos a contactos_exportados.json."
    except (OSError, TypeError, ValueError) as error:
        return False, f"Error al exportar el JSON: {mensaje_error(error)}"