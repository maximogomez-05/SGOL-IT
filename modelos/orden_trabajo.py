import datetime
import random
import string
from config.database import DB

class OrdenTrabajo:
    def __init__(self, id_equipo, id_empleado, id_presupuesto=None, codigo_tracking=None, estado_general="Para Revisión", id_ot=None):
        self.id_ot = id_ot
        self.estado_general = estado_general
        self.fecha_creacion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.id_equipo = id_equipo
        self.id_empleado = id_empleado
        self.id_presupuesto = id_presupuesto
        # Autogeneración de código de seguimiento único si no se pasa
        self.codigo_tracking = codigo_tracking if codigo_tracking else self.generar_codigo()

    @staticmethod
    def generar_codigo():
        chars = string.ascii_uppercase + string.digits
        return "OT-" + "".join(random.choices(chars, k=6))

    def registrar(self):
        cursor = DB.cursor()
        try:
            sql = """INSERT INTO orden_trabajo 
                     (Estado_General, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado, Presupuesto_ID_Presupuesto, Codigo_Tracking_web) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            val = (self.estado_general, self.fecha_creacion, self.id_equipo, self.id_empleado, self.id_presupuesto, self.codigo_tracking)
            cursor.execute(sql, val)
            DB.commit()
            self.id_ot = cursor.lastrowid
            return self.id_ot
        except Exception as e:
            print(f"Error al registrar orden de trabajo: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def buscar_pendientes():
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Codigo_Tracking_web as codigo, 
                     CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, 
                     ot.Estado_General as estado, ot.Diagnostico_Final as diagnostico_final,
                     ot.Equipo_ID_Equipo as id_equipo
                     FROM orden_trabajo ot 
                     LEFT JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar órdenes pendientes: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def actualizar_estado(id_orden, estado):
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE orden_trabajo SET Estado_General = %s WHERE ID_OT = %s", (estado, id_orden))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def actualizar_diagnostico(id_orden, diagnostico):
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE orden_trabajo SET Diagnostico_Final = %s WHERE ID_OT = %s", (diagnostico, id_orden))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar diagnóstico: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def vincular_presupuesto(id_orden, id_presupuesto, estado="Esperando Respuesta"):
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE orden_trabajo SET Presupuesto_ID_Presupuesto = %s, Estado_General = %s WHERE ID_OT = %s", (id_presupuesto, estado, id_orden))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al vincular presupuesto: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(id_orden):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Estado_General as estado, ot.Diagnostico_Final as diagnostico,
                     ot.Codigo_Tracking_web as codigo, ot.Fecha_Creacion as fecha, ot.Equipo_ID_Equipo as id_equipo,
                     CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, e.Numero_Serie as nro_serie,
                     p.Monto_Total_Cotizado as costo, ot.Presupuesto_ID_Presupuesto as id_presupuesto
                     FROM orden_trabajo ot 
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                     LEFT JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto
                     WHERE ot.ID_OT = %s"""
            cursor.execute(sql, (id_orden,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar orden por ID: {e}")
            return None
        finally:
            cursor.close()

    # busca una orden por su codigo de seguimiento web
    @staticmethod
    def buscar_por_codigo_tracking(codigo):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Estado_General as estado, ot.Diagnostico_Final as diagnostico,
                     ot.Fecha_Creacion as fecha, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo,
                     e.Detalles_Visuales as detalles_visuales, e.Fotos as fotos,
                     p.Monto_Total_Cotizado as costo, p.Presupuesto_Preliminar_Web as preliminar
                     FROM orden_trabajo ot 
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                     LEFT JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto
                     WHERE ot.Codigo_Tracking_web = %s"""
            cursor.execute(sql, (codigo,))
            return cursor.fetchone()
        except Exception as e:
            print(f"error al buscar por tracking: {e}")
            return None
        finally:
            cursor.close()

    # busca las ordenes de un cliente especifico
    @staticmethod
    def buscar_por_cliente(id_cliente):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, 
                     ot.Estado_General as estado, p.Monto_Total_Cotizado as costo, p.Presupuesto_Preliminar_Web as preliminar,
                     ot.Codigo_Tracking_web as codigo, e.Detalles_Visuales as detalles_visuales, e.Fotos as fotos
                     FROM orden_trabajo ot 
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                     LEFT JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto 
                     WHERE e.Cliente_ID_Cliente = %s"""
            cursor.execute(sql, (id_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"error al buscar por cliente: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_listos_para_entregar():
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, p.Monto_Total_Cotizado as costo 
                     FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                     JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto 
                     WHERE ot.Estado_General = 'Listo para Entregar'"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar listos para entregar: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_historial_por_nro_serie(nro_serie):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Estado_General as estado, ot.Fecha_Creacion as fecha, 
                             ot.Diagnostico_Final as diagnostico, e.Marca_Modelo as equipo 
                      FROM orden_trabajo ot 
                      JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                      WHERE e.Numero_Serie = %s ORDER BY ot.Fecha_Creacion DESC"""
            cursor.execute(sql, (nro_serie,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar historial por nro serie: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_general():
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Fecha_Creacion as fecha, ot.Estado_General as estado, 
                       CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, 
                       c.Nombre_Completo as cliente, e.Numero_Serie as nro_serie 
                FROM orden_trabajo ot 
                JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente 
                ORDER BY ot.Fecha_Creacion DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar historial general: {e}")
            return []
        finally:
            cursor.close()

    # obtiene toda la info de una orden incluyendo equipo, cliente y fotos
    @staticmethod
    def buscar_detalle_completo(id_orden):
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT ot.ID_OT as id_orden, ot.Fecha_Creacion as fecha, ot.Estado_General as estado, 
                       ot.Diagnostico_Final as diagnostico, 
                       CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, 
                       e.Numero_Serie as nro_serie, 
                       e.Detalles_Visuales as detalles_visuales,
                       e.Fotos as fotos,
                       c.Nombre_Completo as cliente, c.DNI_CUIL as dni, c.Telefono as telefono, c.Email as email, 
                       p.Monto_Total_Cotizado as presupuesto, ot.Presupuesto_ID_Presupuesto as id_presupuesto
                FROM orden_trabajo ot 
                JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                JOIN cliente c ON e.Cliente_ID_Cliente = c.ID_Cliente 
                LEFT JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto 
                WHERE ot.ID_OT = %s"""
            cursor.execute(sql, (id_orden,))
            return cursor.fetchone()
        except Exception as e:
            print(f"error al buscar detalle completo: {e}")
            return None
        finally:
            cursor.close()