from config.database import DB

class DetalleOrden:
    def __init__(self, cantidad, precio_unitario_congelado, orden_trabajo_id_ot, catalogo_inventario_id_item, estado_detalle="Pendiente", id_detalle=None):
        self.id_detalle = id_detalle
        self.cantidad = cantidad
        self.precio_unitario_congelado = precio_unitario_congelado
        self.orden_trabajo_id_ot = orden_trabajo_id_ot
        self.catalogo_inventario_id_item = catalogo_inventario_id_item
        self.estado_detalle = estado_detalle
        self._asegurar_columna_estado()

    def _asegurar_columna_estado(self):
        cursor = DB.cursor()
        try:
            cursor.execute("ALTER TABLE detalle_orden ADD COLUMN Estado_Detalle VARCHAR(20) DEFAULT 'Pendiente'")
            DB.commit()
        except Exception:
            pass
        finally:
            cursor.close()

    def registrar(self):
        cursor = DB.cursor()
        try:
            sql = """INSERT INTO detalle_orden 
                     (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item, Estado_Detalle) 
                     VALUES (%s, %s, %s, %s, %s)"""
            val = (self.cantidad, self.precio_unitario_congelado, self.orden_trabajo_id_ot, self.catalogo_inventario_id_item, self.estado_detalle)
            cursor.execute(sql, val)
            DB.commit()
            self.id_detalle = cursor.lastrowid
            return self.id_detalle
        except Exception as e:
            print(f"Error al registrar detalle de orden: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_orden(id_orden):
        """Retorna los detalles de repuestos y servicios vinculados a una OT."""
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT d.ID_Detalle as id_detalle, d.Cantidad as cantidad, 
                     d.Precio_Unitario_Congelado as precio_unit, 
                     (d.Cantidad * d.Precio_Unitario_Congelado) as subtotal, 
                     d.Estado_Detalle as estado,
                     i.Descripcion as descripcion, d.Catalogo_Inventario_ID_Item as id_item,
                     i.Tipo_Item as tipo_item
                     FROM detalle_orden d 
                     JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                     WHERE d.Orden_Trabajo_ID_OT = %s"""
            cursor.execute(sql, (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar detalles de orden: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def eliminar_item_ot(id_orden, id_item):
        """Elimina un repuesto/servicio específico de una OT."""
        cursor = DB.cursor()
        try:
            cursor.execute("DELETE FROM detalle_orden WHERE Orden_Trabajo_ID_OT = %s AND Catalogo_Inventario_ID_Item = %s", (id_orden, id_item))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar ítem de la OT: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def reservar_componentes(id_orden):
        """Cambia el estado de los componentes de la OT a 'Reservado'."""
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE detalle_orden SET Estado_Detalle = 'Reservado' WHERE Orden_Trabajo_ID_OT = %s AND Estado_Detalle = 'Pendiente'", (id_orden,))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al reservar componentes: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def consumir_componentes(id_orden):
        """Marca los componentes como 'Consumido' y descuenta físicamente el stock de repuestos."""
        cursor = DB.cursor(dictionary=True)
        try:
            # Obtener detalles de la orden para descontar stock de repuestos físicos
            sql_items = """SELECT d.Catalogo_Inventario_ID_Item as id_item, d.Cantidad as cantidad, i.Tipo_Item as tipo_item
                           FROM detalle_orden d
                           JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item
                           WHERE d.Orden_Trabajo_ID_OT = %s AND d.Estado_Detalle IN ('Reservado', 'Pendiente')"""
            cursor.execute(sql_items, (id_orden,))
            items = cursor.fetchall()

            for item in items:
                if item['tipo_item'] == 'Repuesto_Fisico':
                    # Descontar stock
                    cursor.execute("""UPDATE catalogo_inventario 
                                     SET Stock_Disponible = Stock_Disponible - %s 
                                     WHERE ID_Item = %s""", (item['cantidad'], item['id_item']))

            # Marcar detalles como Consumido
            cursor.execute("UPDATE detalle_orden SET Estado_Detalle = 'Consumido' WHERE Orden_Trabajo_ID_OT = %s AND Estado_Detalle IN ('Reservado', 'Pendiente')", (id_orden,))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al consumir componentes e inventario: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_cliente(id_cliente):
        """Retorna todos los detalles de órdenes de trabajo para un cliente específico."""
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT d.Orden_Trabajo_ID_OT as id_orden, d.Cantidad as cantidad, 
                     (d.Cantidad * d.Precio_Unitario_Congelado) as subtotal, 
                     i.Descripcion as descripcion 
                     FROM detalle_orden d 
                     JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                     JOIN orden_trabajo ot ON d.Orden_Trabajo_ID_OT = ot.ID_OT 
                     JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                     WHERE e.Cliente_ID_Cliente = %s"""
            cursor.execute(sql, (id_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar detalles de orden por cliente: {e}")
            return []
        finally:
            cursor.close()