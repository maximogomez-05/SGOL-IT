from config.database import DB

class Cliente:
    def __init__(self, dni, nombre, email, telefono, password_web):
        self.dni = dni
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.password_web = password_web

    def registrar(self):
        cursor = DB.cursor()
        sql = "INSERT INTO Cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) VALUES (%s, %s, %s, %s, %s)"
        val = (self.dni, self.nombre, self.email, self.telefono, self.password_web)
        cursor.execute(sql, val)
        DB.commit()
        id_gen = cursor.lastrowid
        cursor.close()
        return id_gen

    @staticmethod
    def buscar_por_dni(dni):
        cursor = DB.cursor(dictionary=True)
        cursor.execute("SELECT ID_Cliente as id FROM Cliente WHERE DNI_CUIL = %s", (dni,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado