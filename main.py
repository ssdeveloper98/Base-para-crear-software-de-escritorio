import tkinter as GUI
import sys
import persistence
from view import AppGui
from container import construir_contenedor

def main():
    try:
        persistence.migrate()
    except Exception as e:
        print(f"Error al migrar la base de datos: {e}")

    if len(sys.argv) > 1:
        comando = sys.argv[1]
        if comando == "migrate":
            sys.exit(0)
        else:
            sys.exit(1)

    try:
        container = construir_contenedor()
    except Exception as e:
        print(f"Error al inicializar el sistema: {e}")
        sys.exit(1)

    root_app = GUI.Tk()
    
    AppGui(root_app, container)

    def on_closing():
        container.obtener("conexion_bd").close()
        root_app.destroy()
    
    root_app.protocol("WM_DELETE_WINDOW", on_closing)
    root_app.mainloop()

main()