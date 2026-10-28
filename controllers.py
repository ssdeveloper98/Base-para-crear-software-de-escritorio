from models import*
from typing import TypeVar, Generic
from events import EventManager
from mapper import Mapeador
from repositories import Repositorio

T = TypeVar('T')

class BaseCRUDController(Generic[T]):
    def __init__(self, repositorio: Repositorio[T], event_manager:EventManager):
        self.event_manager = event_manager
        self.repositorio = repositorio
        self.table_name = self.repositorio.tabla

        #Suscripción de eventos
        self.event_manager.suscribir(f"request_save_{self.table_name}", self.insertar)
        self.event_manager.suscribir(f"request_delete_{self.table_name}", self.eliminar)
        self.event_manager.suscribir(f"request_read_{self.table_name}", self.leer)
        self.event_manager.suscribir(f"request_read_all_{self.table_name}", self.leer_todos)
        self.event_manager.suscribir(f"request_update_{self.table_name}", self.actualizar)
        
    def insertar(self, data:dict):
        """Creamos el modelo explicitamente"""
        try:
            entidad = Mapeador.convertir_diccionario_a_clase(self.repositorio.clase, data)
            self.repositorio.guardar(entidad)
            self.event_manager.emitir(f"on_success_save_{self.table_name}", "Registro guardado con exito")
        except Exception as e:
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al insertar{e}")

            
    def leer(self,pk):
        try:
            entidad = self.repositorio.obtener_por_id(pk)
            payload = Mapeador.convertir_clase_a_diccionario(entidad) if entidad else {}
            self.event_manager.emitir(f"data_changed_{self.table_name}",payload)
        except Exception as e:
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al conectar a la BD{e}")


    def leer_todos(self, payload: dict):
        try:
            registros = self.repositorio.obtener_todos()
            datos = [Mapeador.convertir_clase_a_diccionario(e) for e in registros]
            self.event_manager.emitir(f'on_data_loaded_{self.table_name}',datos)
        except Exception as e:
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al conectar a la BD{e}")

    def actualizar(self,payload:dict):
        try:
            pk_value = payload.get('id')
            data = payload.get('data',{})
            entidad = Mapeador.convertir_diccionario_a_clase(self.repositorio.clase, data)
            self.repositorio.actualizar(pk_value, entidad)
            self.event_manager.emitir(f"on_success_update_{self.table_name}", "Registro actualizado con exito")
        except Exception as e:
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Error al intentar actualizar el registro {e}")

    def eliminar(self, pk):
        try:
            self.repositorio.eliminar(pk)
            self.event_manager.emitir(f"on_success_delete_{self.table_name}",pk)
        except Exception as e:
            self.event_manager.emitir(f"on_error_{self.table_name}", f"Se ha producido un error{e}")