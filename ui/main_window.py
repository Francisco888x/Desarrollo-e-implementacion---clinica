import tkinter as tk
from tkinter import ttk
# Importamos los módulos desde el paquete que configuramos en modules/__init__.py
from modules import ClientesModulo, MascotasModulo, InventarioModulo, MovimientosModulo, CitasModulo

class SistemaVeterinaria:
    def __init__(self, root, nombre_usuario):
        self.root = root
        self.root.title(f"VetControl - Bienvenido {nombre_usuario}")
        
        self.centrar_ventana(self.root, 1000, 700)
        self.root.configure(bg="#ecf0f1")

        try:
            # Anclaje 1: Guardamos la referencia en el objeto de la clase
            self.img_referencia = tk.PhotoImage(file="logo.png")
            self.logo_img = self.img_referencia.subsample(3, 3)
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
            self.logo_img = None

        # Cambiar el icono de la ventana (la plumita)
        try:
            # Aquí también usamos self.img_referencia para ir sobre seguro
            self.root.iconphoto(False, self.img_referencia)
        except:
            pass

        self._crear_interfaz_base()
        self._cargar_modulos()

    def _crear_interfaz_base(self):
        # Cabecera superior para el logo y el nombre del sistema
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")

        if self.logo_img:
            lbl_logo = tk.Label(header, image=self.logo_img, bg="#2c3e50")
            
            # ANCLAJE 2: Esta línea es el truco maestro. 
            # Obligamos al widget a mantener una referencia interna.
            lbl_logo.image = self.logo_img 
            
            lbl_logo.pack(side="left", padx=20, pady=5)

        tk.Label(
            header, 
            text="VETCONTROL SYSTEM", 
            fg="white", 
            bg="#2c3e50", 
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=10)

        # El notebook (pestañas) ahora se empaqueta después del header
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

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

    def centrar_ventana(self, ventana, ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cerrar_sesion(self):
        """Cierra la ventana actual y permite volver al login."""
        self.root.destroy()