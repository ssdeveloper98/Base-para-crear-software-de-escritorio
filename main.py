import sqlite3
import tkinter as GUI
import sys
from events import EventManager
from view import AppGui
from services import Services
from controllers import ( BienesController, EmpleadosController, EstudiantesController,
    CursosController, AsistenciasController, InscripcionesController)
import persistence

def main():
    if len(sys.argv) > 1:
        comando =sys.argv[1]
        if comando == "migrate":
            persistence.migrate()
            sys.exit(0)
        else:
            sys.exit(1)
    #Core
    try:
        conn_bd = sqlite3.connect("CDC.db")
        conn_bd.execute("PRAGMA foreign_key = ON")
    except sqlite3.Error as e:
        print(f"Error al conectar a la Base de Batos: {e}")
        sys.exit(1)
    
    event_manager= EventManager()
    servicios = Services(conn_bd, event_manager)
    
    #Controladores
    ctrl_bienes = BienesController(conn_bd, event_manager)
    ctrl_empleados = EmpleadosController(conn_bd, event_manager)
    ctrl_estudiante = EstudiantesController(conn_bd, event_manager)
    ctrl_cursos = CursosController(conn_bd, event_manager)
    ctrl_asistencias = AsistenciasController(conn_bd, event_manager)
    ctrl_inscripciones = InscripcionesController(conn_bd, event_manager)

    root_app = GUI.Tk()
    AppGui(root_app, event_manager)

    def on_closing():
        conn_bd.close()
        root_app.destroy()
    
    root_app.protocol("WM_DELETE_WINDOW", on_closing)
    root_app.mainloop()

main()