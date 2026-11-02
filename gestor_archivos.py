import os
import indice_seguridad
from indice_seguridad import RUTA_DATOS, RUTA_INDICE, mensaje_error

NOMBRES_CAMPOS = ["id", "nombre", "telefono", "correo", "ciudad"]
LONGITUDES = {"id": 10, "nombre": 30, "telefono": 15, "correo": 35, "ciudad": 20}
ETIQUETAS = {"id": "ID", "nombre": "Nombre", "telefono": "Teléfono",
             "correo": "Correo", "ciudad": "Ciudad"}
TAMANO_REGISTRO = sum(LONGITUDES.values())  # 110 bytes por registro

def validar_datos(datos):
    """Valida los cinco campos. Devuelve (datos_limpios, error)."""
    limpios = {}
    for campo in NOMBRES_CAMPOS:
        valor = str(datos.get(campo, "")).strip()
        if valor == "":
            return None, f"El campo {ETIQUETAS[campo]} no puede estar vacío."
        usados = len(valor.encode("utf-8"))  # se mide en bytes, no en caracteres
        if usados > LONGITUDES[campo]:
            return None, (f"El campo {ETIQUETAS[campo]} excede el máximo de "
                          f"{LONGITUDES[campo]} bytes (usa {usados}).")
        limpios[campo] = valor
    if not (limpios["id"].isascii() and limpios["id"].isdigit()) or int(limpios["id"]) <= 0:
        return None, "El ID debe ser un número entero positivo."
    limpios["id"] = str(int(limpios["id"]))  # quita ceros a la izquierda
    return limpios, None


def convertir_id(texto):
    """Convierte el texto del ID a entero positivo. Devuelve None si no es válido."""
    texto = str(texto).strip()
    if texto.isascii() and texto.isdigit() and int(texto) > 0:
        return int(texto)
    return None