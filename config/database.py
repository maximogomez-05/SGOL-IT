import mysql.connector

class ConectorDB:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "sgol_it"
        self.conexion = self._conectar()

    def _conectar(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def cursor(self, dictionary=False):
        # Verificamos que la conexión siga viva antes de devolver el cursor
        if not self.conexion.is_connected():
            self.conexion = self._conectar()
        return self.conexion.cursor(dictionary=dictionary)

    def commit(self):
        self.conexion.commit()
        
    def close(self):
        if self.conexion.is_connected():
            self.conexion.close()

# Instanciamos el objeto DB que están esperando importar el resto de los archivos
DB = ConectorDB()