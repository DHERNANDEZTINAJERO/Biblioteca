import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import psycopg2
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ── CONFIGURACION DE CORREO ──────────────────────────────────────
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USER     = "biblioteca.quadralib@gmail.com"
SMTP_PASSWORD = "iblgmqqnbpkngjqp"
CORREO_DEST   = "felipe.mariscal@academicos.udg.mx"


def enviar_correo_multa(archivo_pdf, datos):
    """Envía el PDF de multa al correo del solicitante."""
    msg = MIMEMultipart()
    msg["From"]    = SMTP_USER
    msg["To"]      = CORREO_DEST
    msg["Subject"] = f"Aviso de Multa - Prestamo #{datos['id']} - QuadraLib"

    cuerpo = f"""
Estimado/a {datos['solicitante']},

Se le informa que el libro prestado ha sido devuelto con retraso de {datos['dias_retraso']} dia(s).

Detalles:
- Libro: {datos['titulo']}
- ISBN: {datos['libro']}
- Fecha limite: {datos['fecha_limite']}
- Fecha devolucion: {datos['fecha_dev']}
- Multa a pagar: ${datos['multa']:.2f} MXN

Se adjunta el comprobante de multa en formato PDF.

Atentamente,
QuadraLib - Sistema de Gestion de Biblioteca
    """
    msg.attach(MIMEText(cuerpo, "plain"))

    with open(archivo_pdf, "rb") as f:
        adjunto = MIMEBase("application", "octet-stream")
        adjunto.set_payload(f.read())
    encoders.encode_base64(adjunto)
    adjunto.add_header("Content-Disposition", f"attachment; filename={archivo_pdf}")
    msg.attach(adjunto)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor:
        servidor.starttls()
        servidor.login(SMTP_USER, SMTP_PASSWORD)
        servidor.sendmail(SMTP_USER, CORREO_DEST, msg.as_string())


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


# ── GENERAR PDF DE MULTA ─────────────────────────────────────────
def generar_pdf_multa(datos):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    nombre_archivo = f"multa_{datos['id']}.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, height - 60, "QuadraLib - Aviso de Multa")
    c.setFont("Helvetica", 12)
    c.line(50, height - 75, width - 50, height - 75)

    y = height - 110
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Datos del Prestamo:")
    y -= 25

    campos = [
        ("ID Prestamo:",      str(datos["id"])),
        ("Solicitante:",      datos["solicitante"]),
        ("ISBN del Libro:",   datos["libro"]),
        ("Num. Ejemplar:",    str(datos["num_ejemplar"])),
        ("Titulo:",           datos["titulo"]),
        ("Fecha Prestamo:",   datos["fecha_prestamo"]),
        ("Fecha Limite:",     datos["fecha_limite"]),
        ("Fecha Devolucion:", datos["fecha_dev"]),
        ("Dias de retraso:",  str(datos["dias_retraso"])),
        ("Multa a pagar:",    f"${datos['multa']:.2f} MXN"),
    ]

    for etiqueta, valor in campos:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, y, etiqueta)
        c.setFont("Helvetica", 11)
        c.drawString(220, y, valor)
        y -= 22

    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"TOTAL A PAGAR: ${datos['multa']:.2f} MXN")
    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Este documento fue generado automaticamente por QuadraLib v1.0")
    c.save()
    return nombre_archivo


# ── REGISTRAR PRÉSTAMO ───────────────────────────────────────────
def ventana_registrar(nombre_usuario):
    reg = tk.Toplevel()
    reg.title("Registrar Prestamo")
    reg.geometry("420x430")
    reg.resizable(False, False)
    reg.configure(bg="#f0f4f8")

    barra_usuario(reg, "Registrar Prestamo", nombre_usuario)

    frame = tk.Frame(reg, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=10, fill="x")

    campos = [
        ("Solicitante (nombre)",       "solicitante"),
        ("ISBN del libro",             "libro"),
        ("Num. Ejemplar",              "num_ejemplar"),
        ("Fecha Prestamo (DD-MM-YYYY)","fecha_prestamo"),
        ("Fecha Limite (DD-MM-YYYY)",  "fecha_limite"),
    ]

    entradas = {}
    for etiqueta, clave in campos:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=4)
        tk.Label(fila, text=etiqueta, width=22, anchor="w",
                 bg="white", font=("Arial", 10)).pack(side="left")
        entrada = tk.Entry(fila, font=("Arial", 10), width=20)
        entrada.pack(side="left")
        entradas[clave] = entrada

    lbl = lbl_msg(reg)

    def guardar():
        solicitante    = entradas["solicitante"].get().strip()
        libro          = entradas["libro"].get().strip()
        num_ejemplar   = entradas["num_ejemplar"].get().strip()
        fecha_prestamo = entradas["fecha_prestamo"].get().strip()
        fecha_limite   = entradas["fecha_limite"].get().strip()

        if not all([solicitante, libro, num_ejemplar, fecha_prestamo, fecha_limite]):
            lbl.config(text="⚠ Completa todos los campos.", fg="#e67e22")
            return
        try:
            fp = datetime.strptime(fecha_prestamo, "%d-%m-%Y").strftime("%Y-%m-%d")
            fl = datetime.strptime(fecha_limite,   "%d-%m-%Y").strftime("%Y-%m-%d")
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """INSERT INTO public."Prestamo"
                (solicitante, libro, num_ejemplar, fecha_prestamo, fecha_limite, estatus, multa)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (solicitante, libro, int(num_ejemplar), fp, fl, "Activo", 0)
            )
            conn.commit()
            cur.close()
            conn.close()
            lbl.config(text="✅ Prestamo registrado correctamente.", fg="#27ae60")
            for e in entradas.values():
                e.delete(0, tk.END)
        except Exception as e:
            lbl.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(reg, text="Guardar", command=guardar,
              font=("Arial", 11, "bold"), bg="#27ae60", fg="white",
              width=18, pady=6, relief="flat", cursor="hand2").pack(pady=10)


# ── DEVOLVER PRÉSTAMO ────────────────────────────────────────────
def ventana_devolver(nombre_usuario):
    win = tk.Toplevel()
    win.title("Devolver Prestamo")
    win.geometry("420x390")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Devolver Prestamo", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="ID Prestamo:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_id = tk.Entry(frame_bus, font=("Arial", 11), width=12)
    entry_id.pack(side="left")

    frame = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame.pack(padx=30, pady=5, fill="x")

    campos_info = ["Solicitante", "Libro", "Fecha Limite", "Estatus"]
    labels_val  = {}
    for campo in campos_info:
        fila = tk.Frame(frame, bg="white")
        fila.pack(fill="x", padx=15, pady=3)
        tk.Label(fila, text=f"{campo}:", width=14, anchor="w",
                 bg="white", font=("Arial", 10, "bold")).pack(side="left")
        lbl = tk.Label(fila, text="", anchor="w", bg="white", font=("Arial", 10))
        lbl.pack(side="left")
        labels_val[campo] = lbl

    prestamo_actual = {}

    def cargar():
        id_p = entry_id.get().strip()
        if not id_p:
            lbl_estado.config(text="⚠ Ingresa un ID.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT id, solicitante, libro, num_ejemplar, fecha_prestamo, '
                'fecha_limite, estatus FROM public."Prestamo" WHERE id = %s',
                (int(id_p),)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                prestamo_actual.update({
                    "id": fila[0], "solicitante": fila[1], "libro": fila[2],
                    "num_ejemplar": fila[3], "fecha_prestamo": fila[4],
                    "fecha_limite": fila[5], "estatus": fila[6]
                })
                labels_val["Solicitante"].config(text=fila[1])
                labels_val["Libro"].config(text=f"{fila[2]} - Ej.{fila[3]}")
                labels_val["Fecha Limite"].config(text=fila[5])
                labels_val["Estatus"].config(text=fila[6])
                lbl_estado.config(text="✅ Prestamo cargado.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un prestamo con ese ID.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Cargar", command=cargar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)

    fila_dev = tk.Frame(win, bg="#f0f4f8")
    fila_dev.pack(pady=8)
    tk.Label(fila_dev, text="Fecha Devolucion (DD-MM-YYYY):",
             bg="#f0f4f8", font=("Arial", 10)).pack(side="left", padx=5)
    entry_dev = tk.Entry(fila_dev, font=("Arial", 10), width=14)
    entry_dev.pack(side="left")

    lbl_estado = lbl_msg(win)

    def devolver():
        if not prestamo_actual:
            lbl_estado.config(text="⚠ Primero carga un prestamo.", fg="#e67e22")
            return
        fecha_dev_str = entry_dev.get().strip()
        if not fecha_dev_str:
            lbl_estado.config(text="⚠ Ingresa la fecha de devolucion.", fg="#e67e22")
            return
        try:
            fecha_dev    = datetime.strptime(fecha_dev_str, "%d-%m-%Y").date()
            fecha_limite = datetime.strptime(prestamo_actual["fecha_limite"], "%Y-%m-%d").date()
            dias_retraso = (fecha_dev - fecha_limite).days
            multa   = max(dias_retraso, 0) * 100
            estatus = "Devuelto con multa" if dias_retraso > 0 else "Devuelto"

            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                """UPDATE public."Prestamo"
                SET fecha_dev=%s, estatus=%s, multa=%s WHERE id=%s""",
                (fecha_dev.strftime("%Y-%m-%d"), estatus, multa, prestamo_actual["id"])
            )
            cur.execute(
                'SELECT titulo FROM public."Libro" WHERE isbn=%s AND num_ejemplar=%s',
                (prestamo_actual["libro"], prestamo_actual["num_ejemplar"])
            )
            titulo_fila = cur.fetchone()
            titulo = titulo_fila[0] if titulo_fila else prestamo_actual["libro"]
            conn.commit()
            cur.close()
            conn.close()

            if dias_retraso > 0:
                datos_pdf = {
                    "id":            prestamo_actual["id"],
                    "solicitante":   prestamo_actual["solicitante"],
                    "libro":         prestamo_actual["libro"],
                    "num_ejemplar":  prestamo_actual["num_ejemplar"],
                    "titulo":        titulo,
                    "fecha_prestamo":prestamo_actual["fecha_prestamo"],
                    "fecha_limite":  prestamo_actual["fecha_limite"],
                    "fecha_dev":     fecha_dev.strftime("%Y-%m-%d"),
                    "dias_retraso":  dias_retraso,
                    "multa":         multa,
                }
                archivo_pdf = generar_pdf_multa(datos_pdf)
                try:
                    enviar_correo_multa(archivo_pdf, datos_pdf)
                    lbl_estado.config(
                        text=f"⚠ Multa: ${multa:.2f} MXN. PDF generado y correo enviado a {CORREO_DEST}",
                        fg="#c0392b"
                    )
                except Exception as mail_err:
                    lbl_estado.config(
                        text=f"⚠ Multa: ${multa:.2f}. PDF generado pero error al enviar correo: {str(mail_err)}",
                        fg="#e67e22"
                    )
            else:
                lbl_estado.config(text="✅ Libro devuelto a tiempo. Sin multa.", fg="#27ae60")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(win, text="Registrar Devolucion", command=devolver,
              font=("Arial", 11, "bold"), bg="#e67e22", fg="white",
              width=22, pady=6, relief="flat", cursor="hand2").pack(pady=5)


# ── CONSULTA INDIVIDUAL ──────────────────────────────────────────
def ventana_consulta_prestamo(nombre_usuario):
    win = tk.Toplevel()
    win.title("Consulta de Prestamo")
    win.geometry("420x400")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta de Prestamo", nombre_usuario)

    frame_bus = tk.Frame(win, bg="#f0f4f8")
    frame_bus.pack(pady=8)
    tk.Label(frame_bus, text="ID Prestamo:", bg="#f0f4f8",
             font=("Arial", 11)).pack(side="left", padx=5)
    entry_id = tk.Entry(frame_bus, font=("Arial", 11), width=12)
    entry_id.pack(side="left")

    frame_res = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame_res.pack(padx=30, pady=5, fill="x")

    campos = ["ID", "Solicitante", "Libro", "Num Ejemplar",
              "Fecha Prestamo", "Fecha Limite", "Fecha Dev", "Estatus", "Multa"]
    labels_val = {}

    for campo in campos:
        fila = tk.Frame(frame_res, bg="white")
        fila.pack(fill="x", padx=15, pady=2)
        tk.Label(fila, text=f"{campo}:", width=14, anchor="w",
                 bg="white", font=("Arial", 10, "bold")).pack(side="left")
        lbl = tk.Label(fila, text="", anchor="w", bg="white", font=("Arial", 10))
        lbl.pack(side="left")
        labels_val[campo] = lbl

    lbl_estado = lbl_msg(win)

    def buscar():
        id_p = entry_id.get().strip()
        if not id_p:
            lbl_estado.config(text="⚠ Ingresa un ID.", fg="#e67e22")
            return
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                'SELECT id, solicitante, libro, num_ejemplar, fecha_prestamo, '
                'fecha_limite, fecha_dev, estatus, multa '
                'FROM public."Prestamo" WHERE id = %s', (int(id_p),)
            )
            fila = cur.fetchone()
            cur.close()
            conn.close()
            if fila:
                claves = ["ID", "Solicitante", "Libro", "Num Ejemplar",
                          "Fecha Prestamo", "Fecha Limite", "Fecha Dev", "Estatus", "Multa"]
                for clave, valor in zip(claves, fila):
                    labels_val[clave].config(text=str(valor) if valor else "-")
                lbl_estado.config(text="✅ Prestamo encontrado.", fg="#27ae60")
            else:
                lbl_estado.config(text="❌ No existe un prestamo con ese ID.", fg="#c0392b")
        except Exception as e:
            lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")

    tk.Button(frame_bus, text="Buscar", command=buscar,
              font=("Arial", 10, "bold"), bg="#2980b9", fg="white",
              relief="flat", cursor="hand2", padx=10).pack(side="left", padx=8)


# ── CONSULTA GENERAL ─────────────────────────────────────────────
def ventana_consulta_prestamos(nombre_usuario):
    win = tk.Toplevel()
    win.title("Consulta General de Prestamos")
    win.geometry("950x360")
    win.resizable(False, False)
    win.configure(bg="#f0f4f8")

    barra_usuario(win, "Consulta General de Prestamos", nombre_usuario)

    frame = tk.Frame(win, bg="#f0f4f8")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    columnas = ("id", "solicitante", "libro", "num_ejemplar",
                "fecha_prestamo", "fecha_limite", "fecha_dev", "estatus", "multa")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings", height=8)

    encabezados = ["ID", "Solicitante", "Libro", "Ejemplar",
                   "Fecha Prestamo", "Fecha Limite", "Fecha Dev", "Estatus", "Multa"]
    anchos = [40, 100, 140, 60, 100, 100, 100, 120, 70]

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
            'SELECT id, solicitante, libro, num_ejemplar, fecha_prestamo, '
            'fecha_limite, fecha_dev, estatus, multa FROM public."Prestamo"'
        )
        filas = cur.fetchall()
        cur.close()
        conn.close()
        for fila in filas:
            tabla.insert("", "end", values=[str(v) if v else "-" for v in fila])
        lbl_estado.config(text=f"✅ {len(filas)} prestamo(s) encontrado(s).", fg="#27ae60")
    except Exception as e:
        lbl_estado.config(text=f"❌ Error: {str(e)}", fg="#c0392b")


# ── MENÚ PRÉSTAMOS ───────────────────────────────────────────────
def ventana_prestamos(nombre_usuario):
    pre = tk.Toplevel()
    pre.title("Gestion de Prestamos")
    pre.geometry("340x360")
    pre.resizable(False, False)
    pre.configure(bg="#f0f4f8")

    barra_usuario(pre, "Prestamos", nombre_usuario)

    tk.Label(pre, text="Menu Prestamos",
             font=("Arial", 13, "bold"),
             bg="#f0f4f8", fg="#1a3c5e").pack(pady=12)

    opciones = [
        ("Registrar Prestamo",    "#2980b9", lambda: ventana_registrar(nombre_usuario)),
        ("Devolver Prestamo",     "#27ae60", lambda: ventana_devolver(nombre_usuario)),
        ("Consulta de Prestamo",  "#8e44ad", lambda: ventana_consulta_prestamo(nombre_usuario)),
        ("Consulta de Prestamos", "#e67e22", lambda: ventana_consulta_prestamos(nombre_usuario)),
    ]

    for texto, color, cmd in opciones:
        tk.Button(pre, text=texto, command=cmd,
                  font=("Arial", 11), bg=color, fg="white",
                  width=24, pady=6, relief="flat", cursor="hand2").pack(pady=5)