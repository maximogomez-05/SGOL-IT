from config.database import DB

class ControlCalidad:
    def __init__(self, id_orden, id_empleado, temperaturas, software, observaciones):
        self.id_orden = id_orden
        self.id_empleado = id_empleado
        self.temperaturas = temperaturas
        self.software = software
        self.observaciones = observaciones

    def registrar(self):
        cursor = DB.cursor()
        # Nombres de columnas sincronizados con el SQL de arriba
        sql = """INSERT INTO control_calidad 
                 (Temperaturas_Registradas, Software_Benchmark, Observaciones, Orden_Trabajo_ID_OT, Empleado_ID_Empleado) 
                 VALUES (%s, %s, %s, %s, %s)"""
        val = (self.temperaturas, self.software, self.observaciones, self.id_orden, self.id_empleado)
        
        try:
            cursor.execute(sql, val)
            DB.commit()
        except Exception as e:
            print(f"Error en BD ControlCalidad: {e}")
            raise e
        finally:
            cursor.close()