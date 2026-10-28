import sqlite3
import contextlib
from events import EventManager

class Services:
    """Manejador de logica de negocio"""
    def __init__(self, conn:sqlite3.Connection, event_manager: EventManager):
        self.conn = conn
        self.event_manager = event_manager

        """Registro de eventos para las peticiones operativas de la vista"""
        self.event_manager.suscribir(f"request_calculo_inventario", self.calcular_inventario)
        self.event_manager.suscribir(f"request_calculo_nomina", self.calcular_nomina)
        self.event_manager.suscribir(f"request_operacion_asistencia", self.calcular_asistencia)
        self.event_manager.suscribir(f"request_dashboard_stats", self.calcular_dashboard)
    
    def calcular_inventario(self,payload=None):
        try:
            with contextlib.closing(self.conn.cursor()) as cursor:    
                cursor.execute("SELECT COUNT(*), SUM(cantidad*monto_unit) FROM bien")
                row = cursor.fetchone()
                total_items = row[0] if row[0] else 0
                capital_total = row[1] if row[1] else 0
            
                resultado={
                "total_items": total_items,
                "capital_total": f"${capital_total:,.2f}"
                }
                self.event_manager.emitir("on_inventario_calculado", resultado)
        except sqlite3.Error as e:
            self.event_manager.emitir("on_error_sistema", f"Fallo al calcular el inventario: {e}")
    
    def calcular_nomina(self, payload=None):
        try:
            with contextlib.closing(self.conn.cursor()) as cursor:
                cursor.execute("SELECT COUNT(*) FROM empleado")
                total_emp = cursor.fetchone()[0] or 0
                sueldo_promedio = 400
                total_nomina = total_emp*sueldo_promedio

                resultado = {
                "total_items":total_emp,
                "total_nomina":total_nomina
                }

                self.event_manager.emitir("on_nomina_calculada", resultado)

        except sqlite3.Error as e:
            self.event_manager.emitir("on_error_sistema", f"Fallo al calcular nomina: {e}")

    def calcular_asistencia(self, payload=None):
        try:
            with contextlib.closing(self.conn.cursor()) as cursor:
                cursor.execute("SELECT COUNT(*) FROM asistencia")
                total_asist = cursor.fetchone()[0] or 0
                cursor.execute("SELECT COUNT(*) FROM estudiante")
                total_est = cursor.fetchone()[0] or 1

                porc_asit = (total_asist/total_est) * 100 if total_est > 0 else 0

                resultado ={
                "total_asistencias":total_asist,
                "porcentaje_asistencia":f"{porc_asit:.1f}%"
                }
                self.event_manager.emitir("on_asistencia_calculada", resultado)
        except sqlite3.Error as e:
            self.event_manager.emitir("on_error_sistema", f"Fallo al calcular asistencia: {e}")
    
    def calcular_dashboard(self, payload =None):
        try:
            with contextlib.closing(self.conn.cursor()) as cursor:
                tablas = {"Bienes":"bien",
                       "Empleados":"empleado", 
                       "Estudiantes":"estudiante", 
                       "Cursos":"curso",
                       "Inscripciones":"inscripcion",
                       "Asistencias":"asistencia"}
                stats ={}

                for nombre_iu, tabla in tablas.items():
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    stats[nombre_iu] = cursor.fetchone()[0]
                self.event_manager.emitir("on_dashboard_stats_loaded", stats)
        except sqlite3.Error as e:
            self.event_manager.emitir("on_error_sistema",f"Error al cargar dashboard: {e}")
