from tkinter import ttk

# Paleta de colores profesional (Basada en Flat UI)
COLORES = {
    "primario": "#2c3e50",    # Azul oscuro (Login, Menús)
    "secundario": "#34495e",  # Gris azulado
    "exito": "#27ae60",       # Verde (Botones guardar)
    "peligro": "#e74c3c",     # Rojo (Botones borrar, alertas)
    "alerta": "#f39c12",      # Naranja (Botones editar)
    "fondo": "#ecf0f1",       # Gris muy claro (Fondo de pestañas)
    "texto_claro": "#ffffff"
}

def aplicar_estilos_globales():
    style = ttk.Style()
    style.theme_use('clam') # 'clam' es más personalizable que el default de Windows

    # Estilo para las pestañas (Notebook)
    style.configure("TNotebook", background=COLORES["fondo"])
    style.configure("TNotebook.Tab", 
                    font=('Arial', 10, 'bold'), 
                    padding=[10, 5], 
                    background=COLORES["secundario"], 
                    foreground=COLORES["texto_claro"])
    
    # Cambio de color cuando la pestaña está seleccionada
    style.map("TNotebook.Tab", 
              background=[("selected", COLORES["primario"])])

    # Estilo para las Tablas (Treeview)
    style.configure("Treeview", 
                    font=('Segoe UI', 10), 
                    rowheight=25,
                    background=COLORES["texto_claro"])
    style.configure("Treeview.Heading", 
                    font=('Segoe UI', 10, 'bold'), 
                    background=COLORES["secundario"], 
                    foreground=COLORES["texto_claro"])