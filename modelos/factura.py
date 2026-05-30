import datetime
from config.database import DB

class Factura:
    def __init__(self, id_ot, monto_total, metodo_pago, tipo_factura="B", documento_cliente=""):
        self.id_ot = id_ot
        self.monto_total = monto_total
        self.metodo_pago = metodo_pago
        self.tipo_factura = tipo_factura
        self.documento_cliente = documento_cliente
        self.fecha_emision = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def registrar(self):
        """Guarda el registro de cobro en la base de datos."""
        cursor = DB.cursor()
        try:
            # Asegurar nuevas columnas
            try:
                cursor.execute("ALTER TABLE factura ADD COLUMN Tipo_Factura VARCHAR(10) DEFAULT 'B', ADD COLUMN Documento_Cliente VARCHAR(50) DEFAULT ''")
                DB.commit()
            except:
                pass
                
            sql = """INSERT INTO factura 
                     (Fecha_Emision, Monto_Total, Metodo_Pago, Orden_Trabajo_ID_OT, Tipo_Factura, Documento_Cliente) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            
            valores = (self.fecha_emision, self.monto_total, self.metodo_pago, self.id_ot, self.tipo_factura, self.documento_cliente)
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

    @staticmethod
    def listar_todas():
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT f.ID_Factura as id_factura, f.Fecha_Emision as fecha, f.Monto_Total as monto, 
                            f.Metodo_Pago as metodo, f.Tipo_Factura as tipo, f.Documento_Cliente as documento,
                            f.Orden_Trabajo_ID_OT as id_orden, 
                            CONCAT(c.Nombre_Completo, ' (', c.DNI_CUIL, ')') as cliente,
                            e.Marca_Modelo as equipo
                     FROM factura f
                     JOIN orden_trabajo ot ON f.Orden_Trabajo_ID_OT = ot.ID_OT
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                     JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente
                     ORDER BY f.Fecha_Emision DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar facturas: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(id_factura):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT f.ID_Factura as id_factura, f.Fecha_Emision as fecha, f.Monto_Total as monto, 
                            f.Metodo_Pago as metodo, f.Tipo_Factura as tipo, f.Documento_Cliente as documento,
                            f.Orden_Trabajo_ID_OT as id_orden, 
                            c.Nombre_Completo as cliente_nombre, c.DNI_CUIL as cliente_doc, c.Email as cliente_email, c.Telefono as cliente_tel,
                            e.Marca_Modelo as equipo, ot.Diagnostico_Final as diagnostico
                     FROM factura f
                     JOIN orden_trabajo ot ON f.Orden_Trabajo_ID_OT = ot.ID_OT
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                     JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente
                     WHERE f.ID_Factura = %s"""
            cursor.execute(sql, (id_factura,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar factura: {e}")
            return None
        finally:
            cursor.close()