# pyrefly: ignore [missing-import]
from config.database import DB
from werkzeug.security import check_password_hash

class Autenticacion:
    # valida las credenciales del empleado al iniciar sesion
    def iniciar_sesion(self, usuario, password):
        try:
            # cursor en formato diccionario para leer facil
            cursor = DB.cursor(dictionary=True)
            
            # query para buscar al empleado por su usuario
            sql = """
                SELECT e.ID_Empleado as id, 
                       e.Nombre_Completo as nombre, 
                       e.Password_Hash as password_hash,
                       e.Activo as activo,
                       l.Roles_ID_Rol as rol_id, 
                       r.Nombre_Rol as nombre_rol
                FROM empleado e
                LEFT JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado
                LEFT JOIN roles r ON l.Roles_ID_Rol = r.ID_Rol
                WHERE e.Usuario_Login = %s
            """
            
            cursor.execute(sql, (usuario,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                # revisa que este activo y que coincida el hash de la clave
                if user_data.get('activo', 1) == 1 and check_password_hash(user_data['password_hash'], password):
                    # borra el hash de la password antes de retornar para no guardarlo en session
                    del user_data['password_hash']
                    return user_data
            return None
            
        except Exception as e:
            print(f"error en auth de empleado: {e}")
            return None