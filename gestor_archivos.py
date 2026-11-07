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

def reconstruir_indice():
    """Reconstruye el índice leyendo contactos.dat registro por registro.
    Solo se usa si el índice está corrupto o vacío (no sirve para buscar IDs)."""
    indice = {}
    if not os.path.exists(RUTA_DATOS):
        return indice
    with open(RUTA_DATOS, "rb") as archivo:
        numero = 0
        while True:
            registro = archivo.read(TAMANO_REGISTRO)
            if len(registro) < TAMANO_REGISTRO:
                break
            try:
                indice[str(decodificar_registro(registro)["id"])] = numero
            except ValueError:
                pass  # registro ilegible: se omite
            numero += 1
    return indice


def obtener_indice():
    """Carga el índice. Si está corrupto o vacío (con datos) lo reconstruye.
    Devuelve (indice, aviso)."""
    try:
        indice = indice_seguridad.cargar_indice()
    except ValueError:
        try:
            os.replace(RUTA_INDICE, RUTA_INDICE + ".corrupto")  # conserva copia
        except OSError:
            pass
        indice = reconstruir_indice()
        indice_seguridad.guardar_indice(indice)
        return indice, ("indice.json estaba corrupto. Se guardó una copia "
                        "(indice.json.corrupto) y se reconstruyó desde contactos.dat.")
    if not indice and os.path.exists(RUTA_DATOS) and os.path.getsize(RUTA_DATOS) > 0:
        indice = reconstruir_indice()
        indice_seguridad.guardar_indice(indice)
        return indice, "El índice estaba vacío y se reconstruyó desde contactos.dat."
    return indice, None


def iniciar_almacenamiento():
    """Crea los archivos faltantes y carga el índice al iniciar la aplicación.
    Devuelve una lista de avisos (vacía si todo está bien)."""
    avisos = []
    error = indice_seguridad.inicializar_archivos()
    if error:
        avisos.append(error)
    try:
        indice, aviso = obtener_indice()
        if aviso:
            avisos.append(aviso)
    except OSError as error:
        avisos.append(mensaje_error(error))
    return avisos

def con_aviso(mensaje, aviso):
    """Agrega el aviso del índice (si existe) al mensaje."""
    return mensaje + (f"\n\n{aviso}" if aviso else "")

def agregar_contacto(datos):
    """Agrega un contacto al final del archivo. Devuelve (ok, mensaje)."""
    limpios, error = validar_datos(datos)
    if error:
        return False, error
    try:
        indice, aviso = obtener_indice()
        id_contacto = int(limpios["id"])
        if indice_seguridad.buscar_posicion(indice, id_contacto) is not None:
            return False, f"Ya existe un contacto con el ID {id_contacto}."
        if not os.path.exists(RUTA_DATOS):
            with open(RUTA_DATOS, "wb"):
                pass
        if os.path.getsize(RUTA_DATOS) % TAMANO_REGISTRO != 0:
            return False, "contactos.dat tiene un tamaño inválido (posiblemente dañado)."
        with open(RUTA_DATOS, "rb+") as archivo:
            archivo.seek(0, os.SEEK_END)  # nos ubicamos al final
            posicion = archivo.tell()
            numero_registro = posicion // TAMANO_REGISTRO
            print(f"[tell] Puntero en el byte {posicion} antes de escribir el registro {numero_registro}")
            archivo.write(codificar_registro(limpios))
        indice[str(id_contacto)] = numero_registro
        indice_seguridad.guardar_indice(indice)
        indice_seguridad.guardar_hash()
        return True, con_aviso(f"Contacto {id_contacto} guardado en el registro {numero_registro}.", aviso)
    except (OSError, ValueError) as error:
        return False, mensaje_error(error)


def buscar_contacto(id_texto):
    """Busca un contacto por ID usando el índice. Devuelve (contacto, mensaje)."""
    id_contacto = convertir_id(id_texto)
    if id_contacto is None:
        return None, "El ID debe ser un número entero positivo."
    try:
        indice, aviso = obtener_indice()
        numero_registro = indice_seguridad.buscar_posicion(indice, id_contacto)
        if numero_registro is None:
            return None, con_aviso(f"No existe un contacto con el ID {id_contacto}.", aviso)
        with open(RUTA_DATOS, "rb") as archivo:
            contacto = leer_registro(archivo, numero_registro)
        if contacto["id"] != id_contacto:
            return None, "El índice no coincide con el contenido de contactos.dat."
        byte = numero_registro * TAMANO_REGISTRO
        return contacto, con_aviso(f"Contacto encontrado en el registro {numero_registro} (byte {byte}).", aviso)
    except (OSError, ValueError) as error:
        return None, mensaje_error(error)


def modificar_contacto(datos):
    """Sobrescribe únicamente el registro del contacto. Devuelve (ok, mensaje)."""
    limpios, error = validar_datos(datos)
    if error:
        return False, error
    try:
        indice, aviso = obtener_indice()
        id_contacto = int(limpios["id"])
        numero_registro = indice_seguridad.buscar_posicion(indice, id_contacto)
        if numero_registro is None:
            return False, con_aviso(f"No existe un contacto con el ID {id_contacto}.", aviso)
        with open(RUTA_DATOS, "rb+") as archivo:
            actual = leer_registro(archivo, numero_registro)  # confirma el ID
            if actual["id"] != id_contacto:
                return False, "El índice no coincide con el contenido de contactos.dat."
            archivo.seek(numero_registro * TAMANO_REGISTRO)
            print(f"[tell] Puntero en el byte {archivo.tell()} antes de escribir el registro {numero_registro}")
            archivo.write(codificar_registro(limpios))  # solo este registro
        indice_seguridad.guardar_hash()
        return True, con_aviso(f"Contacto {id_contacto} modificado en el registro {numero_registro}.", aviso)
    except (OSError, ValueError) as error:
        return False, mensaje_error(error)

def exportar_contactos():
    """Lee todos los contactos desde contactos.dat y los devuelve como lista de
    diccionarios, formato usado por herramientas.py. Devuelve (lista, error)."""
    try:
        indice, aviso = obtener_indice()
        contactos = []
        with open(RUTA_DATOS, "rb") as archivo:
            for numero_registro in sorted(indice.values()):
                contactos.append(leer_registro(archivo, numero_registro))
        return contactos, None
    except (OSError, ValueError) as error:
        return None, mensaje_error(error)