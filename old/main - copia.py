import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# --- CONFIGURACIÓN DE CONEXIÓN ---
def crear_conexion():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root", #pon tu usuario de root
            password="",  # Pon tu contraseña de root
            database="veterinaria",
            port=3306
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Error BD", f"No se pudo conectar: {err}")
        return None

# --- CLASE: LOGIN (AUTENTICACIÓN) ---
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
        self.root.geometry("900x650")
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=file_menu)
        file_menu.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        file_menu.add_command(label="Salir", command=root.quit)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # CARGA DE MÓDULOS
        self.crear_modulo_clientes()
        self.crear_modulo_mascotas()
        self.crear_modulo_inventario()  # AQUÍ ESTÁ LA ALERTA DE STOCK
        self.crear_modulo_compras()

    def cerrar_sesion(self):
        self.root.destroy()
        # Nota: Al cerrar esta ventana, la app termina, para reiniciar login habría que volver a ejecutar.

    # ------------------------------------------------------------------
    # MÓDULO 1: CLIENTES
    # ------------------------------------------------------------------
    def crear_modulo_clientes(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Gestión de Clientes")

        form_frame = tk.LabelFrame(frame, text="Datos del Cliente")
        form_frame.pack(fill="x", padx=10, pady=5)

        self.cli_id = tk.StringVar()
        self.cli_nombre = tk.StringVar()
        self.cli_tel = tk.StringVar()
        self.cli_email = tk.StringVar()

        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_id, state="readonly", width=10).grid(row=0, column=1)
        tk.Label(form_frame, text="Nombre:").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_nombre, width=25).grid(row=0, column=3)
        tk.Label(form_frame, text="Teléfono:").grid(row=0, column=4, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_tel, width=15).grid(row=0, column=5)
        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_email, width=25).grid(row=1, column=1, columnspan=3, sticky="w")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Guardar Nuevo", bg="#27ae60", fg="white", command=self.guardar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", bg="#f39c12", fg="white", command=self.actualizar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.eliminar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar Campos", command=self.limpiar_cliente).pack(side="left", padx=5)

        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        cols = ("ID", "Nombre", "Teléfono", "Email")
        self.tree_clientes = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=100)
        self.tree_clientes.pack(fill="both", expand=True)
        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
        self.cargar_tabla_clientes()

    def cargar_tabla_clientes(self):
        for x in self.tree_clientes.get_children(): self.tree_clientes.delete(x)
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        for row in cursor.fetchall():
            self.tree_clientes.insert("", "end", values=row)
        conn.close()

    def seleccionar_cliente(self, event):
        item = self.tree_clientes.focus()
        datos = self.tree_clientes.item(item, 'values')
        if datos:
            self.cli_id.set(datos[0])
            self.cli_nombre.set(datos[1])
            self.cli_tel.set(datos[2])
            self.cli_email.set(datos[3])

    def limpiar_cliente(self):
        self.cli_id.set("")
        self.cli_nombre.set("")
        self.cli_tel.set("")
        self.cli_email.set("")

    def guardar_cliente(self):
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)", 
                           (self.cli_nombre.get(), self.cli_tel.get(), self.cli_email.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente agregado")
            self.cargar_tabla_clientes()
            self.limpiar_cliente()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def actualizar_cliente(self):
        if not self.cli_id.get(): return
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE clientes SET nombre=%s, telefono=%s, email=%s WHERE id_cliente=%s", 
                           (self.cli_nombre.get(), self.cli_tel.get(), self.cli_email.get(), self.cli_id.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado")
            self.cargar_tabla_clientes()
            self.limpiar_cliente()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def eliminar_cliente(self):
        if not self.cli_id.get(): return
        if not messagebox.askyesno("Confirmar", "¿Borrar este cliente?"): return
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM clientes WHERE id_cliente=%s", (self.cli_id.get(),))
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente eliminado")
            self.cargar_tabla_clientes()
            self.limpiar_cliente()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", "No se puede borrar (tiene historial asociado).")
        conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 2: MASCOTAS
    # ------------------------------------------------------------------
    def crear_modulo_mascotas(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Gestión de Mascotas")

        form_frame = tk.LabelFrame(frame, text="Datos de la Mascota")
        form_frame.pack(fill="x", padx=10, pady=5)

        self.mas_id = tk.StringVar()
        self.mas_nombre = tk.StringVar()
        self.mas_especie = tk.StringVar()
        self.mas_raza = tk.StringVar()
        self.mas_edad = tk.StringVar()
        self.mas_id_cliente = tk.StringVar()

        tk.Label(form_frame, text="ID:").grid(row=0, column=0)
        tk.Entry(form_frame, textvariable=self.mas_id, state="readonly", width=5).grid(row=0, column=1)
        tk.Label(form_frame, text="Nombre:").grid(row=0, column=2)
        tk.Entry(form_frame, textvariable=self.mas_nombre).grid(row=0, column=3)
        tk.Label(form_frame, text="Especie:").grid(row=0, column=4)
        tk.Entry(form_frame, textvariable=self.mas_especie).grid(row=0, column=5)
        tk.Label(form_frame, text="Raza:").grid(row=1, column=0)
        tk.Entry(form_frame, textvariable=self.mas_raza).grid(row=1, column=1)
        tk.Label(form_frame, text="Edad:").grid(row=1, column=2)
        tk.Entry(form_frame, textvariable=self.mas_edad).grid(row=1, column=3)
        tk.Label(form_frame, text="ID Dueño:").grid(row=1, column=4)
        tk.Entry(form_frame, textvariable=self.mas_id_cliente).grid(row=1, column=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Guardar Mascota", bg="#27ae60", fg="white", command=self.guardar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", bg="#f39c12", fg="white", command=self.actualizar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.eliminar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_mascota).pack(side="left", padx=5)

        cols = ("ID", "Nombre", "Especie", "Raza", "Edad", "ID Dueño")
        self.tree_mascotas = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            self.tree_mascotas.heading(col, text=col)
            self.tree_mascotas.column(col, width=80)
        self.tree_mascotas.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_mascotas.bind("<<TreeviewSelect>>", self.seleccionar_mascota)
        self.cargar_tabla_mascotas()

    def cargar_tabla_mascotas(self):
        for x in self.tree_mascotas.get_children(): self.tree_mascotas.delete(x)
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mascotas")
        for row in cursor.fetchall():
            self.tree_mascotas.insert("", "end", values=row)
        conn.close()

    def seleccionar_mascota(self, event):
        item = self.tree_mascotas.focus()
        datos = self.tree_mascotas.item(item, 'values')
        if datos:
            self.mas_id.set(datos[0])
            self.mas_nombre.set(datos[1])
            self.mas_especie.set(datos[2])
            self.mas_raza.set(datos[3])
            self.mas_edad.set(datos[4])
            self.mas_id_cliente.set(datos[5])

    def limpiar_mascota(self):
        self.mas_id.set("")
        self.mas_nombre.set("")
        self.mas_especie.set("")
        self.mas_raza.set("")
        self.mas_edad.set("")
        self.mas_id_cliente.set("")

    def guardar_mascota(self):
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO mascotas (nombre, especie, raza, edad, id_cliente) VALUES (%s, %s, %s, %s, %s)",
                           (self.mas_nombre.get(), self.mas_especie.get(), self.mas_raza.get(), self.mas_edad.get(), self.mas_id_cliente.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Mascota guardada")
            self.cargar_tabla_mascotas()
            self.limpiar_mascota()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error (¿El ID Dueño existe?):\n{e}")
        conn.close()

    def actualizar_mascota(self):
        if not self.mas_id.get(): return
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mascotas SET nombre=%s, especie=%s, raza=%s, edad=%s, id_cliente=%s WHERE id_mascota=%s",
                           (self.mas_nombre.get(), self.mas_especie.get(), self.mas_raza.get(), self.mas_edad.get(), self.mas_id_cliente.get(), self.mas_id.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Mascota actualizada")
            self.cargar_tabla_mascotas()
            self.limpiar_mascota()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def eliminar_mascota(self):
        if not self.mas_id.get(): return
        if not messagebox.askyesno("Confirmar", "¿Eliminar mascota?"): return
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM mascotas WHERE id_mascota=%s", (self.mas_id.get(),))
            conn.commit()
            self.cargar_tabla_mascotas()
            self.limpiar_mascota()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 3: INVENTARIO (CON ALERTAS DE STOCK)
    # ------------------------------------------------------------------
    def crear_modulo_inventario(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventario (Catálogo)")

        panel = tk.LabelFrame(frame, text="Administrar Productos", padx=10, pady=10)
        panel.pack(fill="x", padx=10, pady=5)

        self.inv_id = tk.StringVar()
        self.inv_nombre = tk.StringVar()
        self.inv_cat = tk.StringVar()

        tk.Label(panel, text="ID:").grid(row=0, column=0, padx=5)
        tk.Entry(panel, textvariable=self.inv_id, state="readonly", width=5).grid(row=0, column=1)
        tk.Label(panel, text="Nombre:").grid(row=0, column=2, padx=5)
        tk.Entry(panel, textvariable=self.inv_nombre, width=20).grid(row=0, column=3)
        tk.Label(panel, text="Categoría:").grid(row=0, column=4, padx=5)
        tk.Entry(panel, textvariable=self.inv_cat, width=15).grid(row=0, column=5)

        btn_frame = tk.Frame(panel)
        btn_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        tk.Button(btn_frame, text="Nuevo Producto", bg="#2980b9", fg="white", command=self.crear_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Editar Datos", bg="#f39c12", fg="white", command=self.editar_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.borrar_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Recargar Tabla", command=self.cargar_inventario).pack(side="left", padx=5)
        
        # Leyenda de Alerta
        tk.Label(frame, text="Nota: Los productos en ROJO tienen stock bajo (< 5 unidades)", fg="red").pack(pady=5)

        self.tree_inv = ttk.Treeview(frame, columns=("ID", "Nombre", "Categoría", "Stock Total"), show="headings")
        self.tree_inv.heading("ID", text="ID")
        self.tree_inv.heading("Nombre", text="Nombre")
        self.tree_inv.heading("Categoría", text="Categoría")
        self.tree_inv.heading("Stock Total", text="Stock Total")
        
        self.tree_inv.column("ID", width=50)
        self.tree_inv.column("Stock Total", width=100)
        
        # CONFIGURAMOS LA ETIQUETA ROJA
        self.tree_inv.tag_configure("alerta_baja", background="#e74c3c", foreground="white")

        self.tree_inv.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_inv.bind("<<TreeviewSelect>>", self.seleccionar_item_inventario)
        self.cargar_inventario()

    def cargar_inventario(self):
        for item in self.tree_inv.get_children(): self.tree_inv.delete(item)
        conn = crear_conexion()
        c = conn.cursor()
        c.execute("SELECT id_producto, nombre, categoria, cantidad FROM productos")
        
        # LÓGICA DE ALERTA VISUAL
        for row in c.fetchall():
            stock = row[3] # La columna cantidad es la 3
            if stock < 5:
                # Si es menor a 5, usamos la etiqueta "alerta_baja" (Rojo)
                self.tree_inv.insert("", "end", values=row, tags=("alerta_baja",))
            else:
                self.tree_inv.insert("", "end", values=row)
                
        conn.close()

    def seleccionar_item_inventario(self, event):
        item = self.tree_inv.focus()
        data = self.tree_inv.item(item, 'values')
        if data:
            self.inv_id.set(data[0])
            self.inv_nombre.set(data[1])
            self.inv_cat.set(data[2])

    def crear_producto(self):
        conn = crear_conexion()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO productos (nombre, categoria, cantidad) VALUES (%s, %s, 0)", 
                      (self.inv_nombre.get(), self.inv_cat.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Producto registrado en catálogo.")
            self.cargar_inventario()
            self.actualizar_combo_compras() 
        except Exception as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def editar_producto(self):
        if not self.inv_id.get(): return
        conn = crear_conexion()
        c = conn.cursor()
        try:
            c.execute("UPDATE productos SET nombre=%s, categoria=%s WHERE id_producto=%s", 
                      (self.inv_nombre.get(), self.inv_cat.get(), self.inv_id.get()))
            conn.commit()
            self.cargar_inventario()
            self.actualizar_combo_compras()
            messagebox.showinfo("Éxito", "Producto actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        conn.close()

    def borrar_producto(self):
        if not self.inv_id.get(): return
        if not messagebox.askyesno("Alerta", "Borrar el producto eliminará su historial. ¿Seguro?"): return
        conn = crear_conexion()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM productos WHERE id_producto=%s", (self.inv_id.get(),))
            conn.commit()
            self.cargar_inventario()
            self.actualizar_combo_compras()
            messagebox.showinfo("Éxito", "Producto eliminado.")
        except Exception as e:
            messagebox.showerror("Error", "No se puede borrar (tiene movimientos asociados).")
        conn.close()

    # ------------------------------------------------------------------
    # MÓDULO 4: COMPRAS Y VENTAS
    # ------------------------------------------------------------------
    def crear_modulo_compras(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Compras/Ventas")

        tk.Label(frame, text="Registro de Movimientos (Entradas/Salidas)", font=("Arial", 14)).pack(pady=20)

        panel = tk.Frame(frame)
        panel.pack(pady=10)

        # Selección de Producto
        tk.Label(panel, text="Producto:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_prods = ttk.Combobox(panel, state="readonly", width=30)
        self.combo_prods.grid(row=0, column=1, padx=5, pady=5)

        # Tipo de Movimiento
        tk.Label(panel, text="Tipo:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(panel, values=["Entrada (Compra)", "Salida (Venta)"], state="readonly", width=20)
        self.combo_tipo.grid(row=1, column=1, padx=5, pady=5)
        self.combo_tipo.current(0)

        # Cantidad
        tk.Label(panel, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        self.mov_cant = tk.Entry(panel)
        self.mov_cant.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame, text="REGISTRAR MOVIMIENTO", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), 
                  command=self.registrar_movimiento).pack(pady=20)

        self.actualizar_combo_compras()

    def actualizar_combo_compras(self):
        conn = crear_conexion()
        c = conn.cursor()
        # Traemos también el stock actual para validar ventas
        c.execute("SELECT id_producto, nombre, cantidad FROM productos")
        datos = c.fetchall()
        self.lista_productos = datos
        valores = [f"{id_p} - {nom} (Stock: {cant})" for id_p, nom, cant in datos]
        self.combo_prods['values'] = valores
        conn.close()

    def registrar_movimiento(self):
        seleccion = self.combo_prods.current()
        if seleccion == -1:
            messagebox.showerror("Error", "Selecciona un producto.")
            return
        
        try:
            cantidad = int(self.mov_cant.get())
            if cantidad <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return

        id_producto = self.lista_productos[seleccion][0]
        stock_actual = self.lista_productos[seleccion][2]
        tipo_str = self.combo_tipo.get()
        es_entrada = "Entrada" in tipo_str
        tipo_bd = "Entrada" if es_entrada else "Salida"

        # VALIDACIÓN DE STOCK PARA VENTAS
        if not es_entrada and cantidad > stock_actual:
            messagebox.showerror("Error de Stock", f"No puedes vender {cantidad}. Solo tienes {stock_actual} en inventario.")
            return

        conn = crear_conexion()
        c = conn.cursor()
        try:
            # 1. Registrar en Historial
            c.execute("INSERT INTO movimientos_inventario (tipo_movimiento, cantidad, id_producto, id_usuario) VALUES (%s, %s, %s, 1)", 
                      (tipo_bd, cantidad, id_producto))
            
            # 2. Actualizar Stock (+ si es entrada, - si es salida)
            if es_entrada:
                c.execute("UPDATE productos SET cantidad = cantidad + %s WHERE id_producto = %s", (cantidad, id_producto))
            else:
                c.execute("UPDATE productos SET cantidad = cantidad - %s WHERE id_producto = %s", (cantidad, id_producto))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Movimiento registrado correctamente.")
            self.mov_cant.delete(0, tk.END)
            
            # Actualizamos visualmente todo
            self.cargar_inventario() 
            self.actualizar_combo_compras()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error BD", str(e))
        conn.close()

# --- ARRANQUE ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()