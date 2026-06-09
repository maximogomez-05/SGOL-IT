"""Migración: Alinear tabla equipo con el DER definitivo"""
import sys
sys.path.insert(0, '.')
from config.database import DB

cursor = DB.cursor(dictionary=True)

print("=== MIGRACIÓN: Tabla equipo ===")
print("Estado actual: tiene Marca_Modelo (una sola columna)")
print("DER definitivo: requiere Marca + Modelo por separado")

# 1. Agregar columnas nuevas
try:
    cursor.execute("ALTER TABLE equipo ADD COLUMN Marca VARCHAR(45) AFTER Numero_Serie")
    print("[OK] Columna Marca agregada")
except Exception as e:
    print(f"[SKIP] Marca: {e}")

try:
    cursor.execute("ALTER TABLE equipo ADD COLUMN Modelo VARCHAR(100) AFTER Marca")
    print("[OK] Columna Modelo agregada")
except Exception as e:
    print(f"[SKIP] Modelo: {e}")

DB.commit()

# 2. Migrar datos de Marca_Modelo -> Marca + Modelo
# Intentamos splitear inteligentemente
cursor.execute("SELECT ID_Equipo, Marca_Modelo FROM equipo")
equipos = cursor.fetchall()

for eq in equipos:
    marca_modelo = eq['Marca_Modelo'] or 'Desconocida'
    # Intentar separar por espacio - primera palabra = marca, resto = modelo
    parts = marca_modelo.strip().split(' ', 1)
    marca = parts[0] if parts else 'Desconocida'
    modelo = parts[1] if len(parts) > 1 else marca_modelo
    
    cursor.execute("UPDATE equipo SET Marca = %s, Modelo = %s WHERE ID_Equipo = %s", (marca, modelo, eq['ID_Equipo']))
    print(f"  Equipo #{eq['ID_Equipo']}: '{marca_modelo}' -> Marca='{marca}', Modelo='{modelo}'")

DB.commit()

# 3. NO dropeamos Marca_Modelo para no romper nada que ya referencia esa columna
# La dejamos como legacy

print("\n=== VERIFICACIÓN FINAL ===")
cursor.execute("SHOW COLUMNS FROM equipo")
for col in cursor.fetchall():
    print(f"  {col['Field']} ({col['Type']})")

cursor.execute("SELECT ID_Equipo, Marca, Modelo, Tipo_Dispositivo FROM equipo LIMIT 5")
for eq in cursor.fetchall():
    print(f"  #{eq['ID_Equipo']}: Marca={eq['Marca']} | Modelo={eq['Modelo']} | Tipo={eq['Tipo_Dispositivo']}")

cursor.close()
print("\n=== MIGRACIÓN COMPLETADA ===")
