import mysql.connector
from tkinter import messagebox

# --- CONFIGURACIÓN GLOBAL ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", # Pon tu contraseña aquí
    "database": "veterinaria",
    "port": 3306
}

def crear_conexion():
    """Establece y retorna la conexión a la base de datos."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Error BD", f"No se pudo conectar: {err}")
        return None

# --- FUNCIONES DE CONSULTA (SELECTS) ---

def obtener_clientes():
    """Retorna todos los registros de la tabla clientes."""
    conn = crear_conexion()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    datos = cursor.fetchall()
    conn.close()
    return datos

def buscar_clientes_por_nombre(nombre_busqueda):
    """Busca clientes cuyo nombre coincida parcialmente con el término."""
    conn = crear_conexion()
    if not conn: return []
    try:
        cursor = conn.cursor()
        # El símbolo % permite buscar coincidencias parciales (ej: "Cla" encuentra "Claudia")
        query = "SELECT * FROM clientes WHERE nombre LIKE %s"
        cursor.execute(query, (f"%{nombre_busqueda}%",))
        datos = cursor.fetchall()
        return datos
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return []
    finally:
        conn.close()

def obtener_productos_inventario():
    conn = crear_conexion()
    if not conn: return []
    cursor = conn.cursor()
    # Añadimos 'fecha_caducidad' a la consulta
    cursor.execute("SELECT id_producto, nombre, categoria, cantidad, fecha_caducidad FROM productos")
    datos = cursor.fetchall()
    conn.close()
    return datos

# --- FUNCIONES DE ACCIÓN (INSERT / UPDATE / DELETE) ---

def insertar_cliente(nombre, telefono, email):
    """Inserta un nuevo cliente en la base de datos."""
    conn = crear_conexion()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, telefono, email))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo guardar: {e}")
        return False
    finally:
        conn.close()

def actualizar_stock_producto(id_producto, cantidad, tipo_movimiento):
    """Actualiza el stock sumando o restando según el tipo de movimiento."""
    conn = crear_conexion()
    if not conn: return False
    try:
        cursor = conn.cursor()
        operador = "+" if tipo_movimiento == "Entrada" else "-"
        query = f"UPDATE productos SET cantidad = cantidad {operador} %s WHERE id_producto = %s"
        cursor.execute(query, (cantidad, id_producto))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("Error Stock", str(e))
        return False
    finally:
        conn.close()