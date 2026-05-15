from config.database import DB

class Autenticacion:
    def iniciar_sesion(self, usuario, password):
        try:
            # Pedimos un cursor que nos devuelva diccionarios para manejar más fácil los datos
            cursor = DB.cursor(dictionary=True)
            
            # Consulta SQL para verificar credenciales y traer el rol del empleado
            sql = """
                SELECT e.ID_Empleado as id, 
                       e.Nombre_Completo as nombre, 
                       l.Roles_ID_Rol as rol_id, 
                       r.Nombre_Rol as nombre_rol
                FROM empleado e
                LEFT JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado
                LEFT JOIN roles r ON l.Roles_ID_Rol = r.ID_Rol
                WHERE e.Usuario_Login = %s AND e.Password_Hash = %s
            """
            
            cursor.execute(sql, (usuario, password))
            user_data = cursor.fetchone()
            
            cursor.close()
            return user_data
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None