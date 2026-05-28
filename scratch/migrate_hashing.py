import mysql.connector
from werkzeug.security import generate_password_hash

def migrate():
    print("--- Iniciando Migración de Cifrado y Estructura (Fase 2 y 4) ---")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sgol_it"
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return

    # 1. Agregar columna 'Activo' a 'empleado' si no existe
    print("Verificando/Agregando columna 'Activo' a la tabla 'empleado'...")
    try:
        cursor.execute("ALTER TABLE empleado ADD COLUMN Activo TINYINT DEFAULT 1")
        conn.commit()
        print("[+] Columna 'Activo' agregada con éxito.")
    except Exception as e:
        # Si ya existe, fallará de forma controlada y continuará
        print("[!] Columna 'Activo' ya existe o no se pudo agregar:", e)

    # 2. Cifrar contraseñas de empleados
    print("Migrando contraseñas de empleados...")
    cursor.execute("SELECT ID_Empleado, Password_Hash FROM empleado")
    empleados = cursor.fetchall()
    
    updated_emp = 0
    for id_emp, pwd in empleados:
        # Los hashes de werkzeug generalmente contienen ':' (ej. 'scrypt:32768:8:1$...')
        if pwd and ":" not in pwd:
            hashed = generate_password_hash(pwd)
            cursor.execute("UPDATE empleado SET Password_Hash = %s WHERE ID_Empleado = %s", (hashed, id_emp))
            updated_emp += 1
    
    conn.commit()
    print(f"[+] Contraseñas de empleados actualizadas: {updated_emp}")

    # 3. Cifrar contraseñas de clientes
    print("Migrando contraseñas de clientes...")
    cursor.execute("SELECT ID_Cliente, Password_web FROM cliente")
    clientes = cursor.fetchall()
    
    updated_cli = 0
    for id_cli, pwd in clientes:
        if pwd and ":" not in pwd:
            hashed = generate_password_hash(pwd)
            cursor.execute("UPDATE cliente SET Password_web = %s WHERE ID_Cliente = %s", (hashed, id_cli))
            updated_cli += 1
            
    conn.commit()
    print(f"[+] Contraseñas de clientes actualizadas: {updated_cli}")

    cursor.close()
    conn.close()
    print("--- Migración Completada Exitosamente ---")

if __name__ == "__main__":
    migrate()
