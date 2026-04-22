import tkinter as tk
from tkinter import messagebox, ttk
from database import obtener_clientes, crear_conexion #

class ClientesModulo:
    def __init__(self, parent):
        """
        parent: El widget (Notebook) donde se alojará este módulo.
        """
        self.frame = tk.Frame(parent)
        
        # --- VARIABLES DE CONTROL ---
        self.cli_id = tk.StringVar()
        self.cli_nombre = tk.StringVar()
        self.cli_tel = tk.StringVar()
        self.cli_email = tk.StringVar()

        self._crear_ui()
        self.cargar_tabla()

    def _crear_ui(self):
        # Formulario de Datos
        # --- NUEVO: Panel de Búsqueda (Inspirado en el cambio de Claudia) ---
        busqueda_frame = tk.LabelFrame(self.frame, text="Buscar Cliente")
        busqueda_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(busqueda_frame, text="Nombre:").pack(side="left", padx=5)
        self.ent_busqueda = tk.Entry(busqueda_frame)
        self.ent_busqueda.pack(side="left", padx=5, fill="x", expand=True)

        tk.Button(busqueda_frame, text="Consultar", command=self.consultar_cliente, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(busqueda_frame, text="Ver Todos", command=self.cargar_tabla).pack(side="left", padx=5)

        form_frame = tk.LabelFrame(self.frame, text="Datos del Cliente")
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_id, state="readonly", width=10).grid(row=0, column=1)
        
        tk.Label(form_frame, text="Nombre:").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_nombre, width=25).grid(row=0, column=3)
        
        tk.Label(form_frame, text="Teléfono:").grid(row=0, column=4, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_tel, width=15).grid(row=0, column=5)
        
        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.cli_email, width=25).grid(row=1, column=1, columnspan=3, sticky="w")

        # Botones de Acción
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Guardar Nuevo", bg="#27ae60", fg="white", command=self.guardar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", bg="#f39c12", fg="white", command=self.actualizar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.eliminar_cliente).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)

        # Tabla de Visualización
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("ID", "Nombre", "Teléfono", "Email")
        self.tree_clientes = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=100)
        
        self.tree_clientes.pack(fill="both", expand=True)
        self.tree_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente)

    def cargar_tabla(self):
        """Refresca la tabla con datos de la BD."""
        for x in self.tree_clientes.get_children(): 
            self.tree_clientes.delete(x)
        
        datos = obtener_clientes() # Llamada a la capa de datos
        for row in datos:
            self.tree_clientes.insert("", "end", values=row)

    def seleccionar_cliente(self, event):
        """Carga los datos de la fila seleccionada en los Entry."""
        item = self.tree_clientes.focus()
        datos = self.tree_clientes.item(item, 'values')
        if datos:
            self.cli_id.set(datos[0])
            self.cli_nombre.set(datos[1])
            self.cli_tel.set(datos[2])
            self.cli_email.set(datos[3])

    def limpiar_campos(self):
        self.cli_id.set("")
        self.cli_nombre.set("")
        self.cli_tel.set("")
        self.cli_email.set("")

    def guardar_cliente(self):
        """Lógica para insertar un cliente."""
        conn = crear_conexion()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "INSERT INTO clientes (nombre, telefono, email) VALUES (%s, %s, %s)"
            cursor.execute(query, (self.cli_nombre.get(), self.cli_tel.get(), self.cli_email.get()))
            conn.commit()
            messagebox.showinfo("Éxito", "Cliente agregado")
            self.cargar_tabla()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def actualizar_cliente(self):
        """Actualiza los datos del cliente seleccionado."""
        id_cliente = self.cli_id.get()
        
        if not id_cliente:
            messagebox.showwarning("Atención", "Por favor, selecciona un cliente de la tabla primero.")
            return

        nombre = self.cli_nombre.get()
        tel = self.cli_tel.get()
        email = self.cli_email.get()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return

        conn = crear_conexion()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "UPDATE clientes SET nombre=%s, telefono=%s, email=%s WHERE id_cliente=%s"
            cursor.execute(query, (nombre, tel, email, id_cliente))
            conn.commit()
            
            messagebox.showinfo("Éxito", "Datos del cliente actualizados correctamente.")
            self.cargar_tabla() # Refresca la tabla visualmente
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        finally:
            conn.close()

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado tras confirmar."""
        id_cliente = self.cli_id.get()
        
        if not id_cliente:
            messagebox.showwarning("Atención", "Por favor, selecciona un cliente de la tabla primero.")
            return

        # Pedir confirmación para evitar borrados accidentales
        confirmar = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar al cliente con ID {id_cliente}?\nEsta acción no se puede deshacer.")
        
        if confirmar:
            conn = crear_conexion()
            if not conn: return
            try:
                cursor = conn.cursor()
                query = "DELETE FROM clientes WHERE id_cliente = %s"
                cursor.execute(query, (id_cliente,))
                conn.commit()
                
                messagebox.showinfo("Eliminado", "El cliente ha sido borrado.")
                self.cargar_tabla()
                self.limpiar_campos()
            except Exception as e:
                # El error más común aquí es que el cliente tenga mascotas asociadas (Llave foránea)
                messagebox.showerror("Error", f"No se pudo eliminar. Es posible que el cliente tenga mascotas registradas.\nDetalle: {e}")
            finally:
                conn.close()

    def consultar_cliente(self):
        """Filtra la tabla de clientes según el texto del buscador."""
        termino = self.ent_busqueda.get()
        
        # Limpiar la tabla actual
        for x in self.tree_clientes.get_children(): 
            self.tree_clientes.delete(x)
        
        # Obtener solo los clientes que coincidan
        from database import buscar_clientes_por_nombre
        datos = buscar_clientes_por_nombre(termino)
        
        if not datos:
            messagebox.showinfo("Búsqueda", "No se encontraron clientes con ese nombre.")
            self.cargar_tabla() # Mostrar todos si no hay resultados
            return

        for row in datos:
            self.tree_clientes.insert("", "end", values=row)