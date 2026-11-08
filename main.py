import tkinter as tk
from tkinter import ttk, messagebox

import gestor_archivos
import indice_seguridad
import herramientas

#COLORES
COLOR_FONDO = "#F6F0E7"
COLOR_MENU = "#EFE7DB"
COLOR_MENU_HOVER = "#E8DFD0"
COLOR_MENU_ACTIVO = "#E0D6C5"
COLOR_TARJETA = "#EBE3D5"
COLOR_PRIMARIO = "#E87955"
COLOR_PRIMARIO_HOVER = "#D96745"
COLOR_SECUNDARIO_HOVER = "#E3D9C8"
COLOR_TEXTO = "#292724"
COLOR_TEXTO_SEC = "#777168"
COLOR_BORDE = "#D8CFC1"
COLOR_CAMPO = "#FBF9F5"
COLOR_OK = "#6B7F5E"
COLOR_ALERTA = "#C0532F"
FUENTE = "Segoe UI"

#ESTADO GLOBAL
ventana = None
contenido = None
etiqueta_titulo = None
etiqueta_descripcion = None
etiqueta_integridad = None
etiqueta_resultado = None
campos = {}          # variables de los cinco campos del formulario
botones_menu = {}    # widgets del menú lateral
estado = {"seccion": None}


#WIDGETS REUTILIZABLES

def rectangulo_redondeado(lienzo, x1, y1, x2, y2, radio, **opciones):
    """Dibuja un rectángulo con esquinas redondeadas en un Canvas."""
    puntos = [x1 + radio, y1, x1 + radio, y1, x2 - radio, y1, x2 - radio, y1,
              x2, y1, x2, y1 + radio, x2, y1 + radio, x2, y2 - radio,
              x2, y2 - radio, x2, y2, x2 - radio, y2, x2 - radio, y2,
              x1 + radio, y2, x1 + radio, y2, x1, y2, x1, y2 - radio,
              x1, y2 - radio, x1, y1 + radio, x1, y1 + radio, x1, y1]
    return lienzo.create_polygon(puntos, smooth=True, **opciones)


def crear_boton(padre, texto, comando, principal=True, ancho=150, alto=38):
    """Botón plano con esquinas redondeadas y efecto hover.
    principal=True usa terracota; False usa el estilo secundario (crema)."""
    if principal:
        color, color_hover, borde = COLOR_PRIMARIO, COLOR_PRIMARIO_HOVER, COLOR_PRIMARIO
    else:
        color, color_hover, borde = COLOR_FONDO, COLOR_SECUNDARIO_HOVER, COLOR_BORDE
    lienzo = tk.Canvas(padre, width=ancho, height=alto, bg=COLOR_TARJETA,
                       highlightthickness=0, cursor="hand2")
    forma = rectangulo_redondeado(lienzo, 1, 1, ancho - 1, alto - 1, 10,
                                  fill=color, outline=borde)
    lienzo.create_text(ancho / 2, alto / 2, text=texto, fill=COLOR_TEXTO,
                       font=(FUENTE, 10, "bold"))
    lienzo.bind("<Enter>", lambda e: lienzo.itemconfig(forma, fill=color_hover))
    lienzo.bind("<Leave>", lambda e: lienzo.itemconfig(forma, fill=color))
    lienzo.bind("<Button-1>", lambda e: comando())
    return lienzo


def crear_tarjeta(padre):
    """Contenedor beige con borde fino."""
    return tk.Frame(padre, bg=COLOR_TARJETA, highlightbackground=COLOR_BORDE,
                    highlightthickness=1, padx=26, pady=22)


def crear_separador(padre):
    """Línea discreta (ttk.Separator con estilo propio)."""
    return ttk.Separator(padre, orient="horizontal", style="Japandi.TSeparator")


def crear_campo(padre, campo):
    """Etiqueta pequeña + campo de entrada con el estilo de la aplicación."""
    marco = tk.Frame(padre, bg=COLOR_TARJETA)
    texto = f"{gestor_archivos.ETIQUETAS[campo]}  ·  máx. {gestor_archivos.LONGITUDES[campo]} bytes"
    tk.Label(marco, text=texto, bg=COLOR_TARJETA, fg=COLOR_TEXTO_SEC,
             font=(FUENTE, 9), anchor="w").pack(fill="x")
    entrada = tk.Entry(marco, textvariable=campos[campo], relief="flat",
                       bg=COLOR_CAMPO, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO,
                       highlightthickness=1, highlightbackground=COLOR_BORDE,
                       highlightcolor=COLOR_PRIMARIO, font=(FUENTE, 11))
    entrada.pack(fill="x", pady=(4, 0), ipady=6)
    return marco


def crear_fila_accion(padre, titulo, descripcion, texto_boton, comando, principal):
    """Fila con título, descripción y botón a la derecha (Exportar y Herramientas)."""
    fila = tk.Frame(padre, bg=COLOR_TARJETA)
    fila.pack(fill="x", pady=8)
    textos = tk.Frame(fila, bg=COLOR_TARJETA)
    textos.pack(side="left", fill="x", expand=True)
    tk.Label(textos, text=titulo, bg=COLOR_TARJETA, fg=COLOR_TEXTO,
             font=(FUENTE, 11, "bold")).pack(anchor="w")
    tk.Label(textos, text=descripcion, bg=COLOR_TARJETA, fg=COLOR_TEXTO_SEC,
             font=(FUENTE, 9), wraplength=380, justify="left").pack(anchor="w")
    crear_boton(fila, texto_boton, comando, principal, ancho=180).pack(side="right")


def mostrar_ventana_info(titulo, filas):
    """Ventana pequeña con una tarjeta de pares (etiqueta, valor)."""
    ventana_info = tk.Toplevel(ventana)
    ventana_info.title(titulo)
    ventana_info.configure(bg=COLOR_FONDO)
    ventana_info.resizable(False, False)
    ventana_info.transient(ventana)
    tarjeta = crear_tarjeta(ventana_info)
    tarjeta.pack(padx=24, pady=24)
    tk.Label(tarjeta, text=titulo, bg=COLOR_TARJETA, fg=COLOR_TEXTO,
             font=(FUENTE, 14, "bold")).grid(row=0, column=0, columnspan=2,
                                             sticky="w", pady=(0, 12))
    fila = 1
    for etiqueta, valor in filas:
        tk.Label(tarjeta, text=etiqueta, bg=COLOR_TARJETA, fg=COLOR_TEXTO_SEC,
                 font=(FUENTE, 10)).grid(row=fila, column=0, sticky="w", pady=4, padx=(0, 28))
        tk.Label(tarjeta, text=valor, bg=COLOR_TARJETA, fg=COLOR_TEXTO,
                 font=(FUENTE, 10, "bold")).grid(row=fila, column=1, sticky="w", pady=4)
        fila += 1
    crear_boton(tarjeta, "Cerrar", ventana_info.destroy, principal=False,
                ancho=100).grid(row=fila, column=0, columnspan=2, sticky="e", pady=(16, 0))


#ACCIONES: CONTACTOS

def obtener_valores():
    """Lee los cinco campos del formulario."""
    return {campo: campos[campo].get() for campo in gestor_archivos.NOMBRES_CAMPOS}


def limpiar_campos():
    for campo in gestor_archivos.NOMBRES_CAMPOS:
        campos[campo].set("")
    etiqueta_resultado.config(text="")


def accion_agregar():
    ok, mensaje = gestor_archivos.agregar_contacto(obtener_valores())
    if ok:
        messagebox.showinfo("Contacto agregado", mensaje)
        limpiar_campos()
        actualizar_integridad()
    else:
        messagebox.showerror("No se pudo agregar", mensaje)


def accion_buscar():
    contacto, mensaje = gestor_archivos.buscar_contacto(campos["id"].get())
    if contacto is None:
        etiqueta_resultado.config(text=mensaje, fg=COLOR_ALERTA)
        messagebox.showwarning("Búsqueda", mensaje)
        return
    for campo in gestor_archivos.NOMBRES_CAMPOS:
        campos[campo].set(str(contacto[campo]))
    etiqueta_resultado.config(text=mensaje, fg=COLOR_OK)


def accion_modificar():
    ok, mensaje = gestor_archivos.modificar_contacto(obtener_valores())
    if ok:
        messagebox.showinfo("Contacto modificado", mensaje)
        etiqueta_resultado.config(text=mensaje, fg=COLOR_OK)
        actualizar_integridad()
    else:
        messagebox.showerror("No se pudo modificar", mensaje)


#ACCIONES: EXPORTAR Y HERRAMIENTAS

def accion_exportar_json():
    ok, mensaje = herramientas.exportar_json()
    if ok:
        messagebox.showinfo("Exportación completa", mensaje)
    else:
        messagebox.showerror("Error al exportar", mensaje)


def accion_generar_pdf():
    ok, mensaje = herramientas.generar_pdf()
    if ok:
        messagebox.showinfo("Reporte generado", mensaje)
    else:
        messagebox.showerror("Error al generar el PDF", mensaje)


def actualizar_integridad():
    """Verifica el hash y actualiza el indicador del menú lateral."""
    integro, mensaje = indice_seguridad.verificar_integridad()
    if integro:
        etiqueta_integridad.config(text="●  Integridad verificada", fg=COLOR_OK)
    else:
        etiqueta_integridad.config(text="▲  Posible alteración del archivo", fg=COLOR_ALERTA)
    return integro, mensaje


def accion_verificar():
    integro, mensaje = actualizar_integridad()
    if integro:
        messagebox.showinfo("Integridad verificada", mensaje)
    else:
        messagebox.showwarning("Advertencia de integridad", mensaje)


def accion_respaldo():
    ok, mensaje, tamanos = herramientas.crear_respaldo()
    if not ok:
        messagebox.showerror("Error en el respaldo", mensaje)
        return
    mostrar_ventana_info("Respaldo creado", [
        ("Archivo", "respaldo.zip"),
        ("Tamaño original", f"{tamanos['original']} bytes"),
        ("Tamaño comprimido", f"{tamanos['comprimido']} bytes"),
        ("Reducción", f"{tamanos['porcentaje']:.2f} %"),
    ])


def accion_info_archivo():
    info, error = herramientas.obtener_info_archivo()
    if info is None:
        messagebox.showerror("Información del archivo", error)
    else:
        mostrar_ventana_info("Información del archivo", info)


#SECCIONES

def construir_contactos():
    global etiqueta_resultado
    tarjeta = crear_tarjeta(contenido)
    tarjeta.pack(fill="x")
    tarjeta.columnconfigure(0, weight=1, uniform="columna")
    tarjeta.columnconfigure(1, weight=1, uniform="columna")

    distribucion = [("id", "nombre"), ("telefono", "correo"), ("ciudad", None)]
    for fila, (izquierda, derecha) in enumerate(distribucion):
        crear_campo(tarjeta, izquierda).grid(row=fila, column=0, sticky="ew", padx=(0, 10), pady=8)
        if derecha:
            crear_campo(tarjeta, derecha).grid(row=fila, column=1, sticky="ew", padx=(10, 0), pady=8)

    crear_separador(tarjeta).grid(row=3, column=0, columnspan=2, sticky="ew", pady=14)

    botones = tk.Frame(tarjeta, bg=COLOR_TARJETA)
    botones.grid(row=4, column=0, columnspan=2, sticky="w")
    crear_boton(botones, "Agregar", accion_agregar, True, ancho=130).pack(side="left", padx=(0, 10))
    crear_boton(botones, "Buscar", accion_buscar, False, ancho=110).pack(side="left", padx=5)
    crear_boton(botones, "Modificar", accion_modificar, False, ancho=110).pack(side="left", padx=5)
    crear_boton(botones, "Limpiar", accion_limpiar_boton, False, ancho=110).pack(side="left", padx=5)

    etiqueta_resultado = tk.Label(tarjeta, text="", bg=COLOR_TARJETA, fg=COLOR_TEXTO_SEC,
                                  font=(FUENTE, 9), wraplength=600, justify="left")
    etiqueta_resultado.grid(row=5, column=0, columnspan=2, sticky="w", pady=(14, 0))


def accion_limpiar_boton():
    limpiar_campos()


def construir_exportar():
    tarjeta = crear_tarjeta(contenido)
    tarjeta.pack(fill="x")
    crear_fila_accion(tarjeta, "Exportar a JSON",
                      "Guarda todos los contactos de contactos.dat en contactos_exportados.json.",
                      "Exportar JSON", accion_exportar_json, True)
    crear_separador(tarjeta).pack(fill="x", pady=4)
    crear_fila_accion(tarjeta, "Reporte PDF",
                      "Genera reporte_contactos.pdf a partir del JSON exportado.",
                      "Generar PDF", accion_generar_pdf, True)


def construir_herramientas():
    tarjeta = crear_tarjeta(contenido)
    tarjeta.pack(fill="x")
    crear_fila_accion(tarjeta, "Verificar integridad",
                      "Compara el hash SHA-256 de contactos.dat con el guardado en contactos.sha256.",
                      "Verificar SHA-256", accion_verificar, False)
    crear_separador(tarjeta).pack(fill="x", pady=4)
    crear_fila_accion(tarjeta, "Respaldo comprimido",
                      "Crea respaldo.zip con contactos.dat e indice.json y muestra la reducción de tamaño.",
                      "Crear respaldo", accion_respaldo, True)
    crear_separador(tarjeta).pack(fill="x", pady=4)
    crear_fila_accion(tarjeta, "Información del archivo",
                      "Muestra tamaño, fecha de modificación y permisos de contactos.dat.",
                      "Ver información", accion_info_archivo, False)


def construir_ayuda():
    tarjeta = crear_tarjeta(contenido)
    tarjeta.pack(fill="x")
    texto = (
        "Esta agenda guarda los contactos en contactos.dat usando registros de tamaño fijo "
        "(110 bytes), por lo que cada contacto se ubica con seek() según su número de registro.\n\n"
        "•  indice.json relaciona cada ID con su número de registro; toda búsqueda consulta primero el índice.\n"
        "•  Al agregar o modificar un contacto se recalcula el hash SHA-256 en contactos.sha256. "
        "Al iniciar, el programa lo compara para detectar cambios hechos fuera de la aplicación.\n"
        "•  Exportar genera contactos_exportados.json y reporte_contactos.pdf.\n"
        "•  Herramientas permite verificar la integridad, crear respaldo.zip y ver los metadatos del archivo.\n\n"
        "Para modificar un contacto, escribe su ID, pulsa Buscar, cambia los datos y pulsa Modificar. "
        "El ID no se puede cambiar."
    )
    tk.Label(tarjeta, text=texto, bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=(FUENTE, 10),
             wraplength=640, justify="left").pack(anchor="w")


#MENÚ LATERAL

def pintar_menu(nombre, color_fondo, color_indicador):
    fila, indicador, etiqueta = botones_menu[nombre]
    fila.config(bg=color_fondo)
    etiqueta.config(bg=color_fondo)
    indicador.config(bg=color_indicador)


def mostrar_seccion(nombre):
    """Cambia la sección visible y resalta la opción seleccionada del menú."""
    estado["seccion"] = nombre
    for hijo in contenido.winfo_children():
        hijo.destroy()
    titulo, descripcion, construir = SECCIONES[nombre]
    etiqueta_titulo.config(text=titulo)
    etiqueta_descripcion.config(text=descripcion)
    for otro in botones_menu:
        if otro == nombre:
            pintar_menu(otro, COLOR_MENU_ACTIVO, COLOR_PRIMARIO)
        else:
            pintar_menu(otro, COLOR_MENU, COLOR_MENU)
    construir()


def al_entrar_menu(nombre):
    if estado["seccion"] != nombre:
        pintar_menu(nombre, COLOR_MENU_HOVER, COLOR_MENU_HOVER)


def al_salir_menu(nombre):
    if estado["seccion"] != nombre:
        pintar_menu(nombre, COLOR_MENU, COLOR_MENU)


def crear_boton_menu(barra, nombre, icono):
    fila = tk.Frame(barra, bg=COLOR_MENU, cursor="hand2")
    fila.pack(fill="x", pady=2)
    indicador = tk.Frame(fila, width=4, bg=COLOR_MENU)
    indicador.pack(side="left", fill="y")
    etiqueta = tk.Label(fila, text=f"{icono}   {nombre}", anchor="w", padx=16, pady=11,
                        bg=COLOR_MENU, fg=COLOR_TEXTO, font=(FUENTE, 11), cursor="hand2")
    etiqueta.pack(side="left", fill="x", expand=True)
    botones_menu[nombre] = (fila, indicador, etiqueta)
    for widget in (fila, etiqueta):
        widget.bind("<Button-1>", lambda e, n=nombre: mostrar_seccion(n))
        widget.bind("<Enter>", lambda e, n=nombre: al_entrar_menu(n))
        widget.bind("<Leave>", lambda e, n=nombre: al_salir_menu(n))


#INICIO

def verificar_al_iniciar():
    """Inicializa archivos, carga el índice y verifica el hash SHA-256."""
    avisos = gestor_archivos.iniciar_almacenamiento()
    if avisos:
        messagebox.showwarning("Aviso al iniciar", "\n\n".join(avisos))
    integro, mensaje = actualizar_integridad()
    if not integro:
        messagebox.showwarning("Advertencia de integridad", mensaje)


def construir_interfaz():
    global ventana, contenido, etiqueta_titulo, etiqueta_descripcion, etiqueta_integridad
    ventana = tk.Tk()
    ventana.title("Agenda de Contactos")
    ventana.geometry("1000x660")
    ventana.minsize(920, 600)
    ventana.configure(bg=COLOR_FONDO)

    # Estilo ttk (solo para el separador)
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Japandi.TSeparator", background=COLOR_BORDE)

    # Variables del formulario
    for campo in gestor_archivos.NOMBRES_CAMPOS:
        campos[campo] = tk.StringVar()

    # Menú lateral
    barra = tk.Frame(ventana, bg=COLOR_MENU, width=240)
    barra.pack(side="left", fill="y")
    barra.pack_propagate(False)
    tk.Frame(ventana, bg=COLOR_BORDE, width=1).pack(side="left", fill="y")
    tk.Label(barra, text="Agenda de\nContactos", bg=COLOR_MENU, fg=COLOR_TEXTO,
             font=(FUENTE, 17, "bold"), justify="left", anchor="w").pack(fill="x", padx=24, pady=(32, 28))
    crear_boton_menu(barra, "Contactos", "●")
    crear_boton_menu(barra, "Exportar", "↗")
    crear_boton_menu(barra, "Herramientas", "⚙")
    crear_boton_menu(barra, "Ayuda", "?")
    etiqueta_integridad = tk.Label(barra, text="", bg=COLOR_MENU, fg=COLOR_TEXTO_SEC,
                                   font=(FUENTE, 9), wraplength=190, justify="left", anchor="w")
    etiqueta_integridad.pack(side="bottom", fill="x", padx=24, pady=20)

    # Área principal
    area = tk.Frame(ventana, bg=COLOR_FONDO)
    area.pack(side="left", fill="both", expand=True, padx=40, pady=34)
    etiqueta_titulo = tk.Label(area, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO,
                               font=(FUENTE, 22, "bold"), anchor="w")
    etiqueta_titulo.pack(fill="x")
    etiqueta_descripcion = tk.Label(area, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO_SEC,
                                    font=(FUENTE, 11), anchor="w")
    etiqueta_descripcion.pack(fill="x", pady=(2, 22))
    contenido = tk.Frame(area, bg=COLOR_FONDO)
    contenido.pack(fill="both", expand=True)


SECCIONES = {
    "Contactos": ("Contactos", "Agrega, busca o modifica los datos de una persona.", construir_contactos),
    "Exportar": ("Exportar", "Genera copias de tus contactos en JSON o PDF.", construir_exportar),
    "Herramientas": ("Herramientas", "Integridad, respaldo e información del archivo.", construir_herramientas),
    "Ayuda": ("Ayuda", "Cómo funciona el programa.", construir_ayuda),
}


def main():
    construir_interfaz()
    mostrar_seccion("Contactos")
    ventana.after(300, verificar_al_iniciar)
    ventana.mainloop()


if __name__ == "__main__":
    main()