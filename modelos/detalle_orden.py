from config.database import DB

class DetalleOrden:
    def __init__(self, cantidad, precio_unitario_congelado, orden_trabajo_id_ot, catalogo_inventario_id_item):
        self.cantidad = cantidad
        self.precio_unitario_congelado = precio_unitario_congelado
        self.orden_trabajo_id_ot = orden_trabajo_id_ot
        self.catalogo_inventario_id_item = catalogo_inventario_id_item

    def registrar(self):
        cursor = DB.cursor()
        sql = """INSERT INTO Detalle_Orden 
                 (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item) 
                 VALUES (%s, %s, %s, %s)"""
        val = (self.cantidad, self.precio_unitario_congelado, self.orden_trabajo_id_ot, self.catalogo_inventario_id_item)
        cursor.execute(sql, val)
        DB.commit()
        cursor.close()