import sys
sys.path.insert(0, '.')
from config.database import DB

cursor = DB.cursor(dictionary=True)
cursor.execute("SELECT ID_Equipo, Marca, Modelo FROM equipo WHERE Marca = 'Desconocida'")
records = cursor.fetchall()

print(f"Encontrados {len(records)} registros con marca Desconocida")

for r in records:
    id_eq = r['ID_Equipo']
    modelo = r['Modelo']
    if ' ' in modelo:
        parts = modelo.split(' ', 1)
        nueva_marca = parts[0]
        nuevo_modelo = parts[1]
        cursor.execute("UPDATE equipo SET Marca = %s, Modelo = %s WHERE ID_Equipo = %s", (nueva_marca, nuevo_modelo, id_eq))
        print(f"Fijado ID {id_eq}: Marca={nueva_marca}, Modelo={nuevo_modelo}")

DB.commit()
cursor.close()
