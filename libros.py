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


# ── REGISTRAR ────────────────────────────────────────────────────
def ventana_registrar():
    reg = tk.Toplevel()
    reg.title("Registrar Libro")
    reg.geometry("420x370")
    reg.resizable(False, False)
    reg.configure(bg="#f0f4f8")

    tk.Label(reg, text="Registrar Libro",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame = tk.Frame(reg, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, fill="x")

    campos = [
        ("ISBN",            "isbn"),
        ("Titulo",          "titulo"),
        ("Autores",         "autores"),
        ("Editorial",       "editorial"),
        ("Año Publicacion", "anio_pub"),
        ("Num. Ejemplares", "num_ejemplar"),
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

    def guardar():
        isbn         = entradas["isbn"].get().strip()
        titulo       = entradas["titulo"].get().strip()
        autores      = entradas["autores"].get().strip()
        editorial    = entradas["editorial"].get().strip()
        anio_pub     = entradas["anio_pub"].get().strip()
        num_ejemplar = entradas["num_ejemplar"].get().strip()

        if not all([isbn, titulo, autores, editorial, anio_pub, num_ejemplar]):
            messagebox.showwarning("Campos vacios", "Completa todos los campos.")
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
            messagebox.showinfo("Exito", "Libro registrado correctamente.")
            reg.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(reg, text="Guardar",
              command=guardar,
              font=("Arial", 11, "bold"),
              bg="#27ae60", fg="white",
              width=18, pady=6,
              relief="flat", cursor="hand2").pack(pady=16)


# ── CONSULTA INDIVIDUAL ──────────────────────────────────────────
def ventana_consulta_individual():
    win = tk.Toplevel()
    win.title("Consulta Individual de Libro")
    win.geometry("420x320")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Consulta Individual de Libro",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=5)
    tk.Label(frame_bus, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame_bus, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    frame_res = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame_res.pack(padx=30, pady=10, fill="x")

    campos = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplares"]
    labels_val = {}

    for campo in campos:
        fila = tk.Frame(frame_res, bg="white")
        fila.pack(fill="x", padx=15, pady=3)
        tk.Label(fila, text=f"{campo}:", width=14, anchor="w",
                 bg="white", font=("Arial", 10, "bold")).pack(side="left")
        lbl = tk.Label(fila, text="", anchor="w",
                       bg="white", font=("Arial", 10))
        lbl.pack(side="left")
        labels_val[campo] = lbl

    def buscar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Campo vacio", "Ingresa un ISBN.")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT isbn, titulo, autores, editorial, anio_pub, num_ejemplar '
                'FROM public."Libro" WHERE isbn = %s', (isbn,)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplares"]
                for clave, valor in zip(claves, fila):
                    labels_val[clave].config(text=str(valor))
            else:
                messagebox.showinfo("No encontrado", "No existe un libro con ese ISBN.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(frame_bus, text="Buscar",
              command=buscar,
              font=("Arial", 10, "bold"),
              bg="#2980b9", fg="white",
              relief="flat", cursor="hand2",
              padx=10).pack(side="left", padx=8)


# ── CONSULTA GENERAL ─────────────────────────────────────────────
def ventana_consulta_general():
    win = tk.Toplevel()
    win.title("Consulta General de Libros")
    win.geometry("800x300")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Consulta General de Libros",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(fill="both", expand=True, padx=20, pady=5)

    columnas = ("isbn", "titulo", "autores", "editorial", "anio_pub", "num_ejemplar")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)

    encabezados = ["ISBN", "Titulo", "Autores", "Editorial", "Año Pub", "Num Ejemplares"]
    anchos = [130, 200, 160, 100, 70, 100]

    for col, enc, ancho in zip(columnas, encabezados, anchos):
        tabla.heading(col, text=enc)
        tabla.column(col, width=ancho, anchor="center")

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

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
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ── CAMBIAR ──────────────────────────────────────────────────────
def ventana_cambiar():
    win = tk.Toplevel()
    win.title("Cambiar Datos de Libro")
    win.geometry("420x390")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Cambiar Datos de Libro",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=5)
    tk.Label(frame_bus, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame_bus, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    frame = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=8, fill="x")

    campos = [
        ("Titulo",          "titulo"),
        ("Autores",         "autores"),
        ("Editorial",       "editorial"),
        ("Año Publicacion", "anio_pub"),
        ("Num. Ejemplares", "num_ejemplar"),
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

    def cargar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Campo vacio", "Ingresa un ISBN.")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT titulo, autores, editorial, anio_pub, num_ejemplar '
                'FROM public."Libro" WHERE isbn = %s', (isbn,)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["titulo", "autores", "editorial", "anio_pub", "num_ejemplar"]
                for clave, valor in zip(claves, fila):
                    entradas[clave].delete(0, tk.END)
                    entradas[clave].insert(0, str(valor))
            else:
                messagebox.showinfo("No encontrado", "No existe un libro con ese ISBN.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(frame_bus, text="Cargar",
              command=cargar,
              font=("Arial", 10, "bold"),
              bg="#2980b9", fg="white",
              relief="flat", cursor="hand2",
              padx=10).pack(side="left", padx=8)

    def actualizar():
        isbn         = entry_isbn.get().strip()
        titulo       = entradas["titulo"].get().strip()
        autores      = entradas["autores"].get().strip()
        editorial    = entradas["editorial"].get().strip()
        anio_pub     = entradas["anio_pub"].get().strip()
        num_ejemplar = entradas["num_ejemplar"].get().strip()

        if not all([isbn, titulo, autores, editorial, anio_pub, num_ejemplar]):
            messagebox.showwarning("Campos vacios", "Completa todos los campos.")
            return

        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """UPDATE public."Libro"
                SET titulo=%s, autores=%s, editorial=%s,
                    anio_pub=%s, num_ejemplar=%s
                WHERE isbn=%s""",
                (titulo, autores, editorial, int(anio_pub), int(num_ejemplar), isbn)
            )
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Exito", "Datos actualizados correctamente.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Actualizar",
              command=actualizar,
              font=("Arial", 11, "bold"),
              bg="#e67e22", fg="white",
              width=18, pady=6,
              relief="flat", cursor="hand2").pack(pady=12)


# ── ELIMINAR ─────────────────────────────────────────────────────
def ventana_eliminar():
    win = tk.Toplevel()
    win.title("Eliminar Libro")
    win.geometry("360x200")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Eliminar Libro",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=20)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(pady=5)
    tk.Label(frame, text="ISBN:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_isbn = tk.Entry(frame, font=("Arial", 11), width=22)
    entry_isbn.pack(side="left")

    def eliminar():
        isbn = entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning("Campo vacio", "Ingresa un ISBN.")
            return
        confirm = messagebox.askyesno(
            "Confirmar", f"¿Seguro que deseas eliminar el libro con ISBN {isbn}?"
        )
        if not confirm:
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute('DELETE FROM public."Libro" WHERE isbn = %s', (isbn,))
            if cur.rowcount == 0:
                messagebox.showinfo("No encontrado", "No existe un libro con ese ISBN.")
            else:
                conn.commit()
                messagebox.showinfo("Exito", "Libro eliminado correctamente.")
                win.destroy()
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Eliminar",
              command=eliminar,
              font=("Arial", 11, "bold"),
              bg="#c0392b", fg="white",
              width=18, pady=6,
              relief="flat", cursor="hand2").pack(pady=20)


# ── MENÚ LIBROS ──────────────────────────────────────────────────
def ventana_libros():
    lib = tk.Toplevel()
    lib.title("Gestion de Libros")
    lib.geometry("340x360")
    lib.resizable(False, False)
    lib.configure(bg="#f0f4f8")

    tk.Label(lib, text="Libros",
             font=("Arial", 14, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=16)

    opciones = [
        ("Registrar",           "#2980b9", ventana_registrar),
        ("Consulta Individual", "#27ae60", ventana_consulta_individual),
        ("Consulta General",    "#8e44ad", ventana_consulta_general),
        ("Cambiar",             "#e67e22", ventana_cambiar),
        ("Eliminar",            "#c0392b", ventana_eliminar),
    ]

    for texto, color, cmd in opciones:
        tk.Button(lib, text=texto,
                  command=cmd,
                  font=("Arial", 11),
                  bg=color, fg="white",
                  width=24, pady=6,
                  relief="flat",
                  cursor="hand2").pack(pady=5)