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

def ventana_registrar():
    reg = tk.Toplevel()
    reg.title("Registrar Alumno")
    reg.geometry("420x380")
    reg.resizable(False, False)
    reg.configure(bg="#f0f4f8")

    tk.Label(reg, text="Registrar Alumno",
            font=("Arial", 13, "bold"),
            bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame = tk.Frame(reg, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, fill="x")

    campos = [
        ("Codigo",       "codigo"),
        ("Nombre",       "nombre"),
        ("Carrera",    "carrera"),
        ("Correo",     "correo"),
        ("Fecha Nacimiento",    "fecha_nac"),
        ("Sexo",        "sexo"),
        ("Telefono",        "tel"),
        ("Direccion",        "direccion"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=4)
        tk.Label(fila, text=etiqueta, width=12, anchor="w",
               bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=25)
        entrada.pack(side="left")
        entradas[clave] = entrada

    def guardar():
        codigo    = entradas["codigo"].get().strip()
        nombre    = entradas["nombre"].get().strip()
        carrera = entradas["carrera"].get().strip()
        correo  = entradas["correo"].get().strip()
        fecha_nac = entradas["fecha_nac"].get().strip()
        sexo      = entradas["sexo"].get().strip()
        tel     = entradas["tel"].get().strip()
        direccion     = entradas["direccion"].get().strip()

        if not all([codigo, nombre, direccion, tel, sexo, fecha_nac, carrera, correo]):
            messagebox.showwarning("Campos vacios", "Completa todos los campos.")
            return

        try:
            fecha_convertida = datetime.strptime(fecha_nac, "%d-%m-%Y").strftime("%Y-%m-%d")
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO public."Alumno"
                (codigo, nombre, direccion, tel, sexo, fecha_nac, turno)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (codigo, nombre, direccion, tel, sexo, fecha_convertida, turno)
            )
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Exito", "Empleado registrado correctamente.")
            reg.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(reg, text="Guardar",
             command=guardar,
             font=("Arial", 11, "bold"),
             bg="#27ae60", fg="white",
             width=18, pady=6,
             relief="flat", cursor="hand2").pack(pady=16)

def ventana_consulta_general():
    win = tk.Toplevel()
    win.title("Consulta General de Empleados")
    win.geometry("700x300")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    tk.Label(win, text="Consulta General de Empleados",
            font=("Arial", 13, "bold"),
            bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(fill="both", expand=True, padx=20, pady=5)

    columnas = ("codigo", "nombre", "direccion", "telefono", "sexo", "fecha_nac", "turno")

    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)

    encabezados = ["Codigo", "Nombre", "Direccion", "Telefono", "Sexo", "Fecha Nac", "Turno"]
    anchos = [70, 150, 130, 120, 60, 100, 100]

    for col, enc, ancho in zip(columnas, encabezados, anchos):
        tabla.heading(col, text=enc)
        tabla.column(col, width=ancho, anchor="center")

    tabla.pack(fill="both", expand=True)

    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute('SELECT codigo, nombre, direccion, tel, sexo, fecha_nac, turno FROM public."Empleado"')
        filas = cur.fetchall()
        cur.close()
        conn.close()
        for fila in filas:
            tabla.insert("", "end", values=fila)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def ventana_empleados():
    emp = tk.Toplevel()
    emp.title("Empleados")
    emp.geometry("340x320")
    emp.resizable(False, False)
    emp.configure(bg="#f0f4f8")

    tk.Label(emp, text="Empleados",
            font=("Arial", 14, "bold"),
            bg="#f0f4f8", fg="#1a3c5e").pack(pady=16)

    opciones = [
        ("Registrar",          ventana_registrar),
        ("Consulta Individual", lambda: None),
        ("Consulta General",    ventana_consulta_general),
        ("Cambiar",             lambda: None),
        ("Eliminar",            lambda: None),
    ]

    colores = ["#2980b9", "#27ae60", "#8e44ad", "#e67e22", "#c0392b"]

    for (texto, cmd), color in zip(opciones, colores):
        tk.Button(emp, text=texto,
                command=cmd,
                font=("Arial", 11),
                bg=color, fg="white",
                width=24, pady=6,
                relief="flat",
                cursor="hand2").pack(pady=5)

root = tk.Tk()
root.withdraw()
ventana_empleados()
root.mainloop()