from config.database import DB

class Equipo:
    def __init__(self, nro_serie, modelo, tipo, id_cliente):
        self.nro_serie = nro_serie
        self.modelo = modelo
        self.tipo = tipo
        self.id_cliente = id_cliente

    def registrar(self):
        cursor = DB.cursor()
        sql = "INSERT INTO Equipo (Numero_Serie, Marca_Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) VALUES (%s, %s, %s, %s)"
        val = (self.nro_serie, self.modelo, self.tipo, self.id_cliente)
        cursor.execute(sql, val)
        DB.commit()
        id_gen = cursor.lastrowid
        cursor.close()
        return id_gen