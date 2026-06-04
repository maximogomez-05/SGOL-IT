from config.database import DB

class Inventario:
    def __init__(self, tipo_item, descripcion, precio_actual, stock_disponible, stock_minimo=0, url_referencia="", id_item=None):
        self.id_item = id_item
        self.tipo_item = tipo_item
        self.descripcion = descripcion
        self.precio_actual = precio_actual
        self.stock_disponible = stock_disponible
        self.stock_minimo = stock_minimo
        self.url_referencia = url_referencia

    def registrar(self):
        cursor = DB.cursor()
        try:
            # Asegurarse de que las columnas existen
            try:
                cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN Stock_Minimo INT DEFAULT 0")
                DB.commit()
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN URL_Referencia_Externa VARCHAR(500) DEFAULT ''")
                DB.commit()
            except Exception:
                pass
            
            sql = """INSERT INTO catalogo_inventario 
                     (Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible, Stock_Minimo, URL_Referencia_Externa) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            val = (self.tipo_item, self.descripcion, self.precio_actual, self.stock_disponible, self.stock_minimo, self.url_referencia)
            cursor.execute(sql, val)
            DB.commit()
            self.id_item = cursor.lastrowid
            return self.id_item
        except Exception as e:
            print(f"Error al registrar ítem en inventario: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def listar_todo():
        cursor = DB.cursor(dictionary=True)
        try:
            # Asegurarse de que la columna Stock_Minimo existe
            try:
                cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN Stock_Minimo INT DEFAULT 0")
                DB.commit()
            except Exception:
                pass
            
            cursor.execute("SELECT ID_Item as id, Tipo_Item as tipo_item, Descripcion as descripcion, Precio_Actual as precio, Stock_Disponible as stock, Stock_Minimo as stock_minimo, URL_Referencia_Externa as url_referencia FROM catalogo_inventario")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar inventario: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def actualizar(id_item, descripcion, precio, stock, stock_minimo, url_referencia=""):
        cursor = DB.cursor()
        try:
            try:
                cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN URL_Referencia_Externa VARCHAR(500) DEFAULT ''")
                DB.commit()
            except Exception:
                pass
            
            sql = """UPDATE catalogo_inventario 
                     SET Descripcion = %s, Precio_Actual = %s, Stock_Disponible = %s, Stock_Minimo = %s, URL_Referencia_Externa = %s 
                     WHERE ID_Item = %s"""
            cursor.execute(sql, (descripcion, precio, stock, stock_minimo, url_referencia, id_item))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar ítem de inventario: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()

    @staticmethod
    def eliminar(id_item):
        cursor = DB.cursor()
        try:
            cursor.execute("DELETE FROM catalogo_inventario WHERE ID_Item = %s", (id_item,))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar ítem de inventario: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            raise e
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(id_item):
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Item as id, Tipo_Item as tipo_item, Descripcion as descripcion, Precio_Actual as precio, Stock_Disponible as stock, Stock_Minimo as stock_minimo, URL_Referencia_Externa as url_referencia FROM catalogo_inventario WHERE ID_Item = %s", (id_item,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar ítem de inventario por ID: {e}")
            return None
        finally:
            cursor.close()