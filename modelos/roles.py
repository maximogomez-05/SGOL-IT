from config.database import ConexionBD

class Rol:
    def __init__(self, administrador=0, recepcionista=0, tecnico=0):
        self.administrador = administrador
        self.recepcionista = recepcionista
        self.tecnico = tecnico

    def registrar(self):
        """Inserta un nuevo perfil de rol en la base de datos."""
        db = ConexionBD()
        conexion = db.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Roles (Administrador, Recepcionista, Tecnico) 
                         VALUES (%s, %s, %s)"""
                valores = (self.administrador, self.recepcionista, self.tecnico)
                
                cursor.execute(sql, valores)
                conexion.commit()
                
                # mensaje, detecta que rol es.
                nombre_rol = "Desconocido"
                if self.administrador == 1: nombre_rol = "Administrador"
                elif self.recepcionista == 1: nombre_rol = "Recepcionista"
                elif self.tecnico == 1: nombre_rol = "Técnico"

                print(f"Perfil de '{nombre_rol}' registrado con éxito en la BD.")
                
            except Exception as e:
                print(f"Error al registrar el rol: {e}")
            finally:
                cursor.close()
                db.desconectar()

# test
if __name__ == "__main__":
    # cargar 3 roles definidos.
    
    print("--- Cargando perfiles de Roles ---")
    
    # administrador
    rol_admin = Rol(administrador=1, recepcionista=0, tecnico=0)
    rol_admin.registrar()
    
    # recepcionista
    rol_recep = Rol(administrador=0, recepcionista=1, tecnico=0)
    rol_recep.registrar()
    
    # tecnico
    rol_tecnico = Rol(administrador=0, recepcionista=0, tecnico=1)
    rol_tecnico.registrar()