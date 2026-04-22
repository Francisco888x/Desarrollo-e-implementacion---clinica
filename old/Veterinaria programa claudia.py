import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# --- CONFIGURACIÓN DE CONEXIÓN ---
def crear_conexion():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root", 
            password="",  # Coloca tu contraseña aquí si tienes
            database="veterinaria",
            port=3306
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Error BD", f"No se pudo conectar: {err}")
        return None

# --- CLASE: LOGIN ---
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - VetControl")
        self.root.geometry("300x250")
        self.root.configure(bg="#2c3e50")

        frame = tk.Frame(root, bg="#2c3e50")
        frame.pack(pady=40)

        tk.Label(frame, text="Usuario:", fg="white", bg="#2c3e50", font=("Arial", 10)).pack()
        self.entry_user = tk.Entry(frame)
        self.entry_user.pack(pady=5)

        tk.Label(frame, text="Contraseña:", fg="white", bg="#2c3e50", font=("Arial", 10)).pack()
        self.entry_pass = tk.Entry(frame, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(frame, text="INGRESAR", command=self.validar_login, bg="#27ae60", fg="white", width=15).pack(pady=20)

    def validar_login(self):
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (self.entry_user.get(), self.entry_pass.get()))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                self.root.withdraw()
                ventana_principal = tk.Toplevel(self.root)
                app = SistemaVeterinaria(ventana_principal, usuario[1]) 
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# --- CLASE: SISTEMA PRINCIPAL ---
class SistemaVeterinaria:
    def __init__(self, root, nombre_usuario):
        self.root = root
        self.root.title(f"VetControl - Bienvenido {nombre_usuario}")
        self.root.geometry("1000x700")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Inicializar módulos
        self.crear_modulo_clientes()
        self.crear_modulo_mascotas()
        self.crear_modulo_citas()      # <--- NUEVO
        self.crear_modulo_inventario()
        self.crear_modulo_compras()

    # ------------------------------------------------------------------
    # MÓDULO 1: CLIENTES (CON BOTÓN CONSULTAR)
    # ------------------------------------------------------------------
    def crear_modulo_clientes(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Clientes")

        # --- BUSCADOR (BOTÓN CONSULTAR) ---
        busqueda_frame = tk.LabelFrame(frame, text="Buscar Cliente")
        busqueda_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(busqueda_frame, text="Nombre:").pack(side="left", padx=5)
        self.ent_busqueda = tk.Entry(busqueda_frame)
        self.ent_busqueda.pack(side="left", padx=5, fill="x", expand=True)
        
        tk.Button(busqueda_frame, text="Consultar", command=self.consultar_cliente, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(busqueda_frame, text="Refrescar", command=self.cargar_tabla_clientes).pack(side="left", padx=5)

        # Formulario
        form = tk.Frame(frame)
        form.pack(pady=10)
        self.cli_nombre = tk.StringVar(); self.cli_tel = tk.StringVar(); self.cli_email = tk.StringVar()
        
        tk.Label(form, text="Nombre:").grid(row=0, column=0)
        tk.Entry(form, textvariable=self.cli_nombre).grid(row=0, column=1, padx=5)
        tk.Label(form, text="Tel:").grid(row=0, column=2)
        tk.Entry(form, textvariable=self.cli_tel).grid(row=0, column=3, padx=5)
        
        tk.Button(frame, text="Guardar Cliente", command=self.guardar_cliente, bg="#27ae60", fg="white").pack(pady=5)

        self.tree_clientes = ttk.Treeview(frame, columns=("ID", "Nombre", "Tel", "Email"), show="headings")
        for col in ("ID", "Nombre", "Tel", "Email"): self.tree_clientes.heading(col, text=col)
        self.tree_clientes.pack(fill="both", expand=True, padx=10)
        self.cargar_tabla_clientes()

    def consultar_cliente(self):
        termino = self.ent_busqueda.get()
        for x in self.tree_clientes.get_children(): self.tree_clientes.delete(x)
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE nombre LIKE %s", (f"%{termino}%",))
            for row in cursor.fetchall(): self.tree_clientes.insert("", "end", values=row)
            conn.close()

    def cargar_tabla_clientes(self):
        for x in self.tree_clientes.get_children(): self.tree_clientes.delete(x)
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes")
            for row in cursor.fetchall(): self.tree_clientes.insert("", "end", values=row)
            conn.close()

    def guardar_cliente(self):
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)", 
                             (self.cli_nombre.get(), self.cli_tel.get(), self.cli_email.get()))
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente registrado")
                self.cargar_tabla_clientes()
            except Exception as e: messagebox.showerror("Error", str(e))
            conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 2: MASCOTAS
    # ------------------------------------------------------------------
    def crear_modulo_mascotas(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Mascotas")
        self.tree_mascotas = ttk.Treeview(frame, columns=("ID", "Nombre", "Especie", "Dueño"), show="headings")
        for col in ("ID", "Nombre", "Especie", "Dueño"): self.tree_mascotas.heading(col, text=col)
        self.tree_mascotas.pack(fill="both", expand=True, padx=10, pady=10)
        self.cargar_tabla_mascotas()

    def cargar_tabla_mascotas(self):
        for x in self.tree_mascotas.get_children(): self.tree_mascotas.delete(x)
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_mascota, nombre, especie, id_cliente FROM mascotas")
            for row in cursor.fetchall(): self.tree_mascotas.insert("", "end", values=row)
            conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 3: CITAS (REGISTRAR CITA)
    # ------------------------------------------------------------------
    def crear_modulo_citas(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Citas")

        f_cita = tk.LabelFrame(frame, text="Registrar Cita")
        f_cita.pack(fill="x", padx=10, pady=5)

        self.c_fecha = tk.StringVar(); self.c_id_m = tk.StringVar(); self.c_motivo = tk.StringVar()

        tk.Label(f_cita, text="Fecha (AAAA-MM-DD):").grid(row=0, column=0)
        tk.Entry(f_cita, textvariable=self.c_fecha).grid(row=0, column=1, padx=5)
        tk.Label(f_cita, text="ID Mascota:").grid(row=0, column=2)
        tk.Entry(f_cita, textvariable=self.c_id_m).grid(row=0, column=3, padx=5)
        tk.Label(f_cita, text="Motivo:").grid(row=1, column=0)
        tk.Entry(f_cita, textvariable=self.c_motivo, width=40).grid(row=1, column=1, columnspan=3, pady=5)

        tk.Button(frame, text="REGISTRAR CITA", bg="#8e44ad", fg="white", command=self.guardar_cita).pack(pady=5)

        self.tree_citas = ttk.Treeview(frame, columns=("ID", "Fecha", "Mascota", "Motivo"), show="headings")
        for col in ("ID", "Fecha", "Mascota", "Motivo"): self.tree_citas.heading(col, text=col)
        self.tree_citas.pack(fill="both", expand=True, padx=10)
        self.cargar_tabla_citas()

    def guardar_cita(self):
        conn = crear_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO citas (fecha, id_mascota, motivo) VALUES (%s, %s, %s)",
                             (self.c_fecha.get(), self.c_id_m.get(), self.c_motivo.get()))
                conn.commit()
                messagebox.showinfo("Éxito", "Cita registrada con éxito")
                self.cargar_tabla_citas()
            except Exception as e: messagebox.showerror("Error", "Error al guardar: " + str(e))
            conn.close()

    def cargar_tabla_citas(self):
        for x in self.tree_citas.get_children(): self.tree_citas.delete(x)
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM citas")
                for row in cursor.fetchall(): self.tree_citas.insert("", "end", values=row)
            except: pass
            conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 4: INVENTARIO (AVISO STOCK BAJO)
    # ------------------------------------------------------------------
    def crear_modulo_inventario(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventario")

        self.tree_inv = ttk.Treeview(frame, columns=("ID", "Nombre", "Categoría", "Stock"), show="headings")
        for col in ("ID", "Nombre", "Categoría", "Stock"): self.tree_inv.heading(col, text=col)
        
        self.tree_inv.tag_configure("alerta", background="#e74c3c", foreground="white")
        self.tree_inv.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(frame, text="Actualizar Lista e Inventario", command=self.cargar_inventario).pack(pady=5)
        self.cargar_inventario()

    def cargar_inventario(self):
        for item in self.tree_inv.get_children(): self.tree_inv.delete(item)
        conn = crear_conexion()
        if conn:
            c = conn.cursor()
            c.execute("SELECT id_producto, nombre, categoria, cantidad FROM productos")
            
            bajos = []
            for row in c.fetchall():
                if row[3] < 5:
                    self.tree_inv.insert("", "end", values=row, tags=("alerta",))
                    bajos.append(row[1])
                else:
                    self.tree_inv.insert("", "end", values=row)
            
            # --- AVISO QUE INDIQUE STOCK BAJO ---
            if bajos:
                messagebox.showwarning("STOCK BAJO", "Cuidado, productos agotándose:\n" + "\n".join(bajos))
            conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 5: COMPRAS / VENTAS
    # ------------------------------------------------------------------
    def crear_modulo_compras(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Movimientos")
        tk.Label(frame, text="Registro de Compras/Ventas", font=("Arial", 12)).pack(pady=20)
        tk.Label(frame, text="Usa este módulo para sumar o restar stock en inventario.").pack()

# --- EJECUCIÓN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()