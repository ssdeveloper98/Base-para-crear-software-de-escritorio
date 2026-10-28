import sqlite3
from models import*
from controllers import BaseCRUDController
from services import Services
from events import EventManager
from repositories import Repositorio
from strategies import validadores

class IDContenedor:
    def __init__(self):
        self._servicios={}

    def registrar(self, nombre:str, servicio):
        self._servicios[nombre] = servicio

    def obtener(self, nombre:str):
        return self._servicios.get(nombre)

def construir_contenedor()->IDContenedor:
    contenedor = IDContenedor()
    conexion_bd = sqlite3.connect("CDC.db")
    conexion_bd.execute("PRAGMA foreign_keys = ON")
    eventos = EventManager()

    contenedor.registrar("conexion_bd", conexion_bd)
    contenedor.registrar("eventos", eventos)
    contenedor.registrar("validadores", validadores)
    contenedor.registrar("servicios", Services(conexion_bd, eventos))

    modulos = [
        ("bien","codigo",Bienes),
        ("empleado","cedula",Empleados),
        ("estudiante","cedula",Estudiantes),
        ("curso","codigo",Cursos),
        ("inscripcion","id",Inscripciones),
        ("asistencia","id",Asistencias), 
    ]

    for tabla, pk, modelo in modulos:
        repost = Repositorio(conexion_bd, tabla, pk, modelo)
        ctrl = BaseCRUDController(repost, eventos)
        contenedor.registrar(f"ctrl_{tabla}", ctrl)

    return contenedor