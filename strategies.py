from abc import ABC, abstractmethod

class ValidacionesStrategy(ABC):
    @abstractmethod
    def validar(self, text:str)-> bool:
        pass

class ValidarEntero(ValidacionesStrategy):
    def validar(self, text:str)->bool:
        return text == "" or text.isdigit()

class ValidarDecimal(ValidacionesStrategy):
    def validar(self, text:str)->bool:
        if text=="":
            return True

        try:
            float(text)
            return True
        except ValueError:
            return False

class ValidarTexto(ValidacionesStrategy):
    def validar(self, text:str)->bool:
        if text =="":
            return True
        return all(c.isalpha or c.isspace() for c in text)

validadores ={
    "integer": ValidarEntero(),
    "float": ValidarDecimal(),
    "text": ValidarTexto()
    }
