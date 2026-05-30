from config.database import DB

class Equipo:
    # constructor de la clase equipo
    def __init__(self, nro_serie, modelo, tipo, id_cliente, detalles_visuales=None, fotos=None):
        self.nro_serie = nro_serie
        self.modelo = modelo
        self.tipo = tipo
        self.id_cliente = id_cliente
        self.detalles_visuales = detalles_visuales
        self.fotos = fotos

    # guarda el equipo en la bd
    def registrar(self):
        cursor = DB.cursor()
        sql = """INSERT INTO equipo 
                 (Numero_Serie, Marca_Modelo, Tipo_Dispositivo, Cliente_ID_Cliente, Detalles_Visuales, Fotos) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        val = (self.nro_serie, self.modelo, self.tipo, self.id_cliente, self.detalles_visuales, self.fotos)
        cursor.execute(sql, val)
        DB.commit()
        id_gen = cursor.lastrowid
        cursor.close()
        return id_gen