import datetime
from config.database import DB

class Empleado:
    def __init__(self, nombre, usuario, password, id_rol=None, id_empleado=None):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.usuario = usuario
        self.password = password
        self.id_rol = id_rol

    def registrar(self):
        """Guarda al empleado y le genera su legajo con el rol correspondiente."""
        cursor = DB.cursor()
        try:
            # Registrar el empleado
            sql_empleado = "INSERT INTO empleado (Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s, %s, %s)"
            cursor.execute(sql_empleado, (self.nombre, self.usuario, self.password))
            
            # Obtener el ID asignado
            self.id_empleado = cursor.lastrowid
            
            # Registrar el legajo
            fecha_hoy = datetime.date.today().strftime('%Y-%m-%d')
            sql_legajo = """INSERT INTO legajo_empleado (Empleado_ID_Empleado, Roles_ID_Rol, Fecha_Ingreso) 
                            VALUES (%s, %s, %s)"""
            cursor.execute(sql_legajo, (self.id_empleado, self.id_rol, fecha_hoy))
            
            DB.commit()
            print(f"Empleado '{self.nombre}' registrado con éxito con ID {self.id_empleado}.")
            return self.id_empleado
        except Exception as e:
            # Si algo falla, intentamos hacer rollback si la conexión lo requiere
            try:
                DB.conexion.rollback()
            except:
                pass
            print(f"Error al registrar el empleado: {e}")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def eliminar(id_emp):
        """Elimina la relación histórica en legajo_empleado y el empleado del sistema."""
        cursor = DB.cursor()
        try:
            # Primero eliminamos legajos
            cursor.execute("DELETE FROM legajo_empleado WHERE Empleado_ID_Empleado = %s", (id_emp,))
            # Luego eliminamos al empleado
            cursor.execute("DELETE FROM empleado WHERE ID_Empleado = %s", (id_emp,))
            DB.commit()
            return True
        except Exception as e:
            try:
                DB.conexion.rollback()
            except:
                pass
            print(f"Error al eliminar el empleado: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def listar_todos():
        """Retorna una lista de todos los empleados con sus roles correspondientes."""
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT e.ID_Empleado as id, e.Nombre_Completo as nombre, e.Usuario_Login as usuario, r.Nombre_Rol as rol 
                     FROM empleado e 
                     JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado 
                     JOIN roles r ON l.Roles_ID_Rol = r.ID_Rol"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []
        finally:
            cursor.close()