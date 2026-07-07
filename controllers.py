import sqlite3
from models import*
from abc import ABC
from typing import TypeVar, Generic
from events import EventManager

T = TypeVar('T')

class BaseCRUDController(ABC, Generic[T]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager,table_name:str, pk_name:str = "id"):
        self.conn = conn
        self.event_manager = event_manager
        self.table_name = table_name
        self.pk_name = pk_name
        self.modelo_asociado = table_name
        
        #Eventos genericos
        self.event_manager.suscribir(f"request_save_{self.table_name}", self.handle_insert)
        self.event_manager.suscribir(f"request_delete_{self.table_name}", self.handle_delete)
        self.event_manager.suscribir(f"request_read_{self.table_name}", self.handle_read)
        self.event_manager.suscribir(f"request_read_all_{self.table_name}", self.handle_read_all)
        self.event_manager.suscribir(f"request_update_{self.table_name}", self.handle_update)
        
    def handle_insert(self, data:dict):
        """Recibe los datos, construye el model y lo guarda"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            values = tuple(data.values())
            query = f'INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})'
            
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()
            
            self.event_manager.emitir(f"on_success_save_{self.table_name}", "Registro guardado con exito")
        except sqlite3.Error as e:
            self.conn.rollback()
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al insertar{e}")

            
    def handle_read(self,payload:dict):
        pk_value = payload['pk']
        query = f'SELECT * FROM {self.table_name} WHERE {self.pk_name} = ?'
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (pk_value,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                payload = dict(zip(columns, row))
            
            self.event_manager.emitir(f"data_changed_{self.table_name}",payload)

        except sqlite3.Error as e:
            self.conn.rollback()
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al conectar a la BD{e}")


    def handle_read_all(self, payload: dict):
        query = f'SELECT * FROM {self.table_name}'
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            datos= [dict(zip(columns, row)) for row in rows]
            self.event_manager.emitir(f'on_data_loaded_{self.table_name}',datos)
        except sqlite3.Error as e:
            self.conn.rollback()
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al conectar a la BD{e}")

    def handle_update(self, payload:dict):
        pk_value= payload.get('pk')
        data = payload.get('data')
        try:
            if self.pk_name in data:
                del data[self.pk_name]
        
            set_clause = ", ".join([f'{key} = ?'for key in data.keys()])
            values = tuple(data.values()) + (pk_value,)
            query = f'UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_name} = ?'

            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()
            self.event_manager.emitir(f"on_success_update_{self.table_name}", "Registro actualizado con exito")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al intentar actualizar el registro {e}")

    def handle_delete(self, pk):
        pk_value = pk
        try:
            query = f'DELETE FROM {self.table_name} WHERE {self.pk_name} = ?'
            cursor = self.conn.cursor()
            cursor.execute(query, (pk_value,))
            self.conn.commit()
            self.event_manager.emitir(f"on_success_delete_{self.table_name}",pk_value)
        except sqlite3.Error as e:
            self.conn.rollback()
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Se ha producido un error{e}")


class BienesController(BaseCRUDController[Bienes]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="bien", pk_name="codigo")

class EmpleadosController(BaseCRUDController[Empleados]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="empleado", pk_name="cedula")

class EstudiantesController(BaseCRUDController[Estudiantes]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="estudiante", pk_name="cedula")

class CursosController(BaseCRUDController[Cursos]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="curso", pk_name="codigo")

class InscripcionesController(BaseCRUDController[Inscripciones]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="inscripcion", pk_name="id")

class AsistenciasController(BaseCRUDController[Asistencias]):
    def __init__(self, conn: sqlite3.Connection, event_manager:EventManager):
        super().__init__(conn, event_manager,table_name="asistencia", pk_name="id")
