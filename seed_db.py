import sys
import os

# Asegurar que la ruta base esté en sys.path
BASE_DIR = 'c:/Users/maxig/OneDrive/Desktop/Programacion III - BD/SGOLIT'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import datetime
from config.database import DB
from werkzeug.security import generate_password_hash

# Importar Clases del Modelo (Paradigma OOP)
from modelos.roles import Rol
from modelos.empleado import Empleado
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.orden_trabajo import OrdenTrabajo
from modelos.inventario import Inventario
from modelos.presupuesto import Presupuesto
from modelos.factura import Factura
from modelos.seguimiento import Seguimiento
from modelos.detalle_orden import DetalleOrden
from modelos.control_calidad import ControlCalidad

def seed():
    cursor = DB.cursor()
    print("Iniciando el poblado (seeding) de la base de datos...")

    # Desactivar temporariamente las foreign keys para limpiar las tablas
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tablas = [
        "roles", "empleado", "legajo_empleado", "cliente", 
        "catalogo_inventario", "equipo", "orden_trabajo", 
        "detalle_orden", "presupuesto", "factura", 
        "seguimiento_estados", "control_calidad", "turno"
    ]
    
    for t in tablas:
        try:
            cursor.execute(f"TRUNCATE TABLE {t}")
            print(f"Tabla '{t}' limpiada (Truncate).")
        except Exception as e:
            print(f"Error al limpiar la tabla '{t}': {e}")
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    DB.commit()
    cursor.close()

    # 1. Registrar Roles
    print("Registrando roles...")
    r1_id = Rol("Administrador").registrar()
    r2_id = Rol("Recepcionista").registrar()
    r3_id = Rol("Tecnico").registrar()

    # 2. Registrar Empleados (OOP)
    print("Registrando empleados...")
    emp_admin = Empleado("Admin General", "admin", "admin123", 1)
    id_admin = emp_admin.registrar()
    
    emp_recep = Empleado("Lucia Recepcionista", "recep", "123", 2)
    id_recep = emp_recep.registrar()
    
    emp_tecnico = Empleado("Mateo Tecnico", "tecnico", "123", 3)
    id_tecnico = emp_tecnico.registrar()

    # 3. Registrar Clientes (OOP)
    print("Registrando clientes...")
    c1 = Cliente("45000001", "Maximo Piriz", "maximo@gmail.com", "3704111222", "123")
    id_c1 = c1.registrar()
    
    c2 = Cliente("45000002", "Lautaro Torres", "lautaro@gmail.com", "3704333444", "123")
    id_c2 = c2.registrar()
    
    c3 = Cliente("45000003", "Julian Gonzalez", "julian@gmail.com", "3704555666", "123")
    id_c3 = c3.registrar()

    # 4. Registrar Catálogo de Inventario (OOP)
    print("Registrando repuestos y mano de obra...")
    i1 = Inventario("Repuesto_Fisico", "Memoria RAM DDR4 8GB Kingston 3200MHz", 25000, 15, 4, "https://compu-ar.com/ram-8gb")
    id_i1 = i1.registrar()
    
    i2 = Inventario("Repuesto_Fisico", "Disco SSD Kingston 480GB SATA3", 42000, 10, 3, "https://compu-ar.com/ssd-480gb")
    id_i2 = i2.registrar()
    
    i3 = Inventario("Repuesto_Fisico", "Pasta Termica Arctic MX-4 (4g)", 12500, 8, 2, "https://compu-ar.com/mx4")
    id_i3 = i3.registrar()
    
    i4 = Inventario("Repuesto_Fisico", "Fuente Gigabyte 650W 80 Plus", 82000, 5, 2, "https://compu-ar.com/fuente-650w")
    id_i4 = i4.registrar()
    
    i5 = Inventario("Repuesto_Fisico", "Placa Madre Gigabyte A520M K V2 AM4", 95000, 4, 1, "https://compu-ar.com/mb-a520")
    id_i5 = i5.registrar()
    
    i6 = Inventario("Repuesto_Fisico", "Disco SSD M.2 NVMe WD Blue 1TB", 89000, 6, 2, "https://compu-ar.com/ssd-1tb")
    id_i6 = i6.registrar()
    
    i7 = Inventario("Servicio_ManoObra", "Diagnostico Tecnico General", 10000, 0, 0, "")
    id_i7 = i7.registrar()
    
    i8 = Inventario("Servicio_ManoObra", "Limpieza Fisica Completa y Pasta Termica", 18000, 0, 0, "")
    id_i8 = i8.registrar()
    
    i9 = Inventario("Servicio_ManoObra", "Formateo e Instalacion de Windows 11 + Drivers", 20000, 0, 0, "")
    id_i9 = i9.registrar()
    
    i10 = Inventario("Servicio_ManoObra", "Reparacion Compleja Placa Madre", 38000, 0, 0, "")
    id_i10 = i10.registrar()
    
    i11 = Inventario("Servicio_ManoObra", "Ensamblaje y Optimizacion de Computadora", 25000, 0, 0, "")
    id_i11 = i11.registrar()

    # 5. Registrar Equipos y Órdenes de Trabajo para el Cliente 1 (Maximo Piriz) - Escenarios de Prueba
    print("Creando escenarios de órdenes de trabajo para Maximo Piriz...")

    # Escenario A: Equipo recién ingresado ("Para Revisión")
    eq1 = Equipo("SN-DELL-111", "Dell Inspiron 3000", "Notebook", id_c1, "Tapa superior rayada, bisagra derecha floja")
    id_eq1 = eq1.registrar()
    ot1 = OrdenTrabajo(id_eq1, id_recep, estado_general="Para Revisión")
    id_ot1 = ot1.registrar()
    Seguimiento.registrar_hito(id_ot1, "Ingresado", "El equipo ingresó al laboratorio para su revisión inicial.")

    # Escenario B: Equipo en diagnóstico ("En Diagnóstico")
    eq2 = Equipo("SN-ASUS-222", "ASUS ZenBook 14", "Notebook", id_c1, "Pantalla con marcas leves, teclado desgastado")
    id_eq2 = eq2.registrar()
    ot2 = OrdenTrabajo(id_eq2, id_recep, estado_general="En Diagnóstico")
    id_ot2 = ot2.registrar()
    Seguimiento.registrar_hito(id_ot2, "Ingresado", "El equipo ingresó al laboratorio para su revisión inicial.")
    Seguimiento.registrar_hito(id_ot2, "En Diagnóstico", "El técnico comenzó el diagnóstico del equipo.")

    # Escenario C: Equipo esperando aprobación de presupuesto ("Esperando Respuesta")
    eq3 = Equipo("SN-GIGABYTE-333", "Sentey Gamer Core i5", "PC de Escritorio", id_c1, "Polvo acumulado en rejillas, le falta un tornillo lateral")
    id_eq3 = eq3.registrar()
    pres3 = Presupuesto(40500, id_eq3) # Diagnostico(10000) + Pasta(12500) + Limpieza(18000) = 40500
    id_pres3 = pres3.registrar()
    ot3 = OrdenTrabajo(id_eq3, id_recep, id_presupuesto=id_pres3, estado_general="Esperando Respuesta")
    id_ot3 = ot3.registrar()
    # Detalles
    DetalleOrden(1, 10000, id_ot3, id_i7).registrar()
    DetalleOrden(1, 12500, id_ot3, id_i3).registrar()
    DetalleOrden(1, 18000, id_ot3, id_i8).registrar()
    # Hitos
    Seguimiento.registrar_hito(id_ot3, "Ingresado", "El equipo ingresó al laboratorio.")
    Seguimiento.registrar_hito(id_ot3, "En Diagnóstico", "El diagnóstico determinó fallas por temperatura.")
    Seguimiento.registrar_hito(id_ot3, "Esperando Respuesta", "Presupuesto formal generado por $40500 en espera de respuesta del cliente.")

    # Escenario D: Equipo en reparación ("En Reparación")
    eq4 = Equipo("SN-HP-444", "HP Pavilion 15", "Notebook", id_c1, "Carcasa sin marcas notorias")
    id_eq4 = eq4.registrar()
    pres4 = Presupuesto(35000, id_eq4) # Diagnostico(10000) + RAM 8GB(25000) = 35000
    id_pres4 = pres4.registrar()
    Presupuesto.actualizar_estado(id_pres4, "Aprobado")
    ot4 = OrdenTrabajo(id_eq4, id_recep, id_presupuesto=id_pres4, estado_general="En Reparación")
    id_ot4 = ot4.registrar()
    # Detalles
    DetalleOrden(1, 10000, id_ot4, id_i7, estado_detalle="Reservado").registrar()
    DetalleOrden(1, 25000, id_ot4, id_i1, estado_detalle="Reservado").registrar()
    # Hitos
    Seguimiento.registrar_hito(id_ot4, "Ingresado", "El equipo ingresó al laboratorio.")
    Seguimiento.registrar_hito(id_ot4, "En Diagnóstico", "Se diagnosticó cuello de botella en RAM.")
    Seguimiento.registrar_hito(id_ot4, "Esperando Respuesta", "Presupuesto formal de $35000 enviado.")
    Seguimiento.registrar_hito(id_ot4, "En Reparación", "El cliente aprobó el presupuesto. Repuestos reservados en stock.")

    # Escenario E: Equipo listo para retirar ("Listo para Entregar")
    eq5 = Equipo("SN-MAC-555", "MacBook Air M1", "Notebook", id_c1, "Rayaduras leves en tapa inferior")
    id_eq5 = eq5.registrar()
    pres5 = Presupuesto(30000, id_eq5) # Diagnostico(10000) + Windows OS(20000) = 30000
    id_pres5 = pres5.registrar()
    Presupuesto.actualizar_estado(id_pres5, "Aprobado")
    ot5 = OrdenTrabajo(id_eq5, id_recep, id_presupuesto=id_pres5, estado_general="Listo para Entregar")
    id_ot5 = ot5.registrar()
    # Detalles
    DetalleOrden(1, 10000, id_ot5, id_i7, estado_detalle="Reservado").registrar()
    DetalleOrden(1, 20000, id_ot5, id_i9, estado_detalle="Reservado").registrar()
    # Control de Calidad
    ControlCalidad(id_ot5, id_tecnico, "38°C en carga", "Geekbench completado", "Instalación limpia finalizada con temperaturas excelentes.").registrar()
    # Hitos
    Seguimiento.registrar_hito(id_ot5, "Ingresado", "El equipo ingresó al laboratorio.")
    Seguimiento.registrar_hito(id_ot5, "En Diagnóstico", "Se requiere reinstalación de sistema operativo.")
    Seguimiento.registrar_hito(id_ot5, "Esperando Respuesta", "Presupuesto formal de $30000 enviado.")
    Seguimiento.registrar_hito(id_ot5, "En Reparación", "Presupuesto aprobado. Iniciando instalación.")
    Seguimiento.registrar_hito(id_ot5, "Listo para Entregar", "Control QA aprobado satisfactoriamente. Equipo listo para retiro.")

    # Escenario F: Equipo finalizado ("Finalizado")
    eq6 = Equipo("SN-THINK-666", "Lenovo ThinkPad T480", "Notebook", id_c1, "Uso laboral normal")
    id_eq6 = eq6.registrar()
    pres6 = Presupuesto(18000, id_eq6) # Limpieza Fisica(18000) = 18000
    id_pres6 = pres6.registrar()
    Presupuesto.actualizar_estado(id_pres6, "Aprobado")
    ot6 = OrdenTrabajo(id_eq6, id_recep, id_presupuesto=id_pres6, estado_general="Finalizado")
    id_ot6 = ot6.registrar()
    # Detalles
    DetalleOrden(1, 18000, id_ot6, id_i8, estado_detalle="Consumido").registrar()
    # Factura
    fact6 = Factura(id_ot6, 18000, "Transferencia", "B", "45000001")
    id_fact6 = fact6.registrar()
    # Hitos
    Seguimiento.registrar_hito(id_ot6, "Ingresado", "El equipo ingresó para mantenimiento.")
    Seguimiento.registrar_hito(id_ot6, "En Diagnóstico", "Limpieza física recomendada.")
    Seguimiento.registrar_hito(id_ot6, "Esperando Respuesta", "Presupuesto formal de $18000 enviado.")
    Seguimiento.registrar_hito(id_ot6, "En Reparación", "Presupuesto aprobado.")
    Seguimiento.registrar_hito(id_ot6, "Listo para Entregar", "Mantenimiento físico y QA aprobados.")
    Seguimiento.registrar_hito(id_ot6, "Finalizado", "Factura Tipo B generada. Pago de $18000 recibido por Transferencia.")

    print("Seeding completado con éxito!")

if __name__ == "__main__":
    seed()
