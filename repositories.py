import sqlite3
import contextlib
from typing import Any,TypeVar, Generic, Type, List, Optional
from mapper import Mapeador

T = TypeVar('T')

class Repositorio(Generic[T]):
    """Aislamos toda la interacción con SqLite y cerramos la conección automaticamente"""
    def __init__(self, conn: sqlite3.Connection, tabla: str, pk: str, clase: Type[T]):
        self.conn = conn
        self.tabla = tabla
        self.pk = pk
        self.clase = clase
        self.conn.row_factory = sqlite3.Row


    def obtener_todos(self)-> List[T]:
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(f'SELECT * FROM {self.tabla}')
            rows = cursor.fetchall()
            return [Mapeador.convertir_diccionario_a_clase(self.clase, dict(row)) for row in rows]

    def obtener_por_id(self, pk_valor: Any)-> Optional[T]:
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(f'SELECT * FROM {self.tabla} WHERE {self.pk}=?',(pk_valor,))
            row = cursor.fetchone()
            if row:
                return Mapeador.convertir_diccionario_a_clase(self.clase, dict(row))
            return None

    def guardar(self, entidad:T):
        data = Mapeador.convertir_clase_a_diccionario(entidad)
        columnas = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        valores = tuple(data.values())
        query = f"INSERT INTO {self.tabla} ({columnas}) VALUES ({placeholders})"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(query,valores)
            self.conn.commit()

    def actualizar(self, pk_valor:Any, entidad: T):
        data = Mapeador.convertir_clase_a_diccionario(entidad)
        set_clausulas = ", ".join([f"{key}=?"for key in data.keys()])
        valores = tuple(data.values()) + (pk_valor,)
        query = f"UPDATE {self.tabla} SET {set_clausulas} WHERE {self.pk} = ?"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(query, valores)
            self.conn.commit()


    def eliminar(self, pk_valor:Any):
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(f'DELETE FROM {self.tabla} WHERE {self.pk} = ? ', (pk_valor,))
            self.conn.commit()
    