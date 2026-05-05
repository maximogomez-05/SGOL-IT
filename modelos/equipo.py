from config.database import ConexionBD

class Equipo:
    def __init__(self, numero_serie, marca_modelo, tipo_dispositivo, id_cliente):
        self.numero_serie = numero_serie
        self.marca_modelo = marca_modelo
        self.tipo_dispositivo = tipo_dispositivo
        self.id_cliente = id_cliente  # fkey que une al dueño.

    def registrar(self):
        """Guarda el equipo en la base de datos vinculándolo a un cliente."""
        db = ConexionBD()
        conexion = db.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                
                # inserta datos en la tabla equipo
                sql = """INSERT INTO Equipo (Numero_Serie, Marca_Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) 
                         VALUES (%s, %s, %s, %s)"""
                
                valores = (self.numero_serie, self.marca_modelo, self.tipo_dispositivo, self.id_cliente)
                
                cursor.execute(sql, valores)
                conexion.commit()
                
                id_generado = cursor.lastrowid
                
                print(f"Equipo '{self.marca_modelo}' (Serie: {self.numero_serie}) registrado con éxito.")
                
                # devuelve el id para que el menu pueda usarlo en orden de trabajo.
                return id_generado
                
            except Exception as e:
                print(f"Error al registrar el equipo: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()