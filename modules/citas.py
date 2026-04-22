import tkinter as tk
from tkinter import messagebox, ttk
from database import crear_conexion #

class CitasModulo:
    def __init__(self, parent):
        """
        parent: El contenedor (Notebook) donde se insertará la pestaña.
        """
        self.frame = tk.Frame(parent)
        
        # --- VARIABLES DE CONTROL ---
        self.c_fecha = tk.StringVar()
        self.c_id_m = tk.StringVar()
        self.c_motivo = tk.StringVar()

        self._crear_ui()
        self.cargar_tabla_citas()

    def _crear_ui(self):
        # Panel de Registro (Inspirado en el diseño de Claudia)
        f_cita = tk.LabelFrame(self.frame, text="Registrar Cita", padx=10, pady=10)
        f_cita.pack(fill="x", padx=10, pady=5)

        # Campos de entrada
        tk.Label(f_cita, text="Fecha (AAAA-MM-DD):").grid(row=0, column=0, sticky="w")
        tk.Entry(f_cita, textvariable=self.c_fecha).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(f_cita, text="ID Mascota:").grid(row=0, column=2, sticky="w")
        tk.Entry(f_cita, textvariable=self.c_id_m).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(f_cita, text="Motivo:").grid(row=1, column=0, sticky="w")
        tk.Entry(f_cita, textvariable=self.c_motivo, width=50).grid(row=1, column=1, columnspan=3, pady=5, sticky="w")

        # Botón de Acción
        tk.Button(
            self.frame, 
            text="REGISTRAR CITA", 
            bg="#8e44ad", 
            fg="white", 
            font=("Arial", 10, "bold"),
            command=self.guardar_cita
        ).pack(pady=10)

        # Tabla de Visualización
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Fecha", "ID Mascota", "Motivo")
        self.tree_citas = ttk.Treeview(tree_frame, columns=cols, show="headings")
        
        for col in cols:
            self.tree_citas.heading(col, text=col)
            self.tree_citas.column(col, width=100)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_citas.yview)
        self.tree_citas.configure(yscroll=scrollbar.set)
        
        self.tree_citas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def guardar_cita(self):
        """Inserta una nueva cita en la base de datos."""
        fecha = self.c_fecha.get()
        id_m = self.c_id_m.get()
        motivo = self.c_motivo.get()

        if not fecha or not id_m or not motivo:
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return

        conn = crear_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                # Query de inserción
                query = "INSERT INTO citas (fecha, id_mascota, motivo) VALUES (%s, %s, %s)"
                cursor.execute(query, (fecha, id_m, motivo))
                conn.commit()
                
                messagebox.showinfo("Éxito", "Cita registrada con éxito.")
                self.limpiar_campos()
                self.cargar_tabla_citas()
            except Exception as e:
                messagebox.showerror("Error", f"Verifique que el ID de Mascota existe.\n{e}")
            finally:
                conn.close()

    def cargar_tabla_citas(self):
        """Refresca la tabla con los registros de la BD."""
        for x in self.tree_citas.get_children(): 
            self.tree_citas.delete(x)
        
        conn = crear_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM citas ORDER BY fecha DESC")
                for row in cursor.fetchall():
                    self.tree_citas.insert("", "end", values=row)
            except Exception as e:
                print(f"Error al cargar citas: {e}")
            finally:
                conn.close()

    def limpiar_campos(self):
        """Reinicia los campos del formulario."""
        self.c_fecha.set("")
        self.c_id_m.set("")
        self.c_motivo.set("")