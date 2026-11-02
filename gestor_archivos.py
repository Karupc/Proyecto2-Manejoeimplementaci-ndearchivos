import os
import indice_seguridad
from indice_seguridad import RUTA_DATOS, RUTA_INDICE, mensaje_error

NOMBRES_CAMPOS = ["id", "nombre", "telefono", "correo", "ciudad"]
LONGITUDES = {"id": 10, "nombre": 30, "telefono": 15, "correo": 35, "ciudad": 20}
ETIQUETAS = {"id": "ID", "nombre": "Nombre", "telefono": "Teléfono",
             "correo": "Correo", "ciudad": "Ciudad"}
TAMANO_REGISTRO = sum(LONGITUDES.values())  # 110 bytes por registro

def validar_datos(datos):
    #Valida los cinco campos. Devuelve (datos_limpios, error).
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
    #Convierte el texto del ID a entero positivo. Devuelve None si no es válido.
    texto = str(texto).strip()
    if texto.isascii() and texto.isdigit() and int(texto) > 0:
        return int(texto)
    return None

def codificar_registro(datos):
    #Convierte un contacto en bytes de tamaño fijo.
    registro = b""
    for campo in NOMBRES_CAMPOS:
        registro += datos[campo].encode("utf-8").ljust(LONGITUDES[campo], b" ")
    return registro


def decodificar_registro(registro):
    #Convierte los bytes de un registro en un diccionario.
    datos = {}
    inicio = 0
    for campo in NOMBRES_CAMPOS:
        fin = inicio + LONGITUDES[campo]
        datos[campo] = registro[inicio:fin].decode("utf-8").rstrip()
        inicio = fin
    datos["id"] = int(datos["id"])
    return datos


def leer_registro(archivo, numero_registro):
    #Lee un registro usando seek() y tell(). El archivo debe estar abierto en binario.
    posicion = numero_registro * TAMANO_REGISTRO
    archivo.seek(posicion)
    print(f"[tell] Puntero en el byte {archivo.tell()} antes de leer el registro {numero_registro}")
    registro = archivo.read(TAMANO_REGISTRO)
    if len(registro) != TAMANO_REGISTRO:
        raise ValueError(f"El registro {numero_registro} está incompleto o fuera del archivo.")
    return decodificar_registro(registro)