import datetime
import random
from config.database import ConexionBD

class OrdenTrabajo:
    def __init__(self, id_equipo, id_empleado, id_presupuesto=None):
        self.id_equipo = id_equipo
        self.id_empleado = id_empleado  
        self.id_presupuesto = id_presupuesto 
        self.estado_general = "Para Revisión" # NUEVO ESTADO INICIAL
        self.codigo_tracking = f"OT-{random.randint(1000, 9999)}"
        self.fecha_creacion = datetime.datetime.now()

    def registrar(self):
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Orden_Trabajo 
                         (Estado_General, Codigo_Tracking_Web, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado, Presupuesto_ID_Presupuesto) 
                         VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (self.estado_general, self.codigo_tracking, self.fecha_creacion, self.id_equipo, self.id_empleado, self.id_presupuesto))
                conexion.commit()
                print(f"\n TICKET GENERADO: {self.codigo_tracking} (Enviado a Laboratorio para revisión)")
            except Exception as e:
                print(f"Error al crear Orden: {e}")
            finally:
                cursor.close()
                db.desconectar()

    @staticmethod
    def vincular_presupuesto(id_orden, id_presupuesto):
        """Asigna el ID del presupuesto a la orden de trabajo una vez aprobado/rechazado."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Orden_Trabajo SET Presupuesto_ID_Presupuesto = %s WHERE ID_OT = %s"
                cursor.execute(sql, (id_presupuesto, id_orden))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al vincular presupuesto: {e}")
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def buscar_pendientes():
        db = ConexionBD()
        conexion = db.conectar()
        lista = []
        if conexion:
            try:
                cursor = conexion.cursor()
                # Sumamos el Equipo_ID_Equipo (fila 4) para poder armar el presupuesto después
                sql = """SELECT ot.ID_OT, ot.Codigo_Tracking_Web, e.Marca_Modelo, ot.Estado_General, ot.Equipo_ID_Equipo 
                         FROM Orden_Trabajo ot JOIN Equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                         WHERE ot.Estado_General != 'Entregado'"""
                cursor.execute(sql)
                for fila in cursor.fetchall():
                    lista.append({"id_orden": fila[0], "codigo": fila[1], "equipo": fila[2], "estado": fila[3], "id_equipo": fila[4]})
                return lista
            finally:
                cursor.close()
                db.desconectar()
        return []

    @staticmethod
    def actualizar_estado(id_orden, nuevo_estado):
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE Orden_Trabajo SET Estado_General = %s WHERE ID_OT = %s"
                cursor.execute(sql, (nuevo_estado, id_orden))
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error update: {e}")
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def agregar_item_a_orden(id_orden, id_item, cantidad):
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT Precio_Actual, Stock_Disponible, Tipo_Item FROM Catalogo_Inventario WHERE ID_Item = %s", (id_item,))
                item = cursor.fetchone()
                if not item: return False
                
                if item[2] == 'Repuesto_Fisico':
                    cursor.execute("UPDATE Catalogo_Inventario SET Stock_Disponible = Stock_Disponible - %s WHERE ID_Item = %s", (cantidad, id_item))

                sql_detalle = """INSERT INTO Detalle_Orden (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item)
                                 VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql_detalle, (cantidad, item[0], id_orden, id_item))
                conexion.commit()
                print(" Item cargado a la orden.")
                return True
            except Exception as e:
                print(f"Error detalle: {e}")
                return False
            finally:
                cursor.close()
                db.desconectar()

    @staticmethod
    def generar_factura(id_ot):
        db = ConexionBD()
        conexion = db.conectar()
        detalles = []
        total = 0.0
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """SELECT c.Descripcion, d.Cantidad, d.Precio_Unitario_Congelado 
                         FROM Detalle_Orden d JOIN Catalogo_Inventario c ON d.Catalogo_Inventario_ID_Item = c.ID_Item
                         WHERE d.Orden_Trabajo_ID_OT = %s"""
                cursor.execute(sql, (id_ot,))
                for fila in cursor.fetchall():
                    sub = fila[1] * float(fila[2])
                    total += sub
                    detalles.append({"descripcion": fila[0], "cantidad": fila[1], "precio_unit": float(fila[2]), "subtotal": sub})
                return {"detalles": detalles, "total": total}
            finally:
                cursor.close()
                db.desconectar()
        return None