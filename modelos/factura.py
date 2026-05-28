import datetime
from config.database import DB

class Factura:
    def __init__(self, id_ot, monto_total, metodo_pago):
        self.id_ot = id_ot
        self.monto_total = monto_total
        self.metodo_pago = metodo_pago
        self.fecha_emision = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def registrar(self):
        """Guarda el registro de cobro en la base de datos."""
        cursor = DB.cursor()
        try:
            sql = """INSERT INTO factura 
                     (Fecha_Emision, Monto_Total, Metodo_Pago, Orden_Trabajo_ID_OT) 
                     VALUES (%s, %s, %s, %s)"""
            
            valores = (self.fecha_emision, self.monto_total, self.metodo_pago, self.id_ot)
            cursor.execute(sql, valores)
            DB.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error al insertar factura en BD: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()