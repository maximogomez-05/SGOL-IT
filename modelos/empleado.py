import datetime
from config.database import ConexionBD
import datetime

class Empleado:
    def __init__(self, nombre, usuario, password, id_rol):
        self.nombre = nombre
        self.usuario = usuario
        self.password = password
        self.id_rol = id_rol

    def registrar(self):
        """Guarda al empleado y le genera su legajo con el rol correspondiente."""
        db = ConexionBD()
        conexion = db.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                
                #guardar datos personales del personal.
                sql_empleado = "INSERT INTO Empleado (Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s, %s, %s)"
                cursor.execute(sql_empleado, (self.nombre, self.usuario, self.password))
                
                # capturamos el ID automático que le puso SQL al empleado
                id_empleado_nuevo = cursor.lastrowid
                
                # armar contrato/legajo
                fecha_hoy = datetime.date.today()
                sql_legajo = """INSERT INTO Legajo_Empleado (Empleado_ID_Empleado, Roles_ID_Rol, Fecha_Ingreso) 
                                VALUES (%s, %s, %s)"""
                cursor.execute(sql_legajo, (id_empleado_nuevo, self.id_rol, fecha_hoy))
                
                # confirmar
                conexion.commit()
                print(f"Empleado '{self.nombre}' registrado con éxito en su nuevo legajo.")
                
            except Exception as e:
                # si falla, se deshace todo.
                conexion.rollback()
                print(f" Error al registrar el empleado: {e}")
            finally:
                cursor.close()
                db.desconectar()