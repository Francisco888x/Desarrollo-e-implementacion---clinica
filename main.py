import tkinter as tk
from ui import LoginApp
from styles import aplicar_estilos_globales

if __name__ == "__main__":
    root = tk.Tk()
    
    # Aplicar los estilos antes de cargar la UI
    aplicar_estilos_globales()
    
    app = LoginApp(root)
    root.mainloop()