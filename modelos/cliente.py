from config.database import ConexionBD

class Cliente:
    def __init__(self, dni, nombre, email, telefono, password):
        self.dni = dni
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.password = password 

    def registrar(self):
        """Inserta el cliente actual en la BD y devuelve su ID generado."""
        db = ConexionBD()
        conexion = db.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) 
                         VALUES (%s, %s, %s, %s, %s)"""
                valores = (self.dni, self.nombre, self.email, self.telefono, self.password)
                cursor.execute(sql, valores)
                conexion.commit()
                
                #captura id
                id_generado = cursor.lastrowid 
                print(f"Cliente '{self.nombre}' registrado con éxito.")
                
                return id_generado # devolvemos ID, usar en equipo
                
            except Exception as e:
                print(f"Error al registrar el cliente: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()

    @staticmethod
    def buscar_por_dni(dni_buscar):
        """Busca si un cliente ya existe en la BD usando su DNI."""
        db = ConexionBD()
        conexion = db.conectar()
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT ID_Cliente, Nombre_Completo FROM Cliente WHERE DNI_CUIL = %s"
                cursor.execute(sql, (dni_buscar,))
                resultado = cursor.fetchone() # primera fila que encuentre.
                
                if resultado:
                    return {"id": resultado[0], "nombre": resultado[1]}
                else:
                    return None # No lo encontró
                    
            except Exception as e:
                print(f"Error al buscar cliente: {e}")
                return None
            finally:
                cursor.close()
                db.desconectar()