from config.database import DB

class Cliente:
    def __init__(self, dni, nombre, email, telefono, password_web, id_cliente=None):
        self.id_cliente = id_cliente
        self.dni = dni
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.password_web = password_web

    def registrar(self):
        cursor = DB.cursor()
        try:
            sql = "INSERT INTO cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) VALUES (%s, %s, %s, %s, %s)"
            val = (self.dni, self.nombre, self.email, self.telefono, self.password_web)
            cursor.execute(sql, val)
            DB.commit()
            self.id_cliente = cursor.lastrowid
            return self.id_cliente
        except Exception as e:
            print(f"Error al registrar cliente: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_dni(dni):
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Cliente as id, Nombre_Completo as nombre, Email as email, Telefono as telefono FROM cliente WHERE DNI_CUIL = %s", (dni,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar cliente por DNI: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_credenciales(dni, password_web):
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Cliente as id, Nombre_Completo as nombre FROM cliente WHERE DNI_CUIL = %s AND Password_web = %s", (dni, password_web))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar cliente por credenciales: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def actualizar_password(id_cliente, nueva_password):
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE cliente SET Password_web = %s WHERE ID_Cliente = %s", (nueva_password, id_cliente))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar password de cliente: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()