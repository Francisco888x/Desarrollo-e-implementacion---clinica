import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from database import crear_conexion # Importamos la conexión centralizada

class MascotasModulo:
    def __init__(self, parent):
        """
        parent: El contenedor (Notebook) donde se insertará la pestaña.
        """
        self.frame = tk.Frame(parent)
        
        # --- VARIABLES DE CONTROL ---
        self.mas_id = tk.StringVar()
        self.mas_nombre = tk.StringVar()
        self.mas_especie = tk.StringVar()
        self.mas_raza = tk.StringVar()
        self.mas_edad = tk.StringVar()
        self.mas_id_cliente = tk.StringVar()

        self._crear_ui()
        self.cargar_tabla()

    def _crear_ui(self):
        # Formulario de entrada de datos
        form_frame = tk.LabelFrame(self.frame, text="Datos de la Mascota")
        form_frame.pack(fill="x", padx=10, pady=5)

        # Diseño de Rejilla (Grid) para los campos
        tk.Label(form_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_id, state="readonly", width=5).grid(row=0, column=1)
        
        tk.Label(form_frame, text="Nombre:").grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_nombre).grid(row=0, column=3)
        
        tk.Label(form_frame, text="Especie:").grid(row=0, column=4, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_especie).grid(row=0, column=5)
        
        tk.Label(form_frame, text="Raza:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_raza).grid(row=1, column=1)
        
        tk.Label(form_frame, text="Edad:").grid(row=1, column=2, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_edad).grid(row=1, column=3)
        
        tk.Label(form_frame, text="ID Dueño:").grid(row=1, column=4, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.mas_id_cliente).grid(row=1, column=5)

        # Botonera
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Guardar Mascota", bg="#27ae60", fg="white", command=self.guardar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualizar", bg="#f39c12", fg="white", command=self.actualizar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", command=self.eliminar_mascota).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_campos).pack(side="left", padx=5)

        # Tabla (Treeview)
        cols = ("ID", "Nombre", "Especie", "Raza", "Edad", "ID Dueño")
        self.tree_mascotas = ttk.Treeview(self.frame, columns=cols, show="headings")
        for col in cols:
            self.tree_mascotas.heading(col, text=col)
            self.tree_mascotas.column(col, width=80)
        
        self.tree_mascotas.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_mascotas.bind("<<TreeviewSelect>>", self.seleccionar_fila)

    def cargar_tabla(self):
        """Refresca la lista de mascotas desde la base de datos."""
        for x in self.tree_mascotas.get_children(): 
            self.tree_mascotas.delete(x)
        
        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mascotas")
            for row in cursor.fetchall():
                self.tree_mascotas.insert("", "end", values=row)
            conn.close()

    def seleccionar_fila(self, event):
        item = self.tree_mascotas.focus()
        datos = self.tree_mascotas.item(item, 'values')
        if datos:
            self.mas_id.set(datos[0])
            self.mas_nombre.set(datos[1])
            self.mas_especie.set(datos[2])
            self.mas_raza.set(datos[3])
            self.mas_edad.set(datos[4])
            self.mas_id_cliente.set(datos[5])

    def limpiar_campos(self):
        self.mas_id.set("")
        self.mas_nombre.set("")
        self.mas_especie.set("")
        self.mas_raza.set("")
        self.mas_edad.set("")
        self.mas_id_cliente.set("")

    def guardar_mascota(self):
        conn = crear_conexion()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = """INSERT INTO mascotas (nombre, especie, raza, edad, id_cliente) 
                       VALUES (%s, %s, %s, %s, %s)"""
            params = (self.mas_nombre.get(), self.mas_especie.get(), 
                      self.mas_raza.get(), self.mas_edad.get(), self.mas_id_cliente.get())
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Éxito", "Mascota registrada correctamente")
            self.cargar_tabla()
            self.limpiar_campos()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Verifique que el ID del Dueño exista.\nDetalle: {e}")
        finally:
            conn.close()

    def actualizar_mascota(self):
        if not self.mas_id.get(): return
        # Lógica de UPDATE similar a guardar...
        pass

    def eliminar_mascota(self):
        if not self.mas_id.get(): return
        if not messagebox.askyesno("Confirmar", "¿Eliminar registro de mascota?"): return
        # Lógica de DELETE...
        pass