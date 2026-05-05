from config.database import ConexionBD

class ControlCalidad:
    def __init__(self, id_ot, software, temperaturas, aprobado=1):
        self.id_ot = id_ot
        self.software = software
        self.temperaturas = temperaturas
        self.aprobado = aprobado

    def registrar_prueba(self):
        """Registra los resultados técnicos de la reparación (RF-3.3)."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Control_Calidad 
                         (Aprobado_Entrega, Software_Benchmark_Utilizado, Temperaturas_Registradas, Orden_Trabajo_ID_OT) 
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (self.aprobado, self.software, self.temperaturas, self.id_ot))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al registrar control de calidad: {e}")
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def verificar_aprobacion(id_ot):
        """Verifica si la OT ya tiene una prueba de calidad aprobada."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT Aprobado_Entrega FROM Control_Calidad WHERE Orden_Trabajo_ID_OT = %s"
                cursor.execute(sql, (id_ot,))
                resultado = cursor.fetchone()
                return resultado is not None and resultado[0] == 1
            finally:
                cursor.close()
                db.desconectar()
        return False