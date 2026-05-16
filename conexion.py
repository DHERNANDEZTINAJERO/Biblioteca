import psycopg2

try:
    conexion = psycopg2.connect(
        host="localhost",
        database="Biblioteca",
        user="postgres",
        password="2405",
        port="5432"
    )
    print("Conexion exitosa")
    conexion.close()

except Exception as e:
    print("Error al conectar:", e)