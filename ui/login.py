import tkinter as tk
from tkinter import messagebox
from database import crear_conexion
from ui.main_window import SistemaVeterinaria

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - VetControl")
        self.root.geometry("300x250")
        self.root.configure(bg="#2c3e50")

        # --- DISEÑO DE LA INTERFAZ ---
        self._crear_interfaz()

    def _crear_interfaz(self):
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(pady=40)

        tk.Label(frame, text="Usuario:", fg="white", bg="#2c3e50", font=("Arial", 10)).pack()
        self.entry_user = tk.Entry(frame)
        self.entry_user.pack(pady=5)

        tk.Label(frame, text="Contraseña:", fg="white", bg="#2c3e50", font=("Arial", 10)).pack()
        self.entry_pass = tk.Entry(frame, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(
            frame, 
            text="INGRESAR", 
            command=self.validar_login, 
            bg="#27ae60", 
            fg="white", 
            width=15,
            cursor="hand2"
        ).pack(pady=20)

    def validar_login(self):
        """Verifica las credenciales contra la base de datos."""
        user = self.entry_user.get()
        password = self.entry_pass.get()

        conn = crear_conexion()
        if conn:
            cursor = conn.cursor()
            # Consulta segura usando parámetros para evitar inyecciones SQL
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (user, password))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                self.abrir_sistema_principal(usuario[1]) # usuario[1] suele ser el nombre real
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def abrir_sistema_principal(self, nombre_completo):
        """Oculta el login y lanza la ventana principal."""
        self.root.withdraw() # Oculta la ventana de login
        
        # Crear una nueva ventana superior (Toplevel)
        nueva_ventana = tk.Toplevel(self.root)
        
        # Al cerrar la ventana principal, se cierra toda la aplicación
        nueva_ventana.protocol("WM_DELETE_WINDOW", self.root.destroy)
        
        # Instanciar la clase que armamos en ui/main_window.py
        SistemaVeterinaria(nueva_ventana, nombre_completo)

    def centrar_ventana(ventana, ancho, alto):
        # Obtener el ancho y alto de la pantalla del usuario
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()

        # Calcular las coordenadas X e Y para el centro
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))

        # Aplicar la geometría: "ancho x alto + posicion_x + posicion_y"
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")