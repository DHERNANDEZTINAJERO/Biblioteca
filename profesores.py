import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
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
    reg.title("Registrar Profesor")
    reg.geometry("420x450")
    reg.resizable(False, False)
    reg.configure(bg="#f0f4f8")

    barra_usuario(reg, "Registrar Profesor", nombre_usuario)

    frame = tk.Frame(reg, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=10, fill="x")

    campos = [
        ("Codigo",                 "codigo"),
        ("Nombre",                 "nombre"),
        ("Departamento",           "departamento"),
        ("Correo",                 "correo"),
        ("Direccion",              "direccion"),
        ("Telefono",               "tel"),
        ("Sexo (M/F)",             "sexo"),
        ("Fecha Nac (DD-MM-YYYY)", "fecha_nac"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=4)
        tk.Label(fila, text=etiqueta, width=20, anchor="w",
                 bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=22)
        entrada.pack(side="left")
        entradas[clave] = entrada

    lbl = lbl_msg(reg)

    def guardar():
        codigo       = entradas["codigo"].get().strip()
        nombre       = entradas["nombre"].get().strip()
        departamento = entradas["departamento"].get().strip()
        correo       = entradas["correo"].get().strip()
        direccion    = entradas["direccion"].get().strip()
        tel          = entradas["tel"].get().strip()
        sexo         = entradas["sexo"].get().strip()
        fecha_nac    = entradas["fecha_nac"].get().strip()

        if not all([codigo, nombre, departamento, correo, direccion, tel, sexo, fecha_nac]):
            lbl.config(text="⚠ Completa todos los campos.", fg="#e67e22")
            return
        try:
            fecha_convertida = datetime.strptime(fecha_nac, "%d-%m-%Y").strftime("%Y-%m-%d")
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO public."Profesor"
                (codigo, nombre, departamento, correo, direccion, tel, sexo, fecha_nac)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (int(codigo), nombre, departamento, correo, direccion, int(tel), sexo, fecha_convertida)
            )
            conn.commit()
            cur.close()
            conn.close()
            lbl.config(text="✅ Profesor registrado correctamente.", fg="#27ae60")
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
    win.title("Consulta Individual de Profesor")
    win.geometry("420x420")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta Individual de Profesor", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="Codigo:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_cod = tk.Entry(frame_bus, font=("Arial", 11), width=18)
    entry_cod.pack(side="left")

    frame_res = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame_res.pack(padx=30, pady=5, fill="x")

    campos = ["Codigo", "Nombre", "Departamento", "Correo",
              "Direccion", "Telefono", "Sexo", "Fecha Nac"]
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
        codigo = entry_cod.get().strip()
        if not codigo:
            lbl_estado.config(text="⚠ Ingresa un codigo.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT codigo, nombre, departamento, correo, direccion, tel, sexo, fecha_nac '
                'FROM public."Profesor" WHERE codigo = %s', (int(codigo),)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["Codigo", "Nombre", "Departamento", "Correo",
                          "Direccion", "Telefono", "Sexo", "Fecha Nac"]
                for clave, valor in zip(claves, fila):
                    labels_val[clave].config(text=str(valor))
                lbl_estado.config(text="✅ Profesor encontrado.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un profesor con ese codigo.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Buscar", command=buscar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)


# ── CONSULTA GENERAL ─────────────────────────────────────────────
def ventana_consulta_general(nombre_usuario):
    win = tk.Toplevel()
    win.title("Consulta General de Profesores")
    win.geometry("900x360")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta General de Profesores", nombre_usuario)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("codigo", "nombre", "departamento", "correo",
                "direccion", "tel", "sexo", "fecha_nac")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)

    encabezados = ["Codigo", "Nombre", "Departamento", "Correo",
                   "Direccion", "Telefono", "Sexo", "Fecha Nac"]
    anchos = [70, 160, 140, 180, 120, 100, 50, 90]

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
            'SELECT codigo, nombre, departamento, correo, direccion, tel, sexo, fecha_nac '
            'FROM public."Profesor"'
        )
        filas = cur.fetchall()
        cur.close()
        conn.close()
        for fila in filas:
            tabla.insert("", "end", values=fila)
        lbl_estado.config(text=f"✅ {len(filas)} profesor(es) encontrado(s).", fg="#27ae60")
    except Exception as e:
        lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")


# ── CAMBIAR ──────────────────────────────────────────────────────
def ventana_cambiar(nombre_usuario):
    win = tk.Toplevel()
    win.title("Cambiar Datos de Profesor")
    win.geometry("420x470")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Cambiar Datos de Profesor", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="Codigo:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_cod = tk.Entry(frame_bus, font=("Arial", 11), width=18)
    entry_cod.pack(side="left")

    frame = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=5, fill="x")

    campos = [
        ("Nombre",                 "nombre"),
        ("Departamento",           "departamento"),
        ("Correo",                 "correo"),
        ("Direccion",              "direccion"),
        ("Telefono",               "tel"),
        ("Sexo (M/F)",             "sexo"),
        ("Fecha Nac (DD-MM-YYYY)", "fecha_nac"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=3)
        tk.Label(fila, text=etiqueta, width=20, anchor="w",
                 bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=20)
        entrada.pack(side="left")
        entradas[clave] = entrada

    lbl_estado = lbl_msg(win)

    def cargar():
        codigo = entry_cod.get().strip()
        if not codigo:
            lbl_estado.config(text="⚠ Ingresa un codigo.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT nombre, departamento, correo, direccion, tel, sexo, fecha_nac '
                'FROM public."Profesor" WHERE codigo = %s', (int(codigo),)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["nombre", "departamento", "correo", "direccion", "tel", "sexo", "fecha_nac"]
                for clave, valor in zip(claves, fila):
                    entradas[clave].delete(0, tk.END)
                    entradas[clave].insert(0, str(valor))
                lbl_estado.config(text="✅ Datos cargados.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un profesor con ese codigo.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Cargar", command=cargar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)

    def actualizar():
        codigo       = entry_cod.get().strip()
        nombre       = entradas["nombre"].get().strip()
        departamento = entradas["departamento"].get().strip()
        correo       = entradas["correo"].get().strip()
        direccion    = entradas["direccion"].get().strip()
        tel          = entradas["tel"].get().strip()
        sexo         = entradas["sexo"].get().strip()
        fecha_nac    = entradas["fecha_nac"].get().strip()

        if not all([codigo, nombre, departamento, correo, direccion, tel, sexo, fecha_nac]):
            lbl_estado.config(text="⚠ Completa todos los campos.", fg="#e67e22")
            return
        try:
            fecha_convertida = datetime.strptime(fecha_nac, "%Y-%m-%d").strftime("%Y-%m-%d")
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """UPDATE public."Profesor"
                SET nombre=%s, departamento=%s, correo=%s, direccion=%s,
                    tel=%s, sexo=%s, fecha_nac=%s
                WHERE codigo=%s""",
                (nombre, departamento, correo, direccion, int(tel), sexo, fecha_convertida, int(codigo))
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
    win.title("Eliminar Profesor")
    win.geometry("360x250")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Eliminar Profesor", nombre_usuario)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(pady=15)
    tk.Label(frame, text="Codigo:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_cod = tk.Entry(frame, font=("Arial", 11), width=18)
    entry_cod.pack(side="left")

    lbl_estado = lbl_msg(win)

    def eliminar():
        codigo = entry_cod.get().strip()
        if not codigo:
            lbl_estado.config(text="⚠ Ingresa un codigo.", fg="#e67e22")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar profesor con codigo {codigo}?"):
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute('DELETE FROM public."Profesor" WHERE codigo = %s', (int(codigo),))
            if cur.rowcount == 0:
                lbl_estado.config(text="❌ No existe un profesor con ese codigo.", fg="#c0392b")
            else:
                conn.commit()
                lbl_estado.config(text="✅ Profesor eliminado correctamente.", fg="#27ae60")
                entry_cod.delete(0, tk.END)
            cur.close()
            conn.close()
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(win, text="Eliminar", command=eliminar,
              font=("Arial", 11, "bold"), bg="#c0392b", fg="white",
              width=18, pady=6, relief="flat", cursor="hand2").pack(pady=10)


# ── MENÚ PROFESORES ──────────────────────────────────────────────
def ventana_profesores(nombre_usuario):
    pro = tk.Toplevel()
    pro.title("Gestion de Profesores")
    pro.geometry("340x390")
    pro.resizable(False, False)
    pro.configure(bg="#f0f4f8")

    barra_usuario(pro, "Profesores", nombre_usuario)

    tk.Label(pro, text="Menu Profesores",
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
        tk.Button(pro, text=texto, command=cmd,
                  font=("Arial", 11), bg=color, fg="white",
                  width=24, pady=6, relief="flat", cursor="hand2").pack(pady=5)