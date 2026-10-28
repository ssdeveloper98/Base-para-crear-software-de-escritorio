from typing import Callable, Any

class EventManager:
    def __init__(self):
        """Constructor donde creamos un diccionario para guardar nuestros eventos registrados"""
        self.listeners : dict[str, list[Callable]] = {}
    
    def suscribir(self, event_type:str, listener:Callable):
        """Suscribe un evento"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)
    
    def desuscribir(self, evento: str, listener: Callable):
        """Elimina un evento de la lista"""
        if evento in self.listeners and listener in self.listeners[evento]:
            self.listeners[evento].remove(listener)

    def emitir(self, event_type:str, data:Any = None):
        """Emite la señal para que el receptor sepa que se esta dando un evento"""
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(data)
    