from config.database import DB

class Rol:
    def __init__(self, nombre_rol, id_rol=None):
        self.id_rol = id_rol
        self.nombre_rol = nombre_rol

    def registrar(self):
        """Inserta un nuevo perfil de rol en la base de datos."""
        cursor = DB.cursor()
        try:
            sql = "INSERT INTO roles (Nombre_Rol) VALUES (%s)"
            cursor.execute(sql, (self.nombre_rol,))
            DB.commit()
            self.id_rol = cursor.lastrowid
            print(f"Rol '{self.nombre_rol}' registrado con éxito con ID {self.id_rol}.")
            return self.id_rol
        except Exception as e:
            print(f"Error al registrar el rol: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def listar_todos():
        """Retorna una lista con todos los roles registrados."""
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Rol as id, Nombre_Rol as nombre FROM roles")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar roles: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_id(id_rol):
        """Busca un rol por su identificador único."""
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Rol as id, Nombre_Rol as nombre FROM roles WHERE ID_Rol = %s", (id_rol,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar rol: {e}")
            return None
        finally:
            cursor.close()