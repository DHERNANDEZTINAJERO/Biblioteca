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
        lbl_bienvenida.config(
            text="⚠ Por favor llena todos los campos.",
            fg="#e67e22"
        )
        return

    if verificar_credenciales(usuario, contrasena):
        lbl_bienvenida.config(
            text=f"✅ ¡Bienvenido, {usuario}!",
            fg="#27ae60"
        )
        btn_ingresar.config(state="disabled")
        ventana.after(1200, lambda: abrir_menu(usuario))
    else:
        lbl_bienvenida.config(
            text="❌ Usuario o contraseña incorrectos.",
            fg="#c0392b"
        )


def abrir_menu(usuario):
    ventana.destroy()
    from menuprincipal import abrir_menu_principal
    # Si es administrador abre menú admin, si no menú empleado
    es_admin = (usuario.lower() == "administrador")
    abrir_menu_principal(usuario, es_admin)


# ── Ventana principal ────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Sistema Biblioteca — Inicio de Sesión")
ventana.geometry("400x320")
ventana.resizable(False, False)
ventana.configure(bg="#f0f4f8")

tk.Label(
    ventana,
    text="📚 Sistema Biblioteca",
    font=("Arial", 16, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50"
).pack(pady=20)

frame = tk.Frame(ventana, bg="white", bd=1, relief="solid")
frame.pack(padx=40, pady=5, fill="both")

tk.Label(
    frame, text="Usuario:",
    bg="white", font=("Arial", 11)
).pack(anchor="w", padx=15, pady=(15, 2))

entry_usuario = tk.Entry(frame, font=("Arial", 11), width=30)
entry_usuario.pack(padx=15)

tk.Label(
    frame, text="Contraseña:",
    bg="white", font=("Arial", 11)
).pack(anchor="w", padx=15, pady=(10, 2))

entry_contrasena = tk.Entry(frame, font=("Arial", 11), width=30, show="*")
entry_contrasena.pack(padx=15, pady=(0, 15))

ventana.bind("<Return>", lambda event: iniciar_sesion())

btn_ingresar = tk.Button(
    ventana,
    text="Ingresar",
    command=iniciar_sesion,
    font=("Arial", 12, "bold"),
    bg="#2980b9", fg="white",
    width=20, pady=6,
    relief="flat", cursor="hand2"
)
btn_ingresar.pack(pady=15)

lbl_bienvenida = tk.Label(
    ventana, text="",
    font=("Arial", 10, "bold"),
    bg="#f0f4f8"
)
lbl_bienvenida.pack()

ventana.mainloop()