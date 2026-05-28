import mysql.connector
import datetime

def seed():
    print("--- Iniciando Siembra de Datos de Prueba (Seed) ---")
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
        print("Asegúrate de que XAMPP y el servidor MySQL estén iniciados.")
        return

    # 1. Asegurar columnas en las tablas (por si acaso no fueron creadas aún)
    try:
        cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN Stock_Minimo INT DEFAULT 0")
        conn.commit()
        print("[!] Columna 'Stock_Minimo' agregada/verificada en 'catalogo_inventario'.")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE detalle_orden ADD COLUMN Estado_Detalle VARCHAR(20) DEFAULT 'Pendiente'")
        conn.commit()
        print("[!] Columna 'Estado_Detalle' agregada/verificada en 'detalle_orden'.")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE orden_trabajo ADD COLUMN Codigo_Tracking_web VARCHAR(45) DEFAULT NULL")
        conn.commit()
        print("[!] Columna 'Codigo_Tracking_web' agregada/verificada en 'orden_trabajo'.")
    except Exception:
        pass

    # Limpiar tablas para evitar duplicados en pruebas
    print("Limpiando tablas de accesos e inventario...")
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE legajo_empleado")
        cursor.execute("TRUNCATE TABLE empleado")
        cursor.execute("TRUNCATE TABLE roles")
        cursor.execute("TRUNCATE TABLE cliente")
        cursor.execute("TRUNCATE TABLE equipo")
        cursor.execute("TRUNCATE TABLE catalogo_inventario")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    except Exception as e:
        print(f"Advertencia al limpiar tablas: {e}")

    # 2. Insertar Roles
    print("Insertando roles...")
    roles = [
        (1, "Administrador"),
        (2, "Recepcionista"),
        (3, "Técnico")
    ]
    cursor.executemany("INSERT INTO roles (ID_Rol, Nombre_Rol) VALUES (%s, %s)", roles)
    conn.commit()

    # 3. Insertar Empleados
    print("Insertando empleados del personal...")
    empleados = [
        (1, "Admin General", "admin", "admin123"),
        (2, "Lucía Recepcionista", "recep", "recep123"),
        (3, "Mateo Técnico", "tecnico", "tecnico123")
    ]
    for id_emp, nombre, user, pwd in empleados:
        cursor.execute("INSERT INTO empleado (ID_Empleado, Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s, %s, %s, %s)", (id_emp, nombre, user, pwd))
        # Generar legajo activo desde hoy
        fecha_ing = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO legajo_empleado (Empleado_ID_Empleado, Roles_ID_Rol, Fecha_Ingreso) VALUES (%s, %s, %s)", (id_emp, id_emp, fecha_ing))
    conn.commit()

    # 4. Insertar Clientes
    print("Insertando clientes de prueba...")
    clientes = [
        (1, "45000001", "Maximo Piriz", "maximo@mail.com", "3704888881", "1234"),
        (2, "45000002", "Lautaro Torres", "lautaro@mail.com", "3704888882", "1234"),
        (3, "45000003", "Julian Gonzalez", "julian@mail.com", "3704888883", "1234")
    ]
    cursor.executemany("INSERT INTO cliente (ID_Cliente, DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) VALUES (%s, %s, %s, %s, %s, %s)", clientes)
    conn.commit()

    # 5. Insertar Catálogo de Inventario (Precios de Argentina ARS)
    print("Insertando catálogo e inventario...")
    items = [
        ("Repuesto_Fisico", "Memoria RAM DDR4 8GB Kingston 3200MHz", 25000.00, 15, 4, "https://compu-ar.com/ram-8gb"),
        ("Repuesto_Fisico", "Disco SSD Kingston 480GB SATA3", 42000.00, 10, 3, "https://compu-ar.com/ssd-480gb"),
        ("Repuesto_Fisico", "Pasta Térmica Arctic MX-4 (4g)", 12500.00, 8, 2, "https://compu-ar.com/mx4"),
        ("Repuesto_Fisico", "Fuente de Alimentación Gigabyte 650W 80 Plus", 82000.00, 5, 2, "https://compu-ar.com/fuente-650w"),
        ("Repuesto_Fisico", "Placa Madre Gigabyte A520M K V2 AM4", 95000.00, 4, 1, "https://compu-ar.com/mb-a520"),
        ("Repuesto_Fisico", "Disco SSD M.2 NVMe WD Blue 1TB", 89000.00, 6, 2, "https://compu-ar.com/ssd-1tb"),
        
        ("Servicio_ManoObra", "Diagnóstico Técnico General", 10000.00, 0, 0, ""),
        ("Servicio_ManoObra", "Limpieza Física Completa y Cambio de Pasta Térmica", 18000.00, 0, 0, ""),
        ("Servicio_ManoObra", "Formateo e Instalación de Windows 11 + Drivers", 20000.00, 0, 0, ""),
        ("Servicio_ManoObra", "Reparación Compleja a Nivel Componente (Placa)", 38000.00, 0, 0, ""),
        ("Servicio_ManoObra", "Ensamblaje y Optimización de Computadora Nueva", 25000.00, 0, 0, "")
    ]
    cursor.executemany("INSERT INTO catalogo_inventario (Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible, Stock_Minimo, URL_Referencia_Externa) VALUES (%s, %s, %s, %s, %s, %s)", items)
    conn.commit()

    cursor.close()
    conn.close()
    print("--- Siembra de Datos Completada Exitosamente ---")
    print("\nCuentas de Personal creadas:")
    print(" - Administrador -> Usuario: admin | Clave: admin123")
    print(" - Recepcionista -> Usuario: recep | Clave: recep123")
    print(" - Técnico       -> Usuario: tecnico | Clave: tecnico123")
    print("\nCuentas de Cliente creadas:")
    print(" - Maximo Piriz -> DNI: 45000001 | Clave Web: 1234")
    print(" - Lautaro Torres -> DNI: 45000002 | Clave Web: 1234")
    print(" - Julian Gonzalez -> DNI: 45000003 | Clave Web: 1234")

if __name__ == "__main__":
    seed()
