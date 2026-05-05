from config.database import ConexionBD

class Presupuesto:
    def __init__(self, monto_cotizado, preliminar_web, id_equipo, estado="Pendiente"):
        self.monto_cotizado = monto_cotizado
        self.preliminar_web = preliminar_web
        self.estado = estado
        self.id_equipo = id_equipo

    def registrar(self):
        """Guarda el presupuesto en la base de datos."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Presupuesto 
                         (Monto_Total_Cotizado, Estado_Presupuesto, Presupuesto_Preliminar_Web, Equipo_ID_Equipo) 
                         VALUES (%s, %s, %s, %s)"""
                valores = (self.monto_cotizado, self.estado, self.preliminar_web, self.id_equipo)
                cursor.execute(sql, valores)
                conexion.commit()
                return cursor.lastrowid  # Devuelve el ID_Presupuesto generado
            except Exception as e:
                print(f"Error al registrar presupuesto: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None