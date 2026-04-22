import tkinter as tk
from tkinter import ttk
# Importamos los módulos desde el paquete que configuramos en modules/__init__.py
from modules import ClientesModulo, MascotasModulo, InventarioModulo, MovimientosModulo, CitasModulo

class SistemaVeterinaria:
    def __init__(self, root, nombre_usuario):
        self.root = root
        self.root.title(f"VetControl - Bienvenido {nombre_usuario}")
        self.root.geometry("1000x700")
        
        # --- CONFIGURACIÓN DE MENÚ ---
        self._crear_menu()

        # --- CONTENEDOR DE PESTAÑAS (Notebook) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # --- CARGA DINÁMICA DE MÓDULOS ---
        self._cargar_modulos()

    def _crear_menu(self):
        """Configura la barra de menú superior."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=file_menu)
        file_menu.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        file_menu.add_command(label="Salir", command=self.root.quit)

    def _cargar_modulos(self):
        # 1. Instanciar módulos
        self.mod_clientes = ClientesModulo(self.notebook)
        self.mod_mascotas = MascotasModulo(self.notebook)
        self.mod_inventario = InventarioModulo(self.notebook)
        self.mod_citas = CitasModulo(self.notebook)
        
        
        # 2. Al instanciar Movimientos, le pasamos la referencia de Inventario
        self.mod_movimientos = MovimientosModulo(self.notebook, self.mod_inventario)
        
        # 3. Al instanciar Inventario (o mediante un método), le pasamos Movimientos
        self.mod_inventario.set_movimientos(self.mod_movimientos)

        # Añadir pestañas al notebook...
        self.notebook.add(self.mod_clientes.frame, text="Clientes")
        self.notebook.add(self.mod_mascotas.frame, text="Mascotas")
        self.notebook.add(self.mod_citas.frame, text="Gestión de Citas")
        self.notebook.add(self.mod_inventario.frame, text="Inventario")
        self.notebook.add(self.mod_movimientos.frame, text="Movimientos")

    def centrar_ventana(self, ancho, alto):
        # Obtener el ancho y alto de la pantalla del usuario
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()

        # Calcular las coordenadas X e Y para el centro
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))

        # Aplicar la geometría: "ancho x alto + posicion_x + posicion_y"
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cerrar_sesion(self):
        """Cierra la ventana actual y permite volver al login."""
        self.root.destroy()