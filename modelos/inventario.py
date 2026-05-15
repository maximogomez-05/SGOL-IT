from config.database import DB

class Inventario:
    def __init__(self, tipo_item, descripcion, precio_actual, stock_disponible, url_referencia=""):
        self.tipo_item = tipo_item
        self.descripcion = descripcion
        self.precio_actual = precio_actual
        self.stock_disponible = stock_disponible
        self.url_referencia = url_referencia

    def registrar(self):
        cursor = DB.cursor()
        sql = """INSERT INTO Catalogo_Inventario 
                 (Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible, URL_Referencia_Externa) 
                 VALUES (%s, %s, %s, %s, %s)"""
        val = (self.tipo_item, self.descripcion, self.precio_actual, self.stock_disponible, self.url_referencia)
        cursor.execute(sql, val)
        DB.commit()
        cursor.close()

    @staticmethod
    def listar_todo():
        cursor = DB.cursor(dictionary=True)
        cursor.execute("SELECT ID_Item as id, Tipo_Item as tipo_item, Descripcion as descripcion, Precio_Actual as precio, Stock_Disponible as stock FROM Catalogo_Inventario")
        resultados = cursor.fetchall()
        cursor.close()
        return resultados