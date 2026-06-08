"""
seed_db.py - Script para insertar datos de prueba en SGOL-IT.
Ejecutar una vez para popular la BD con clientes, equipos, ordenes y seguimientos de ejemplo.
Todos los clientes tienen password '123' (hasheada).

USO: python seed_db.py
"""

import sys
import os
import datetime
import random
import string

# Asegurar que el path del proyecto está disponible
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from config.database import DB

# ============================================================
# CONFIGURACION DE DATOS DE PRUEBA
# ============================================================

CLIENTES = [
    {"dni": "40123456", "nombre": "Juan Carlos Martinez", "email": "jcmartinez@gmail.com", "telefono": "1155667788"},
    {"dni": "35987654", "nombre": "Maria Laura Gonzalez", "email": "mlgonzalez@hotmail.com", "telefono": "1143218765"},
    {"dni": "42567890", "nombre": "Lucas Andres Fernandez", "email": "lucas.fernandez@gmail.com", "telefono": "1167894532"},
    {"dni": "38456123", "nombre": "Valentina Lopez Suarez", "email": "vlopez@yahoo.com.ar", "telefono": "1198765432"},
    {"dni": "44321789", "nombre": "Santiago Nicolas Ramirez", "email": "sramirez@outlook.com", "telefono": "1134567891"},
    {"dni": "36789012", "nombre": "Camila Sofia Torres", "email": "camilatorres@gmail.com", "telefono": "1176543210"},
    {"dni": "41234567", "nombre": "Mateo Agustin Diaz", "email": "mateodiaz@hotmail.com", "telefono": "1123456789"},
]

PASSWORD_TEMPORAL = "123"

# Equipos variados con servicios asignados
EQUIPOS_Y_ORDENES = [
    # Juan Carlos Martinez - 2 ordenes (una finalizada, una en curso)
    {"cliente_idx": 0, "equipo": {"nro_serie": "SN-DELL-001", "marca": "Dell", "modelo": "Inspiron 3510", "tipo": "Notebook"},
     "orden": {"servicio": "Limpieza y Mantenimiento", "estado": "Finalizado", "garantia": 0, "diagnostico": "Equipo con acumulacion de polvo en ventiladores y disipador. Se realizo limpieza integral y cambio de pasta termica. Temperaturas normalizadas.", "dias_atras": 15}},
    {"cliente_idx": 0, "equipo": {"nro_serie": "SN-DELL-002", "marca": "Dell", "modelo": "Latitude 5420", "tipo": "Notebook"},
     "orden": {"servicio": "Lentitud extrema", "estado": "En Diagnóstico", "garantia": 0, "diagnostico": None, "dias_atras": 2}},

    # Maria Laura Gonzalez - 3 ordenes (2 finalizadas, 1 esperando respuesta)
    {"cliente_idx": 1, "equipo": {"nro_serie": "SN-HP-003", "marca": "HP", "modelo": "Pavilion 15-eh1023", "tipo": "Notebook"},
     "orden": {"servicio": "Formateo e Instalación OS", "estado": "Finalizado", "garantia": 0, "diagnostico": "Se realizo backup de datos, formateo completo e instalacion de Windows 11 Pro con drivers actualizados.", "dias_atras": 30}},
    {"cliente_idx": 1, "equipo": {"nro_serie": "SN-HP-004", "marca": "HP", "modelo": "ProDesk 400 G7", "tipo": "PC de Escritorio"},
     "orden": {"servicio": "No enciende", "estado": "Finalizado", "garantia": 0, "diagnostico": "Fuente de alimentacion defectuosa (capacitor inflado). Se reemplazo fuente ATX 500W. Equipo operativo.", "dias_atras": 20}},
    {"cliente_idx": 1, "equipo": {"nro_serie": "SN-HP-005", "marca": "HP", "modelo": "205 G4 AiO", "tipo": "All-in-One"},
     "orden": {"servicio": "Lentitud extrema", "estado": "Esperando Respuesta", "garantia": 0, "diagnostico": "Disco HDD con sectores defectuosos. Se recomienda reemplazo por SSD 480GB.", "dias_atras": 3}},

    # Lucas Andres Fernandez - 1 orden (en reparacion)
    {"cliente_idx": 2, "equipo": {"nro_serie": "SN-LEN-006", "marca": "Lenovo", "modelo": "IdeaPad 3 15ALC6", "tipo": "Notebook"},
     "orden": {"servicio": "No enciende", "estado": "En Reparación", "garantia": 1, "diagnostico": "Falla en chip de carga del motherboard. Se procede a microsoldadura BGA.", "dias_atras": 5}},

    # Valentina Lopez Suarez - 2 ordenes (1 finalizada, 1 listo para entregar)
    {"cliente_idx": 3, "equipo": {"nro_serie": "SN-ASUS-007", "marca": "ASUS", "modelo": "VivoBook X515JA", "tipo": "Notebook"},
     "orden": {"servicio": "Limpieza y Mantenimiento", "estado": "Finalizado", "garantia": 0, "diagnostico": "Limpieza preventiva completa. Sin fallas detectadas.", "dias_atras": 45}},
    {"cliente_idx": 3, "equipo": {"nro_serie": "SN-EPSON-008", "marca": "Epson", "modelo": "L3250 EcoTank", "tipo": "Impresora"},
     "orden": {"servicio": "Otro", "estado": "Listo para Entregar", "garantia": 0, "diagnostico": "Cabezal de impresion obstruido. Se realizo limpieza quimica y purga de tintas. Test de impresion satisfactorio.", "dias_atras": 4}},

    # Santiago Nicolas Ramirez - 1 orden (para revision)
    {"cliente_idx": 4, "equipo": {"nro_serie": "SN-ACER-009", "marca": "Acer", "modelo": "Nitro 5 AN515-57", "tipo": "Notebook"},
     "orden": {"servicio": "Lentitud extrema", "estado": "Para Revisión", "garantia": 0, "diagnostico": None, "dias_atras": 1}},

    # Camila Sofia Torres - 2 ordenes (ambas finalizadas)
    {"cliente_idx": 5, "equipo": {"nro_serie": "SN-MSI-010", "marca": "MSI", "modelo": "Modern 14 B11MOU", "tipo": "Notebook"},
     "orden": {"servicio": "Formateo e Instalación OS", "estado": "Finalizado", "garantia": 0, "diagnostico": "Formateo completo con instalacion dual boot Windows 11 / Ubuntu 22.04.", "dias_atras": 60}},
    {"cliente_idx": 5, "equipo": {"nro_serie": "SN-CUSTOM-011", "marca": "Custom", "modelo": "PC Gamer (Ryzen 5 5600X)", "tipo": "PC de Escritorio"},
     "orden": {"servicio": "Limpieza y Mantenimiento", "estado": "Finalizado", "garantia": 0, "diagnostico": "Limpieza integral, cambio de pasta termica en CPU y GPU, reorganizacion de cables internos.", "dias_atras": 25}},

    # Mateo Agustin Diaz - 1 orden (en diagnostico)
    {"cliente_idx": 6, "equipo": {"nro_serie": "SN-SAMSUNG-012", "marca": "Samsung", "modelo": "Galaxy Book2 Pro", "tipo": "Notebook"},
     "orden": {"servicio": "No enciende", "estado": "En Diagnóstico", "garantia": 1, "diagnostico": None, "dias_atras": 1}},
]

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def generar_codigo_tracking():
    chars = string.ascii_uppercase + string.digits
    return "OT-" + "".join(random.choices(chars, k=6))


def insertar_cliente(cursor, datos):
    """Inserta un cliente si no existe por DNI. Retorna el ID."""
    cursor.execute("SELECT ID_Cliente FROM cliente WHERE DNI_CUIL = %s", (datos['dni'],))
    existente = cursor.fetchone()
    if existente:
        print(f"  [EXISTE] Cliente {datos['nombre']} (DNI: {datos['dni']}) ya existe con ID {existente[0]}")
        return existente[0]
    
    hashed_pwd = generate_password_hash(PASSWORD_TEMPORAL)
    cursor.execute(
        "INSERT INTO cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web, Password_Cambiada) VALUES (%s, %s, %s, %s, %s, 0)",
        (datos['dni'], datos['nombre'], datos['email'], datos['telefono'], hashed_pwd)
    )
    id_cliente = cursor.lastrowid
    print(f"  [NUEVO] Cliente {datos['nombre']} (DNI: {datos['dni']}) creado con ID {id_cliente}")
    return id_cliente


def insertar_equipo(cursor, datos, id_cliente):
    """Inserta un equipo si no existe por nro_serie. Retorna el ID."""
    cursor.execute("SELECT ID_Equipo FROM equipo WHERE Numero_Serie = %s", (datos['nro_serie'],))
    existente = cursor.fetchone()
    if existente:
        print(f"  [EXISTE] Equipo {datos['modelo']} ya existe con ID {existente[0]}")
        return existente[0]
    
    cursor.execute(
        "INSERT INTO equipo (Numero_Serie, Marca, Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) VALUES (%s, %s, %s, %s, %s)",
        (datos['nro_serie'], datos['marca'], datos['modelo'], datos['tipo'], id_cliente)
    )
    id_equipo = cursor.lastrowid
    print(f"  [NUEVO] Equipo {datos['marca']} {datos['modelo']} ({datos['tipo']}) creado con ID {id_equipo}")
    return id_equipo


def obtener_id_tecnico(cursor):
    """Obtiene el ID del primer empleado con rol 3 (técnico). Si no hay, retorna el primer empleado."""
    cursor.execute("""
        SELECT e.ID_Empleado 
        FROM empleado e 
        JOIN legajo_empleado le ON e.ID_Empleado = le.Empleado_ID_Empleado 
        WHERE le.Roles_ID_Rol = 3 AND e.Activo = 1
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # fallback: primer empleado activo
    cursor.execute("SELECT ID_Empleado FROM empleado WHERE Activo = 1 LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[0]
    
    print("[ERROR] No hay empleados en el sistema. Registre al menos un empleado antes de ejecutar el seed.")
    sys.exit(1)


def obtener_id_recepcionista(cursor):
    """Obtiene el ID del primer empleado con rol 2 (recepcion)."""
    cursor.execute("""
        SELECT e.ID_Empleado 
        FROM empleado e 
        JOIN legajo_empleado le ON e.ID_Empleado = le.Empleado_ID_Empleado 
        WHERE le.Roles_ID_Rol = 2 AND e.Activo = 1
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        return result[0]
    return obtener_id_tecnico(cursor)


def insertar_orden(cursor, id_equipo, id_empleado, datos_orden):
    """Inserta una orden de trabajo con su historial de seguimiento."""
    fecha_creacion = datetime.datetime.now() - datetime.timedelta(days=datos_orden['dias_atras'])
    codigo = generar_codigo_tracking()
    
    cursor.execute(
        """INSERT INTO orden_trabajo 
           (Estado_General, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado, 
            Codigo_Tracking_web, Garantia, Servicio, Diagnostico_Final) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (datos_orden['estado'], fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'), 
         id_equipo, id_empleado, codigo, datos_orden['garantia'], 
         datos_orden.get('servicio'), datos_orden.get('diagnostico'))
    )
    id_ot = cursor.lastrowid
    print(f"  [ORDEN] OT #{id_ot} - {datos_orden['servicio']} - Estado: {datos_orden['estado']} - Codigo: {codigo}")
    
    # Crear historial de seguimiento segun el estado
    estados_progresion = {
        'Para Revisión': ['Ingresado'],
        'En Diagnóstico': ['Ingresado', 'En Diagnóstico'],
        'Esperando Respuesta': ['Ingresado', 'En Diagnóstico', 'Esperando Aprobación'],
        'En Reparación': ['Ingresado', 'En Diagnóstico', 'Esperando Aprobación', 'En Reparación'],
        'Listo para Entregar': ['Ingresado', 'En Diagnóstico', 'Esperando Aprobación', 'En Reparación', 'Listo para Entregar'],
        'Finalizado': ['Ingresado', 'En Diagnóstico', 'Esperando Aprobación', 'En Reparación', 'Listo para Entregar', 'Finalizado'],
    }
    
    comentarios = {
        'Ingresado': 'Equipo recibido en recepcion. Se genera orden de trabajo.',
        'En Diagnóstico': 'El equipo fue derivado al laboratorio para revision tecnica.',
        'Esperando Aprobación': 'Diagnostico completado. Presupuesto enviado al cliente para aprobacion.',
        'En Reparación': 'Presupuesto aprobado por el cliente. Se inicia la reparacion.',
        'Listo para Entregar': 'Reparacion finalizada. Control de calidad aprobado. Listo para retiro.',
        'Finalizado': 'Equipo entregado al cliente. Orden cerrada.',
    }
    
    progresion = estados_progresion.get(datos_orden['estado'], ['Ingresado'])
    
    for i, estado in enumerate(progresion):
        fecha_hito = fecha_creacion + datetime.timedelta(hours=i * random.randint(4, 24))
        cursor.execute(
            """INSERT INTO Seguimiento_Estados 
               (Fecha_Actualizacion, Estado_Alcanzado, Comentario_Frontal, Orden_Trabajo_ID_OT) 
               VALUES (%s, %s, %s, %s)""",
            (fecha_hito.strftime('%Y-%m-%d %H:%M:%S'), estado, 
             comentarios.get(estado, ''), id_ot)
        )
    
    # Si la orden tiene presupuesto (estados avanzados), crear presupuesto
    if datos_orden['estado'] in ('Esperando Respuesta', 'En Reparación', 'Listo para Entregar', 'Finalizado'):
        monto = round(random.uniform(8000, 45000), 2)
        cursor.execute(
            "INSERT INTO presupuesto (Monto_Total_Cotizado, Presupuesto_Preliminar_Web) VALUES (%s, %s)",
            (monto, monto)
        )
        id_presupuesto = cursor.lastrowid
        cursor.execute(
            "UPDATE orden_trabajo SET Presupuesto_ID_Presupuesto = %s WHERE ID_OT = %s",
            (id_presupuesto, id_ot)
        )
        print(f"         Presupuesto: ${monto}")
    
    # Si la orden esta finalizada, crear factura
    if datos_orden['estado'] == 'Finalizado':
        cursor.execute("SELECT Presupuesto_ID_Presupuesto FROM orden_trabajo WHERE ID_OT = %s", (id_ot,))
        row = cursor.fetchone()
        if row and row[0]:
            cursor.execute("SELECT Monto_Total_Cotizado FROM presupuesto WHERE ID_Presupuesto = %s", (row[0],))
            prow = cursor.fetchone()
            if prow:
                monto_factura = float(prow[0])
                metodo = random.choice(['Efectivo', 'Tarjeta Debito', 'Tarjeta Credito', 'Transferencia'])
                fecha_factura = fecha_creacion + datetime.timedelta(days=datos_orden['dias_atras'] - 1)
                cursor.execute(
                    """INSERT INTO factura 
                       (Fecha_Emision, Monto_Total, Metodo_Pago, Orden_Trabajo_ID_OT) 
                       VALUES (%s, %s, %s, %s)""",
                    (fecha_factura.strftime('%Y-%m-%d %H:%M:%S'), monto_factura, metodo, id_ot)
                )
                print(f"         Factura: ${monto_factura} ({metodo})")
    
    return id_ot


# ============================================================
# EJECUCION PRINCIPAL
# ============================================================

def main():
    print("=" * 60)
    print("  SGOL-IT - Seed de Datos de Prueba")
    print("=" * 60)
    
    cursor = DB.cursor()
    
    try:
        # Verificar que existe la columna Password_Cambiada
        cursor.execute("SHOW COLUMNS FROM cliente LIKE 'Password_Cambiada'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE cliente ADD COLUMN Password_Cambiada TINYINT(1) DEFAULT 0")
            print("[MIGRACION] Columna Password_Cambiada creada.\n")
        
        # Obtener empleados disponibles
        id_tecnico = obtener_id_tecnico(cursor)
        id_recepcion = obtener_id_recepcionista(cursor)
        print(f"\n[INFO] Tecnico ID: {id_tecnico} | Recepcionista ID: {id_recepcion}\n")
        
        # Cache de IDs de clientes creados
        ids_clientes = {}
        
        for entry in EQUIPOS_Y_ORDENES:
            cliente_data = CLIENTES[entry['cliente_idx']]
            
            # Insertar cliente (solo una vez)
            if entry['cliente_idx'] not in ids_clientes:
                print(f"\n--- Cliente: {cliente_data['nombre']} ---")
                ids_clientes[entry['cliente_idx']] = insertar_cliente(cursor, cliente_data)
            
            id_cliente = ids_clientes[entry['cliente_idx']]
            
            # Insertar equipo
            id_equipo = insertar_equipo(cursor, entry['equipo'], id_cliente)
            
            # Insertar orden (usar tecnico para ordenes avanzadas, recepcion para las iniciales)
            estado = entry['orden']['estado']
            if estado in ('Para Revisión', 'Ingresado'):
                id_empleado = id_recepcion
            else:
                id_empleado = id_tecnico
            
            insertar_orden(cursor, id_equipo, id_empleado, entry['orden'])
        
        DB.commit()
        
        print("\n" + "=" * 60)
        print(f"  Seed completado exitosamente!")
        print(f"  {len(CLIENTES)} clientes | {len(EQUIPOS_Y_ORDENES)} ordenes")
        print(f"  Password de todos los clientes: '{PASSWORD_TEMPORAL}'")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        try:
            DB.conexion.rollback()
        except:
            pass
    finally:
        cursor.close()


if __name__ == '__main__':
    main()
