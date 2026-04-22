import tkinter as tk
from tkinter import messagebox, ttk
from database import crear_conexion, obtener_productos_inventario # Importamos desde tu nueva capa de datos
from datetime import datetime
from tkcalendar import DateEntry

class InventarioModulo:
    def __init__(self, parent):
        """
        parent: Es el notebook o frame donde se insertará este módulo.
        """
        self.frame = tk.Frame(parent)
        
        # --- VARIABLES DE CONTROL ---
        self.inv_id = tk.StringVar()
        self.inv_nombre = tk.StringVar()
        self.inv_cat = tk.StringVar()

        self._crear_ui()
        self.cargar_inventario()

    def cargar_inventario(self):
        """Obtiene datos de database.py y aplica la lógica de alertas."""
        for item in self.tree_inv.get_children(): 
            self.tree_inv.delete(item)
        
        productos = obtener_productos_inventario() 
        bajos = [] # Lista para capturar nombres de productos escasos
        
        for row in productos:
            stock = row[3] 
            if stock < 5:
                self.tree_inv.insert("", "end", values=row, tags=("alerta_baja",))
                bajos.append(row[1]) # Agrega el nombre a la lista
            else:
                self.tree_inv.insert("", "end", values=row)
        
        # Si hay productos bajos, muestra una ventana emergente
        if bajos:
            messagebox.showwarning(
                "STOCK BAJO", 
                "Cuidado, productos agotándose:\n" + "\n".join(bajos)
            )

    def seleccionar_item(self, event):
        item = self.tree_inv.focus()
        data = self.tree_inv.item(item, 'values')
        if data:
            self.inv_id.set(data[0])
            self.inv_nombre.set(data[1])
            self.inv_cat.set(data[2])
            self.inv_caducidad.set(data[4])

    def set_movimientos(self, mod_mov):
        self.mod_movimientos = mod_mov

    def crear_producto(self):
        nombre = self.inv_nombre.get()
        categoria = self.inv_cat.get()
        caducidad = self.inv_caducidad.get()

        if not nombre or not categoria:
            messagebox.showwarning("Atención", "Nombre y Categoría son obligatorios.")
            return

        # 🔒 Validación de fecha
        try:
            fecha_obj = datetime.strptime(caducidad, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido (AAAA-MM-DD).")
            return

         # (opcional pero pro)
        if fecha_obj < datetime.now().date():
            messagebox.showwarning("Atención", "La fecha de caducidad no puede ser pasada.")
            return

        conn = crear_conexion()
        if not conn: return

        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO productos (nombre, categoria, cantidad, fecha_caducidad)
            VALUES (%s, %s, 0, %s)
            """
            cursor.execute(query, (nombre, categoria, caducidad))
            conn.commit()

            messagebox.showinfo("Éxito", f"Producto '{nombre}' creado correctamente.")
            self.cargar_inventario()
            self.limpiar_campos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear: {e}")
        finally:
            conn.close()

    def editar_producto(self):
        id_prod = self.inv_id.get()
        if not id_prod:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla.")
            return

        nombre = self.inv_nombre.get()
        categoria = self.inv_cat.get()
        caducidad = self.inv_caducidad.get()

        # 🔒 Validación de fecha
        try:
            fecha_obj = datetime.strptime(caducidad, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido (AAAA-MM-DD).")
            return

        conn = crear_conexion()
        if not conn: return

        try:
            cursor = conn.cursor()
            query = """
            UPDATE productos
            SET nombre = %s, categoria = %s, fecha_caducidad = %s
            WHERE id_producto = %s
            """
            cursor.execute(query, (nombre, categoria, caducidad, id_prod))
            conn.commit()

            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            self.cargar_inventario()
            self.limpiar_campos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar: {e}")
        finally:
            conn.close()

    def borrar_producto(self):
        """Elimina el producto seleccionado."""
        id_prod = self.inv_id.get()
        if not id_prod:
            messagebox.showwarning("Atención", "Selecciona un producto para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este producto?\nEsto borrará también su historial de movimientos."):
            conn = crear_conexion()
            if not conn: return
            try:
                cursor = conn.cursor()
                # Nota: Si tienes FK en movimientos_inventario, asegúrate de que sea ON DELETE CASCADE
                query = "DELETE FROM productos WHERE id_producto = %s"
                cursor.execute(query, (id_prod,))
                conn.commit()
                
                messagebox.showinfo("Eliminado", "Producto eliminado del sistema.")
                self.cargar_inventario()
                self.limpiar_campos()
            except Exception as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            finally:
                conn.close()

    def limpiar_campos(self):
        """Limpia las variables de control."""
        self.inv_id.set("")
        self.inv_nombre.set("")
        self.inv_cat.set("")
        self.inv_caducidad.set("")

    # --- AGREGANDO PARA CONTROLAR CADUCIDAD (Mejora de Claudia) ---

    def _crear_ui(self):
        # --- PANEL DE ADMINISTRACIÓN (Formulario) ---
        panel = tk.LabelFrame(self.frame, text="Administrar Productos", padx=10, pady=10)
        panel.pack(fill="x", padx=10, pady=5)

        # Variables de control adicionales para el formulario
        self.inv_caducidad = tk.StringVar() # Nueva variable para la fecha

        # Fila 1: ID, Nombre y Categoría
        tk.Label(panel, text="ID:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(panel, textvariable=self.inv_id, state="readonly", width=5).grid(row=0, column=1)
        
        tk.Label(panel, text="Nombre:").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(panel, textvariable=self.inv_nombre, width=20).grid(row=0, column=3)
        
        tk.Label(panel, text="Categoría:").grid(row=0, column=4, padx=5, pady=5)
        tk.Entry(panel, textvariable=self.inv_cat, width=15).grid(row=0, column=5)

        # Fila 2: Fecha de Caducidad
        tk.Label(panel, text="Caducidad (AAAA-MM-DD):").grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.date_caducidad = DateEntry(
            panel,
            textvariable=self.inv_caducidad,
            date_pattern='yyyy-mm-dd',  # Formato compatible con MySQL
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.date_caducidad.grid(row=1, column=2, sticky="w")
        self.inv_caducidad.set(datetime.now().strftime("%Y-%m-%d"))

        # Botones de acción
        btn_frame = tk.Frame(panel)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=10)
        
        tk.Button(btn_frame, text="Nuevo Producto", bg="#2980b9", fg="white", command=self.crear_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Editar Datos", bg="#f39c12", fg="white", command=self.editar_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.borrar_producto).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Recargar", command=self.cargar_inventario).pack(side="left", padx=5)
        
        # --- LEYENDA DE COLORES ---
        leyenda_frame = tk.Frame(self.frame)
        leyenda_frame.pack(fill="x", padx=10)
        tk.Label(leyenda_frame, text="■ Stock Bajo (<5)", fg="#e74c3c", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        tk.Label(leyenda_frame, text="■ Producto Caducado", fg="#f1c40f", font=("Arial", 9, "bold")).pack(side="left", padx=10)

        # --- TABLA (TREEVIEW) ---
        cols = ("ID", "Nombre", "Categoría", "Stock", "Caducidad")
        self.tree_inv = ttk.Treeview(self.frame, columns=cols, show="headings")
        
        # Configuración de encabezados y anchos
        for col in cols:
            self.tree_inv.heading(col, text=col)
            if col == "ID":
                self.tree_inv.column(col, width=50, anchor="center")
            else:
                self.tree_inv.column(col, width=120, anchor="center")
        
        # Configuración de colores (Tags)
        self.tree_inv.tag_configure("alerta_caducado", background="#f1c40f", foreground="black")
        self.tree_inv.tag_configure("alerta_baja", background="#e74c3c", foreground="white")

        self.tree_inv.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Evento de selección
        self.tree_inv.bind("<<TreeviewSelect>>", self.seleccionar_item)

    def cargar_inventario(self):
        for item in self.tree_inv.get_children(): 
            self.tree_inv.delete(item)
        
        productos = obtener_productos_inventario()
        hoy = datetime.now().date()
        caducados = []
        bajos = []

        for row in productos:
            # row[3] es stock, row[4] es la fecha de caducidad
            stock = row[3]
            fecha_cad = row[4] # Asegúrate que en MySQL sea tipo DATE
            
            tag = ""
            # Lógica de colores
            if fecha_cad and fecha_cad < hoy:
                tag = "alerta_caducado"
                caducados.append(row[1])
            elif stock < 5:
                tag = "alerta_baja"
                bajos.append(row[1])

            self.tree_inv.insert("", "end", values=row, tags=(tag,))

        # Alertas emergentes (Mejora de Claudia extendida)
        mensaje_alerta = ""
        if bajos:
            mensaje_alerta += f"STOCK BAJO: {', '.join(bajos)}\n"
        if caducados:
            mensaje_alerta += f"PRODUCTOS CADUCADOS: {', '.join(caducados)}"
        
        if mensaje_alerta:
            messagebox.showwarning("ALERTAS DE INVENTARIO", mensaje_alerta)