import tkinter as tk
from tkinter import messagebox
from database import crear_conexion
from ui.main_window import SistemaVeterinaria

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VetControl - Acceso")
        
        # 1. Ajustamos el tamaño de la ventana para que quepa el logo grande y el formulario
        # Un ancho de 400 y alto de 600 suele ir bien para logos de ese tamaño
        self.centrar_ventana(self.root, 400, 600)
        self.root.configure(bg="#2c3e50") # Color primario de styles.py

        # 2. Cargar y redimensionar el logo
        try:
            # Cargamos la imagen original
            img_original = tk.PhotoImage(file="logo.png")
            # Como 331x331 es muy grande para un login, la reducimos a la mitad (aprox 165x165)
            # Si la quieres a tamaño completo, quita el '.subsample(2, 2)'
            self.logo_img = img_original.subsample(2, 2)
        except Exception as e:
            print(f"Error: No se encontró logo.png en la carpeta raíz. {e}")
            self.logo_img = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Contenedor principal con margen
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(expand=True)

        # 3. Logo con diseño circular o centrado
        if self.logo_img:
            lbl_logo = tk.Label(frame, image=self.logo_img, bg="#2c3e50")
            lbl_logo.pack(pady=(0, 20)) # Espacio extra abajo del logo

        # Título de bienvenida
        tk.Label(frame, text="BIENVENIDO", fg="white", bg="#2c3e50", 
                 font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        # Campos de entrada con estilo limpio
        tk.Label(frame, text="Usuario", fg="#bdc3c7", bg="#2c3e50", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_user = tk.Entry(frame, font=("Segoe UI", 12), width=25, bd=0)
        self.entry_user.pack(pady=(5, 15), ipady=5)
        self.entry_user.focus() # Pone el cursor aquí al abrir

        tk.Label(frame, text="Contraseña", fg="#bdc3c7", bg="#2c3e50", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.entry_pass = tk.Entry(frame, show="*", font=("Segoe UI", 12), width=25, bd=0)
        self.entry_pass.pack(pady=(5, 15), ipady=5)

        # Botón estilizado
        btn_ingresar = tk.Button(
            frame, 
            text="INICIAR SESIÓN", 
            command=self.validar_login, 
            bg="#27ae60", # Color 'exito' de styles.py
            fg="white", 
            font=("Segoe UI", 11, "bold"),
            width=20,
            bd=0,
            cursor="hand2",
            activebackground="#2ecc71",
            activeforeground="white"
        )
        btn_ingresar.pack(pady=20, ipady=8)

    def centrar_ventana(self, ventana, ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def validar_login(self):
        user = self.entry_user.get()
        password = self.entry_pass.get()
        
        if not user or not password:
            messagebox.showwarning("Campos vacíos", "Por favor ingrese sus credenciales.")
            return

        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (user, password))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                self.abrir_sistema_principal(usuario[1])
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def abrir_sistema_principal(self, nombre_completo):
        self.root.withdraw()
        nueva_ventana = tk.Toplevel(self.root)
        nueva_ventana.protocol("WM_DELETE_WINDOW", self.root.destroy)
        SistemaVeterinaria(nueva_ventana, nombre_completo)