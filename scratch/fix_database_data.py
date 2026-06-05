import os
import sys

# Asegurar ruta del proyecto en el path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from config.database import DB

def fix_database():
    cursor = DB.cursor(dictionary=True)
    print("Iniciando reparación de datos en la base de datos...")
    
    # 1. Obtener todas las órdenes que no están en revisión ni diagnóstico pero no tienen presupuesto
    cursor.execute("""
        SELECT ot.ID_OT, ot.Estado_General, ot.Servicio, ot.Garantia, ot.Presupuesto_ID_Presupuesto
        FROM orden_trabajo ot
        WHERE ot.Presupuesto_ID_Presupuesto IS NULL 
        AND ot.Estado_General NOT IN ('Para Revisión', 'En Diagnóstico', 'Ingresado')
    """)
    ordenes_rotas = cursor.fetchall()
    
    if not ordenes_rotas:
        print("No se encontraron órdenes avanzadas sin presupuesto.")
        cursor.close()
        return

    print(f"Se encontraron {len(ordenes_rotas)} órdenes avanzadas con presupuesto faltante.")

    # Obtener catálogo para vincular un servicio por defecto
    cursor.execute("SELECT ID_Item, Descripcion, Precio_Actual FROM catalogo_inventario")
    items_catalogo = {item['Descripcion']: item for item in cursor.fetchall()}
    
    # Mapeo de servicios a ítems de catálogo para rellenar detalles
    mapeo_servicios = {
        "Limpieza y Mantenimiento": "Limpieza Fisica Completa y Pasta Termica",
        "Formateo e Instalación OS": "Formateo e Instalacion de Windows 11 + Drivers",
        "No enciende": "Diagnostico Tecnico General",
        "Lentitud extrema": "Diagnostico Tecnico General",
        "Otro": "Diagnostico Tecnico General"
    }

    for ord in ordenes_rotas:
        id_ot = ord['ID_OT']
        estado = ord['Estado_General']
        servicio = ord['Servicio'] or 'No enciende'
        
        print(f"\nReparando Orden #{id_ot} (Estado: {estado}, Servicio: {servicio})...")
        
        # Consultar si ya tiene detalles cargados en detalle_orden
        cursor.execute("SELECT SUM(Cantidad * Precio_Unitario_Congelado) as total FROM detalle_orden WHERE Orden_Trabajo_ID_OT = %s", (id_ot,))
        res_detalles = cursor.fetchone()
        monto_total = res_detalles['total'] if res_detalles and res_detalles['total'] is not None else 0.0
        
        # Si no tiene detalles, insertamos un servicio básico basado en el tipo de servicio
        if monto_total == 0.0:
            nombre_servicio_catalogo = mapeo_servicios.get(servicio, "Diagnostico Tecnico General")
            item_catalogo = items_catalogo.get(nombre_servicio_catalogo)
            
            if item_catalogo:
                item_id = item_catalogo['ID_Item']
                item_precio = item_catalogo['Precio_Actual']
                
                print(f"  -> Insertando ítem de servicio '{nombre_servicio_catalogo}' (${item_precio}) en detalle_orden...")
                cursor.execute("""
                    INSERT INTO detalle_orden (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item, Estado_Detalle)
                    VALUES (%s, %s, %s, %s, %s)
                """, (1, item_precio, id_ot, item_id, 'Consumido' if estado == 'Finalizado' else 'Reservado'))
                monto_total = float(item_precio)
            else:
                # Fallback por si no encuentra el catálogo
                print("  -> No se encontró ítem en catálogo. Usando precio de fallback $15000.")
                monto_total = 15000.0
                
        # Crear el presupuesto en la tabla presupuesto
        print(f"  -> Creando presupuesto de ${monto_total} con estado 'Aprobado'...")
        cursor.execute("""
            INSERT INTO presupuesto (Monto_Total_Cotizado, Estado_Presupuesto)
            VALUES (%s, %s)
        """, (monto_total, 'Aprobado'))
        id_presupuesto = cursor.lastrowid
        
        # Vincular el presupuesto a la orden
        print(f"  -> Vinculando Presupuesto #{id_presupuesto} a la Orden #{id_ot}...")
        cursor.execute("""
            UPDATE orden_trabajo 
            SET Presupuesto_ID_Presupuesto = %s
            WHERE ID_OT = %s
        """, (id_presupuesto, id_ot))
        
        # Registrar hito de rectificación
        cursor.execute("""
            INSERT INTO seguimiento_estados (Fecha_Actualizacion, Estado_Alcanzado, Comentario_Frontal, Orden_Trabajo_ID_OT)
            VALUES (NOW(), %s, %s, %s)
        """, (estado, f"Sistema de datos reparado: presupuesto formal de ${monto_total} vinculado con éxito.", id_ot))
        
    DB.commit()
    print("\n¡Reparación de base de datos finalizada con éxito!")
    cursor.close()

if __name__ == '__main__':
    fix_database()
