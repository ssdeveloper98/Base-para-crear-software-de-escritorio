import sqlite3

def migrate()->None:
    """Ejecuta script para creacion de BD"""
    conn = sqlite3.connect('CDC.db')
    cursor = conn.cursor()
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS bien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre VARCHAR(20),
        cantidad INTEGER,
        monto_unit REAL
    );
    
    CREATE TABLE IF NOT EXISTS empleado(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(20),
        apellido VARCHAR(20),
        cedula VARCHAR(20) UNIQUE,
        cargo VARCHAR(20),
        modalidad_trab VARCHAR(20)
    );
    
    CREATE TABLE IF NOT EXISTS estudiante(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(20),
        apellido VARCHAR(20),
        cedula VARCHAR(20) UNIQUE,
        edad INTEGER,
        genero VARCHAR(20));
    
    CREATE TABLE IF NOT EXISTS curso(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER,
            codigo VARCHAR(5) UNIQUE,
            nombre VARCHAR(20),
            fecha_inicio DATE,
            fecha_fin DATE,
            modalidad VARCHAR(6),
            horario VARCHAR(14),
            dia VARCHAR(10),
            FOREIGN KEY (empleado_id) REFERENCES empleado(id) ON DELETE CASCADE);
               
    CREATE TABLE IF NOT EXISTS inscripcion(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               fecha_inscripcion DATE,
               estudiante_id INTEGER,
               curso_id INTEGER,
               FOREIGN KEY (estudiante_id) REFERENCES estudiante(id) ON DELETE CASCADE,
               FOREIGN KEY (curso_id) REFERENCES curso(id) 
                     ON DELETE CASCADE); 
        
    CREATE TABLE IF NOT EXISTS asistencia(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               fecha_asistencia DATE,
               estudiante_id INTEGER,
               curso_id INTEGER,
               FOREIGN KEY (estudiante_id) REFERENCES estudiante(id) ON DELETE CASCADE,
               FOREIGN KEY (curso_id) REFERENCES curso(id) ON DELETE CASCADE);''')

    conn.commit()
    cursor.close()
    conn.close()