import tkinter as tk
from tkinter import messagebox, ttk
from database import crear_conexion

class MovimientosModulo:
    def __init__(self, parent, mod_inventario):
        # parent: El contenedor (Notebook) donde se insertará la pestaña.
        self.frame = tk.Frame(parent)
        self.mod_inventario = mod_inventario # Guardamos la referencia
        
        # --- VARIABLES DE CONTROL ---
        self.mov_tipo = tk.StringVar(value="Salida (Venta)")
        self.mov_prod_seleccionado = tk.StringVar()
        self.mov_cantidad = tk.StringVar()
        
        # Diccionario para guardar ID de productos asociados al nombre
        self.productos_dict = {}

        self._crear_ui()
        self.actualizar_combo_productos()

    def _crear_ui(self):
        # Panel de Registro
        panel = tk.LabelFrame(self.frame, text="Registrar Entrada/Salida de Inventario", padx=20, pady=20)
        panel.pack(pady=20, padx=20)

        # 1. Selección de Producto
        tk.Label(panel, text="Seleccione Producto:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_prod = ttk.Combobox(panel, textvariable=self.mov_prod_seleccionado, state="readonly", width=30)
        self.combo_prod.grid(row=0, column=1, pady=5)

        # 2. Tipo de Movimiento
        tk.Label(panel, text="Tipo:").grid(row=1, column=0, sticky="w", pady=5)
        combo_tipo = ttk.Combobox(panel, textvariable=self.mov_tipo, values=["Entrada (Compra)", "Salida (Venta)"], state="readonly")
        combo_tipo.grid(row=1, column=1, pady=5)

        # 3. Cantidad
        tk.Label(panel, text="Cantidad:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_cant = tk.Entry(panel, textvariable=self.mov_cantidad)
        self.entry_cant.grid(row=2, column=1, pady=5)

        # 4. Botón Procesar
        btn_procesar = tk.Button(
            panel, 
            text="PROCESAR MOVIMIENTO", 
            bg="#2c3e50", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=self.ejecutar_movimiento
        )
        btn_procesar.grid(row=3, column=0, columnspan=2, pady=20, sticky="nsew")

    def actualizar_combo_productos(self):
        """Carga los nombres de productos en el combobox y guarda sus IDs."""
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, nombre, cantidad FROM productos")
            rows = cursor.fetchall()
            
            nombres = []
            self.productos_dict = {}
            for r in rows:
                # Guardamos info extra: id y stock actual
                nombre_display = f"{r[1]} (Stock: {r[2]})"
                nombres.append(nombre_display)
                self.productos_dict[nombre_display] = {"id": r[0], "stock": r[2]}
            
            self.combo_prod['values'] = nombres
            conn.close()

    def ejecutar_movimiento(self):
        prod_sel = self.mov_prod_seleccionado.get()
        tipo = self.mov_tipo.get()
        cant_str = self.mov_cantidad.get()

        # Validaciones básicas
        if not prod_sel or not cant_str:
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        try:
            cantidad = int(cant_str)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
            return

        info_prod = self.productos_dict[prod_sel]
        id_prod = info_prod["id"]
        stock_actual = info_prod["stock"]
        es_entrada = "Entrada" in tipo

        # Validación de Stock para ventas
        if not es_entrada and cantidad > stock_actual:
            messagebox.showerror("Error de Stock", f"No puedes vender {cantidad}. Solo hay {stock_actual} disponible.")
            return

        # --- Lógica de Base de Datos ---
        conn = crear_conexion()
        if not conn: return
        cursor = conn.cursor()
        try:
            # 1. Insertar en historial de movimientos
            tipo_db = "Entrada" if es_entrada else "Salida"
            query_hist = "INSERT INTO movimientos_inventario (tipo_movimiento, cantidad, id_producto) VALUES (%s, %s, %s)"
            cursor.execute(query_hist, (tipo_db, cantidad, id_prod))

            # 2. Actualizar tabla de productos
            operador = "+" if es_entrada else "-"
            query_update = f"UPDATE productos SET cantidad = cantidad {operador} %s WHERE id_producto = %s"
            cursor.execute(query_update, (cantidad, id_prod))

            conn.commit()
            messagebox.showinfo("Éxito", "Movimiento registrado y stock actualizado")
            
            # Refresca la tabla del catálogo automáticamente para ver el nuevo stock
            self.mod_inventario.cargar_inventario() 

            # Limpiar y refrescar
            self.mov_cantidad.set("")
            self.actualizar_combo_productos()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"No se pudo procesar: {e}")
        finally:
            conn.close() 