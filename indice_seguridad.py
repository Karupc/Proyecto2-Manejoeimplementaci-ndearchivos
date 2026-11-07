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

def cargar_indice():
    """Carga indice.json y devuelve un diccionario {"id": numero_registro}.
    Si el archivo no existe o está vacío devuelve un diccionario vacío.
    Si el contenido está corrupto lanza ValueError."""
    if not os.path.exists(RUTA_INDICE):
        return {}
    with open(RUTA_INDICE, "r", encoding="utf-8") as archivo:
        texto = archivo.read()
    if texto.strip() == "":
        return {}
    indice = json.loads(texto)  # JSONDecodeError es un ValueError
    if not isinstance(indice, dict):
        raise ValueError("El índice no es un diccionario.")
    # Cada clave debe ser un ID numérico y cada valor un número de registro entero
    for clave, valor in indice.items():
        if not clave.isdigit() or not isinstance(valor, int) or valor < 0:
            raise ValueError("El índice contiene valores inválidos.")
    return indice

def guardar_indice(indice):
    """Guarda o actualiza el diccionario del índice en indice.json."""
    with open(RUTA_INDICE, "w", encoding="utf-8") as archivo:
        json.dump(indice, archivo, ensure_ascii=False)

def buscar_posicion(indice, id_contacto):
    """Devuelve el número de registro de un ID, o None si no existe."""
    return indice.get(str(id_contacto))

#SHA-256

def calcular_hash(ruta=RUTA_DATOS):
    """Calcula el hash SHA-256 de un archivo leyéndolo por bloques."""
    sha = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        while True:
            bloque = archivo.read(4096)
            if not bloque:
                break
            sha.update(bloque)
    return sha.hexdigest()

def guardar_hash():
    """Calcula el hash actual de contactos.dat y lo guarda en contactos.sha256."""
    codigo = calcular_hash()
    with open(RUTA_HASH, "w", encoding="utf-8") as archivo:
        archivo.write(codigo)
    return codigo

def leer_hash_guardado():
    """Lee el hash almacenado. Devuelve None si el archivo no existe."""
    if not os.path.exists(RUTA_HASH):
        return None
    with open(RUTA_HASH, "r", encoding="utf-8") as archivo:
        return archivo.read().strip()

def verificar_integridad():
    """Compara el hash actual con el guardado. Devuelve (integro, mensaje)."""
    try:
        if not os.path.exists(RUTA_DATOS):
            return False, "El archivo contactos.dat no existe."
        guardado = leer_hash_guardado()
        if guardado is None:
            return False, "No se encontró contactos.sha256, no se puede verificar."
        actual = calcular_hash()
        if actual == guardado:
            return True, "El archivo contactos.dat mantiene su integridad."
        return False, ("ADVERTENCIA: el hash de contactos.dat no coincide con el "
                       "almacenado. El archivo pudo haber sido modificado fuera "
                       "de la aplicación.")
    except OSError as error:
        return False, mensaje_error(error)