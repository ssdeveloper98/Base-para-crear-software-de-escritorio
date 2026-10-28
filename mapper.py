import inspect
from typing import Any, Type, TypeVar

T = TypeVar('T')

class Mapeador:
    """Convierte diccionadios de la IU en clases de modelo y viceversa"""
    @staticmethod
    def convertir_diccionario_a_clase(clase: Type[T], data: dict) -> T:
        #Verificamos el constructor para obtener atributos limpios sin inyeccion SQL
        atributos = inspect.signature(clase.__init__)
        llaves = [p for p in atributos.parameters.keys() if p !='self']
        datos_filtrados={k: v for k, v in data.items() if k in llaves}
        return clase(**datos_filtrados)

    @staticmethod
    def convertir_clase_a_diccionario(clase:Any) -> dict:
        data:dict={}
        data = {k: v for k,v in vars(clase).items() if not k.startswith('_')}
        return data
