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

#PDF

def preparar_fuente(pdf):
    """Intenta usar una fuente TTF con soporte Unicode; si no, usa Helvetica.
    Devuelve el nombre de la fuente elegida."""
    for ruta in RUTAS_FUENTES:
        if os.path.exists(ruta):
            try:
                pdf.add_font("FuenteUnicode", "", ruta)
                return "FuenteUnicode"
            except Exception:
                pass  # si falla, se prueba con la siguiente
    return "Helvetica"

def ajustar_texto(texto, fuente):
    """Helvetica solo admite Latin-1 (incluye ñ y tildes); lo demás se reemplaza."""
    if fuente == "Helvetica":
        return texto.encode("latin-1", "replace").decode("latin-1")
    return texto

def generar_pdf():
    """Genera reporte_contactos.pdf leyendo contactos_exportados.json."""
    # Se actualiza el JSON para que el reporte tenga los datos más recientes
    ok, mensaje = exportar_json()
    if not ok:
        return False, mensaje
    try:
        from fpdf import FPDF
    except ImportError:
        return False, "Falta la librería fpdf2. Instálala con: pip install fpdf2"
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            contactos = json.load(archivo)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        fuente = preparar_fuente(pdf)

        # Título y fecha de generación
        pdf.set_font(fuente, "", 18)
        pdf.cell(0, 12, ajustar_texto("Reporte de contactos", fuente),
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font(fuente, "", 10)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(0, 8, ajustar_texto(f"Fecha de generación: {fecha}", fuente),
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        # Datos de cada contacto
        pdf.set_font(fuente, "", 12)
        if not contactos:
            pdf.cell(0, 8, ajustar_texto("No hay contactos registrados.", fuente),
                     new_x="LMARGIN", new_y="NEXT")
        for contacto in contactos:
            lineas = [f"ID: {contacto['id']}",
                      f"Nombre: {contacto['nombre']}",
                      f"Teléfono: {contacto['telefono']}",
                      f"Correo: {contacto['correo']}",
                      f"Ciudad: {contacto['ciudad']}"]
            for linea in lineas:
                pdf.cell(0, 7, ajustar_texto(linea, fuente), new_x="LMARGIN", new_y="NEXT")
            y = pdf.get_y() + 2
            pdf.line(10, y, 200, y)  # separador entre contactos
            pdf.ln(5)

        pdf.output(RUTA_PDF)
        return True, f"Reporte generado con {len(contactos)} contactos: reporte_contactos.pdf"
    except Exception as error:
        return False, f"Error al generar el PDF: {mensaje_error(error)}"

#ZIP

def crear_respaldo():
    """Crea respaldo.zip con contactos.dat e indice.json.
    Devuelve (ok, mensaje, tamanos). tamanos es un diccionario o None."""
    archivos = [("contactos.dat", RUTA_DATOS), ("indice.json", RUTA_INDICE)]
    for nombre, ruta in archivos:
        if not os.path.exists(ruta):
            return False, f"No se puede crear el respaldo: {nombre} no existe.", None
        if not os.access(ruta, os.R_OK):
            return False, f"No hay permiso de lectura sobre {nombre}.", None
    try:
        with zipfile.ZipFile(RUTA_ZIP, "w", zipfile.ZIP_DEFLATED) as zip_archivo:
            for nombre, ruta in archivos:
                zip_archivo.write(ruta, arcname=nombre)
        original = sum(os.path.getsize(ruta) for nombre, ruta in archivos)
        comprimido = os.path.getsize(RUTA_ZIP)
        if original == 0:
            porcentaje = 0.0  # evita la división entre cero
        else:
            porcentaje = ((original - comprimido) / original) * 100
        tamanos = {"original": original, "comprimido": comprimido, "porcentaje": porcentaje}
        return True, "Respaldo creado: respaldo.zip", tamanos
    except (OSError, zipfile.BadZipFile) as error:
        return False, f"Error al crear el respaldo: {mensaje_error(error)}", None

#METADATOS

def obtener_info_archivo():
    """Devuelve (lista de pares (etiqueta, valor), error) sobre contactos.dat."""
    ruta = Path(RUTA_DATOS)
    try:
        if not ruta.exists():
            return None, "El archivo contactos.dat no existe."
        datos = os.stat(ruta)
        modificado = datetime.fromtimestamp(datos.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
        info = [
            ("Nombre del archivo", ruta.name),
            ("Tamaño", f"{datos.st_size} bytes"),
            ("Última modificación", modificado),
            ("Permiso de lectura", "Sí" if os.access(ruta, os.R_OK) else "No"),
            ("Permiso de escritura", "Sí" if os.access(ruta, os.W_OK) else "No"),
        ]
        return info, None
    except OSError as error:
        return None, mensaje_error(error)