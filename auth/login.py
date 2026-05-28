from config.database import DB
from werkzeug.security import check_password_hash

class Autenticacion:
    def iniciar_sesion(self, usuario, password):
        try:
            # Pedimos un cursor que nos devuelva diccionarios para manejar más fácil los datos
            cursor = DB.cursor(dictionary=True)
            
            # Consulta SQL para verificar credenciales y traer el rol del empleado
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
                # Validar que la cuenta esté activa (1) y coincida el hash de contraseña
                if user_data.get('activo', 1) == 1 and check_password_hash(user_data['password_hash'], password):
                    # Limpiamos el hash por seguridad antes de guardarlo en la sesión
                    del user_data['password_hash']
                    return user_data
            return None
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None