import tkinter as tk
from tkinter import messagebox
import psycopg2

def verificar_credenciales(usuario, contrasena):
    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="Biblioteca",
            user="postgres",
            password="2405",
            port="5432"
        )
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM public.\"Usuario\" "
            "WHERE nombre_usuario=%s AND contrasena=%s",
            (usuario, contrasena)
        )
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        return resultado is not None
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        return False

def iniciar_sesion():
    usuario    = entry_usuario.get().strip()
    contrasena = entry_contrasena.get().strip()

    if not usuario or not contrasena:
        messagebox.showwarning("Campos vacíos",
                                "Por favor llena todos los campos.")
        return

    if verificar_credenciales(usuario, contrasena):
        messagebox.showinfo("Acceso concedido",
                             f"¡Bienvenido, {usuario}!")
        ventana.destroy()
        abrir_menu_principal()
    else:
        messagebox.showerror("Acceso denegado",
                              "Usuario o contraseña incorrectos.")

def abrir_menu_principal():
    menu = tk.Tk()
    menu.title("Sistema Biblioteca — Menú Principal")
    menu.geometry("400x300")
    tk.Label(menu, text="Menú Principal",
            font=("Arial", 18)).pack(pady=40)
    menu.mainloop()

# ── Ventana ────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Sistema Biblioteca — Inicio de Sesión")
ventana.geometry("400x300")
ventana.resizable(False, False)
ventana.configure(bg="#f0f4f8")

tk.Label(ventana, text="📚 Sistema Biblioteca",
       font=("Arial", 16, "bold"),
       bg="#f0f4f8", fg="#2c3e50").pack(pady=20)

frame = tk.Frame(ventana, bg="white", bd=1, relief="solid")
frame.pack(padx=40, pady=5, fill="both")

tk.Label(frame, text="Usuario:", bg="white",
       font=("Arial", 11)).pack(anchor="w", padx=15, pady=(15,2))
entry_usuario = tk.Entry(frame, font=("Arial", 11), width=30)
entry_usuario.pack(padx=15)

tk.Label(frame, text="Contraseña:", bg="white",
       font=("Arial", 11)).pack(anchor="w", padx=15, pady=(10,2))
entry_contrasena = tk.Entry(frame, font=("Arial", 11),
                            width=30, show="*")
entry_contrasena.pack(padx=15, pady=(0,15))

tk.Button(ventana, text="Ingresar",
         command=iniciar_sesion,
         font=("Arial", 12, "bold"),
         bg="#2980b9", fg="white",
         width=20, pady=6,
         relief="flat", cursor="hand2").pack(pady=15)

ventana.mainloop()