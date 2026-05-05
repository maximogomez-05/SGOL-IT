from config.database import ConexionBD

class Autenticacion:
    def iniciar_sesion(self, usuario, password):
        """Verifica las credenciales y devuelve todos los datos del usuario y su rol."""
        db = ConexionBD()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                # Cruzamos las 3 tablas para traer el ID, Nombre, Rol y Nombre del Rol
                sql = """
                    SELECT e.ID_Empleado, e.Nombre_Completo, r.ID_Rol, r.Nombre_Rol
                    FROM empleado e
                    JOIN legajo_empleado le ON e.ID_Empleado = le.Empleado_ID_Empleado
                    JOIN roles r ON le.Roles_ID_Rol = r.ID_Rol
                    WHERE e.Usuario_Login = %s AND e.Password_Hash = %s
                    AND (le.Fecha_Cese IS NULL OR le.Fecha_Cese > CURDATE())
                """
                cursor.execute(sql, (usuario, password))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Armamos el diccionario exacto que main esta esperando
                    return {
                        'id': resultado[0],
                        'nombre': resultado[1],
                        'rol_id': resultado[2],
                        'nombre_rol': resultado[3]
                    }
                else:
                    return None
                    
            except Exception as e:
                print(f"Error de base de datos durante el login: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None