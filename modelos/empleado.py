import datetime
from config.database import DB
from werkzeug.security import generate_password_hash

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
            # Hash password before storing it
            hashed_pwd = generate_password_hash(self.password)
            # Registrar el empleado
            sql_empleado = "INSERT INTO empleado (Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s, %s, %s)"
            cursor.execute(sql_empleado, (self.nombre, self.usuario, hashed_pwd))
            
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
        """Desactiva lógicamente al empleado del sistema (Baja Lógica)."""
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE empleado SET Activo = 0 WHERE ID_Empleado = %s", (id_emp,))
            DB.commit()
            return True
        except Exception as e:
            try:
                DB.conexion.rollback()
            except:
                pass
            print(f"Error al desactivar el empleado: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def activar(id_emp):
        """Activa lógicamente al empleado en el sistema (Alta/Reactivación)."""
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE empleado SET Activo = 1 WHERE ID_Empleado = %s", (id_emp,))
            DB.commit()
            return True
        except Exception as e:
            try:
                DB.conexion.rollback()
            except:
                pass
            print(f"Error al activar el empleado: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def actualizar_password(id_emp, nueva_password):
        """Actualiza la contraseña del empleado de forma segura (hasheada)."""
        cursor = DB.cursor()
        try:
            hashed = generate_password_hash(nueva_password)
            cursor.execute("UPDATE empleado SET Password_Hash = %s WHERE ID_Empleado = %s", (hashed, id_emp))
            DB.commit()
            return True
        except Exception as e:
            try:
                DB.conexion.rollback()
            except:
                pass
            print(f"Error al actualizar la contraseña del empleado: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def listar_todos():
        """Retorna una lista de todos los empleados con sus roles y estado de activación."""
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """SELECT e.ID_Empleado as id, e.Nombre_Completo as nombre, e.Usuario_Login as usuario, r.Nombre_Rol as rol, l.Roles_ID_Rol as rol_id, e.Activo as activo 
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