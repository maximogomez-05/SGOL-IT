"""Diagnóstico completo de la base de datos SGOL-IT"""
import sys
sys.path.insert(0, '.')
from config.database import DB
from werkzeug.security import generate_password_hash, check_password_hash

print("="*60)
print("DIAGNÓSTICO SGOL-IT")
print("="*60)

cursor = DB.cursor(dictionary=True)

# 1. Verificar tablas existentes
print("\n--- TABLAS EN LA BASE DE DATOS ---")
cursor.execute("SHOW TABLES")
tables = [list(r.values())[0] for r in cursor.fetchall()]
for t in tables:
    print(f"  - {t}")

# 2. Verificar empleados
print("\n--- EMPLEADOS ---")
cursor.execute("SELECT e.ID_Empleado, e.Nombre_Completo, e.Usuario_Login, e.Password_Hash, e.Activo, l.Roles_ID_Rol FROM empleado e LEFT JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado")
empleados = cursor.fetchall()
for emp in empleados:
    pwd_hash = emp['Password_Hash']
    # Test passwords
    test_passwords = ['123456', 'admin123', '123', '1234']
    matched = None
    for tp in test_passwords:
        try:
            if check_password_hash(pwd_hash, tp):
                matched = tp
                break
        except:
            pass
    print(f"  ID:{emp['ID_Empleado']} | User:{emp['Usuario_Login']} | Nombre:{emp['Nombre_Completo']} | Activo:{emp['Activo']} | Rol:{emp['Roles_ID_Rol']} | PwdMatch:{matched} | Hash:{pwd_hash[:30]}...")

# 3. Verificar clientes
print("\n--- CLIENTES ---")
cursor.execute("SELECT ID_Cliente, DNI_CUIL, Nombre_Completo, Password_web, IFNULL(Password_Cambiada,0) as pc FROM cliente LIMIT 10")
clientes = cursor.fetchall()
for cl in clientes:
    pwd_hash = cl['Password_web']
    matched = None
    for tp in ['123', '123456', '1234']:
        try:
            if check_password_hash(pwd_hash, tp):
                matched = tp
                break
        except:
            pass
    print(f"  ID:{cl['ID_Cliente']} | DNI:{cl['DNI_CUIL']} | {cl['Nombre_Completo']} | PwdMatch:{matched} | PwdCambiada:{cl['pc']}")

# 4. Verificar ordenes
print("\n--- ORDENES DE TRABAJO ---")
cursor.execute("SELECT ID_OT, Estado_General, Codigo_Tracking_web, Equipo_ID_Equipo, Empleado_ID_Empleado, Presupuesto_ID_Presupuesto, Servicio FROM orden_trabajo LIMIT 15")
ordenes = cursor.fetchall()
for o in ordenes:
    print(f"  OT#{o['ID_OT']} | Estado:{o['Estado_General']} | Tracking:{o['Codigo_Tracking_web']} | Equipo:{o['Equipo_ID_Equipo']} | Emp:{o['Empleado_ID_Empleado']} | Presup:{o['Presupuesto_ID_Presupuesto']} | Servicio:{o['Servicio']}")

# 5. Verificar columnas de orden_trabajo
print("\n--- COLUMNAS DE orden_trabajo ---")
cursor.execute("SHOW COLUMNS FROM orden_trabajo")
for col in cursor.fetchall():
    print(f"  {col['Field']} ({col['Type']}) - Null:{col['Null']} - Default:{col['Default']}")

# 6. Verificar stored procedures
print("\n--- STORED PROCEDURES ---")
cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'sgol_it'")
procs = cursor.fetchall()
for p in procs:
    print(f"  {p['Name']}")

# 7. Verificar triggers
print("\n--- TRIGGERS ---")
cursor.execute("SHOW TRIGGERS FROM sgol_it")
triggers = cursor.fetchall()
for t in triggers:
    print(f"  {t['Trigger']} on {t['Table']}")

# 8. Verificar equipos
print("\n--- EQUIPOS ---")
cursor.execute("SELECT ID_Equipo, Marca, Modelo, Tipo_Dispositivo, Cliente_ID_Cliente FROM equipo LIMIT 10")
for eq in cursor.fetchall():
    print(f"  #{eq['ID_Equipo']} | {eq['Marca']} {eq['Modelo']} ({eq['Tipo_Dispositivo']}) | Cliente:{eq['Cliente_ID_Cliente']}")

# 9. Verificar presupuestos
print("\n--- PRESUPUESTOS ---")
cursor.execute("SELECT * FROM presupuesto LIMIT 10")
for p in cursor.fetchall():
    print(f"  {p}")

# 10. Verificar facturas
print("\n--- FACTURAS ---")
cursor.execute("SELECT ID_Factura, Orden_Trabajo_ID_OT, Monto_Total, Metodo_Pago FROM factura LIMIT 10")
for f in cursor.fetchall():
    print(f"  F#{f['ID_Factura']} | OT:{f['Orden_Trabajo_ID_OT']} | ${f['Monto_Total']} | {f['Metodo_Pago']}")

# 11. Verificar seguimiento
print("\n--- SEGUIMIENTO_ESTADOS (ultimos 10) ---")
cursor.execute("SELECT * FROM seguimiento_estados ORDER BY ID_Seguimiento DESC LIMIT 10")
for s in cursor.fetchall():
    print(f"  #{s['ID_Seguimiento']} | OT:{s['Orden_Trabajo_ID_OT']} | {s['Estado_Alcanzado']} | {s['Comentario_Frontal'][:60]}")

# 12. Verificar detalle_orden
print("\n--- DETALLE_ORDEN ---")
cursor.execute("SHOW COLUMNS FROM detalle_orden")
for col in cursor.fetchall():
    print(f"  {col['Field']} ({col['Type']})")

cursor.close()
print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETADO")
print("="*60)
