from abc import ABC, abstractmethod
from datetime import date

class Bienes:
    def __init__(self, codigo : str, nombre : str, cantidad : int, monto_unit : float):
        self.codigo = codigo
        self.nombre = nombre
        self.cantidad = cantidad
        self.monto_unit = monto_unit

    def __str__(self):
        return f' {self.codigo} {self.nombre}'

class Personas(ABC):
    @abstractmethod
    def __init__(self, nombre : str, apellido : str, cedula : str):
        self.nombre = nombre
        self.apellido = apellido
        self.cedula = cedula


class Empleados(Personas):
    def __init__(self, nombre : str, apellido : str, cedula : str, cargo : str, modalidad_trab : str):
        super().__init__(nombre, apellido, cedula)
        self.cargo = cargo
        self.modalidad_trab = modalidad_trab

    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.cedula} {self.cargo} {self.modalidad_trab}'
    

class Estudiantes(Personas):
    def __init__(self, nombre : str, apellido : str, cedula : str, edad : int, genero : str):
        super().__init__(nombre, apellido, cedula)
        self.edad = edad
        self.genero = genero
    
    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.cedula}'

class Cursos:
    def __init__(self, codigo : str, empleado_id:Empleados, nombre : str, fecha_inicio : date, fecha_fin : date, modalidad : str, horario : str, dia : str):
        self.codigo = codigo
        self.empleadi_id = empleado_id
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.modalidad = modalidad
        self.horario = horario
        self.dia = dia
    def __str__(self):
        return f'{self.codigo} {self.nombre}'

class Inscripciones:
    def __init__(self, id:int, fecha_inscripcion : date, estudiante : Estudiantes, curso: Cursos):
        self.id = id
        self.fecha_inscripcion = fecha_inscripcion
        self.estudiante = estudiante
        self.curso = curso

    def __str__(self):
        return f'{self.id} {self.fecha_inscripcion} {self.estudiante} {self.curso}'

class Asistencias:
    def __init__(self, id:int, fecha_asistencia : date, estudiante: Estudiantes, curso: Cursos):
        self.id = id
        self.fecha_asistencia = fecha_asistencia
        self.estudiante = estudiante
        self.curso = curso

    def __str__(self):
        return f'{self.id} {self.fecha_asistencia} {self.estudiante} {self.curso}'