import mysql.connector
import threading

class ConectorDB:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "sgol_it"
        self._local = threading.local()

    def _conectar(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    @property
    def conexion(self):
        # obtiene o crea la conexion especifica de este hilo
        if not hasattr(self._local, 'conexion') or not self._local.conexion.is_connected():
            self._local.conexion = self._conectar()
        return self._local.conexion

    def cursor(self, dictionary=False):
        return self.conexion.cursor(dictionary=dictionary)

    def commit(self):
        self.conexion.commit()
        
    def close(self):
        if hasattr(self._local, 'conexion') and self._local.conexion.is_connected():
            self._local.conexion.close()

# instanciamos el objeto DB que estan esperando importar el resto de los archivos
DB = ConectorDB()