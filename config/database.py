import mysql.connector
from mysql.connector import Error

class ConexionBD:
    def __init__(self):
        # credenciales defecto.
        self.host = 'localhost'
        self.database = 'sgol_it' 
        self.user = 'root'
        self.password = '' 
        self.conexion = None

    def conectar(self):
        """Establece la conexión con la base de datos."""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.conexion.is_connected():
                print("Conexión exitosa a la base de datos SGOL-IT.")
                return self.conexion
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None

    def desconectar(self):
        """Cierra la conexión para liberar recursos."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("Conexión cerrada.")

# test
# probar conexion ejecutando el archivo
if __name__ == "__main__":
    db = ConexionBD()
    con = db.conectar()
    if con:
        db.desconectar()