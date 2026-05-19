import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2


def conectar():
    return psycopg2.connect(
        host="localhost",
        database="Biblioteca",
        user="postgres",
        password="2405",
        port="5432"
    )


def barra_usuario(ventana, titulo, nombre_usuario):
    barra = tk.Frame(ventana, bg="#1a3c5e", height=45)
    barra.pack(fill="x")
    barra.pack_propagate(False)
    tk.Label(barra, text=titulo, font=("Arial", 12, "bold"),
             bg="#1a3c5e", fg="white").pack(side="left", padx=15, pady=10)
    tk.Label(barra, text=f"Usuario: {nombre_usuario}", font=("Arial", 10),
             bg="#1a3c5e", fg="#a8d8f0").pack(side="right", padx=15)


def lbl_msg(ventana):
    lbl = tk.Label(ventana, text="", font=("Arial", 10, "bold"), bg="#f0f4f8")
    lbl.pack(pady=4)
    return lbl


# ── REGISTRAR ────────────────────────────────────────────────────
def ventana_registrar(nombre_usuario):
    reg = tk.Toplevel()
    reg.title("Registrar Libro")
    reg.geometry("420x400")
    reg.resizable(False, False)
    reg.configure(bg="#f0f4f8")

    barra_usuario(reg, "Registrar Libro", nombre_usuario)

    frame = tk.Frame(reg, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=10, fill="x")

    campos = [
        ("ISBN",            "isbn"),
        ("Titulo",          "titulo"),
        ("Autores",         "autores"),
        ("Editorial",       "editorial"),
        ("Año Publicacion", "anio_pub"),
        ("Num. Ejemplar",   "num_ejemplar"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=4)
        tk.Label(fila, text=etiqueta, width=18, anchor="w",
                 bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=24)
        entrada.pack(side="left")
        entradas[clave] = entrada

    lbl = lbl_msg(reg)

    def guardar():
        isbn         = entradas["isbn"].get().strip()
        titulo       = entradas["titulo"].get().strip()
        autores      = entradas["autores"].get().strip()
        editorial    = entradas["editorial"].get().strip()
        anio_pub     = entradas["anio_pub"].get().strip()
        num_ejemplar = entradas["num_ejemplar"].get().strip()

        if not all([isbn, titulo, autores, editorial, anio_pub, num_ejemplar]):
            lbl.config(text="⚠ Completa todos los campos.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO public."Libro"
                (isbn, titulo, autores, editorial, anio_pub, num_ejemplar)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (isbn, titulo, autores, editorial, int(anio_pub), int(num_ejemplar))
            )
            conn.commit()
            cur.close()
            conn.close()
            lbl.config(text="✅ Libro registrado correctamente.", fg="#27ae60")
            for e in entradas.values():
                e.delete(0, tk.END)
        except Exception as e:
            lbl.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(reg, text="Guardar", command=guardar,
              font=("Arial", 11, "bold"), bg="#27ae60", fg="white",
              width=18, pady=6, relief="flat", cursor="hand2").pack(pady=10)


# ── CONSULTA INDIVIDUAL ──────────────────────────────────────────
def ventana_consulta_individual(nombre_usuario):
    win = tk.Toplevel()
    win.title("Consulta Individual de Libro")
    win.geometry("420x370")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta Individual de Libro", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame_bus, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    frame_res = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame_res.pack(padx=30, pady=5, fill="x")

    campos = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplar"]
    labels_val = {}

    for campo in campos:
        fila = tk.Frame(frame_res, bg="white")
        fila.pack(fill="x", padx=15, pady=3)
        tk.Label(fila, text=f"{campo}:", width=14, anchor="w",
                 bg="white", font=("Arial", 10, "bold")).pack(side="left")
        lbl = tk.Label(fila, text="", anchor="w", bg="white", font=("Arial", 10))
        lbl.pack(side="left")
        labels_val[campo] = lbl

    lbl_estado = lbl_msg(win)

    def buscar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            lbl_estado.config(text="⚠ Ingresa un ISBN.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT isbn, titulo, autores, editorial, anio_pub, num_ejemplar '
                'FROM public."Libro" WHERE isbn = %s LIMIT 1', (isbn,)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplar"]
                for clave, valor in zip(claves, fila):
                    labels_val[clave].config(text=str(valor))
                lbl_estado.config(text="✅ Libro encontrado.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un libro con ese ISBN.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Buscar", command=buscar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)


# ── CONSULTA GENERAL ─────────────────────────────────────────────
def ventana_consulta_general(nombre_usuario):
    win = tk.Toplevel()
    win.title("Consulta General de Libros")
    win.geometry("800x360")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta General de Libros", nombre_usuario)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("isbn", "titulo", "autores", "editorial", "anio_pub", "num_ejemplar")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)

    encabezados = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplar"]
    anchos = [130, 200, 160, 100, 70, 100]

    for col, enc, ancho in zip(columnas, encabezados, anchos):
        tabla.heading(col, text=enc)
        tabla.column(col, width=ancho, anchor="center")

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    lbl_estado = lbl_msg(win)

    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute(
            'SELECT isbn, titulo, autores, editorial, anio_pub, num_ejemplar '
            'FROM public."Libro"'
        )
        filas = cur.fetchall()
        cur.close()
        conn.close()
        for fila in filas:
            tabla.insert("", "end", values=fila)
        lbl_estado.config(text=f"✅ {len(filas)} registro(s) encontrado(s).", fg="#27ae60")
    except Exception as e:
        lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")


# ── CAMBIAR ──────────────────────────────────────────────────────
def ventana_cambiar(nombre_usuario):
    win = tk.Toplevel()
    win.title("Cambiar Datos de Libro")
    win.geometry("420x420")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Cambiar Datos de Libro", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame_bus, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    frame = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=5, fill="x")

    campos = [
        ("Titulo",          "titulo"),
        ("Autores",         "autores"),
        ("Editorial",       "editorial"),
        ("Año Publicacion", "anio_pub"),
        ("Num. Ejemplar",   "num_ejemplar"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=3)
        tk.Label(fila, text=etiqueta, width=18, anchor="w",
                 bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=22)
        entrada.pack(side="left")
        entradas[clave] = entrada

    lbl_estado = lbl_msg(win)

    def cargar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            lbl_estado.config(text="⚠ Ingresa un ISBN.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT titulo, autores, editorial, anio_pub, num_ejemplar '
                'FROM public."Libro" WHERE isbn = %s LIMIT 1', (isbn,)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["titulo", "autores", "editorial", "anio_pub", "num_ejemplar"]
                for clave, valor in zip(claves, fila):
                    entradas[clave].delete(0, tk.END)
                    entradas[clave].insert(0, str(valor))
                lbl_estado.config(text="✅ Datos cargados.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un libro con ese ISBN.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Cargar", command=cargar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)

    def actualizar():
        isbn         = entry_isbn.get().strip()
        titulo       = entradas["titulo"].get().strip()
        autores      = entradas["autores"].get().strip()
        editorial    = entradas["editorial"].get().strip()
        anio_pub     = entradas["anio_pub"].get().strip()
        num_ejemplar = entradas["num_ejemplar"].get().strip()

        if not all([isbn, titulo, autores, editorial, anio_pub, num_ejemplar]):
            lbl_estado.config(text="⚠ Completa todos los campos.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """UPDATE public."Libro"
                SET titulo=%s, autores=%s, editorial=%s, anio_pub=%s, num_ejemplar=%s
                WHERE isbn=%s""",
                (titulo, autores, editorial, int(anio_pub), int(num_ejemplar), isbn)
            )
            conn.commit()
            cur.close()
            conn.close()
            lbl_estado.config(text="✅ Datos actualizados correctamente.", fg="#27ae60")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(win, text="Actualizar", command=actualizar,
              font=("Arial", 11, "bold"), bg="#e67e22", fg="white",
              width=18, pady=6, relief="flat", cursor="hand2").pack(pady=8)


# ── ELIMINAR ─────────────────────────────────────────────────────
def ventana_eliminar(nombre_usuario):
    win = tk.Toplevel()
    win.title("Eliminar Libro")
    win.geometry("360x250")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Eliminar Libro", nombre_usuario)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(pady=15)
    tk.Label(frame, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    lbl_estado = lbl_msg(win)

    def eliminar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            lbl_estado.config(text="⚠ Ingresa un ISBN.", fg="#e67e22")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar libro con ISBN {isbn}?"):
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute('DELETE FROM public."Libro" WHERE isbn = %s', (isbn,))
            if cur.rowcount == 0:
                lbl_estado.config(text="❌ No existe un libro con ese ISBN.", fg="#c0392b")
            else:
                conn.commit()
                lbl_estado.config(text="✅ Libro eliminado correctamente.", fg="#27ae60")
                entry_isbn.delete(0, tk.END)
            cur.close()
            conn.close()
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(win, text="Eliminar", command=eliminar,
              font=("Arial", 11, "bold"), bg="#c0392b", fg="white",
              width=18, pady=6, relief="flat", cursor="hand2").pack(pady=10)


# ── MENÚ LIBROS ──────────────────────────────────────────────────
def ventana_libros(nombre_usuario):
    lib = tk.Toplevel()
    lib.title("Gestion de Libros")
    lib.geometry("340x390")
    lib.resizable(False, False)
    lib.configure(bg="#f0f4f8")

    barra_usuario(lib, "Libros", nombre_usuario)

    tk.Label(lib, text="Menu Libros",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    opciones = [
        ("Registrar",           "#2980b9", lambda: ventana_registrar(nombre_usuario)),
        ("Consulta Individual", "#27ae60", lambda: ventana_consulta_individual(nombre_usuario)),
        ("Consulta General",    "#8e44ad", lambda: ventana_consulta_general(nombre_usuario)),
        ("Cambiar",             "#e67e22", lambda: ventana_cambiar(nombre_usuario)),
        ("Eliminar",            "#c0392b", lambda: ventana_eliminar(nombre_usuario)),
    ]

    for texto, color, cmd in opciones:
        tk.Button(lib, text=texto, command=cmd,
                  font=("Arial", 11), bg=color, fg="white",
                  width=24, pady=6, relief="flat", cursor="hand2").pack(pady=5)