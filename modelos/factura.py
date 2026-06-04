import datetime
from config.database import DB

class Factura:
    def __init__(self, id_ot, monto_total, metodo_pago, tipo_factura="B", documento_cliente="", subtotal=None, monto_iva=None, nro_factura="", id_factura=None):
        self.id_factura = id_factura
        self.id_ot = id_ot
        self.monto_total = float(monto_total)
        self.metodo_pago = metodo_pago
        self.tipo_factura = tipo_factura
        self.documento_cliente = documento_cliente
        self.fecha_emision = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calcular IVA y Subtotal
        if subtotal is not None:
            self.subtotal = float(subtotal)
        else:
            self.subtotal = round(self.monto_total / 1.21, 2)
            
        if monto_iva is not None:
            self.monto_iva = float(monto_iva)
        else:
            self.monto_iva = round(self.monto_total - self.subtotal, 2)
            
        self.nro_factura = nro_factura

    def registrar(self):
        """Guarda el registro de cobro en la base de datos."""
        cursor = DB.cursor()
        try:
            # Asegurar nuevas columnas de forma individual
            for alter_sql in [
                "ALTER TABLE factura ADD COLUMN Tipo_Factura VARCHAR(10) DEFAULT 'B'",
                "ALTER TABLE factura ADD COLUMN Documento_Cliente VARCHAR(50) DEFAULT ''",
                "ALTER TABLE factura ADD COLUMN Subtotal DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Monto_IVA DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Nro_Factura VARCHAR(20) DEFAULT ''"
            ]:
                try:
                    cursor.execute(alter_sql)
                    DB.commit()
                except Exception:
                    pass
            
            # Generar número secuencial de factura
            cursor.execute("SELECT MAX(ID_Factura) FROM factura")
            res = cursor.fetchone()
            max_id = res[0] if res and res[0] is not None else 0
            next_id = max_id + 1
            self.nro_factura = f"0001-{next_id:08d}"
            
            sql = """INSERT INTO factura 
                     (Fecha_Emision, Monto_Total, Metodo_Pago, Orden_Trabajo_ID_OT, Tipo_Factura, Documento_Cliente, Subtotal, Monto_IVA, Nro_Factura) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            valores = (self.fecha_emision, self.monto_total, self.metodo_pago, self.id_ot, self.tipo_factura, self.documento_cliente, self.subtotal, self.monto_iva, self.nro_factura)
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
            # Asegurar columnas también al listar por si se invoca antes de registrar
            for alter_sql in [
                "ALTER TABLE factura ADD COLUMN Tipo_Factura VARCHAR(10) DEFAULT 'B'",
                "ALTER TABLE factura ADD COLUMN Documento_Cliente VARCHAR(50) DEFAULT ''",
                "ALTER TABLE factura ADD COLUMN Subtotal DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Monto_IVA DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Nro_Factura VARCHAR(20) DEFAULT ''"
            ]:
                try:
                    cursor.execute(alter_sql)
                    DB.commit()
                except Exception:
                    pass

            sql = """SELECT f.ID_Factura as id_factura, f.Fecha_Emision as fecha, f.Monto_Total as monto, 
                            f.Metodo_Pago as metodo, f.Tipo_Factura as tipo, f.Documento_Cliente as documento,
                            f.Orden_Trabajo_ID_OT as id_orden, f.Subtotal as subtotal, f.Monto_IVA as monto_iva,
                            COALESCE(f.Nro_Factura, '') as nro_factura,
                            CONCAT(c.Nombre_Completo, ' (', c.DNI_CUIL, ')') as cliente,
                            e.Marca_Modelo as equipo
                     FROM factura f
                     JOIN orden_trabajo ot ON f.Orden_Trabajo_ID_OT = ot.ID_OT
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                     JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente
                     ORDER BY f.Fecha_Emision DESC"""
            cursor.execute(sql)
            res = cursor.fetchall()
            for r in res:
                if not r.get('nro_factura'):
                    r['nro_factura'] = f"0001-{r['id_factura']:08d}"
            return res
        except Exception as e:
            print(f"Error al listar facturas: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(id_factura):
        cursor = DB.cursor(dictionary=True)
        try:
            # Asegurar columnas por robustez
            for alter_sql in [
                "ALTER TABLE factura ADD COLUMN Tipo_Factura VARCHAR(10) DEFAULT 'B'",
                "ALTER TABLE factura ADD COLUMN Documento_Cliente VARCHAR(50) DEFAULT ''",
                "ALTER TABLE factura ADD COLUMN Subtotal DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Monto_IVA DECIMAL(10,2) DEFAULT 0.00",
                "ALTER TABLE factura ADD COLUMN Nro_Factura VARCHAR(20) DEFAULT ''"
            ]:
                try:
                    cursor.execute(alter_sql)
                    DB.commit()
                except Exception:
                    pass

            sql = """SELECT f.ID_Factura as id_factura, f.Fecha_Emision as fecha, f.Monto_Total as monto, 
                            f.Metodo_Pago as metodo, f.Tipo_Factura as tipo, f.Documento_Cliente as documento,
                            f.Orden_Trabajo_ID_OT as id_orden, f.Subtotal as subtotal, f.Monto_IVA as monto_iva,
                            COALESCE(f.Nro_Factura, '') as nro_factura,
                            c.Nombre_Completo as cliente_nombre, c.DNI_CUIL as cliente_doc, c.Email as cliente_email, c.Telefono as cliente_tel,
                            e.Marca_Modelo as equipo, ot.Diagnostico_Final as diagnostico
                     FROM factura f
                     JOIN orden_trabajo ot ON f.Orden_Trabajo_ID_OT = ot.ID_OT
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                     JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente
                     WHERE f.ID_Factura = %s"""
            cursor.execute(sql, (id_factura,))
            r = cursor.fetchone()
            if r and not r.get('nro_factura'):
                r['nro_factura'] = f"0001-{r['id_factura']:08d}"
            return r
        except Exception as e:
            print(f"Error al buscar factura: {e}")
            return None
        finally:
            cursor.close()