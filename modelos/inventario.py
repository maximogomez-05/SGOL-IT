from config.database import ConexionBD

class Inventario:
    def __init__(self, tipo_item, descripcion, precio_actual, stock, url_ref=""):
        self.tipo_item = tipo_item # Debe ser 'Repuesto_Fisico' o 'Servicio_ManoObra'
        self.descripcion = descripcion
        self.precio_actual = precio_actual
        self.stock = stock
        self.url_ref = url_ref

    def registrar(self):
        """Guarda un nuevo repuesto o servicio en el catalogo."""
        db = ConexionBD()
        conexion = db.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Catalogo_Inventario 
                         (Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible, URL_Referencia_Externa) 
                         VALUES (%s, %s, %s, %s, %s)"""
                
                valores = (self.tipo_item, self.descripcion, self.precio_actual, self.stock, self.url_ref)
                cursor.execute(sql, valores)
                conexion.commit()
                return True
            except Exception as e:
                print(f"Error al guardar en el inventario: {e}")
                return False
            finally:
                cursor.close()
                db.desconectar()
        return False

    @staticmethod
    def listar_todo():
        """Trae todos los items del catalogo para mostrarlos en pantalla."""
        db = ConexionBD()
        conexion = db.conectar()
        items = []

        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT ID_Item, Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible FROM Catalogo_Inventario")
                resultados = cursor.fetchall()
                
                for fila in resultados:
                    items.append({
                        "id": fila[0],
                        "tipo": fila[1],
                        "descripcion": fila[2],
                        "precio": fila[3],
                        "stock": fila[4] if fila[4] is not None else "N/A"
                    })
                return items
            except Exception as e:
                print(f"Error al consultar el inventario: {e}")
                return []
            finally:
                cursor.close()
                db.desconectar()