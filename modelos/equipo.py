from config.database import DB

class Equipo:
    # constructor de la clase equipo
    def __init__(self, nro_serie, marca, modelo, tipo, id_cliente, id_equipo=None):
        self.id_equipo = id_equipo
        self.nro_serie = nro_serie
        self.marca = marca
        self.modelo = modelo
        self.tipo = tipo
        self.id_cliente = id_cliente

    # guarda el equipo en la bd
    def registrar(self):
        cursor = DB.cursor()
        try:
            sql = """INSERT INTO equipo 
                     (Numero_Serie, Marca, Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) 
                     VALUES (%s, %s, %s, %s, %s)"""
            val = (self.nro_serie, self.marca, self.modelo, self.tipo, self.id_cliente)
            cursor.execute(sql, val)
            DB.commit()
            self.id_equipo = cursor.lastrowid
            return self.id_equipo
        except Exception as e:
            print(f"Error al registrar equipo: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_numero_serie(nro_serie):
        """Busca un equipo existente por su número de serie para evitar duplicados."""
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Equipo as id, Numero_Serie as nro_serie, Marca as marca, Modelo as modelo, Tipo_Dispositivo as tipo, Cliente_ID_Cliente as id_cliente FROM equipo WHERE Numero_Serie = %s", (nro_serie,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar equipo por número de serie: {e}")
            return None
        finally:
            cursor.close()