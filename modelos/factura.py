import datetime
from config.database import ConexionBD

class Factura:
    def __init__(self, id_ot, monto_total, metodo_pago):
        self.id_ot = id_ot
        self.monto_total = monto_total
        self.metodo_pago = metodo_pago
        self.fecha_emision = datetime.datetime.now().date()

    def registrar(self):
        """Guarda el registro de cobro en la base de datos."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                
                sql = """INSERT INTO Factura 
                         (Fecha_Emision, Monto_Total, Metodo_Pago, Orden_Trabajo_ID_OT) 
                         VALUES (%s, %s, %s, %s)"""
                
                valores = (self.fecha_emision, self.monto_total, self.metodo_pago, self.id_ot)
                cursor.execute(sql, valores)
                conexion.commit()
                return cursor.lastrowid 
            except Exception as e:
                print(f" Error al insertar factura en BD: {e}")
                conexion.rollback()
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None
    