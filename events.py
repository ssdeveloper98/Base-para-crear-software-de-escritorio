from typing import Callable, Any

class EventManager:
    def __init__(self):
    #Mapeo de nombre del evento a lista de funciones
        self.listeners : dict[str, list[Callable]] = {}
    
    def suscribir(self, event_type:str, listener:Callable):
    #registra el evento
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)
    
    def emitir(self, event_type:str, data:Any = None):
    #Emite una señal
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(data)
    